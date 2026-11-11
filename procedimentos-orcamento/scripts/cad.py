#!/usr/bin/env python3
"""DWG/DXF: conversão, inventário, extração de contornos, prints marcados e comparação de revisões.

  converter   DWG → DXF pelo ODA File Converter (via ezdxf.addons.odafc) ou, sem ele, pelo
              AcCoreConsole do AutoCAD (sem interface, sobre cópias); hashes, ferramenta e
              tentativas vão para o manifesto conversao_dxf.json da pasta de saída
  inventario  unidade, camadas, layouts e viewports, blocos com contagem, textos, cotas,
              hachuras, referências externas e as regiões desenhadas no Model
  extrair     polilinhas, hachuras e círculos (arcos exatos, furos) no formato do geometria.py
  render      PNG de uma região do Model ou de um layout, com marcas desenhadas nas
              coordenadas do próprio desenho (formato em marcas.py)
  comparar    entidades acrescentadas e removidas por camada entre duas revisões

Precisa de ezdxf (a conversão pelo AcCoreConsole, não); render também de matplotlib. O arquivo
de origem nunca é gravado.
"""

import argparse
import fnmatch
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

import geometria as g
import marcas as mk


def _ezdxf():
    try:
        import ezdxf
    except ImportError:
        sys.exit("cad.py precisa de ezdxf: python3 -m pip install -r scripts/requirements.txt")
    return ezdxf


def abrir(caminho):
    ezdxf = _ezdxf()
    try:
        return ezdxf.readfile(caminho)
    except ezdxf.DXFStructureError:
        from ezdxf import recover
        doc, _ = recover.readfile(caminho)
        return doc
    except OSError as erro:
        sys.exit(f"Não foi possível abrir {caminho}: {erro}")


def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _layouts(doc):
    return [doc.layouts.get(nome) for nome in doc.layouts.names_in_taborder()]


def _ponto(entidade):
    """Um ponto representativo da entidade, para agrupar regiões e localizar mudanças."""
    tipo = entidade.dxftype()
    try:
        if tipo in ("INSERT", "TEXT", "MTEXT", "ATTRIB"):
            p = entidade.dxf.insert
        elif tipo == "LINE":
            p = entidade.dxf.start
        elif tipo in ("CIRCLE", "ARC", "ELLIPSE"):
            p = entidade.dxf.center
        elif tipo == "LWPOLYLINE":
            p = next(iter(entidade.get_points("xy")))
        elif tipo == "POLYLINE":
            p = next(iter(entidade.vertices)).dxf.location
        elif tipo == "HATCH":
            caminho = next(iter(entidade.paths))
            p = caminho.vertices[0] if hasattr(caminho, "vertices") else caminho.edges[0].start
        elif tipo == "DIMENSION":
            p = entidade.dxf.defpoint
        elif tipo == "SPLINE":
            p = entidade.control_points[0]
        else:
            return None
        return (float(p[0]), float(p[1]))
    except (StopIteration, IndexError, AttributeError, TypeError):
        return None


def _nome_bloco(insercao, doc):
    """Nome efetivo do bloco (blocos dinâmicos aparecem como *U…; o nome original vem do registro)."""
    return _nome_bloco_por_nome(doc, insercao.dxf.name)


def _multiplicidade(insercao):
    """Quantidade de cópias de uma inserção (MINSERT tem linhas × colunas)."""
    try:
        return max(1, int(getattr(insercao, "mcount", 1) or 1))
    except (TypeError, ValueError):
        return 1


def _contar_aninhados(doc, nome_bloco, multiplicador, contagem, profundidade=0):
    """Soma as inserções dentro da definição do bloco, recursivamente (até 8 níveis)."""
    if profundidade > 8:
        return
    bloco = doc.blocks.get(nome_bloco)
    if bloco is None:
        return
    pai = _nome_bloco_por_nome(doc, nome_bloco)
    for entidade in bloco:
        if entidade.dxftype() == "INSERT":
            quantidade = multiplicador * _multiplicidade(entidade)
            contagem[(_nome_bloco(entidade, doc), pai)] += quantidade
            _contar_aninhados(doc, entidade.dxf.name, quantidade, contagem, profundidade + 1)


def _nome_bloco_por_nome(doc, nome):
    if not nome.startswith("*"):
        return nome
    registro = doc.block_records.get(nome)
    try:
        if registro is not None and registro.has_xdata("AcDbBlockRepBTag"):
            for codigo, valor in registro.get_xdata("AcDbBlockRepBTag"):
                if codigo == 1005 and doc.entitydb.get(valor) is not None:
                    return doc.entitydb.get(valor).dxf.name
    except Exception:  # noqa: BLE001 - nome efetivo é melhor esforço
        pass
    return nome


def _texto_entidade(entidade):
    if entidade.dxftype() == "MTEXT":
        return entidade.plain_text()
    return entidade.dxf.text


def _tracado(entidade):
    """Segmentos e pontos que representam a entidade no plano, para agrupar regiões."""
    tipo = entidade.dxftype()
    try:
        if tipo == "LINE":
            a, b = entidade.dxf.start, entidade.dxf.end
            return [((float(a.x), float(a.y)), (float(b.x), float(b.y)))], []
        if tipo in ("LWPOLYLINE", "POLYLINE"):
            if tipo == "LWPOLYLINE":
                pontos, fechada = [(float(x), float(y)) for x, y in entidade.get_points("xy")], entidade.closed
            else:
                pontos = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in entidade.vertices]
                fechada = entidade.is_closed
            segmentos = list(zip(pontos, pontos[1:])) + ([(pontos[-1], pontos[0])] if fechada and len(pontos) > 2 else [])
            return segmentos, pontos[:1]
        if tipo in ("CIRCLE", "ARC"):
            c, r = entidade.dxf.center, float(entidade.dxf.radius)
            pontos = [(float(c.x) + r * math.cos(t), float(c.y) + r * math.sin(t)) for t in (0, math.pi / 2, math.pi,
                                                                                               3 * math.pi / 2)]
            return list(zip(pontos, pontos[1:] + pontos[:1])), []
        if tipo == "HATCH":
            segmentos = []
            for contorno in entidade.paths:
                if hasattr(contorno, "vertices"):
                    pontos = [(float(v[0]), float(v[1])) for v in contorno.vertices]
                else:
                    pontos = [(float(e.start[0]), float(e.start[1])) for e in contorno.edges if hasattr(e, "start")]
                segmentos += list(zip(pontos, pontos[1:] + pontos[:1]))
            return segmentos, []
    except (AttributeError, TypeError, IndexError):
        pass
    p = _ponto(entidade)
    return [], [p] if p else []


def _regioes(tracados, divisoes=100, alcance=2, minimo=3):
    """Agrupa entidades próximas (grade com vizinhança de `alcance` células) em regiões separadas."""
    coordenadas = [p for segmentos, pontos, _ in tracados for s in segmentos for p in s] + \
                  [p for _, pontos, _ in tracados for p in pontos]
    if not coordenadas:
        return []
    xs, ys = [p[0] for p in coordenadas], [p[1] for p in coordenadas]
    lado = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9) / divisoes

    def celula(p):
        return (math.floor(p[0] / lado), math.floor(p[1] / lado))

    celulas_entidade, ocupadas = [], set()
    for segmentos, pontos, _ in tracados:
        proprias = {celula(p) for p in pontos}
        for a, b in segmentos:
            partes = min(200, max(1, math.ceil(math.dist(a, b) / lado)))
            proprias |= {celula((a[0] + (b[0] - a[0]) * i / partes, a[1] + (b[1] - a[1]) * i / partes))
                         for i in range(partes + 1)}
        celulas_entidade.append(proprias)
        ocupadas |= proprias
    componente = {}
    for inicio in ocupadas:
        if inicio in componente:
            continue
        rotulo = len(set(componente.values()))
        fila = [inicio]
        componente[inicio] = rotulo
        while fila:
            cx, cy = fila.pop()
            for dx in range(-alcance, alcance + 1):
                for dy in range(-alcance, alcance + 1):
                    vizinha = (cx + dx, cy + dy)
                    if vizinha in ocupadas and vizinha not in componente:
                        componente[vizinha] = rotulo
                        fila.append(vizinha)
    grupos = defaultdict(list)
    for indice, proprias in enumerate(celulas_entidade):
        if proprias:
            grupos[componente[next(iter(proprias))]].append(indice)
    saida = []
    for membros in sorted(grupos.values(), key=len, reverse=True):
        if len(membros) < minimo:
            continue
        pontos = [p for i in membros for s in tracados[i][0] for p in s] + [p for i in membros for p in tracados[i][1]]
        textos = sorted((tracados[i][2] for i in membros if tracados[i][2]), key=lambda t: -t[1])
        saida.append({"id": f"R{len(saida) + 1:02d}", "entidades": len(membros),
                      "bbox": [min(p[0] for p in pontos), min(p[1] for p in pontos),
                               max(p[0] for p in pontos), max(p[1] for p in pontos)],
                      "titulo_provavel": textos[0][0] if textos else None,
                      "textos_destaque": [t[0] for t in textos[:5]]})
    return saida


def inventario(caminho):
    doc = abrir(caminho)
    insunits = int(doc.header.get("$INSUNITS", 0) or 0)
    contagem_camada = defaultdict(Counter)
    blocos = Counter()
    aninhados = Counter()
    atributos = defaultdict(set)
    textos, cotas, hachuras, polilinhas, imagens = [], [], Counter(), Counter(), 0
    pontos_model = []
    layouts = []
    for layout in _layouts(doc):
        nome_layout = layout.name
        registro = {"nome": nome_layout, "entidades": len(layout), "viewports": []}
        for entidade in layout:
            tipo = entidade.dxftype()
            camada = entidade.dxf.get("layer", "0")
            contagem_camada[camada][nome_layout] += 1
            if tipo == "INSERT":
                nome = _nome_bloco(entidade, doc)
                blocos[(nome, camada, nome_layout)] += _multiplicidade(entidade)
                _contar_aninhados(doc, entidade.dxf.name, _multiplicidade(entidade), aninhados)
                for atributo in getattr(entidade, "attribs", []):
                    if len(atributos[nome]) < 12:
                        atributos[nome].add(f"{atributo.dxf.tag}={atributo.dxf.text}")
            elif tipo in ("TEXT", "MTEXT"):
                p = _ponto(entidade)
                altura = float((entidade.dxf.get("char_height", 0) if tipo == "MTEXT"
                                else entidade.dxf.get("height", 0)) or 0)
                textos.append({"texto": _texto_entidade(entidade), "camada": camada, "layout": nome_layout,
                               "x": p[0] if p else None, "y": p[1] if p else None, "altura": altura})
            elif tipo == "DIMENSION":
                try:
                    medida = float(entidade.get_measurement())
                except Exception:  # noqa: BLE001 - cota sem medida legível
                    medida = None
                cotas.append({"medida": medida, "texto": entidade.dxf.get("text", ""), "camada": camada,
                              "layout": nome_layout})
            elif tipo == "HATCH":
                hachuras[(camada, entidade.dxf.get("pattern_name", ""))] += 1
            elif tipo in ("LWPOLYLINE", "POLYLINE"):
                if getattr(entidade, "closed", False) or getattr(entidade, "is_closed", False):
                    polilinhas[camada] += 1
            elif tipo == "IMAGE":
                imagens += 1
            elif tipo == "VIEWPORT" and nome_layout != "Model" and entidade.dxf.get("id", 2) != 1:
                altura_vista = float(entidade.dxf.get("view_height", 0) or 0)
                registro["viewports"].append({
                    "centro": list(entidade.dxf.center)[:2], "largura": entidade.dxf.width,
                    "altura": entidade.dxf.height, "centro_vista": list(entidade.dxf.view_center_point)[:2],
                    "altura_vista": altura_vista,
                    "escala_papel_por_modelo": (entidade.dxf.height / altura_vista) if altura_vista else None,
                    "camadas_congeladas": list(entidade.frozen_layers)})
            if nome_layout == "Model":
                segmentos, pontos = _tracado(entidade)
                if segmentos or pontos:
                    destaque = (_texto_entidade(entidade), textos[-1]["altura"]) if tipo in ("TEXT", "MTEXT") else None
                    pontos_model.append((segmentos, pontos, destaque))
        layouts.append(registro)
    camadas = []
    for camada in doc.layers:
        nome = camada.dxf.name
        camadas.append({"nome": nome, "ligada": not camada.is_off(), "congelada": camada.is_frozen(),
                        "travada": camada.is_locked(), "cor": camada.color,
                        "entidades": dict(contagem_camada.get(nome, {}))})
    referencias = []
    for bloco in doc.blocks:
        try:
            if bloco.block is not None and bloco.block.dxf.get("flags", 0) & 4:
                referencias.append({"nome": bloco.name, "caminho": bloco.block.dxf.get("xref_path", "")})
        except AttributeError:
            continue
    definicoes_imagem = [obj.dxf.get("filename", "") for obj in doc.objects.query("IMAGEDEF")]
    return {
        "arquivo": str(caminho), "sha256": _sha256(caminho), "versao_dxf": doc.dxfversion,
        "unidade": {"insunits": insunits, "k": g.fator_insunits(insunits), "validada": False},
        "camadas": camadas, "layouts": layouts,
        "blocos": [{"bloco": b, "camada": c, "layout": l, "quantidade": n,
                    "atributos": sorted(atributos.get(b, []))} for (b, c, l), n in blocos.most_common()],
        "blocos_aninhados": [{"bloco": b, "dentro_de": pai, "quantidade": n} for (b, pai), n in aninhados.most_common()],
        "textos": textos, "cotas": cotas,
        "hachuras": [{"camada": c, "padrao": p, "quantidade": n} for (c, p), n in hachuras.most_common()],
        "polilinhas_fechadas": dict(polilinhas), "referencias_externas": referencias,
        "imagens": {"quantidade": imagens, "arquivos": definicoes_imagem},
        "regioes_model": _regioes(pontos_model),
        "observacao": "blocos = inserções diretas no layout; blocos_aninhados = inserções dentro de outros blocos, "
                      "já multiplicadas pelas inserções do bloco pai. Referências externas precisam do arquivo "
                      "referenciado. Unidade a validar com duas cotas conhecidas.",
    }


def inventario_markdown(inv):
    linhas = [f"# Inventário CAD — {Path(inv['arquivo']).name}", "",
              f"Unidade: $INSUNITS={inv['unidade']['insunits']} (k = {inv['unidade']['k']} m por unidade, a validar).", "",
              "## Regiões desenhadas no Model", "", "| ID | Entidades | Limites | Título provável |", "|---|---:|---|---|"]
    for r in inv["regioes_model"]:
        bbox = ", ".join(f"{v:.0f}" for v in r["bbox"])
        linhas.append(f"| {r['id']} | {r['entidades']} | {bbox} | {r['titulo_provavel'] or ''} |")
    linhas += ["", "## Layouts", "", "| Layout | Entidades | Viewports |", "|---|---:|---:|"]
    linhas += [f"| {l['nome']} | {l['entidades']} | {len(l['viewports'])} |" for l in inv["layouts"]]
    linhas += ["", "## Camadas", "", "| Camada | Ligada | Congelada | Entidades por layout |", "|---|---|---|---|"]
    for c in inv["camadas"]:
        linhas.append(f"| {c['nome']} | {'sim' if c['ligada'] else 'não'} | {'sim' if c['congelada'] else 'não'} | "
                      + ", ".join(f"{k}: {v}" for k, v in c["entidades"].items()) + " |")
    linhas += ["", "## Blocos", "", "| Bloco | Camada | Layout | Quantidade |", "|---|---|---|---:|"]
    linhas += [f"| {b['bloco']} | {b['camada']} | {b['layout']} | {b['quantidade']} |" for b in inv["blocos"][:200]]
    if inv["referencias_externas"]:
        linhas += ["", "Referências externas: " + ", ".join(r["nome"] for r in inv["referencias_externas"])]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- extração

def _intersecta(bbox, pontos):
    if bbox is None or not pontos:
        return True
    xs, ys = [p[0] for p in pontos], [p[1] for p in pontos]
    return not (max(xs) < bbox[0] or min(xs) > bbox[2] or max(ys) < bbox[1] or min(ys) > bbox[3])


def _camada_aceita(camada, filtros):
    return not filtros or any(fnmatch.fnmatchcase(camada, f) for f in filtros)


def _aneis_hachura(hachura, tolerancia):
    from ezdxf import path as dxfpath
    aneis, aproximado = [], False
    plano = tuple(hachura.dxf.get("extrusion", (0, 0, 1))) == (0, 0, 1)
    for contorno in hachura.paths:
        if hasattr(contorno, "vertices") and plano:
            aneis.append([(float(v[0]), float(v[1]), float(v[2]) if len(v) > 2 else 0.0) for v in contorno.vertices])
        else:
            caminho = dxfpath.from_hatch_boundary_path(contorno, hachura.ocs(), hachura.dxf.elevation.z)
            aneis.append([(float(p.x), float(p.y)) for p in caminho.flattening(tolerancia)])
            aproximado = True
    return aneis, aproximado


def _virtuais(insercao, camada_pai, doc, profundidade=0):
    """Entidades de um bloco já posicionadas no desenho; a camada 0 herda a camada da inserção."""
    if profundidade > 8:
        return
    try:
        filhas = list(insercao.virtual_entities())
    except Exception:  # noqa: BLE001 - bloco sem geometria explodível
        return
    for filha in filhas:
        camada = filha.dxf.get("layer", "0")
        camada = camada_pai if camada == "0" else camada
        if filha.dxftype() == "INSERT":
            yield from _virtuais(filha, camada, doc, profundidade + 1)
        else:
            yield filha, camada, _nome_bloco(insercao, doc)


def _entidades(espaco, doc, blocos):
    for entidade in espaco:
        camada = entidade.dxf.get("layer", "0")
        if blocos and entidade.dxftype() == "INSERT":
            yield from _virtuais(entidade, camada, doc)
        else:
            yield entidade, camada, None


def extrair(caminho, camadas=None, bbox=None, layout=None, abertas=False, tolerancia=None, blocos=False):
    doc = abrir(caminho)
    espaco = doc.modelspace() if not layout or layout == "Model" else doc.layouts.get(layout)
    insunits = int(doc.header.get("$INSUNITS", 0) or 0)
    if tolerancia is None:
        fator = g.fator_insunits(insunits) or 1.0
        tolerancia = 0.0005 / fator
    regioes = []

    def acrescentar(entidade, camada, bloco, tipo, fechada, vertices=None, aneis=None, aproximado=False, **extra):
        pontos = vertices or (aneis[0] if aneis else [])
        if not _intersecta(bbox, pontos):
            return
        registro = {"id": f"R{len(regioes) + 1:04d}", "handle": entidade.dxf.get("handle"), "camada": camada,
                    "tipo": tipo, "fechada": fechada, "aproximado": aproximado, **extra}
        if bloco:
            registro["bloco"] = bloco
        if aneis is not None:
            registro["aneis"] = aneis
        else:
            registro["vertices"] = vertices
        regioes.append(registro)

    for entidade, camada, bloco in _entidades(espaco, doc, blocos):
        if not _camada_aceita(camada, camadas):
            continue
        tipo = entidade.dxftype()
        contexto = (entidade, camada, bloco, tipo)
        if tipo == "LWPOLYLINE":
            vertices = [(float(x), float(y), float(b)) for x, y, b in entidade.get_points("xyb")]
            fechada = bool(entidade.closed) or (len(vertices) > 2 and vertices[0][:2] == vertices[-1][:2])
            if fechada or abertas:
                acrescentar(*contexto, fechada, vertices)
        elif tipo == "POLYLINE" and entidade.is_2d_polyline:
            vertices = [(float(v.dxf.location.x), float(v.dxf.location.y), float(v.dxf.get("bulge", 0)))
                        for v in entidade.vertices]
            if entidade.is_closed or abertas:
                acrescentar(*contexto, entidade.is_closed, vertices)
        elif tipo == "CIRCLE":
            cx, cy, r = float(entidade.dxf.center.x), float(entidade.dxf.center.y), float(entidade.dxf.radius)
            acrescentar(*contexto, True, [(cx - r, cy, 1.0), (cx + r, cy, 1.0)])
        elif tipo == "HATCH":
            aneis, aproximado = _aneis_hachura(entidade, tolerancia)
            if aneis:
                acrescentar(*contexto, True, aneis=aneis, aproximado=aproximado,
                            padrao=entidade.dxf.get("pattern_name", ""))
        elif abertas and tipo == "LINE":
            a, b = entidade.dxf.start, entidade.dxf.end
            acrescentar(*contexto, False, [(float(a.x), float(a.y)), (float(b.x), float(b.y))])
        elif abertas and tipo == "ARC":
            c, r = entidade.dxf.center, float(entidade.dxf.radius)
            inicio, fim = math.radians(entidade.dxf.start_angle), math.radians(entidade.dxf.end_angle)
            varredura = (fim - inicio) % (2 * math.pi) or 2 * math.pi
            a = (float(c.x) + r * math.cos(inicio), float(c.y) + r * math.sin(inicio), math.tan(varredura / 4))
            b = (float(c.x) + r * math.cos(fim), float(c.y) + r * math.sin(fim), 0.0)
            acrescentar(*contexto, False, [a, b])
    return {"origem": str(caminho), "sha256": _sha256(caminho), "layout": espaco.name,
            "unidade": {"insunits": insunits, "k": g.fator_insunits(insunits), "validada": False},
            "tolerancia_curvas": tolerancia, "regioes": regioes}


# ---------------------------------------------------------------- render

def render(caminho, saida, bbox=None, layout=None, arquivo_marcas=None, largura=1600, ocultar=(),
           titulo=None, cores_originais=False, hachuras_solidas=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, PathPatch
    from matplotlib.path import Path as CaminhoMpl
    from ezdxf import bbox as dxfbbox
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration, HatchPolicy
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    doc = abrir(caminho)
    espaco = doc.modelspace() if not layout or layout == "Model" else doc.layouts.get(layout)
    dados = mk.carregar(arquivo_marcas) if arquivo_marcas else {"marcas": []}
    if bbox is None:
        bbox = mk.limites(dados)
    if bbox is None:
        extensao = dxfbbox.extents(espaco, fast=True)
        bbox = (extensao.extmin.x, extensao.extmin.y, extensao.extmax.x, extensao.extmax.y)
    x0, y0, x1, y1 = bbox
    ocultas = set(ocultar or ())

    def filtro(entidade):
        if entidade.dxf.get("layer", "0") in ocultas:
            return False
        caixa = dxfbbox.extents([entidade], fast=True)
        if not caixa.has_data:
            return True
        return not (caixa.extmax.x < x0 or caixa.extmin.x > x1 or caixa.extmax.y < y0 or caixa.extmin.y > y1)

    proporcao = max((y1 - y0) / max(x1 - x0, 1e-9), 0.05)
    figura = plt.figure(figsize=(largura / 100, largura / 100 * proporcao + 0.45), dpi=100)
    eixo = figura.add_axes([0, 0.45 / (largura / 100 * proporcao + 0.45), 1, 1 - 0.45 / (largura / 100 * proporcao + 0.45)])
    configuracao = Configuration(background_policy=BackgroundPolicy.WHITE,
                                 color_policy=ColorPolicy.COLOR if cores_originais else ColorPolicy.CUSTOM,
                                 custom_fg_color="#555555",
                                 hatch_policy=HatchPolicy.NORMAL if hachuras_solidas else HatchPolicy.SHOW_OUTLINE)
    Frontend(RenderContext(doc), MatplotlibBackend(eixo, adjust_figure=False), config=configuracao).draw_layout(
        espaco, finalize=True, filter_func=filtro)
    for marca in dados.get("marcas") or []:
        cor = mk.cor_rgb(marca.get("cor"))
        tipo = marca.get("tipo", "poligono")
        espessura = marca.get("espessura", 2.5)
        if tipo == "poligono":
            vertices, codigos = [], []
            for indice, anel in enumerate(mk.aneis(marca)):
                if len(anel) < 3:
                    continue
                horario = g.area_assinada(anel) < 0
                if (indice == 0) == horario:
                    anel = anel[::-1]
                vertices += anel + [anel[0]]
                codigos += [CaminhoMpl.MOVETO] + [CaminhoMpl.LINETO] * (len(anel) - 1) + [CaminhoMpl.CLOSEPOLY]
            if vertices:
                eixo.add_patch(PathPatch(CaminhoMpl(vertices, codigos), facecolor=(*cor, marca.get("preenchimento", 0.3)),
                                         edgecolor=cor, linewidth=espessura, zorder=10))
        elif tipo == "linha":
            pontos = mk.linha(marca)
            eixo.plot([p[0] for p in pontos], [p[1] for p in pontos], color=cor, linewidth=espessura + 1, zorder=11)
        elif tipo == "ponto":
            for p in marca["pontos"]:
                eixo.plot([p[0]], [p[1]], marker="o", markersize=12, markerfacecolor="none",
                          markeredgecolor=cor, markeredgewidth=2.5, zorder=12)
        if tipo == "texto" or marca.get("rotulo"):
            posicao = marca["pontos"][0] if tipo in ("texto", "ponto") else mk.posicao_rotulo(marca)
            if posicao:
                eixo.annotate(marca.get("texto") or marca.get("rotulo"), (posicao[0], posicao[1]), fontsize=9,
                              fontweight="bold", color=cor if tipo != "texto" else "black", ha="center", va="center",
                              zorder=13, xytext=(0, 14) if tipo == "ponto" else (0, 0), textcoords="offset points",
                              bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": cor, "lw": 0.8, "alpha": 0.9})
    eixo.set_xlim(x0, x1)
    eixo.set_ylim(y0, y1)
    eixo.set_aspect("equal", adjustable="box")
    eixo.axis("off")
    legenda = [Patch(facecolor=(*mk.cor_rgb(item.get("cor")), 0.4), edgecolor=mk.cor_rgb(item.get("cor")),
                     label=item.get("texto", "")) for item in dados.get("legenda") or []]
    if legenda:
        eixo.legend(handles=legenda, loc="upper left", fontsize=9, framealpha=0.9)
    rodape = " — ".join(filter(None, [Path(caminho).name, titulo or dados.get("titulo"), espaco.name,
                                      f"região {x0:.0f},{y0:.0f} a {x1:.0f},{y1:.0f}", "cad.py render"]))
    figura.text(0.01, 0.15 / (largura / 100 * proporcao + 0.45), rodape, fontsize=8, color="#333333")
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(saida, dpi=100, facecolor="white")
    plt.close(figura)
    _otimizar_png(saida, largura)
    return saida


def _otimizar_png(caminho, largura):
    try:
        from PIL import Image
    except ImportError:
        return
    with Image.open(caminho) as imagem:
        imagem = imagem.convert("RGB")
        if imagem.width > largura:
            imagem = imagem.resize((largura, round(imagem.height * largura / imagem.width)), Image.Resampling.LANCZOS)
        imagem.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(caminho, optimize=True)


# ---------------------------------------------------------------- comparação

def _assinatura(entidade, tol):
    def r(v):
        return int(round(float(v) / tol))

    tipo = entidade.dxftype()
    try:
        if tipo == "LINE":
            a, b = sorted([(r(entidade.dxf.start.x), r(entidade.dxf.start.y)), (r(entidade.dxf.end.x), r(entidade.dxf.end.y))])
            geometria = (a, b)
        elif tipo == "LWPOLYLINE":
            geometria = (tuple((r(x), r(y), round(float(b), 6)) for x, y, b in entidade.get_points("xyb")),
                         bool(entidade.closed))
        elif tipo in ("CIRCLE", "ARC"):
            angulos = ((round(entidade.dxf.start_angle, 4), round(entidade.dxf.end_angle, 4))
                       if tipo == "ARC" else (0, 0))
            geometria = (r(entidade.dxf.center.x), r(entidade.dxf.center.y), r(entidade.dxf.radius), *angulos)
        elif tipo == "INSERT":
            geometria = (entidade.dxf.name, r(entidade.dxf.insert.x), r(entidade.dxf.insert.y),
                         round(entidade.dxf.get("rotation", 0), 4), round(entidade.dxf.get("xscale", 1), 6))
        elif tipo in ("TEXT", "MTEXT"):
            geometria = (_texto_entidade(entidade), r(entidade.dxf.insert.x), r(entidade.dxf.insert.y))
        else:
            p = _ponto(entidade)
            geometria = (r(p[0]), r(p[1])) if p else (entidade.dxf.handle,)
    except (AttributeError, TypeError, ValueError):
        geometria = (entidade.dxf.handle,)
    return (tipo, geometria)


def comparar(caminho_a, caminho_b, tol=1e-3):
    resumo = {}
    conjuntos = []
    for caminho in (caminho_a, caminho_b):
        doc = abrir(caminho)
        por_camada = defaultdict(Counter)
        pontos = defaultdict(dict)
        for layout in _layouts(doc):
            for entidade in layout:
                camada = entidade.dxf.get("layer", "0")
                chave = (layout.name, *_assinatura(entidade, tol))
                por_camada[camada][chave] += 1
                pontos[camada].setdefault(chave, _ponto(entidade))
        conjuntos.append((por_camada, pontos))
    (a, pa), (b, pb) = conjuntos
    for camada in sorted(set(a) | set(b)):
        novas = b.get(camada, Counter()) - a.get(camada, Counter())
        removidas = a.get(camada, Counter()) - b.get(camada, Counter())
        if not novas and not removidas:
            continue
        locais = [pb[camada].get(k) for k in novas] + [pa[camada].get(k) for k in removidas]
        locais = [p for p in locais if p]
        regiao = ([min(p[0] for p in locais), min(p[1] for p in locais), max(p[0] for p in locais),
                   max(p[1] for p in locais)] if locais else None)
        resumo[camada] = {"acrescentadas": sum(novas.values()), "removidas": sum(removidas.values()),
                          "regiao": regiao}
    return {"a": str(caminho_a), "b": str(caminho_b), "tolerancia": tol, "camadas": resumo,
            "total": {"acrescentadas": sum(c["acrescentadas"] for c in resumo.values()),
                      "removidas": sum(c["removidas"] for c in resumo.values())}}


# ---------------------------------------------------------------- conversão

def arquivos_dwg(entrada):
    """DWG de um arquivo ou pasta (com subpastas), sem diferenciar maiúsculas na extensão."""
    entrada = Path(entrada)
    if not entrada.is_dir():
        return [entrada]
    return sorted(p for p in entrada.rglob("*") if p.is_file() and p.suffix.lower() == ".dwg")


def destino_dxf(dwg, entrada, pasta_saida):
    """Caminho do DXF preservando subpastas, para revisões de mesmo nome não se sobrescreverem."""
    entrada, dwg = Path(entrada), Path(dwg)
    relativo = dwg.relative_to(entrada).parent if entrada.is_dir() else Path()
    return Path(pasta_saida) / relativo / f"{dwg.stem}.dxf"


ACCORECONSOLE_PADROES = (
    "/Applications/Autodesk/AutoCAD */AutoCAD *.app/Contents/Helpers/AcCoreConsole.app/Contents/MacOS/AcCoreConsole",
    "C:/Program Files/Autodesk/AutoCAD */accoreconsole.exe",
)
VERSOES_DXFOUT = ("R12", "2000", "2004", "2007", "2010", "2013", "2018")
MANIFESTO_CONVERSAO = "conversao_dxf.json"


def localizar_accoreconsole():
    """Console sem interface do AutoCAD (o mais novo instalado); a variável ACCORECONSOLE tem prioridade."""
    candidatos = [os.environ.get("ACCORECONSOLE")]
    for padrao in ACCORECONSOLE_PADROES:
        candidatos += sorted(glob.glob(padrao), reverse=True)
    return next((str(c) for c in candidatos if c and Path(c).is_file()), None)


def _oda_instalado():
    try:
        from ezdxf.addons import odafc
    except ImportError:
        return False
    return odafc.is_installed()


def _escolher_conversor(via):
    """Rota de conversão na ordem ODA → AcCoreConsole; sem nenhuma, encerra explicando as alternativas."""
    if via == "oda":
        _ezdxf()
    if via in ("auto", "oda") and _oda_instalado():
        return "oda", None
    if via == "oda":
        sys.exit("ODA File Converter não encontrado. Instale-o (gratuito, Open Design Alliance), use --via "
                 "accoreconsole com o AutoCAD instalado ou siga a referência 07 §2.")
    executavel = localizar_accoreconsole()
    if executavel:
        return "accoreconsole", executavel
    if via == "accoreconsole":
        sys.exit("AcCoreConsole não encontrado nas pastas do AutoCAD; indique o executável na variável ACCORECONSOLE "
                 "ou siga a referência 07 §2.")
    sys.exit("Nenhum conversor de DWG: ODA File Converter e AcCoreConsole do AutoCAD não encontrados. Instale o ODA "
             "(gratuito), exporte DXF de uma cópia pelo AutoCAD pela interface ou peça DXF/PDF (referência 07 §2).")


def _versao_dxfout(versao):
    """Versão no formato do DXFOUT (2018, 2013… R12) a partir de --versao (R2018 ou 2018)."""
    texto = str(versao).upper()
    texto = texto[1:] if texto.startswith("R") else texto
    texto = "R12" if texto == "12" else texto
    if texto not in VERSOES_DXFOUT:
        sys.exit(f"Versão {versao} não exportável pelo DXFOUT; use uma destas: {', '.join(VERSOES_DXFOUT)}.")
    return texto


def dxf_completo(caminho):
    """Todo DXF ASCII termina no par 0/EOF; exportação interrompida não chega a ele."""
    try:
        with open(caminho, "rb") as arquivo:
            arquivo.seek(0, os.SEEK_END)
            arquivo.seek(max(0, arquivo.tell() - 256))
            linhas = [linha.strip() for linha in arquivo.read().splitlines() if linha.strip()]
    except OSError:
        return False
    return linhas[-2:] == [b"0", b"EOF"]


def _pasta_ascii():
    """Pasta temporária de caminho ASCII: o AcCoreConsole lê o .scr em cp1252 e não abre caminhos com acento."""
    bases = [tempfile.gettempdir()]
    bases += ([os.environ.get("PUBLIC"), os.environ.get("SystemDrive", "C:") + "\\"] if os.name == "nt"
              else ["/tmp", "/var/tmp"])
    for base in bases:
        if not base or not base.isascii():
            continue
        try:
            pasta = tempfile.mkdtemp(prefix="accoreconsole_", dir=base)
        except OSError:
            continue
        if pasta.isascii():
            return Path(pasta)
        shutil.rmtree(pasta, ignore_errors=True)
    raise RuntimeError("nenhuma pasta temporária com caminho ASCII; defina TMPDIR (no Windows, TEMP) sem acentos")


def _texto_console(bruto):
    """Saída do AcCoreConsole como texto (no Windows ela vem em UTF-16, com bytes nulos)."""
    return bruto.replace(b"\x00", b"").decode("utf-8", errors="replace")


def _final(texto, quantidade=8):
    return [linha.strip() for linha in texto.splitlines() if linha.strip()][-quantidade:]


def _nome_accoreconsole(executavel):
    versao = re.search(r"AutoCAD \d{4}", executavel)
    return f"AcCoreConsole ({versao[0]})" if versao else "AcCoreConsole"


def _tentativa_accoreconsole(executavel, copia, pasta, numero, versao, audit, tempo_limite):
    """Uma exportação: grava o .scr (uma resposta por linha), roda o console e confere o DXF gerado."""
    saida, roteiro, log = (pasta / f"tentativa{numero}{extensao}" for extensao in (".dxf", ".scr", ".log"))
    respostas = ["FILEDIA", "0", *(["AUDIT", "Y"] if audit else []), "DXFOUT", f'"{saida}"', "V", versao, "16",
                 "QUIT", "Y"]
    roteiro.write_text("\n".join(respostas) + "\n", encoding="ascii")
    chave = "/" if os.name == "nt" else "-"
    comando = [executavel, f"{chave}i", str(copia), f"{chave}s", str(roteiro), f"{chave}l", "en-US"]
    registro = {"tentativa": numero, "versao_dxf": versao, "audit": audit}
    inicio = time.monotonic()
    try:
        with open(log, "wb") as saida_console:  # arquivo, não pipe: o tempo-limite não espera processos filhos
            processo = subprocess.run(comando, stdin=subprocess.DEVNULL, stdout=saida_console,
                                      stderr=subprocess.STDOUT, cwd=pasta, timeout=tempo_limite)
        registro["codigo_saida"] = processo.returncode
    except subprocess.TimeoutExpired:
        registro["erro"] = f"tempo esgotado ({tempo_limite} s)"
    except OSError as erro:
        registro["erro"] = f"AcCoreConsole não executou: {erro}"
    registro["segundos"] = round(time.monotonic() - inicio, 1)
    texto = _texto_console(log.read_bytes()) if log.is_file() else ""
    if "erro" not in registro:
        if not saida.is_file():
            registro["erro"] = "DXF não gerado"
        elif not dxf_completo(saida):
            registro["erro"] = "DXF truncado: não termina em EOF"
    return registro, saida, texto


def _avisos_console(texto, audit):
    """Resumo do AUDIT e alertas da saída do console que pedem conferir o DXF contra o PDF."""
    avisos, alertas = {}, []
    if "Custom object" in texto:
        alertas.append("o desenho tem objetos personalizados (proxy), que podem faltar no DXF: conferir o conteúdo "
                       "contra o PDF")
    if audit:
        encontrados = re.search(r"Total errors found (\d+) fixed (\d+)", texto)
        apagados = re.search(r"Erased (\d+) objects", texto)
        if encontrados:
            avisos["auditoria"] = {"erros": int(encontrados[1]), "corrigidos": int(encontrados[2]),
                                   "apagados": int(apagados[1]) if apagados else 0}
        alertas.append("DXF exportado depois do AUDIT, que corrige o desenho e pode apagar objetos: conferir o "
                       "conteúdo contra o PDF")
    if alertas:
        avisos["alertas"] = alertas
    return avisos


def _converter_accoreconsole(dwg, destino, executavel, versao, tempo_limite):
    """Converte uma cópia do DWG numa pasta ASCII; sem DXF completo, refaz com AUDIT e versão 2013."""
    registro = {"dwg": str(dwg), "dxf": str(destino), "ferramenta": _nome_accoreconsole(executavel),
                "executavel": executavel}
    falhas, pasta = [], None
    try:
        registro["sha256_dwg"] = _sha256(dwg)
        pasta = _pasta_ascii()
        copia = pasta / "desenho.dwg"
        shutil.copyfile(dwg, copia)
        for numero, (versao_tentativa, audit) in enumerate(((versao, False), ("2013", True)), start=1):
            tentativa, saida, texto = _tentativa_accoreconsole(executavel, copia, pasta, numero, versao_tentativa,
                                                               audit, tempo_limite)
            if "erro" not in tentativa:
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(saida), str(destino))
                registro.update(sha256_dxf=_sha256(destino), versao_dxf=versao_tentativa, audit=audit,
                                tentativas=numero, falhas_tentativas=falhas, segundos=tentativa["segundos"],
                                codigo_saida=tentativa["codigo_saida"], **_avisos_console(texto, audit))
                return registro
            falhas.append({**tentativa, "log_final": _final(texto)})
            if "codigo_saida" not in tentativa:  # tempo esgotado ou programa que não iniciou: AUDIT não resolve
                break
        erro = falhas[-1]["erro"]
    except (OSError, RuntimeError) as falha:  # leitura do original, pasta temporária, cópia ou destino
        erro = str(falha)
    finally:
        if pasta:
            shutil.rmtree(pasta, ignore_errors=True)
    return {**registro, "tentativas": len(falhas), "falhas_tentativas": falhas, "erro": erro}


def _converter_oda(dwg, destino, versao):
    from ezdxf.addons import odafc
    registro = {"dwg": str(dwg), "dxf": str(destino), "ferramenta": "ODA File Converter", "versao_dxf": versao,
                "tentativas": 1, "falhas_tentativas": []}
    try:
        registro["sha256_dwg"] = _sha256(dwg)
        destino.parent.mkdir(parents=True, exist_ok=True)
        odafc.convert(str(dwg), str(destino), version=versao, replace=True)
        registro["sha256_dxf"] = _sha256(destino)
    except Exception as erro:  # noqa: BLE001 - registrar falha por arquivo e seguir
        registro.update(erro=str(erro), falhas_tentativas=[{"tentativa": 1, "erro": str(erro)}])
    return registro


def _gravar_manifesto(caminho, resultado):
    """Acumula as conversões: o registro novo de um DXF substitui o anterior; os demais ficam."""
    manifesto = {}
    if caminho.is_file():
        try:
            manifesto = json.loads(caminho.read_text(encoding="utf-8"))
        except ValueError:
            manifesto = {}
    refeitos = {r["dxf"] for r in resultado["convertidos"] + resultado["falhas"]}
    for chave in ("convertidos", "falhas"):
        manifesto[chave] = [r for r in manifesto.get(chave, []) if r.get("dxf") not in refeitos] + resultado[chave]
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return caminho


def converter(entrada, pasta_saida, versao="R2018", via="auto", tempo_limite=600):
    """DWG → DXF de um arquivo ou pasta. O original só é lido; o resultado também vai para o manifesto."""
    entrada, pasta_saida = Path(entrada).resolve(), Path(pasta_saida).resolve()
    rota, executavel = _escolher_conversor(via)
    versao_console = _versao_dxfout(versao) if rota == "accoreconsole" else None
    dwgs = arquivos_dwg(entrada)
    resultados = []
    for numero, dwg in enumerate(dwgs, start=1):
        destino = destino_dxf(dwg, entrada, pasta_saida)
        if destino.exists() and destino.samefile(dwg):
            registro = {"dwg": str(dwg), "dxf": str(destino), "tentativas": 0,
                        "erro": "o DXF de saída seria gravado sobre o arquivo de entrada; escolha outra pasta"}
        elif rota == "oda":
            registro = _converter_oda(dwg, destino, versao)
        else:
            registro = _converter_accoreconsole(dwg, destino, executavel, versao_console, tempo_limite)
        resultados.append(registro)
        print(f"[{numero}/{len(dwgs)}] {'falha' if 'erro' in registro else 'ok'}: {dwg}", file=sys.stderr, flush=True)
    resultado = {"convertidos": [r for r in resultados if "erro" not in r],
                 "falhas": [r for r in resultados if "erro" in r]}
    resultado["manifesto"] = str(_gravar_manifesto(pasta_saida / MANIFESTO_CONVERSAO, resultado))
    return resultado


# ---------------------------------------------------------------- linha de comando

def _bbox(texto):
    if not texto:
        return None
    valores = [float(v) for v in texto.split(",")]
    if len(valores) != 4:
        raise argparse.ArgumentTypeError("use x0,y0,x1,y1")
    return valores


def _gravar(dados, saida):
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    if saida:
        Path(saida).parent.mkdir(parents=True, exist_ok=True)
        Path(saida).write_text(texto + "\n", encoding="utf-8")
    return texto


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("converter", help="DWG → DXF (ODA File Converter ou AcCoreConsole do AutoCAD)")
    p.add_argument("entrada", help="arquivo .dwg ou pasta")
    p.add_argument("--saida", required=True, help="pasta dos DXF; o manifesto conversao_dxf.json fica nela")
    p.add_argument("--versao", default="R2018")
    p.add_argument("--via", choices=("auto", "oda", "accoreconsole"), default="auto",
                   help="auto: ODA File Converter se instalado; senão, AcCoreConsole do AutoCAD")
    p.add_argument("--tempo-limite", type=int, default=600, help="segundos por tentativa do AcCoreConsole")
    p = sub.add_parser("inventario")
    p.add_argument("dxf")
    p.add_argument("--saida")
    p.add_argument("--md")
    p = sub.add_parser("extrair")
    p.add_argument("dxf")
    p.add_argument("--camadas", help="nomes separados por vírgula; aceita curingas (ARQ-*)")
    p.add_argument("--bbox", type=_bbox, help="x0,y0,x1,y1 nas unidades do desenho")
    p.add_argument("--layout", default="Model")
    p.add_argument("--abertas", action="store_true", help="incluir linhas, arcos e polilinhas abertas")
    p.add_argument("--blocos", action="store_true",
                   help="ler também a geometria dentro de blocos (camada 0 herda a da inserção)")
    p.add_argument("--saida", required=True)
    p = sub.add_parser("render")
    p.add_argument("dxf")
    p.add_argument("--saida", required=True)
    p.add_argument("--bbox", type=_bbox)
    p.add_argument("--layout", default="Model")
    p.add_argument("--marcas", help="JSON de marcas (marcas.py) ou de regiões")
    p.add_argument("--largura", type=int, default=1600)
    p.add_argument("--ocultar", help="camadas a ocultar, separadas por vírgula")
    p.add_argument("--titulo")
    p.add_argument("--cores-originais", action="store_true")
    p.add_argument("--hachuras-solidas", action="store_true", help="desenhar hachuras do projeto preenchidas")
    p = sub.add_parser("comparar")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--tolerancia", type=float, default=1e-3)
    p.add_argument("--saida")
    a = parser.parse_args()

    if a.comando == "converter":
        print(_gravar(converter(a.entrada, a.saida, a.versao, a.via, a.tempo_limite), None))
    elif a.comando == "inventario":
        inv = inventario(a.dxf)
        _gravar(inv, a.saida)
        if a.md:
            Path(a.md).write_text(inventario_markdown(inv), encoding="utf-8")
        print(inventario_markdown(inv) if a.saida else _gravar(inv, None))
    elif a.comando == "extrair":
        camadas = [c.strip() for c in a.camadas.split(",")] if a.camadas else None
        dados = extrair(a.dxf, camadas, a.bbox, a.layout, a.abertas, blocos=a.blocos)
        _gravar(dados, a.saida)
        print(json.dumps({"regioes": len(dados["regioes"]), "unidade": dados["unidade"], "saida": a.saida},
                         ensure_ascii=False))
    elif a.comando == "render":
        ocultar = [c.strip() for c in a.ocultar.split(",")] if a.ocultar else ()
        saida = render(a.dxf, a.saida, a.bbox, a.layout, a.marcas, a.largura, ocultar, a.titulo, a.cores_originais,
                       a.hachuras_solidas)
        print(json.dumps({"saida": str(saida)}, ensure_ascii=False))
    else:
        dados = comparar(a.a, a.b, a.tolerancia)
        print(_gravar(dados, a.saida))


if __name__ == "__main__":
    main()
