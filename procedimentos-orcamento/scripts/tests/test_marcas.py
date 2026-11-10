import tempfile
import unittest
from pathlib import Path

from apoio import escrever_json

import geometria as g
import marcas as mk


class Rotulos(unittest.TestCase):
    def test_rotulo_de_poligono_com_furo_central_fica_fora_do_furo(self):
        furo = [(1000, 1000), (2000, 1000), (2000, 2000), (1000, 2000)]
        marca = {"tipo": "poligono", "pontos": [(0, 0), (3000, 0), (3000, 3000), (0, 3000)], "furos": [furo]}
        x, y = mk.posicao_rotulo(marca)
        self.assertTrue(g._dentro((x, y), marca["pontos"]))
        self.assertFalse(g._dentro((x, y), furo))

    def test_rotulo_de_linha_fica_no_meio(self):
        self.assertEqual(mk.posicao_rotulo({"tipo": "linha", "pontos": [(0, 0), (10, 0)]}), (5.0, 0.0))


class Carga(unittest.TestCase):
    def test_aceita_arquivo_de_regioes_e_completa_cores(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = escrever_json(Path(pasta) / "regioes.json", {"regioes": [
                {"id": "R0001", "fechada": True, "aneis": [[[0, 0], [4, 0], [4, 4], [0, 4]], [[1, 1], [2, 1], [2, 2], [1, 2]]]},
                {"id": "R0002", "fechada": False, "vertices": [[0, 0], [5, 0]]}]})
            dados = mk.carregar(caminho)
        primeira, segunda = dados["marcas"]
        self.assertEqual(primeira["tipo"], "poligono")
        self.assertEqual(len(primeira["furos"]), 1)
        self.assertEqual(segunda["tipo"], "linha")
        self.assertTrue(primeira["cor"].startswith("#"))


if __name__ == "__main__":
    unittest.main()
