import io
import json
import math
import tempfile
import unittest
from pathlib import Path

from apoio import escrever_json, pixels, rodar, tem

PRECISA = tem("pymupdf") and tem("PIL")
K_1_50 = 0.0254 / 72 * 50


def pdf_exemplo(caminho):
    """Página 1 vetorial com retângulo fechado, caminho aberto e textos; página 2 só com imagem."""
    import pymupdf
    from PIL import Image
    doc = pymupdf.open()
    pagina = doc.new_page(width=1190, height=842)
    forma = pagina.new_shape()
    forma.draw_rect(pymupdf.Rect(100, 100, 300, 200))
    forma.finish(color=(0, 0, 0), width=1)
    forma.draw_polyline([(400, 100), (500, 100), (500, 160)])
    forma.finish(color=(0, 0, 1), width=1, closePath=False)
    for i in range(40):
        forma.draw_line((600 + i * 5, 600), (600 + i * 5, 700))
    forma.finish(color=(0.5, 0.5, 0.5), width=0.3)
    forma.commit()
    pagina.insert_text((100, 260), "SALA 01", fontsize=12)
    pagina.insert_text((100, 280), "A=12,34 m2", fontsize=10)
    pagina.insert_text((900, 800), "ESCALA 1:50", fontsize=14)
    imagem = Image.new("RGB", (400, 300), "white")
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    raster = doc.new_page(width=595, height=842)
    raster.insert_image(raster.rect, stream=buffer.getvalue())
    doc.save(caminho)
    doc.close()
    return caminho


@unittest.skipUnless(PRECISA, "PyMuPDF e Pillow não instalados")
class Pdf(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.pdf = pdf_exemplo(self.dir / "arq.pdf")

    def tearDown(self):
        self.pasta.cleanup()

    def test_inventario(self):
        processo = rodar("pdf.py", "inventario", self.pdf, "--saida", self.dir / "inv.json")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        paginas = json.loads((self.dir / "inv.json").read_text(encoding="utf-8"))["paginas"]
        self.assertEqual(paginas[0]["tipo"], "vetorial")
        self.assertIn("1:50", paginas[0]["escalas"])
        self.assertEqual(paginas[1]["tipo"], "raster")

    def test_texto(self):
        processo = rodar("pdf.py", "texto", self.pdf, "--busca", r"A\s*=\s*\d", "--saida", self.dir / "achados.json")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        achados = json.loads((self.dir / "achados.json").read_text(encoding="utf-8"))["achados"]
        self.assertEqual(len(achados), 1)
        self.assertEqual(achados[0]["pagina"], 1)

    def test_medir_com_escala_e_com_calibracao(self):
        for argumentos in (["--escala", "1:50"], ["--calibrar", f"100,100,300,100,{200 * K_1_50}"]):
            regioes = self.dir / "regioes.json"
            processo = rodar("pdf.py", "medir", self.pdf, "--pagina", 1, "--recorte", "50,50,350,250",
                             *argumentos, "--saida", regioes)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            dados = json.loads(regioes.read_text(encoding="utf-8"))
            self.assertAlmostEqual(dados["unidade"]["k"], K_1_50, places=12)
            fechadas = [r for r in dados["regioes"] if r["fechada"]]
            self.assertEqual(len(fechadas), 1)
            resultado = self.dir / "areas.json"
            processo = rodar("geometria.py", "calcular", regioes, "--saida", resultado)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            area = json.loads(resultado.read_text(encoding="utf-8"))["area_total_m2"]
            self.assertAlmostEqual(area, (200 * K_1_50) * (100 * K_1_50), places=9)

    def test_rotacao_original_e_relatada(self):
        import pymupdf
        girado = self.dir / "girado.pdf"
        doc = pymupdf.open(self.pdf)
        doc[0].set_rotation(90)
        doc.save(girado)
        doc.close()
        processo = rodar("pdf.py", "inventario", girado, "--saida", self.dir / "inv.json")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        paginas = json.loads((self.dir / "inv.json").read_text(encoding="utf-8"))["paginas"]
        self.assertEqual(paginas[0]["rotacao_original"], 90)

    def test_medir_poligono_marcado_a_mao_em_pagina_raster(self):
        regioes = self.dir / "manual.json"
        processo = rodar("pdf.py", "medir", self.pdf, "--pagina", 2, "--calibrar", "0,0,100,0,1.0",
                         "--poligono", "0,0;100,0;100,50;0,50", "--saida", regioes)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        dados = json.loads(regioes.read_text(encoding="utf-8"))
        self.assertEqual(len(dados["regioes"]), 1)
        self.assertEqual(dados["regioes"][0]["origem"], "medicao_grafica")
        resultado = self.dir / "areas.json"
        self.assertEqual(rodar("geometria.py", "calcular", regioes, "--saida", resultado).returncode, 0)
        self.assertAlmostEqual(json.loads(resultado.read_text(encoding="utf-8"))["area_total_m2"], 0.5)

    def test_render_com_grade_de_coordenadas(self):
        png = self.dir / "grade.png"
        processo = rodar("pdf.py", "render", self.pdf, "--pagina", 2, "--grade", 50, "--saida", png)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertTrue(png.is_file())

    def test_medir_sem_escala_falha(self):
        processo = rodar("pdf.py", "medir", self.pdf, "--pagina", 1)
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("escala", (processo.stdout + processo.stderr).lower())

    def test_render_com_marcas(self):
        from PIL import Image
        marcas = escrever_json(self.dir / "marcas.json", {
            "legenda": [{"cor": "#ff0000", "texto": "Área A01"}],
            "marcas": [{"id": "A01", "tipo": "poligono", "pontos": [[100, 100], [300, 100], [300, 200], [100, 200]],
                        "cor": "#ff0000", "preenchimento": 0.4, "rotulo": "A01"}]})
        png = self.dir / "print.png"
        processo = rodar("pdf.py", "render", self.pdf, "--pagina", 1, "--recorte", "50,50,350,250", "--dpi", 150,
                         "--marcas", marcas, "--saida", png)
        self.assertEqual(processo.returncode, 0, processo.stderr)
        with Image.open(png) as imagem:
            rgb = list(pixels(imagem))
            vermelhos = sum(1 for r, g, b in rgb if r > 200 and g < 170 and b < 170)
        self.assertGreater(vermelhos, 500)


if __name__ == "__main__":
    unittest.main()
