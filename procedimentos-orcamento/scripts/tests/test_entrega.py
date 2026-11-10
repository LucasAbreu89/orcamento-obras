import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from apoio import escrever_json, rodar, tem
from apoio_xlsx import criar_xlsx, lista_exemplo

import planilha as pl

PRECISA = tem("openpyxl") and tem("PIL")


def lista_com_indireto():
    aba = lista_exemplo()
    aba["celulas"].update({"A8": ("s", "1.2"), "B8": ("s", "Administração local"), "C8": ("s", "mês"),
                           "D8": ("n", 6)})
    return aba


def montar_execucao(raiz, imagem_na_planilha=False):
    for pasta in ("fontes", "dados", "evidencias", "planilha", "conferencia"):
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    original = criar_xlsx(raiz / "planilha" / "ORIGINAL_s.xlsx", [lista_com_indireto()],
                          imagem_na_aba=0 if imagem_na_planilha else None)
    shutil.copy2(original, raiz / "planilha" / "s_TRABALHO.xlsx")
    pl.salvar_snapshot(pl.snapshot(original), raiz / "fontes" / "snapshot.json.gz")
    from PIL import Image, ImageDraw
    imagem = Image.new("RGB", (2000, 1200), "white")
    ImageDraw.Draw(imagem).rectangle([200, 200, 1800, 1000], outline="red", width=12)
    imagem.save(raiz / "evidencias" / "planta_pisos.png")
    dados = {
        "versao": "levantamento/1", "obra": "Obra de teste",
        "planilha": {"recebida": "planilha/ORIGINAL_s.xlsx", "trabalho": "planilha/s_TRABALHO.xlsx",
                     "entrega": "planilha/s_LEVANTAMENTO.xlsx", "snapshot": "fontes/snapshot.json.gz",
                     "listas": [{"aba": "Orçamento", "linha_cabecalho": 4,
                                 "colunas": {"item": "A", "descricao": "B", "unidade": "C", "quantidade": "D"}}]},
        "criterios": [{"id": "C01", "familia": "Pisos", "regra": "Projeção do contorno interno", "fonte": "11"}],
        "pendencias": [{"id": "D001", "natureza": "falta de dado", "itens": ["1.10"],
                        "pergunta": "Qual o comprimento da parede sul?", "responsavel": "Projetista", "situacao": "aberta"}],
        "itens": [
            {"chave": "Orçamento!6", "id": "1.1", "descricao": "Piso cerâmico", "unidade": "m²", "natureza": "medivel",
             "estado": "CONFIRMADO", "criterio": "C01",
             "parcelas": [{"id": "A01", "dimensoes": [3.2, 2.4], "origem": "cotas", "unidade": "m²"},
                          {"id": "A02", "dimensoes": [0.8, 0.18], "origem": "cotas", "unidade": "m²"},
                          {"id": "D01", "dimensoes": [0.3, 0.4], "sinal": -1, "origem": "cotas", "unidade": "m²"}],
             "evidencias": [{"arquivo": "evidencias/planta_pisos.png", "legenda": "A01, A02 e D01",
                             "parcelas": ["A01", "A02", "D01"]}],
             "texto": {"entrou": "Sala e faixa da porta", "ficou_fora": "Shaft D01", "falta": "Nada"}},
            {"chave": "Orçamento!7", "id": "1.10", "descricao": "Rodapé cerâmico", "unidade": "m", "natureza": "medivel",
             "estado": "SUBTOTAL", "criterio": "C01", "pendencias": ["D001"],
             "parcelas": [{"id": "S01", "dimensoes": [4.2], "origem": "cotas", "unidade": "m"},
                          {"id": "S02", "dimensoes": [None], "origem": "cotas", "unidade": "m", "refs": ["D001"]}],
             "evidencias": [{"arquivo": "evidencias/planta_pisos.png", "legenda": "S01 medido; S02 sem cota",
                             "parcelas": ["S01", "S02"]}],
             "texto": {"entrou": "Parede norte", "ficou_fora": "", "falta": "Parede sul (D001)"},
             "observacao": "Falta a parede sul (D001)"},
            {"chave": "Orçamento!8", "id": "1.2", "descricao": "Administração local", "unidade": "mês",
             "natureza": "indireto", "estado": "NÃO APLICÁVEL",
             "observacao": "Custo indireto — definir pela engenharia"},
        ],
    }
    return escrever_json(raiz / "dados" / "levantamento.json", dados)


def duas_listas():
    """Uma aba com duas listas: cabeçalhos nas linhas 4 e 12."""
    celulas = {"A1": ("s", "ORÇAMENTO")}
    for linha in (4, 12):
        celulas.update({f"A{linha}": ("s", "ITEM"), f"B{linha}": ("s", "DESCRIÇÃO"), f"C{linha}": ("s", "UNID."),
                        f"D{linha}": ("s", "QUANT.")})
    celulas.update({"A5": ("s", "1"), "B5": ("s", "PISOS"),
                    "A6": ("s", "1.1"), "B6": ("s", "Piso cerâmico"), "C6": ("s", "m²"), "D6": ("n", 10),
                    "A13": ("s", "2"), "B13": ("s", "ADMINISTRAÇÃO"),
                    "A14": ("s", "2.1"), "B14": ("s", "Administração local"), "C14": ("s", "mês"), "D14": ("n", 6)})
    return {"nome": "Orçamento", "celulas": celulas}


def montar_duas_listas(raiz, imagem_na_planilha=False):
    json_path = montar_execucao(raiz, imagem_na_planilha)
    original = criar_xlsx(raiz / "planilha" / "ORIGINAL_s.xlsx", [duas_listas()],
                          imagem_na_aba=0 if imagem_na_planilha else None)
    shutil.copy2(original, raiz / "planilha" / "s_TRABALHO.xlsx")
    pl.salvar_snapshot(pl.snapshot(original), raiz / "fontes" / "snapshot.json.gz")
    dados = json.loads(json_path.read_text(encoding="utf-8"))
    colunas = {"item": "A", "descricao": "B", "unidade": "C", "quantidade": "D"}
    dados["planilha"]["listas"] = [{"aba": "Orçamento", "linha_cabecalho": 4, "linha_final": 10, "colunas": colunas},
                                   {"aba": "Orçamento", "linha_cabecalho": 12, "colunas": colunas}]
    piso, _, indireto = dados["itens"]
    indireto["chave"] = "Orçamento!14"
    dados["itens"] = [piso, indireto]
    dados["pendencias"] = []
    return escrever_json(json_path, dados)


@unittest.skipUnless(PRECISA, "openpyxl e Pillow não instalados")
class Geracao(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.raiz = Path(self.pasta.name)

    def tearDown(self):
        self.pasta.cleanup()

    def gerar(self, json_path, *extra):
        processo = rodar("gerar_planilha.py", "--levantamento", json_path, *extra)
        return processo

    def validar(self, json_path, *extra):
        processo = rodar("validar_entrega.py", "--levantamento", json_path, *extra)
        relatorio = json.loads(processo.stdout) if processo.stdout.strip().startswith("{") else None
        return processo, relatorio

    def test_gera_no_mesmo_arquivo_e_valida(self):
        json_path = montar_execucao(self.raiz)
        processo = self.gerar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        entrega = self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx"
        with pl.ler_pasta(entrega) as pasta:
            orc = pasta.ler("Orçamento")
            memoria = pasta.ler("ITEM 1.1")
            abas = [a["nome"] for a in pasta.abas]
            imagens = pasta.recursos()["por_aba"]["ITEM 1.1"]["imagens"]
        self.assertEqual(orc["G4"].valor, "QTD LEVANTADA")
        self.assertAlmostEqual(orc["G6"].valor, 3.2 * 2.4 + 0.8 * 0.18 - 0.3 * 0.4)
        self.assertEqual(orc["H6"].valor, "CONFIRMADO")
        self.assertEqual(orc["G7"].valor, "")
        self.assertEqual(orc["H7"].valor, "SUBTOTAL")
        self.assertEqual(orc["H8"].valor, "NÃO APLICÁVEL")
        self.assertEqual(orc["D6"].valor, 10)
        self.assertAlmostEqual(memoria["G8"].valor, 7.704)
        self.assertEqual(memoria["G9"].valor, "CONFIRMADO")
        self.assertGreaterEqual(imagens, 1)
        for nome in ("Resumo do levantamento", "Pendências", "Premissas", "Critérios", "Fontes", "ITEM 1.10", "ITEM 1.2"):
            self.assertIn(nome, abas)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        self.assertTrue(relatorio["ok"], relatorio["erros"])

    def test_imagem_e_reduzida(self):
        json_path = montar_execucao(self.raiz)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        from PIL import Image
        with zipfile.ZipFile(self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx") as pacote:
            midias = [n for n in pacote.namelist() if n.startswith("xl/media/")]
            self.assertTrue(midias)
            with pacote.open(midias[0]) as fluxo:
                self.assertLessEqual(Image.open(fluxo).size[0], 1400)

    def test_validador_aponta_celula_original_alterada(self):
        json_path = montar_execucao(self.raiz)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        import openpyxl
        entrega = self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx"
        wb = openpyxl.load_workbook(entrega)
        wb["Orçamento"]["D6"] = 999
        wb.save(entrega)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 1)
        self.assertTrue(any("Orçamento!D6" in e for e in relatorio["erros"]))

    def test_validador_aponta_qtd_ligada_a_quantidade_recebida_ou_com_iferror(self):
        json_path = montar_execucao(self.raiz)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        import openpyxl
        entrega = self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx"
        wb = openpyxl.load_workbook(entrega)
        wb["Orçamento"]["G6"] = "=D6"
        wb["Orçamento"]["G7"] = "=IFERROR('ITEM 1.10'!$G$8,0)"
        wb.save(entrega)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 1)
        self.assertTrue(any("Orçamento!G6" in e for e in relatorio["erros"]))
        self.assertTrue(any("IFERROR" in e for e in relatorio["erros"]))

    def test_planilha_com_imagem_vai_para_arquivo_separado(self):
        json_path = montar_execucao(self.raiz, imagem_na_planilha=True)
        processo = self.gerar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        self.assertEqual(json.loads(processo.stdout)["modo"], "arquivo_separado")
        with pl.ler_pasta(self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx") as pasta:
            abas = [a["nome"] for a in pasta.abas]
        self.assertIn("Orçamento (cópia)", abas)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)

    def test_duas_listas_na_mesma_aba_no_mesmo_arquivo(self):
        json_path = montar_duas_listas(self.raiz)
        processo = self.gerar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        with pl.ler_pasta(self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx") as pasta:
            orc = pasta.ler("Orçamento")
        self.assertEqual(orc["E4"].valor, "QTD LEVANTADA")
        self.assertEqual(orc["E12"].valor, "QTD LEVANTADA")
        self.assertEqual(orc["F14"].valor, "NÃO APLICÁVEL")
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)

    def test_duas_listas_no_arquivo_separado_copiam_agrupadores_e_linha_original(self):
        json_path = montar_duas_listas(self.raiz, imagem_na_planilha=True)
        processo = self.gerar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        with pl.ler_pasta(self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx") as pasta:
            abas = [a["nome"] for a in pasta.abas]
            primeira = pasta.ler("Orçamento (cópia)")
            segunda = pasta.ler("Orçamento (cópia 2)")
        textos_primeira = {c.valor for c in primeira.values()}
        self.assertIn("PISOS", textos_primeira)
        self.assertNotIn("Administração local", textos_primeira)
        self.assertIn("Administração local", {c.valor for c in segunda.values()})
        self.assertIn("LINHA ORIGINAL", textos_primeira)
        self.assertIn(6, textos_primeira)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)

    def test_entrega_fora_da_execucao_e_recusada(self):
        json_path = montar_execucao(self.raiz / "execucao")
        processo = self.gerar(json_path, "--saida", self.raiz / "servicos_entregue.xlsx")
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("execução", processo.stdout + processo.stderr)

    def test_sugestoes_comparacao_e_limitacoes_viram_abas(self):
        json_path = montar_execucao(self.raiz)
        dados = json.loads(json_path.read_text(encoding="utf-8"))
        dados["sugestoes"] = [{"id": "S01", "servico": "Rodapé do depósito", "motivo": "piso novo sem rodapé na lista"}]
        dados["comparacao"] = [{"chave": "Orçamento!6", "referencia": 10, "fonte": "coluna QUANT. (D)",
                                "classe": "comparável", "explicacao": "faixa da porta incluída"}]
        dados["limitacoes"] = ["Planilha não aberta no Excel"]
        escrever_json(json_path, dados)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        with pl.ler_pasta(self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx") as pasta:
            sugestoes = {c.valor for c in pasta.ler("Sugestões").values()}
            comparacao = pasta.ler("Comparação")
            resumo = {c.valor for c in pasta.ler("Resumo do levantamento").values()}
        self.assertIn("Rodapé do depósito", sugestoes)
        delta = next(c.valor for ref, c in comparacao.items() if ref.startswith("J") and ref != "J1")
        self.assertAlmostEqual(delta, 7.704 - 10)
        self.assertIn("Planilha não aberta no Excel", resumo)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)

    def test_validador_aponta_item_da_lista_ausente_do_json(self):
        json_path = montar_execucao(self.raiz)
        dados = json.loads(json_path.read_text(encoding="utf-8"))
        dados["itens"] = [i for i in dados["itens"] if i["chave"] != "Orçamento!7"]
        dados["pendencias"] = []
        escrever_json(json_path, dados)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 1)
        self.assertTrue(any("Orçamento!7" in e for e in relatorio["erros"]))
        dados["planilha"]["listas"][0]["linhas_ignoradas"] = [{"linha": 7, "motivo": "subtotal informativo"}]
        escrever_json(json_path, dados)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)

    def test_validador_aponta_fonte_alterada(self):
        json_path = montar_execucao(self.raiz)
        projeto = self.raiz / "projeto"
        projeto.mkdir()
        fonte = projeto / "ARQ.pdf"
        fonte.write_bytes(b"%PDF original")
        import hashlib
        escrever_json(self.raiz / "fontes" / "inventario.json", {"fontes": [
            {"id": "F001", "caminho": str(fonte), "sha256": hashlib.sha256(fonte.read_bytes()).hexdigest()}]})
        self.assertEqual(self.gerar(json_path).returncode, 0)
        self.assertEqual(self.validar(json_path)[0].returncode, 0)
        fonte.write_bytes(b"%PDF alterado")
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 1)
        self.assertTrue(any("ARQ.pdf" in e for e in relatorio["erros"]))

    def test_arquivo_separado_com_entrega_xlsm_vira_xlsx_e_valida(self):
        json_path = montar_execucao(self.raiz, imagem_na_planilha=True)
        dados = json.loads(json_path.read_text(encoding="utf-8"))
        dados["planilha"]["entrega"] = "planilha/s_LEVANTAMENTO.xlsm"
        escrever_json(json_path, dados)
        processo = self.gerar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        self.assertTrue(json.loads(processo.stdout)["entrega"].endswith(".xlsx"))
        processo, relatorio = self.validar(json_path)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)

    def test_json_com_erro_nao_gera(self):
        json_path = montar_execucao(self.raiz)
        dados = json.loads(json_path.read_text(encoding="utf-8"))
        dados["itens"][0]["parcelas"][0]["dimensoes"] = [3.2, None]
        escrever_json(json_path, dados)
        processo = self.gerar(json_path)
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("sem valor", processo.stdout + processo.stderr)
        self.assertFalse((self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx").exists())

    def test_saida_nao_sobrescreve_a_copia_de_trabalho(self):
        json_path = montar_execucao(self.raiz)
        processo = self.gerar(json_path, "--saida", self.raiz / "planilha" / "s_TRABALHO.xlsx")
        self.assertNotEqual(processo.returncode, 0)

    @unittest.skipUnless(shutil.which("soffice") or Path("/Applications/LibreOffice.app").exists(),
                         "LibreOffice não instalado")
    def test_recalculo_independente_confere(self):
        json_path = montar_execucao(self.raiz)
        self.assertEqual(self.gerar(json_path).returncode, 0)
        recalculado = self.raiz / "conferencia" / "recalculado.xlsx"
        caderno = self.raiz / "conferencia" / "caderno.pdf"
        processo = rodar("recalcular.py", self.raiz / "planilha" / "s_LEVANTAMENTO.xlsx", "--saida", recalculado,
                         "--pdf", caderno)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        self.assertTrue(caderno.read_bytes().startswith(b"%PDF"))
        with pl.ler_pasta(recalculado) as pasta:
            self.assertAlmostEqual(pasta.ler("ITEM 1.1")["G8"].valor, 7.704)
        processo, relatorio = self.validar(json_path, "--recalculado", recalculado)
        self.assertEqual(processo.returncode, 0, processo.stdout + processo.stderr)
        self.assertEqual(relatorio["resumo"]["recalculo"], "executado")


if __name__ == "__main__":
    unittest.main()
