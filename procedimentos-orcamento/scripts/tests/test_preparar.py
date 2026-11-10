import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from apoio import rodar
from apoio_xlsx import criar_xlsx, lista_exemplo

import levantamento as lv


def sha(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


class Ambiente(unittest.TestCase):
    def test_relata_bibliotecas_programas_e_rotas(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "ambiente.json"
            processo = rodar("ambiente.py", "--saida", saida)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            dados = json.loads(saida.read_text(encoding="utf-8"))
            for chave in ("python", "bibliotecas", "programas", "rotas"):
                self.assertIn(chave, dados)
            self.assertIn("ezdxf", dados["bibliotecas"])
            self.assertIn("dwg", dados["rotas"])
            self.assertIn("ifc", dados["rotas"])
            if dados["instalar"]:
                self.assertIn("venv", dados["instalar"])


class Preparacao(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.projeto = Path(self.pasta.name) / "obra"
        (self.projeto / "antigos").mkdir(parents=True)
        (self.projeto / "ARQ-01.dwg").write_bytes(b"AC1032 desenho")
        (self.projeto / "ARQ-01.pdf").write_bytes(b"%PDF-1.4 planta")
        (self.projeto / "antigos" / "ARQ-01_R00.pdf").write_bytes(b"%PDF-1.4 revisao antiga")
        self.planilha = criar_xlsx(self.projeto / "servicos.xlsx", [lista_exemplo()])
        self.hashes = {p: sha(p) for p in self.projeto.rglob("*") if p.is_file()}

    def tearDown(self):
        self.pasta.cleanup()

    def test_cria_execucao_completa_sem_tocar_nos_originais(self):
        processo = rodar("preparar_projeto.py", "--projeto", self.projeto, "--planilha", self.planilha)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        resultado = json.loads(processo.stdout)
        execucao = Path(resultado["execucao"])
        for pasta in ("fontes", "dados", "evidencias", "planilha", "conferencia"):
            self.assertTrue((execucao / pasta).is_dir(), pasta)
        inventario = json.loads((execucao / "fontes" / "inventario.json").read_text(encoding="utf-8"))
        self.assertEqual(len(inventario["fontes"]), 4)
        self.assertTrue(all(f["leitura"] == "nao_examinado" for f in inventario["fontes"]))
        self.assertEqual(sha(execucao / "planilha" / "ORIGINAL_servicos.xlsx"), self.hashes[self.planilha])
        self.assertEqual(sha(execucao / "planilha" / "servicos_TRABALHO.xlsx"), self.hashes[self.planilha])
        self.assertTrue((execucao / "fontes" / "snapshot_planilha.json.gz").is_file())
        self.assertIn("Orçamento", (execucao / "fontes" / "mapa_planilha.md").read_text(encoding="utf-8"))
        self.assertTrue((execucao / "fontes" / "ambiente.json").is_file())
        dados, raiz = lv.carregar(execucao / "dados" / "levantamento.json")
        self.assertEqual(raiz, execucao.resolve())
        self.assertEqual(lv.validar(dados, raiz)[0], [])
        lista = dados["planilha"]["listas"][0]
        self.assertEqual((lista["aba"], lista["linha_cabecalho"], lista["colunas"]["item"]), ("Orçamento", 4, "A"))
        self.assertEqual(dados["planilha"]["entrega"], "planilha/servicos_LEVANTAMENTO.xlsx")
        self.assertEqual(len(dados["fontes"]), 4)
        self.assertEqual({p: sha(p) for p in self.hashes}, self.hashes)

    def test_varias_colunas_de_quantidade_e_aba_oculta(self):
        aba = lista_exemplo()
        aba["celulas"].update({"D4": ("s", "QUANT. ORÇADA"), "G4": ("s", "QUANT. EXECUTADA"), "G6": ("n", 9)})
        oculta = dict(lista_exemplo(), nome="Composições", estado="hidden")
        planilha = criar_xlsx(self.projeto / "duas_quantidades.xlsx", [aba, oculta])
        processo = rodar("preparar_projeto.py", "--projeto", self.projeto, "--planilha", planilha)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        dados = json.loads((Path(json.loads(processo.stdout)["execucao"]) / "dados" / "levantamento.json")
                           .read_text(encoding="utf-8"))
        self.assertEqual([l["aba"] for l in dados["planilha"]["listas"]], ["Orçamento"])
        lista = dados["planilha"]["listas"][0]
        self.assertIsNone(lista["colunas"]["quantidade"])
        self.assertEqual(lista["_quantidades_candidatas"], ["D", "G"])
        self.assertEqual(dados["planilha"]["_listas_ocultas_detectadas"], ["Composições"])

    def test_sem_planilha_registra_alerta(self):
        processo = rodar("preparar_projeto.py", "--projeto", self.projeto)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        resultado = json.loads(processo.stdout)
        inventario = json.loads((Path(resultado["execucao"]) / "fontes" / "inventario.json").read_text(encoding="utf-8"))
        self.assertTrue(any(a["natureza"] == "planilha_ausente" for a in inventario["alertas_tecnicos"]))

    def test_saida_existente_e_recusada(self):
        destino = Path(self.pasta.name) / "ja_existe"
        destino.mkdir()
        processo = rodar("preparar_projeto.py", "--projeto", self.projeto, "--saida", destino)
        self.assertNotEqual(processo.returncode, 0)


if __name__ == "__main__":
    unittest.main()
