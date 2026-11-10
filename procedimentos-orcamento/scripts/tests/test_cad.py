import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path

from apoio import escrever_json, pixels, rodar, tem

PRECISA = tem("ezdxf") and tem("matplotlib")


def desenho_exemplo(caminho):
    """DXF em milímetros com duas plantas no Model, hachura com furo, blocos, textos, cota e layout."""
    import ezdxf
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 4
    for nome in ("ARQ-AREA", "ARQ-PAREDE", "ELE-TOMADA", "MOB"):
        doc.layers.add(nome)
    doc.layers.get("MOB").off()
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (4000, 0), (4000, 3000), (0, 3000)], close=True, dxfattribs={"layer": "ARQ-AREA"})
    msp.add_lwpolyline([(5000, 0, 0), (7000, 0, 0), (7000, 1000, 1), (5000, 1000, 0)], format="xyb", close=True,
                       dxfattribs={"layer": "ARQ-AREA"})
    hachura = msp.add_hatch(dxfattribs={"layer": "ARQ-AREA"})
    hachura.paths.add_polyline_path([(0, 4000), (3000, 4000), (3000, 7000), (0, 7000)], is_closed=True, flags=1)
    hachura.paths.add_polyline_path([(1000, 5000), (2000, 5000), (2000, 6000), (1000, 6000)], is_closed=True, flags=0)
    for x in (0, 4000, 8000):
        msp.add_line((x, -500), (x, 8000), dxfattribs={"layer": "ARQ-PAREDE"})
    msp.add_line((0, 8000), (8000, 8000), dxfattribs={"layer": "ARQ-PAREDE"})
    bloco = doc.blocks.new("TOMADA")
    bloco.add_circle((0, 0), 50)
    bloco.add_attdef("TIPO", (0, -80), dxfattribs={"height": 40})
    for x in (500, 1500, 2500):
        insercao = msp.add_blockref("TOMADA", (x, 100), dxfattribs={"layer": "ELE-TOMADA"})
        insercao.add_auto_attribs({"TIPO": "TUG"})
    msp.add_text("SALA 01", dxfattribs={"layer": "ARQ-AREA", "height": 150}).set_placement((1500, 1500))
    msp.add_mtext("A=12,00 m²", dxfattribs={"layer": "ARQ-AREA", "char_height": 100, "insert": (1500, 1200)})
    msp.add_linear_dim(base=(0, -300), p1=(0, 0), p2=(4000, 0), dxfattribs={"layer": "ARQ-PAREDE"}).render()
    msp.add_line((50000, 0), (60000, 0), dxfattribs={"layer": "ARQ-PAREDE"})
    msp.add_line((60000, 0), (60000, 8000), dxfattribs={"layer": "ARQ-PAREDE"})
    msp.add_line((60000, 8000), (50000, 8000), dxfattribs={"layer": "ARQ-PAREDE"})
    msp.add_line((50000, 8000), (50000, 0), dxfattribs={"layer": "ARQ-PAREDE"})
    msp.add_text("PLANTA PAVIMENTO SUPERIOR", dxfattribs={"height": 400}).set_placement((50000, -800))
    msp.add_text("MESA", dxfattribs={"layer": "MOB", "height": 100}).set_placement((2000, 2000))
    folha = doc.layouts.new("PR-01")
    folha.add_viewport(center=(200, 150), size=(300, 200), view_center_point=(2000, 1500), view_height=4000)
    doc.saveas(caminho)
    return caminho


def desenho_com_blocos(caminho):
    """Bloco BANHEIRO (polilinha na camada 0 e dois VASO) inserido duas vezes na camada ARQ-AREA."""
    import ezdxf
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 4
    doc.layers.add("ARQ-AREA")
    vaso = doc.blocks.new("VASO")
    vaso.add_circle((0, 0), 150)
    banheiro = doc.blocks.new("BANHEIRO")
    banheiro.add_lwpolyline([(0, 0), (1000, 0), (1000, 2000), (0, 2000)], close=True, dxfattribs={"layer": "0"})
    banheiro.add_blockref("VASO", (300, 300))
    banheiro.add_blockref("VASO", (700, 300))
    msp = doc.modelspace()
    for x in (0, 5000):
        msp.add_blockref("BANHEIRO", (x, 0), dxfattribs={"layer": "ARQ-AREA"})
    doc.saveas(caminho)
    return caminho


@unittest.skipUnless(tem("ezdxf"), "ezdxf não instalado")
class Blocos(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.dxf = desenho_com_blocos(self.dir / "blocos.dxf")

    def tearDown(self):
        self.pasta.cleanup()

    def test_inventario_conta_blocos_aninhados(self):
        processo = rodar("cad.py", "inventario", self.dxf, "--saida", self.dir / "inv.json")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        aninhados = json.loads((self.dir / "inv.json").read_text(encoding="utf-8"))["blocos_aninhados"]
        self.assertIn({"bloco": "VASO", "dentro_de": "BANHEIRO", "quantidade": 4}, aninhados)

    def test_extrair_le_geometria_dentro_de_blocos(self):
        saida = self.dir / "regioes.json"
        processo = rodar("cad.py", "extrair", self.dxf, "--camadas", "ARQ-AREA", "--saida", saida)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertEqual(json.loads(saida.read_text(encoding="utf-8"))["regioes"], [])
        processo = rodar("cad.py", "extrair", self.dxf, "--camadas", "ARQ-AREA", "--blocos", "--saida", saida)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        regioes = [r for r in json.loads(saida.read_text(encoding="utf-8"))["regioes"] if r["tipo"] == "LWPOLYLINE"]
        self.assertEqual(len(regioes), 2)
        self.assertEqual({r["bloco"] for r in regioes}, {"BANHEIRO"})
        import geometria as g
        self.assertTrue(all(math.isclose(g.area(r["vertices"]) * 1e-6, 2.0) for r in regioes))
        self.assertEqual(sorted(min(v[0] for v in r["vertices"]) for r in regioes), [0.0, 5000.0])

    def test_descoberta_de_dwg_sem_caixa_e_sem_colisao(self):
        import cad
        (self.dir / "proj" / "rev").mkdir(parents=True)
        (self.dir / "proj" / "A.DWG").write_bytes(b"x")
        (self.dir / "proj" / "rev" / "A.dwg").write_bytes(b"y")
        (self.dir / "proj" / "notas.txt").write_text("z")
        arquivos = cad.arquivos_dwg(self.dir / "proj")
        self.assertEqual(len(arquivos), 2)
        destinos = {cad.destino_dxf(a, self.dir / "proj", self.dir / "dxf") for a in arquivos}
        self.assertEqual(destinos, {self.dir / "dxf" / "A.dxf", self.dir / "dxf" / "rev" / "A.dxf"})


@unittest.skipUnless(PRECISA, "ezdxf e matplotlib não instalados")
class Cad(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.dxf = desenho_exemplo(self.dir / "arq.dxf")

    def tearDown(self):
        self.pasta.cleanup()

    def test_inventario(self):
        processo = rodar("cad.py", "inventario", self.dxf, "--saida", self.dir / "inv.json", "--md", self.dir / "inv.md")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        inv = json.loads((self.dir / "inv.json").read_text(encoding="utf-8"))
        self.assertEqual(inv["unidade"]["insunits"], 4)
        self.assertEqual(inv["unidade"]["k"], 0.001)
        camadas = {c["nome"]: c for c in inv["camadas"]}
        self.assertFalse(camadas["MOB"]["ligada"])
        blocos = {(b["bloco"], b["camada"]): b["quantidade"] for b in inv["blocos"]}
        self.assertEqual(blocos[("TOMADA", "ELE-TOMADA")], 3)
        textos = {t["texto"] for t in inv["textos"]}
        self.assertTrue({"SALA 01", "A=12,00 m²"} <= textos)
        self.assertTrue(any(math.isclose(c["medida"], 4000) for c in inv["cotas"]))
        self.assertGreaterEqual(len(inv["regioes_model"]), 2)
        self.assertTrue(any("PAVIMENTO SUPERIOR" in (r.get("titulo_provavel") or "") for r in inv["regioes_model"]))
        layouts = {l["nome"]: l for l in inv["layouts"]}
        self.assertEqual(len(layouts["PR-01"]["viewports"]), 1)
        self.assertIn("ARQ-AREA", (self.dir / "inv.md").read_text(encoding="utf-8"))

    def test_extrair_e_calcular(self):
        regioes = self.dir / "regioes.json"
        processo = rodar("cad.py", "extrair", self.dxf, "--camadas", "ARQ-AREA", "--saida", regioes)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        dados = json.loads(regioes.read_text(encoding="utf-8"))
        self.assertEqual(dados["unidade"]["k"], 0.001)
        self.assertEqual(len(dados["regioes"]), 3)
        resultado = self.dir / "areas.json"
        processo = rodar("geometria.py", "calcular", regioes, "--saida", resultado)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        areas = sorted(r["area_m2"] for r in json.loads(resultado.read_text(encoding="utf-8"))["regioes"])
        esperadas = sorted([12.0, 2 + math.pi / 2, 8.0])
        for area, esperada in zip(areas, esperadas):
            self.assertAlmostEqual(area, esperada, places=6)

    def test_extrair_com_curinga_e_recorte(self):
        regioes = self.dir / "regioes.json"
        processo = rodar("cad.py", "extrair", self.dxf, "--camadas", "ARQ-*", "--bbox", "40000,-1000,70000,10000",
                         "--saida", regioes)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertEqual(json.loads(regioes.read_text(encoding="utf-8"))["regioes"], [])
        processo = rodar("cad.py", "extrair", self.dxf, "--camadas", "ARQ-PAREDE", "--abertas", "--saida", regioes)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        abertas = [r for r in json.loads(regioes.read_text(encoding="utf-8"))["regioes"] if not r["fechada"]]
        self.assertGreaterEqual(len(abertas), 4)

    def test_render_com_marcas(self):
        from PIL import Image
        marcas = escrever_json(self.dir / "marcas.json", {
            "titulo": "Piso da sala", "legenda": [{"cor": "#ff0000", "texto": "Área considerada"}],
            "marcas": [{"id": "A01", "tipo": "poligono", "pontos": [[0, 0], [4000, 0], [4000, 3000], [0, 3000]],
                        "cor": "#ff0000", "preenchimento": 0.35, "rotulo": "A01"},
                       {"id": "E01", "tipo": "ponto", "pontos": [[500, 100]], "cor": "#0000ff", "rotulo": "E01"}]})
        png = self.dir / "print.png"
        processo = rodar("cad.py", "render", self.dxf, "--saida", png, "--bbox", "-1000,-1000,9000,9000",
                         "--marcas", marcas, "--largura", 900)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        with Image.open(png) as imagem:
            self.assertLessEqual(imagem.width, 900)
            rgb = list(pixels(imagem))
            vermelhos = sum(1 for r, g, b in rgb if r > 200 and g < 160 and b < 160)
        self.assertGreater(vermelhos, 100)

    def test_comparar_revisoes(self):
        import ezdxf
        revisao = self.dir / "arq_r01.dxf"
        shutil.copy2(self.dxf, revisao)
        doc = ezdxf.readfile(revisao)
        doc.modelspace().add_line((0, 0), (1000, 1000), dxfattribs={"layer": "ARQ-PAREDE"})
        doc.saveas(revisao)
        processo = rodar("cad.py", "comparar", self.dxf, revisao, "--saida", self.dir / "dif.json")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        dif = json.loads((self.dir / "dif.json").read_text(encoding="utf-8"))
        self.assertEqual(dif["camadas"]["ARQ-PAREDE"]["acrescentadas"], 1)
        self.assertEqual(dif["camadas"]["ARQ-PAREDE"]["removidas"], 0)
        self.assertNotIn("ARQ-AREA", dif["camadas"])

    def test_converter_sem_oda_explica(self):
        from ezdxf.addons import odafc
        if odafc.is_installed() if hasattr(odafc, "is_installed") else False:
            self.skipTest("ODA File Converter instalado")
        falso = self.dir / "arq.dwg"
        falso.write_bytes(b"AC1032")
        processo = rodar("cad.py", "converter", falso, "--saida", self.dir / "dxf")
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("ODA", processo.stdout + processo.stderr)


if __name__ == "__main__":
    unittest.main()
