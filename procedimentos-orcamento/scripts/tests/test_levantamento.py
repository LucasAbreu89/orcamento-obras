import copy
import tempfile
import unittest
from pathlib import Path

from apoio import escrever_json

import levantamento as lv


def base(raiz):
    (raiz / "evidencias").mkdir(parents=True, exist_ok=True)
    (raiz / "evidencias" / "item_2.1.png").write_bytes(b"png")
    return {
        "versao": "levantamento/1",
        "obra": "Obra exemplo",
        "planilha": {"recebida": "planilha/ORIGINAL_s.xlsx", "trabalho": "planilha/s_TRABALHO.xlsx",
                     "entrega": "planilha/s_LEVANTAMENTO.xlsx", "snapshot": "fontes/snapshot.json.gz",
                     "listas": [{"aba": "Orçamento", "linha_cabecalho": 4,
                                 "colunas": {"item": "A", "descricao": "B", "unidade": "C", "quantidade": "D"}}]},
        "criterios": [{"id": "C01", "familia": "Pintura", "regra": "por face", "fonte": "11"}],
        "premissas": [{"id": "P001", "itens": ["2.1"], "parametro": "altura", "valor": "2,70 m"}],
        "pendencias": [{"id": "D001", "itens": ["2.2"], "pergunta": "Qual a altura?"}],
        "itens": [
            {"chave": "Orçamento!12", "id": "2.1", "descricao": "Pintura", "unidade": "m²", "natureza": "medivel",
             "estado": "CONFIRMADO", "criterio": "C01",
             "parcelas": [
                 {"id": "S01", "dimensoes": [4.2, 2.7], "origem": "cotas"},
                 {"id": "S02", "dimensoes": [3.1, 2.7], "origem": "cotas"},
                 {"id": "V01", "dimensoes": [0.8, 2.1], "sinal": -1, "origem": "indicado"}],
             "evidencias": [{"arquivo": "evidencias/item_2.1.png", "legenda": "faces", "parcelas": ["S01", "S02", "V01"]}],
             "texto": {"entrou": "faces", "ficou_fora": "porta", "falta": "nada"}},
            {"chave": "Orçamento!13", "id": "2.2", "descricao": "Administração local", "unidade": "mês",
             "natureza": "indireto", "estado": "NÃO APLICÁVEL", "observacao": "Custo indireto — definir pela engenharia"},
        ],
    }


class Validacao(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.raiz = Path(self.pasta.name)
        self.dados = base(self.raiz)

    def tearDown(self):
        self.pasta.cleanup()

    def erros(self, dados):
        return lv.validar(dados, self.raiz)[0]

    def test_exemplo_valido(self):
        erros, avisos = lv.validar(self.dados, self.raiz)
        self.assertEqual(erros, [])
        self.assertEqual(avisos, [])

    def test_chave_repetida(self):
        self.dados["itens"][1]["chave"] = "Orçamento!12"
        self.assertTrue(any("repetida" in e for e in self.erros(self.dados)))

    def test_chave_fora_das_listas(self):
        self.dados["itens"][0]["chave"] = "Outra!12"
        self.assertTrue(any("listas" in e for e in self.erros(self.dados)))

    def test_pendente_sem_pendencia(self):
        self.dados["itens"][1].update(estado="PENDENTE")
        self.assertTrue(any("pendência" in e for e in self.erros(self.dados)))

    def test_premissa_exige_premissa_ou_medicao_grafica(self):
        item = self.dados["itens"][0]
        item["estado"] = "PREMISSA"
        self.assertTrue(self.erros(self.dados))
        item["premissas"] = ["P001"]
        self.assertEqual(self.erros(self.dados), [])
        item["premissas"] = []
        item["parcelas"][0]["origem"] = "medicao_grafica"
        self.assertEqual(self.erros(self.dados), [])

    def test_nao_aplicavel_exige_motivo(self):
        self.dados["itens"][1]["observacao"] = ""
        self.assertTrue(any("motivo" in e for e in self.erros(self.dados)))

    def test_confirmado_com_parcela_sem_valor(self):
        self.dados["itens"][0]["parcelas"][0]["dimensoes"] = [4.2, None]
        self.assertTrue(any("sem valor" in e for e in self.erros(self.dados)))

    def test_item_fisico_exige_evidencia_ou_justificativa(self):
        item = self.dados["itens"][0]
        item["evidencias"] = []
        self.assertTrue(any("evidência" in e for e in self.erros(self.dados)))
        item["sem_representacao_grafica"] = "serviço sem desenho próprio"
        self.assertEqual(self.erros(self.dados), [])

    def test_evidencia_inexistente(self):
        self.dados["itens"][0]["evidencias"][0]["arquivo"] = "evidencias/nao_existe.png"
        self.assertTrue(any("não encontrada" in e for e in self.erros(self.dados)))

    def test_referencia_a_pendencia_inexistente(self):
        self.dados["itens"][0].update(estado="SUBTOTAL", pendencias=["D999"])
        self.assertTrue(any("D999" in e for e in self.erros(self.dados)))

    def test_estado_e_origem_invalidos(self):
        dados = copy.deepcopy(self.dados)
        dados["itens"][0]["estado"] = "ESTIMATIVA"
        dados["itens"][0]["parcelas"][0]["origem"] = "chute"
        erros = self.erros(dados)
        self.assertTrue(any("estado" in e for e in erros))
        self.assertTrue(any("origem" in e for e in erros))

    def test_parcela_que_nao_aparece_no_print_e_erro(self):
        self.dados["itens"][0]["evidencias"][0]["parcelas"] = ["S01"]
        self.assertTrue(any("S02" in e for e in self.erros(self.dados)))

    def test_confirmado_nao_pode_depender_de_premissa_ou_medicao_grafica(self):
        item = self.dados["itens"][0]
        item["parcelas"][0]["refs"] = ["P001"]
        self.assertTrue(any("PREMISSA" in e for e in self.erros(self.dados)))
        item["parcelas"][0]["refs"] = []
        item["parcelas"][0]["origem"] = "medicao_grafica"
        self.assertTrue(any("PREMISSA" in e for e in self.erros(self.dados)))

    def test_unidade_da_parcela_precisa_bater_com_a_do_item(self):
        item = self.dados["itens"][0]
        item["parcelas"][0]["unidade"] = "m"
        self.assertTrue(any("unidade" in e for e in self.erros(self.dados)))
        item["parcelas"][0]["unidade"] = "m2"
        self.assertEqual(self.erros(self.dados), [])

    def test_item_mensuravel_excluido_mostra_ou_explica(self):
        item = self.dados["itens"][0]
        item.update(estado="NÃO APLICÁVEL", observacao="Piso existente mantido", evidencias=[], parcelas=[])
        self.assertTrue(any("evidência" in e for e in self.erros(self.dados)))
        item["sem_representacao_grafica"] = "a legenda não distingue o piso mantido"
        self.assertEqual(self.erros(self.dados), [])

    def test_item_por_parametro_tambem_exige_print_ou_explicacao(self):
        item = self.dados["itens"][0]
        item["natureza"] = "parametro"
        item["evidencias"] = []
        self.assertTrue(any("evidência" in e for e in self.erros(self.dados)))

    def test_varias_listas_na_mesma_aba(self):
        self.dados["planilha"]["listas"] = [
            {"aba": "Orçamento", "linha_cabecalho": 4, "linha_final": 15},
            {"aba": "Orçamento", "linha_cabecalho": 20}]
        listas = self.dados["planilha"]["listas"]
        self.assertEqual(lv.lista_do_item(listas, "Orçamento", 12), 0)
        self.assertEqual(lv.lista_do_item(listas, "Orçamento", 25), 1)
        self.assertIsNone(lv.lista_do_item(listas, "Orçamento", 17))
        self.dados["itens"][0]["chave"] = "Orçamento!17"
        self.assertTrue(any("fora" in e for e in self.erros(self.dados)))

    def test_sugestoes_comparacao_e_limitacoes(self):
        self.dados["sugestoes"] = [{"id": "S01", "servico": "Impermeabilização do box", "motivo": "área molhada"}]
        self.dados["comparacao"] = [{"chave": "Orçamento!12", "referencia": 20, "fonte": "coluna D", "classe": "comparável"}]
        self.dados["limitacoes"] = ["recálculo independente não executado"]
        self.assertEqual(self.erros(self.dados), [])
        self.dados["comparacao"][0]["classe"] = "parecido"
        self.dados["sugestoes"][0]["motivo"] = ""
        erros = self.erros(self.dados)
        self.assertTrue(any("classe" in e for e in erros))
        self.assertTrue(any("S01" in e for e in erros))


class Calculo(unittest.TestCase):
    def test_soma_com_deducao(self):
        item = base(Path(tempfile.mkdtemp()))["itens"][0]
        resultado = lv.calcular_item(item)
        self.assertAlmostEqual(resultado["total"], 4.2 * 2.7 + 3.1 * 2.7 - 0.8 * 2.1)
        self.assertEqual(resultado["estado"], "CONFIRMADO")
        self.assertEqual(resultado["faltantes"], 0)

    def test_dimensao_faltante_rebaixa_para_subtotal(self):
        item = base(Path(tempfile.mkdtemp()))["itens"][0]
        item["parcelas"][1]["dimensoes"] = [3.1, None]
        resultado = lv.calcular_item(item)
        self.assertEqual(resultado["estado"], "SUBTOTAL")
        self.assertIsNone(resultado["total"])
        self.assertAlmostEqual(resultado["subtotal"], 4.2 * 2.7 - 0.8 * 2.1)
        self.assertEqual(resultado["valores"][1], None)

    def test_valor_direto_e_multiplicidade(self):
        item = {"estado": "CONFIRMADO", "parcelas": [{"id": "E01", "valor": 3, "multiplicidade": 2, "origem": "contagem"}]}
        self.assertEqual(lv.calcular_item(item)["total"], 6)

    def test_sem_parcelas(self):
        resultado = lv.calcular_item({"estado": "PENDENTE", "parcelas": []})
        self.assertIsNone(resultado["total"])
        self.assertIsNone(resultado["subtotal"])


class NomesDeAba(unittest.TestCase):
    def test_saneia_e_desambigua(self):
        itens = [{"chave": "A!1", "id": "1/2"}, {"chave": "A!2", "id": "1.1"}, {"chave": "B!3", "id": "1.1"},
                 {"chave": "A!4", "id": "9" * 40}]
        nomes = lv.nomes_abas_memoria(itens, existentes={"Orçamento"})
        self.assertEqual(nomes["A!1"], "ITEM 1-2")
        self.assertEqual(nomes["A!2"], "ITEM 1.1")
        self.assertEqual(nomes["B!3"], "ITEM 1.1 (2)")
        self.assertLessEqual(len(nomes["A!4"]), 31)

    def test_nome_existente_na_planilha_nao_colide(self):
        nomes = lv.nomes_abas_memoria([{"chave": "A!1", "id": "1"}], existentes={"item 1"})
        self.assertEqual(nomes["A!1"], "ITEM 1 (2)")


class Raiz(unittest.TestCase):
    def test_raiz_e_a_pasta_da_execucao(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = escrever_json(Path(pasta) / "dados" / "levantamento.json", {}) if (Path(pasta) / "dados").mkdir() is None else None
            dados, raiz = lv.carregar(caminho)
            self.assertEqual(raiz, Path(pasta).resolve())


if __name__ == "__main__":
    unittest.main()
