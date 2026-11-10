"""Formato comum das marcas desenhadas por cad.py render e pdf.py render.

{"titulo": "...", "legenda": [{"cor": "#d62728", "texto": "Faces pintadas"}],
 "marcas": [
   {"id": "A01", "tipo": "poligono", "pontos": [[x, y, bulge?], ...], "furos": [[[x, y], ...]],
    "cor": "#1f77b4", "preenchimento": 0.35, "rotulo": "A01"},
   {"id": "S01", "tipo": "linha", "pontos": [[x, y], ...], "espessura": 3},
   {"id": "E01", "tipo": "ponto", "pontos": [[x, y]]},
   {"tipo": "texto", "pontos": [[x, y]], "texto": "h = 2,70 m (P001)"}]}

As coordenadas são as do próprio desenho (unidades do DXF ou pontos do PDF). As regiões
de cad.py extrair / pdf.py medir também servem: "vertices" e "aneis" são aceitos.
"""

import json
from pathlib import Path

import geometria as g

PALETA = ("#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#e377c2", "#8c564b")


def cor_rgb(cor, padrao="#1f77b4"):
    texto = (cor or padrao).lstrip("#")
    if len(texto) == 3:
        texto = "".join(c * 2 for c in texto)
    return tuple(int(texto[i:i + 2], 16) / 255 for i in (0, 2, 4))


def carregar(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if "marcas" not in dados and "regioes" in dados:
        dados = {"marcas": [{"id": r.get("id"), "tipo": "poligono" if r.get("fechada", True) else "linha",
                             "pontos": r.get("vertices") or (r.get("aneis") or [[]])[0],
                             "furos": r.get("furos") or (r.get("aneis") or [])[1:], "rotulo": r.get("id")}
                            for r in dados["regioes"]]}
    for i, marca in enumerate(dados.get("marcas") or []):
        marca.setdefault("cor", PALETA[i % len(PALETA)])
        marca.setdefault("tipo", "poligono")
        if "pontos" not in marca:
            marca["pontos"] = marca.get("vertices") or (marca.get("aneis") or [[]])[0]
            if marca.get("aneis") and "furos" not in marca:
                marca["furos"] = marca["aneis"][1:]
    return dados


def aneis(marca):
    """Anéis já discretizados (arcos viram pontos) para desenhar."""
    externos = [g.achatar(marca["pontos"], True)]
    return externos + [g.achatar(f, True) for f in marca.get("furos") or []]


def linha(marca):
    return g.achatar(marca["pontos"], False)


def posicao_rotulo(marca):
    """Ponto para o rótulo: centro do polígono, fora dos furos; meio da linha."""
    if marca["tipo"] != "poligono":
        pontos = linha(marca)
        if len(pontos) >= 2:
            meio = len(pontos) // 2
            a, b = pontos[meio - 1], pontos[meio]
            return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return pontos[0] if pontos else None
    contornos = aneis(marca)
    externo, furos = contornos[0], contornos[1:]
    if not externo:
        return None
    centro = (sum(p[0] for p in externo) / len(externo), sum(p[1] for p in externo) / len(externo))
    candidatos = [centro] + [((centro[0] + p[0]) / 2, (centro[1] + p[1]) / 2) for p in externo]
    for candidato in candidatos:
        if g._dentro(candidato, externo) and not any(g._dentro(candidato, f) for f in furos):
            return candidato
    return centro


def limites(dados, margem=0.05):
    """Retângulo que envolve todas as marcas, com margem."""
    xs, ys = [], []
    for marca in dados.get("marcas") or []:
        for p in marca.get("pontos") or []:
            xs.append(p[0])
            ys.append(p[1])
    if not xs:
        return None
    dx, dy = (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    return (min(xs) - dx * margem, min(ys) - dy * margem, max(xs) + dx * margem, max(ys) + dy * margem)
