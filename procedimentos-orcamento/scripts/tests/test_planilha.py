import json
import tempfile
import unittest
from pathlib import Path

from apoio import rodar, tem
from apoio_xlsx import criar_xlsx, lista_exemplo

import planilha as pl


class Leitura(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo = Path(self.pasta.name) / "servicos.xlsx"
        criar_xlsx(self.arquivo, [
            lista_exemplo(),
            {"nome": "Resumo", "estado": "hidden", "celulas": {
                "A1": ("inline", "Total"), "B1": ("f", "SUM(Orçamento!F6:F7)", 750.0),
                "C1": ("b", True), "D1": ("e", "#N/A")}},
        ])

    def tearDown(self):
        self.pasta.cleanup()

    def test_le_tipos_de_celula(self):
        with pl.ler_pasta(self.arquivo) as pasta:
            orc = pasta.ler("Orçamento")
            resumo = pasta.ler("Resumo")
        self.assertEqual(orc["B6"].valor, "Piso cerâmico")
        self.assertEqual(orc["A7"].valor, "1.10")
        self.assertEqual(orc["D6"].valor, 10)
        self.assertEqual(resumo["A1"].valor, "Total")
        self.assertEqual(resumo["B1"].formula, "SUM(Orçamento!F6:F7)")
        self.assertEqual(resumo["B1"].valor, 750.0)
        self.assertIs(resumo["C1"].valor, True)
        self.assertEqual(resumo["D1"].tipo, "e")

    def test_formula_compartilhada_e_expandida(self):
        with pl.ler_pasta(self.arquivo) as pasta:
            orc = pasta.ler("Orçamento")
        self.assertEqual(orc["F6"].formula, "D6*E6")
        self.assertEqual(orc["F7"].formula, "D7*E7")

    def test_abas_e_visibilidade(self):
        with pl.ler_pasta(self.arquivo) as pasta:
            abas = {a["nome"]: a["estado"] for a in pasta.abas}
        self.assertEqual(abas, {"Orçamento": "visible", "Resumo": "hidden"})


class Traducao(unittest.TestCase):
    def test_respeita_ancoras_e_textos(self):
        traduzida = pl.traduzir_formula('SUM($A$1:A1)*B$2&"A1"&\'Plan A1\'!C3', 2, 1)
        self.assertEqual(traduzida, 'SUM($A$1:B3)*C$2&"A1"&\'Plan A1\'!D5')

    def test_intervalos_de_linhas_e_colunas(self):
        self.assertEqual(pl.traduzir_formula("SUM(A:A)+SUM(1:2)+LOG10(B2)", 1, 1), "SUM(B:B)+SUM(2:3)+LOG10(C3)")

    @unittest.skipUnless(tem("openpyxl"), "openpyxl não instalado")
    def test_igual_ao_openpyxl(self):
        from openpyxl.formula.translate import Translator
        for formula in ["D6*E6", "SUM($A$1:A1)*B$2", "IF(A1>0,B1,C$1)", "Plan2!A1+'Plan 3'!$B2", "SUM(A:A)"]:
            esperado = Translator("=" + formula, origin="D6").translate_formula("F9")[1:]
            self.assertEqual(pl.traduzir_formula(formula, 3, 2), esperado, formula)


class Mapa(unittest.TestCase):
    def test_detecta_cabecalho_colunas_e_itens(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = criar_xlsx(Path(pasta) / "s.xlsx", [lista_exemplo(), {"nome": "Oculta", "estado": "hidden"}])
            mapa = pl.mapear(arquivo)
            aba = next(a for a in mapa["abas"] if a["nome"] == "Orçamento")
            cab = aba["cabecalho"]
            self.assertEqual(cab["linha"], 4)
            self.assertEqual(cab["colunas"]["item"], "A")
            self.assertEqual(cab["colunas"]["descricao"], "B")
            self.assertEqual(cab["colunas"]["unidade"], "C")
            self.assertEqual(cab["colunas"]["quantidade"], ["D"])
            self.assertEqual(cab["colunas"]["preco_unitario"], "E")
            self.assertEqual(aba["itens_provaveis"], 2)
            self.assertEqual(aba["agrupadores_provaveis"], 1)
            self.assertEqual(aba["primeira_coluna_livre"], "G")
            self.assertIn("Oculta", [a["nome"] for a in mapa["abas"] if a["estado"] == "hidden"])
            self.assertEqual(mapa["riscos_de_gravacao"], [])

    def test_imagem_existente_gera_risco(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = criar_xlsx(Path(pasta) / "s.xlsx", [lista_exemplo()], imagem_na_aba=0)
            mapa = pl.mapear(arquivo)
            self.assertEqual(mapa["recursos"]["por_aba"]["Orçamento"]["imagens"], 1)
            self.assertTrue(mapa["riscos_de_gravacao"])


class Verificacao(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.original = criar_xlsx(self.dir / "original.xlsx", [lista_exemplo()])
        self.foto = pl.snapshot(self.original)

    def tearDown(self):
        self.pasta.cleanup()

    def test_mesmo_arquivo_passa(self):
        self.assertTrue(pl.verificar(self.foto, self.original)["ok"])

    def test_celula_alterada_e_apontada(self):
        alterado = criar_xlsx(self.dir / "alterado.xlsx", [lista_exemplo(quantidade_item_1=11)])
        relatorio = pl.verificar(self.foto, alterado)
        self.assertFalse(relatorio["ok"])
        self.assertTrue(any("Orçamento!D6" in e for e in relatorio["erros"]))

    def test_colunas_novas_a_direita_e_abas_novas_sao_aceitas(self):
        aba = lista_exemplo()
        aba["celulas"].update({"G4": ("s", "QTD LEVANTADA"), "G6": ("f", "'ITEM 1.1'!$G$8", 9.5)})
        novo = criar_xlsx(self.dir / "novo.xlsx", [aba, {"nome": "ITEM 1.1", "celulas": {"G8": ("n", 9.5)}}])
        self.assertTrue(pl.verificar(self.foto, novo, colunas_novas={"Orçamento": 7})["ok"])
        self.assertFalse(pl.verificar(self.foto, novo, colunas_novas={"Orçamento": 8})["ok"])

    def test_formula_sem_cache_continua_igual(self):
        aba = lista_exemplo()
        aba["celulas"]["F6"] = ("f", "D6*E6", None)
        aba["celulas"]["F7"] = ("f", "D7*E7", None)
        novo = criar_xlsx(self.dir / "sem_cache.xlsx", [aba])
        self.assertTrue(pl.verificar(self.foto, novo)["ok"], pl.verificar(self.foto, novo)["erros"])

    def test_imagem_perdida_e_erro(self):
        com_imagem = criar_xlsx(self.dir / "com_imagem.xlsx", [lista_exemplo()], imagem_na_aba=0)
        relatorio = pl.verificar(pl.snapshot(com_imagem), self.original)
        self.assertFalse(relatorio["ok"])
        self.assertTrue(any("imagens" in e for e in relatorio["erros"]))

    def test_mesclagem_perdida_e_erro(self):
        aba = lista_exemplo()
        aba["mescladas"] = []
        relatorio = pl.verificar(self.foto, criar_xlsx(self.dir / "sem_merge.xlsx", [aba]))
        self.assertFalse(relatorio["ok"])


class Cli(unittest.TestCase):
    def test_mapear_snapshot_verificar(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            arquivo = criar_xlsx(pasta / "s.xlsx", [lista_exemplo()])
            processo = rodar("planilha.py", "mapear", arquivo, "--saida", pasta / "mapa.json", "--md", pasta / "mapa.md")
            self.assertEqual(processo.returncode, 0, processo.stderr)
            self.assertIn("Orçamento", (pasta / "mapa.md").read_text(encoding="utf-8"))
            processo = rodar("planilha.py", "snapshot", arquivo, "--saida", pasta / "foto.json.gz")
            self.assertEqual(processo.returncode, 0, processo.stderr)
            processo = rodar("planilha.py", "verificar", "--snapshot", pasta / "foto.json.gz", "--arquivo", arquivo)
            self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
            outro = criar_xlsx(pasta / "outro.xlsx", [lista_exemplo(quantidade_item_1=99)])
            processo = rodar("planilha.py", "verificar", "--snapshot", pasta / "foto.json.gz", "--arquivo", outro)
            self.assertEqual(processo.returncode, 1)
            self.assertFalse(json.loads(processo.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
