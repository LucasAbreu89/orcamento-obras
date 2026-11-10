import json
import math
import random
import tempfile
import unittest
from pathlib import Path

from apoio import escrever_json, rodar, tem

import geometria as g


class AreaPerimetro(unittest.TestCase):
    def test_retangulo(self):
        ret = [(0, 0), (4, 0), (4, 3), (0, 3)]
        self.assertAlmostEqual(g.area(ret), 12.0)
        self.assertAlmostEqual(g.perimetro(ret), 14.0)

    def test_orientacao_muda_sinal_mas_nao_area(self):
        horario = [(0, 0), (0, 3), (4, 3), (4, 0)]
        self.assertLess(g.area_assinada(horario), 0)
        self.assertAlmostEqual(g.area(horario), 12.0)

    def test_circulo_por_dois_bulges(self):
        circulo = [(-1, 0, 1), (1, 0, 1)]
        self.assertAlmostEqual(g.area(circulo), math.pi, places=9)
        self.assertAlmostEqual(g.perimetro(circulo), 2 * math.pi, places=9)

    def test_semicirculo_para_fora_soma_area(self):
        figura = [(0, 0, 0), (2, 0, 0), (2, 1, 1), (0, 1, 0)]
        self.assertAlmostEqual(g.area(figura), 2 + math.pi / 2, places=9)
        self.assertAlmostEqual(g.perimetro(figura), 4 + math.pi, places=9)

    def test_semicirculo_para_dentro_desconta_area(self):
        figura = [(0, 0, 0), (2, 0, 0), (2, 1, -1), (0, 1, 0)]
        self.assertAlmostEqual(g.area(figura), 2 - math.pi / 2, places=9)

    def test_polilinha_aberta_mede_comprimento_sem_fechar(self):
        trecho = [(0, 0), (3, 0), (3, 4)]
        self.assertAlmostEqual(g.perimetro(trecho, fechado=False), 7.0)

    def test_ultimo_vertice_repetindo_o_primeiro_nao_duplica(self):
        ret = [(0, 0), (4, 0), (4, 3), (0, 3), (0, 0)]
        self.assertAlmostEqual(g.area(ret), 12.0)
        self.assertAlmostEqual(g.perimetro(ret), 14.0)

    def test_area_com_furos(self):
        externo = [(0, 0), (10, 0), (10, 10), (0, 10)]
        furo = [(4, 4), (6, 4), (6, 6), (4, 6)]
        self.assertAlmostEqual(g.area_com_furos(externo, [furo]), 96.0)

    def test_area_por_paridade_com_ilha_dentro_do_furo(self):
        aneis = [
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            [(3, 3), (7, 3), (7, 7), (3, 7)],
            [(4.5, 4.5), (5.5, 4.5), (5.5, 5.5), (4.5, 5.5)],
        ]
        area, niveis = g.area_por_paridade(aneis)
        self.assertAlmostEqual(area, 100 - 16 + 1)
        self.assertEqual(niveis, [0, 1, 2])


class Validacao(unittest.TestCase):
    def test_autointersecao(self):
        laco = [(0, 0), (2, 2), (2, 0), (0, 2)]
        resultado = g.validar(laco)
        self.assertFalse(resultado["valido"])
        self.assertTrue(any("autointerse" in p for p in resultado["problemas"]))

    def test_vertices_repetidos(self):
        resultado = g.validar([(0, 0), (0, 0), (1, 0), (1, 1)])
        self.assertFalse(resultado["valido"])
        self.assertTrue(any("repetid" in p for p in resultado["problemas"]))

    def test_poligono_correto_e_valido(self):
        resultado = g.validar([(0, 0), (4, 0), (4, 3), (0, 3)])
        self.assertTrue(resultado["valido"], resultado["problemas"])
        self.assertEqual(resultado["orientacao"], "anti-horario")

    def test_menos_de_tres_vertices(self):
        self.assertFalse(g.validar([(0, 0), (1, 0)])["valido"])


class Ciclos(unittest.TestCase):
    @staticmethod
    def arestas_quadrado(x, y, lado):
        p = [(x, y), (x + lado, y), (x + lado, y + lado), (x, y + lado)]
        return [(p[i], p[(i + 1) % 4]) for i in range(4)]

    def embaralhar(self, arestas):
        rnd = random.Random(7)
        saida = [(b, a) if rnd.random() < 0.5 else (a, b) for a, b in arestas]
        rnd.shuffle(saida)
        return saida

    def test_componentes_separadas_nao_se_ligam(self):
        arestas = self.embaralhar(self.arestas_quadrado(0, 0, 4) + self.arestas_quadrado(10, 10, 1))
        resultado = g.reconstruir_ciclos(arestas, tol=1e-9)
        self.assertEqual(len(resultado["ciclos"]), 2)
        self.assertEqual(resultado["abertas"], [])
        self.assertAlmostEqual(resultado["area"], 17.0)

    def test_furo_entre_arestas_e_descontado(self):
        arestas = self.embaralhar(self.arestas_quadrado(0, 0, 10) + self.arestas_quadrado(4, 4, 2))
        resultado = g.reconstruir_ciclos(arestas, tol=1e-9)
        self.assertAlmostEqual(resultado["area"], 96.0)

    def test_cadeia_aberta_e_relatada(self):
        arestas = self.arestas_quadrado(0, 0, 4)[:3]
        resultado = g.reconstruir_ciclos(arestas, tol=1e-9)
        self.assertEqual(resultado["ciclos"], [])
        self.assertEqual(len(resultado["abertas"]), 1)
        self.assertAlmostEqual(resultado["lacunas"][0]["distancia"], 4.0)

    def test_lacuna_pequena_dentro_da_tolerancia_fica_registrada(self):
        arestas = self.arestas_quadrado(0, 0, 4)
        (a, b) = arestas[1]
        arestas[1] = (a, (b[0], b[1] + 1e-4))
        sem_tolerancia = g.reconstruir_ciclos(arestas, tol=1e-6)
        self.assertEqual(sem_tolerancia["ciclos"], [])
        com_tolerancia = g.reconstruir_ciclos(arestas, tol=1e-3)
        self.assertEqual(len(com_tolerancia["ciclos"]), 1)
        self.assertAlmostEqual(com_tolerancia["lacunas"][0]["distancia"], 1e-4, places=9)

    def test_invariancia_a_translacao(self):
        fechado = self.arestas_quadrado(0, 0, 4)
        self.assertTrue(g.invariante_translacao(fechado))
        self.assertFalse(g.invariante_translacao(fechado[:3]))


class Unidades(unittest.TestCase):
    def test_fator_insunits(self):
        self.assertEqual(g.fator_insunits(4), 0.001)
        self.assertEqual(g.fator_insunits(6), 1.0)
        self.assertIsNone(g.fator_insunits(0))


class Cli(unittest.TestCase):
    def test_calcular_converte_milimetros(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = escrever_json(Path(pasta) / "regioes.json", {
                "unidade": {"k": 0.001},
                "regioes": [
                    {"id": "A01", "fechada": True, "vertices": [[0, 0], [4000, 0], [4000, 3000], [0, 3000]]},
                    {"id": "S01", "fechada": False, "vertices": [[0, 0], [2500, 0]]},
                ],
            })
            saida = Path(pasta) / "resultado.json"
            processo = rodar("geometria.py", "calcular", entrada, "--saida", saida)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            dados = json.loads(saida.read_text(encoding="utf-8"))
            por_id = {r["id"]: r for r in dados["regioes"]}
            self.assertAlmostEqual(por_id["A01"]["area_m2"], 12.0)
            self.assertAlmostEqual(por_id["A01"]["perimetro_m"], 14.0)
            self.assertAlmostEqual(por_id["S01"]["comprimento_m"], 2.5)
            self.assertTrue(por_id["A01"]["validacao"]["valido"])

    def test_calcular_avisa_quando_k_nao_foi_validado(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = escrever_json(Path(pasta) / "regioes.json", {
                "unidade": {"k": 0.001, "validada": False},
                "regioes": [{"id": "A01", "fechada": True, "vertices": [[0, 0], [1000, 0], [1000, 1000]]}]})
            saida = Path(pasta) / "r.json"
            self.assertEqual(rodar("geometria.py", "calcular", entrada, "--saida", saida).returncode, 0)
            dados = json.loads(saida.read_text(encoding="utf-8"))
            self.assertFalse(dados["k_validado"])
            self.assertIn("aviso", dados)
            self.assertEqual(rodar("geometria.py", "calcular", entrada, "--k", "0.001", "--saida", saida).returncode, 0)
            self.assertTrue(json.loads(saida.read_text(encoding="utf-8"))["k_validado"])

    def test_calcular_sem_unidade_falha(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = escrever_json(Path(pasta) / "regioes.json", {
                "regioes": [{"id": "A01", "fechada": True, "vertices": [[0, 0], [1, 0], [1, 1]]}]})
            processo = rodar("geometria.py", "calcular", entrada)
            self.assertNotEqual(processo.returncode, 0)
            self.assertIn("unidade", processo.stderr.lower())


@unittest.skipUnless(tem("shapely"), "shapely não instalado")
class Uniao(unittest.TestCase):
    def test_uniao_de_parcelas_adjacentes(self):
        partes = [
            {"contorno": [(0, 0), (2, 0), (2, 3), (0, 3)]},
            {"contorno": [(2, 0), (3, 0), (3, 3), (2, 3)]},
        ]
        resultado = g.uniao(partes)
        self.assertAlmostEqual(sum(g.area_com_furos(p["contorno"], p["furos"]) for p in resultado), 9.0)
        self.assertAlmostEqual(sum(g.perimetro(p["contorno"]) for p in resultado), 12.0)

    def test_uniao_com_hachura_e_subtracao_pela_linha_de_comando(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = escrever_json(Path(pasta) / "regioes.json", {"unidade": {"k": 1.0, "validada": True}, "regioes": [
                {"id": "H1", "fechada": True, "aneis": [[[0, 0], [10, 0], [10, 10], [0, 10]],
                                                         [[4, 4], [6, 4], [6, 6], [4, 6]]]},
                {"id": "R2", "fechada": True, "vertices": [[10, 0], [12, 0], [12, 10], [10, 10]]},
                {"id": "D1", "fechada": True, "vertices": [[0, 0], [2, 0], [2, 2], [0, 2]]}]})
            saida = Path(pasta) / "uniao.json"
            processo = rodar("geometria.py", "uniao", entrada, "--ids", "H1,R2", "--subtrair", "D1", "--saida", saida)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            dados = json.loads(saida.read_text(encoding="utf-8"))
            self.assertAlmostEqual(dados["area_m2"], 100 - 4 + 20 - 4)
            calculo = Path(pasta) / "calculo.json"
            self.assertEqual(rodar("geometria.py", "calcular", saida, "--saida", calculo).returncode, 0)
            self.assertAlmostEqual(json.loads(calculo.read_text(encoding="utf-8"))["area_total_m2"], 112.0)


if __name__ == "__main__":
    unittest.main()
