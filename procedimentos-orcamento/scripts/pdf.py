#!/usr/bin/env python3
"""PDF de projeto: inventário, busca de texto, medição de vetores e prints marcados.

  inventario  por página: tamanho, rotação, se é vetorial/raster/misto, escalas escritas e
              os textos de maior destaque (carimbo, títulos)
  texto       linhas que casam com uma expressão regular, com página e posição
  medir       caminhos vetoriais de uma página (ou recorte) no formato do geometria.py, com o
              fator k (metros por ponto) vindo da escala escrita ou de calibração por cota
  render      PNG de uma página ou recorte com marcas desenhadas nas coordenadas do PDF

Coordenadas em pontos do PDF, origem no canto superior esquerdo, sempre na página sem
rotação. O arquivo de origem nunca é gravado. Precisa de PyMuPDF; Pillow melhora o PNG.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

import geometria as g
import marcas as mk

PONTO_EM_METROS = 0.0254 / 72
SEGMENTOS_VETORIAIS = 30


def _pymupdf():
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            sys.exit("pdf.py precisa de PyMuPDF: python3 -m pip install -r scripts/requirements.txt")
    return pymupdf


def _abrir(caminho):
    pymupdf = _pymupdf()
    return pymupdf, pymupdf.open(caminho)


def _pagina(doc, numero):
    if not 1 <= numero <= doc.page_count:
        sys.exit(f"Página {numero} não existe (o arquivo tem {doc.page_count}).")
    pagina = doc[numero - 1]
    if pagina.rotation:
        pagina.set_rotation(0)
    return pagina


def _linhas(pagina):
    for bloco in pagina.get_text("dict").get("blocks", []):
        for linha in bloco.get("lines", []):
            spans = linha.get("spans", [])
            texto = "".join(s.get("text", "") for s in spans).strip()
            if texto:
                yield texto, linha.get("bbox"), max((s.get("size", 0) for s in spans), default=0)


def _escalas(texto):
    perto = re.findall(r"ESC(?:ALA)?\.?[^\n\d]{0,15}1\s*[:/]\s*(\d{1,5})", texto, flags=re.IGNORECASE)
    soltas = re.findall(r"(?<![\d/.,])1\s*:\s*(\d{1,5})(?![\d/])", texto)
    return sorted({f"1:{n}" for n in perto + soltas if 0 < int(n) <= 10000}, key=lambda s: int(s[2:]))


def inventario(caminho):
    _, doc = _abrir(caminho)
    paginas = []
    for numero in range(1, doc.page_count + 1):
        rotacao = doc[numero - 1].rotation
        pagina = _pagina(doc, numero)
        texto = pagina.get_text("text")
        segmentos = sum(len(d.get("items", [])) for d in pagina.get_drawings())
        imagens = len(pagina.get_images())
        if not segmentos and not imagens and not texto.strip():
            tipo = "vazia"
        elif imagens and segmentos < SEGMENTOS_VETORIAIS:
            tipo = "raster"
        elif segmentos >= SEGMENTOS_VETORIAIS and not imagens:
            tipo = "vetorial"
        else:
            tipo = "misto"
        destaque = sorted(_linhas(pagina), key=lambda l: -l[2])[:6]
        paginas.append({"pagina": numero, "largura_pt": pagina.rect.width, "altura_pt": pagina.rect.height,
                        "rotacao_original": rotacao, "tipo": tipo, "segmentos_vetoriais": segmentos,
                        "imagens": imagens, "caracteres": len(texto.strip()), "escalas": _escalas(texto),
                        "destaque": [t for t, _, _ in destaque],
                        "areas_escritas": re.findall(r"A\s*=\s*[\d.,]+\s*m", texto)})
    doc.close()
    return {"arquivo": str(caminho), "paginas": paginas,
            "observacao": "Página raster só admite medição gráfica (PREMISSA); escala escrita deve ser confirmada por cota."}


def texto(caminho, busca, paginas=None):
    _, doc = _abrir(caminho)
    padrao = re.compile(busca, re.IGNORECASE)
    achados = []
    for numero in paginas or range(1, doc.page_count + 1):
        for linha, caixa, _ in _linhas(_pagina(doc, numero)):
            if padrao.search(linha):
                achados.append({"pagina": numero, "texto": linha, "bbox": [round(v, 2) for v in caixa]})
    doc.close()
    return {"arquivo": str(caminho), "busca": busca, "achados": achados}


def _bezier(p0, p1, p2, p3, partes=16):
    pontos = []
    for i in range(1, partes + 1):
        t = i / partes
        u = 1 - t
        pontos.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                       u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return pontos


def _hex(cor):
    return None if cor is None else "#" + "".join(f"{round(c * 255):02x}" for c in cor[:3])


def _subcaminhos(desenho, eps=0.01):
    """Divide um caminho do PDF em anéis/linhas, marcando curvas como aproximadas."""
    partes, atual, aproximado = [], None, False
    for item in desenho.get("items", []):
        tipo = item[0]
        if tipo == "re":
            r = item[1]
            partes.append({"pontos": [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)], "fechado": True})
            atual = None
            continue
        if tipo == "qu":
            q = item[1]
            partes.append({"pontos": [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)],
                           "fechado": True})
            atual = None
            continue
        inicio = (item[1].x, item[1].y)
        if atual is None or math.dist(atual["pontos"][-1], inicio) > eps:
            atual = {"pontos": [inicio], "fechado": False}
            partes.append(atual)
        if tipo == "l":
            atual["pontos"].append((item[2].x, item[2].y))
        elif tipo == "c":
            atual["pontos"] += _bezier(inicio, (item[2].x, item[2].y), (item[3].x, item[3].y), (item[4].x, item[4].y))
            aproximado = True
    for parte in partes:
        pts = parte["pontos"]
        if not parte["fechado"] and len(pts) > 2 and math.dist(pts[0], pts[-1]) <= eps:
            parte["fechado"] = True
            pts.pop()
    if partes and (desenho.get("closePath") or desenho.get("fill") is not None):
        for parte in partes:
            parte["fechado"] = parte["fechado"] or len(parte["pontos"]) > 2
    return partes, aproximado


def _fator(escala, calibracoes):
    avisos, k_escala, ks = [], None, []
    if escala:
        m = re.fullmatch(r"\s*1\s*[:/]\s*(\d+(?:[.,]\d+)?)\s*", escala)
        if not m:
            sys.exit("Escala inválida; use o formato 1:50.")
        k_escala = PONTO_EM_METROS * float(m.group(1).replace(",", "."))
    for calibracao in calibracoes or []:
        x1, y1, x2, y2, distancia = (float(v) for v in calibracao.split(","))
        comprimento = math.hypot(x2 - x1, y2 - y1)
        if comprimento == 0:
            sys.exit("Calibração com pontos coincidentes.")
        ks.append(distancia / comprimento)
    if not ks and k_escala is None:
        sys.exit("Escala não definida: informe --escala 1:N (escrita na prancha) ou --calibrar x1,y1,x2,y2,metros "
                 "com uma cota conhecida.")
    if ks:
        k = sum(ks) / len(ks)
        if len(ks) > 1 and (max(ks) - min(ks)) / k > 0.005:
            avisos.append("calibrações divergem mais de 0,5%: página distorcida ou escala diferente por vista")
        if k_escala and abs(k - k_escala) / k_escala > 0.005:
            avisos.append(f"calibração difere da escala escrita em {abs(k - k_escala) / k_escala:.1%}")
        return k, "calibração por cota", True, avisos
    avisos.append("escala escrita na prancha, sem confirmação por cota (use --calibrar)")
    return k_escala, f"escala {escala}", False, avisos


def medir(caminho, pagina_numero, escala=None, calibracoes=None, recorte=None, abertas=False, cor=None,
          area_minima_m2=0.0, poligono=None, aberto=False):
    k, fonte, validada, avisos = _fator(escala, calibracoes)
    if poligono:
        # Medição gráfica: pontos lidos na imagem (ver render --grade), em coordenadas da página.
        return {"origem": str(caminho), "pagina": pagina_numero, "recorte": recorte,
                "unidade": {"k": k, "fonte": fonte, "validada": validada},
                "avisos": avisos + ["medição gráfica: o item que usar este resultado fica em PREMISSA"],
                "regioes": [{"id": "M0001", "tipo": "poligono_manual", "origem": "medicao_grafica",
                             "fechada": not aberto, "vertices": [list(p) for p in poligono], "aproximado": True}]}
    _, doc = _abrir(caminho)
    pagina = _pagina(doc, pagina_numero)
    regioes = []
    for desenho in pagina.get_drawings():
        if cor and cor.lower() not in (_hex(desenho.get("color")), _hex(desenho.get("fill"))):
            continue
        partes, aproximado = _subcaminhos(desenho)
        for parte in partes:
            pontos = parte["pontos"]
            if len(pontos) < 2 or (not parte["fechado"] and not abertas):
                continue
            if recorte:
                xs, ys = [p[0] for p in pontos], [p[1] for p in pontos]
                if max(xs) < recorte[0] or min(xs) > recorte[2] or max(ys) < recorte[1] or min(ys) > recorte[3]:
                    continue
            if parte["fechado"] and g.area(pontos) * k * k < area_minima_m2:
                continue
            regioes.append({"id": f"R{len(regioes) + 1:04d}", "tipo": "caminho_pdf", "fechada": parte["fechado"],
                            "vertices": [[round(x, 4), round(y, 4)] for x, y in pontos], "aproximado": aproximado,
                            "cor": _hex(desenho.get("color")), "preenchimento": _hex(desenho.get("fill"))})
    doc.close()
    return {"origem": str(caminho), "pagina": pagina_numero, "recorte": recorte,
            "unidade": {"k": k, "fonte": fonte, "validada": validada}, "avisos": avisos, "regioes": regioes}


def _grade(pagina, pymupdf, passo, janela):
    """Linhas de coordenadas a cada `passo` pontos, para ler posições numa página raster."""
    forma = pagina.new_shape()
    x = math.floor(janela.x0 / passo) * passo
    while x <= janela.x1:
        forma.draw_line((x, janela.y0), (x, janela.y1))
        x += passo
    y = math.floor(janela.y0 / passo) * passo
    while y <= janela.y1:
        forma.draw_line((janela.x0, y), (janela.x1, y))
        y += passo
    forma.finish(color=(0.2, 0.6, 0.9), width=0.3, stroke_opacity=0.7)
    forma.commit()
    x = math.floor(janela.x0 / passo) * passo
    while x <= janela.x1:
        pagina.insert_text((x + 1, janela.y0 + 7), f"{x:.0f}", fontsize=5, color=(0.1, 0.4, 0.8))
        x += passo
    y = math.floor(janela.y0 / passo) * passo
    while y <= janela.y1:
        pagina.insert_text((janela.x0 + 1, y - 1), f"{y:.0f}", fontsize=5, color=(0.1, 0.4, 0.8))
        y += passo


def render(caminho, pagina_numero, saida, recorte=None, dpi=150, arquivo_marcas=None, largura_max=1600, titulo=None,
           grade=None):
    pymupdf, doc = _abrir(caminho)
    pagina = _pagina(doc, pagina_numero)
    dados = mk.carregar(arquivo_marcas) if arquivo_marcas else {"marcas": []}
    if grade:
        _grade(pagina, pymupdf, grade, pymupdf.Rect(*recorte) if recorte else pagina.rect)
    forma = pagina.new_shape()
    rotulos = []
    for marca in dados.get("marcas") or []:
        cor = mk.cor_rgb(marca.get("cor"))
        tipo = marca.get("tipo", "poligono")
        espessura = marca.get("espessura", 1.5)
        if tipo == "poligono":
            for anel in mk.aneis(marca):
                if len(anel) >= 3:
                    forma.draw_polyline([*anel, anel[0]])
            forma.finish(color=cor, fill=cor, fill_opacity=marca.get("preenchimento", 0.3), width=espessura,
                         even_odd=True, closePath=True)
        elif tipo == "linha":
            forma.draw_polyline(mk.linha(marca))
            forma.finish(color=cor, width=espessura + 1, closePath=False)
        elif tipo == "ponto":
            for p in marca["pontos"]:
                forma.draw_circle(p[:2], 5)
            forma.finish(color=cor, width=2, closePath=True)
        texto_rotulo = marca.get("texto") if tipo == "texto" else marca.get("rotulo")
        posicao = marca["pontos"][0] if tipo in ("texto", "ponto") else mk.posicao_rotulo(marca)
        if texto_rotulo and posicao:
            rotulos.append((texto_rotulo, posicao, cor))
    for texto_rotulo, (x, y, *_), cor in rotulos:
        largura_texto = 0.55 * 8 * len(str(texto_rotulo))
        forma.draw_rect(pymupdf.Rect(x - largura_texto / 2 - 2, y - 7, x + largura_texto / 2 + 2, y + 4))
        forma.finish(color=cor, fill=(1, 1, 1), width=0.5, fill_opacity=0.9)
    forma.commit()
    for texto_rotulo, (x, y, *_), cor in rotulos:
        largura_texto = 0.55 * 8 * len(str(texto_rotulo))
        pagina.insert_text((x - largura_texto / 2, y + 2), str(texto_rotulo), fontsize=8, color=cor)
    if recorte:
        janela = pymupdf.Rect(*recorte)
    elif mk.limites(dados):
        janela = pymupdf.Rect(*mk.limites(dados, margem=0.15))
    else:
        janela = pagina.rect
    zoom = dpi / 72
    if janela.width * zoom > largura_max:
        zoom = largura_max / janela.width
    imagem = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=janela, alpha=False)
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    imagem.save(str(saida))
    doc.close()
    rodape = " — ".join(filter(None, [Path(caminho).name, f"página {pagina_numero}", titulo or dados.get("titulo"),
                                      f"recorte {', '.join(f'{v:.0f}' for v in janela)}", "pdf.py render"]))
    _acabamento(saida, rodape, dados.get("legenda") or [])
    return saida


FONTES = ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf")


def _fonte(tamanho):
    """Fonte TrueType com acentos; sem nenhuma, devolve None e o texto sai sem acentos."""
    from PIL import ImageFont
    candidatos = list(FONTES)
    try:
        from matplotlib import font_manager
        candidatos.insert(0, font_manager.findfont("DejaVu Sans", fallback_to_default=True))
    except Exception:  # noqa: BLE001 - matplotlib é opcional aqui
        pass
    for caminho in candidatos:
        if caminho and Path(caminho).is_file():
            try:
                return ImageFont.truetype(caminho, tamanho)
            except OSError:
                continue
    return None


def _acabamento(caminho, rodape, legenda):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    fonte = _fonte(12)
    if fonte is None:
        import unicodedata
        fonte = ImageFont.load_default()

        def sem_acento(texto):
            return unicodedata.normalize("NFKD", texto.replace("—", "-")).encode("ascii", "ignore").decode()

        rodape = sem_acento(rodape)
        legenda = [{**item, "texto": sem_acento(str(item.get("texto", "")))} for item in legenda]
    with Image.open(caminho) as original:
        base = original.convert("RGB")
    tela = Image.new("RGB", (base.width, base.height + 22), "white")
    tela.paste(base, (0, 0))
    desenho = ImageDraw.Draw(tela)
    desenho.text((6, base.height + 4), rodape, fill=(50, 50, 50), font=fonte)
    if legenda:
        largura = max(desenho.textlength(str(item.get("texto", "")), font=fonte) for item in legenda) + 44
        desenho.rectangle([6, 6, 6 + largura, 14 + 18 * len(legenda)], fill=(255, 255, 255), outline=(120, 120, 120))
        for i, item in enumerate(legenda):
            cor = tuple(round(c * 255) for c in mk.cor_rgb(item.get("cor")))
            y = 11 + 18 * i
            desenho.rectangle([12, y + 2, 26, y + 13], fill=cor)
            desenho.text((32, y), str(item.get("texto", "")), fill=(30, 30, 30), font=fonte)
    tela.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(caminho, optimize=True)


def _pontos(texto):
    try:
        pontos = [tuple(float(v) for v in par.split(",")) for par in texto.split(";") if par.strip()]
    except ValueError as erro:
        raise argparse.ArgumentTypeError("use 'x1,y1;x2,y2;...'") from erro
    if len(pontos) < 2 or any(len(p) != 2 for p in pontos):
        raise argparse.ArgumentTypeError("use 'x1,y1;x2,y2;...' com ao menos dois pontos")
    return pontos


def _numeros(texto, quantidade):
    valores = [float(v) for v in texto.split(",")]
    if len(valores) != quantidade:
        raise argparse.ArgumentTypeError(f"esperados {quantidade} números separados por vírgula")
    return valores


def _gravar(dados, saida):
    texto_json = json.dumps(dados, ensure_ascii=False, indent=2)
    if saida:
        Path(saida).parent.mkdir(parents=True, exist_ok=True)
        Path(saida).write_text(texto_json + "\n", encoding="utf-8")
    return texto_json


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("inventario")
    p.add_argument("pdf")
    p.add_argument("--saida")
    p = sub.add_parser("texto")
    p.add_argument("pdf")
    p.add_argument("--busca", required=True, help="expressão regular, ex.: 'A\\s*=\\s*\\d'")
    p.add_argument("--paginas", help="ex.: 1,3,5")
    p.add_argument("--saida")
    p = sub.add_parser("medir")
    p.add_argument("pdf")
    p.add_argument("--pagina", type=int, required=True)
    p.add_argument("--escala", help="escala escrita na prancha, ex.: 1:50")
    p.add_argument("--calibrar", action="append", help="x1,y1,x2,y2,metros de uma cota conhecida (pode repetir)")
    p.add_argument("--recorte", type=lambda t: _numeros(t, 4), help="x0,y0,x1,y1 em pontos")
    p.add_argument("--abertas", action="store_true", help="incluir caminhos abertos (comprimentos)")
    p.add_argument("--cor", help="só caminhos com esta cor de traço ou preenchimento (#rrggbb)")
    p.add_argument("--area-minima", type=float, default=0.0, help="m²; descarta anéis menores")
    p.add_argument("--poligono", type=_pontos,
                   help="medição gráfica: 'x1,y1;x2,y2;...' em pontos da página (leia com render --grade)")
    p.add_argument("--aberto", action="store_true", help="com --poligono: trecho aberto (comprimento)")
    p.add_argument("--saida")
    p = sub.add_parser("render")
    p.add_argument("pdf")
    p.add_argument("--pagina", type=int, required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--recorte", type=lambda t: _numeros(t, 4))
    p.add_argument("--dpi", type=int, default=150)
    p.add_argument("--marcas")
    p.add_argument("--largura", type=int, default=1600)
    p.add_argument("--titulo")
    p.add_argument("--grade", type=float, help="desenha linhas de coordenadas a cada N pontos")
    a = parser.parse_args()

    if a.comando == "inventario":
        print(_gravar(inventario(a.pdf), a.saida) if not a.saida else
              json.dumps({"saida": a.saida, "paginas": len(json.loads(_gravar(inventario(a.pdf), a.saida))["paginas"])},
                         ensure_ascii=False))
    elif a.comando == "texto":
        paginas = [int(n) for n in a.paginas.split(",")] if a.paginas else None
        dados = texto(a.pdf, a.busca, paginas)
        _gravar(dados, a.saida)
        print(json.dumps({"achados": len(dados["achados"]), "saida": a.saida}, ensure_ascii=False)
              if a.saida else _gravar(dados, None))
    elif a.comando == "medir":
        dados = medir(a.pdf, a.pagina, a.escala, a.calibrar, a.recorte, a.abertas, a.cor, a.area_minima,
                      a.poligono, a.aberto)
        _gravar(dados, a.saida)
        print(json.dumps({"regioes": len(dados["regioes"]), "unidade": dados["unidade"], "avisos": dados["avisos"]},
                         ensure_ascii=False))
    else:
        saida = render(a.pdf, a.pagina, a.saida, a.recorte, a.dpi, a.marcas, a.largura, a.titulo, a.grade)
        print(json.dumps({"saida": str(saida)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
