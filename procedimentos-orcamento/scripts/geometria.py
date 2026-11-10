#!/usr/bin/env python3
"""Áreas, perímetros, validação de polígonos, ciclos de arestas e uniões.

Vértices são (x, y) ou (x, y, bulge). O bulge vale para o segmento do vértice i ao
seguinte (convenção DXF: tan(ângulo/4); positivo = arco anti-horário). Arcos são
tratados analiticamente. Usa só a biblioteca padrão; `uniao` precisa de shapely.

Formato de regiões (saída de cad.py extrair / pdf.py medir):
  {"unidade": {"k": metros_por_unidade, "insunits": codigo},
   "regioes": [{"id", "fechada", "vertices": [[x, y, b], ...],
                "furos": [[[x, y, b], ...]], "aneis": [...]}]}
"""

import argparse
import json
import math
import sys
from pathlib import Path

# Códigos $INSUNITS do DXF -> metros por unidade de desenho.
INSUNITS = {
    1: 0.0254, 2: 0.3048, 3: 1609.344, 4: 0.001, 5: 0.01, 6: 1.0, 7: 1000.0,
    8: 2.54e-8, 9: 2.54e-5, 10: 0.9144, 11: 1e-10, 12: 1e-9, 13: 1e-6, 14: 0.1,
    15: 10.0, 16: 100.0, 17: 1e9, 21: 1200 / 3937, 22: 100 / 3937, 23: 3600 / 3937,
    24: 6336000 / 3937,
}
PASSO_ANGULAR = math.radians(2.0)


def fator_insunits(codigo):
    """Metros por unidade para um código $INSUNITS; None se sem unidade ou desconhecido."""
    if codigo is None:
        return None
    return INSUNITS.get(int(codigo))


def _normalizar(vertices, fechado=True):
    pts = []
    for v in vertices:
        bulge = float(v[2]) if len(v) > 2 and v[2] is not None else 0.0
        pts.append((float(v[0]), float(v[1]), bulge))
    if fechado and len(pts) > 1 and _iguais(pts[0], pts[-1], 0.0):
        pts.pop()
    return pts


def _iguais(a, b, tol):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def _segmentos(pts, fechado):
    n = len(pts)
    for i in range(n if fechado else n - 1):
        x1, y1, bulge = pts[i]
        x2, y2, _ = pts[(i + 1) % n]
        yield x1, y1, x2, y2, bulge


def _arco(x1, y1, x2, y2, bulge):
    """Corda, área assinada do segmento circular e comprimento do arco."""
    corda = math.hypot(x2 - x1, y2 - y1)
    if corda == 0.0 or bulge == 0.0:
        return corda, 0.0, corda
    theta = 4.0 * math.atan(bulge)
    raio = corda / (2.0 * abs(math.sin(theta / 2.0)))
    segmento = 0.5 * raio * raio * (theta - math.sin(theta))
    return corda, segmento, raio * abs(theta)


def area_assinada(vertices):
    """Área com sinal (positiva no sentido anti-horário), incluindo arcos."""
    pts = _normalizar(vertices, True)
    if len(pts) < 2:
        return 0.0
    x0, y0 = pts[0][0], pts[0][1]
    dobro = 0.0
    for x1, y1, x2, y2, bulge in _segmentos(pts, True):
        dobro += (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if bulge:
            dobro += 2.0 * _arco(x1, y1, x2, y2, bulge)[1]
    return dobro / 2.0


def area(vertices):
    return abs(area_assinada(vertices))


def perimetro(vertices, fechado=True):
    """Perímetro (fechado) ou comprimento (aberto), com arcos pelo comprimento real."""
    pts = _normalizar(vertices, fechado)
    return sum(_arco(*seg)[2] for seg in _segmentos(pts, fechado))


def area_com_furos(contorno, furos=()):
    return area(contorno) - sum(area(f) for f in furos or ())


def achatar(vertices, fechado=True, passo=PASSO_ANGULAR):
    """Pontos (x, y) com os arcos discretizados, para desenhar ou testar interseções."""
    pts = _normalizar(vertices, fechado)
    saida = []
    for x1, y1, x2, y2, bulge in _segmentos(pts, fechado):
        saida.append((x1, y1))
        if not bulge:
            continue
        corda = math.hypot(x2 - x1, y2 - y1)
        if corda == 0.0:
            continue
        theta = 4.0 * math.atan(bulge)
        ux, uy = (x2 - x1) / corda, (y2 - y1) / corda
        distancia = (corda / 2.0) / math.tan(theta / 2.0)
        cx = (x1 + x2) / 2.0 - uy * distancia
        cy = (y1 + y2) / 2.0 + ux * distancia
        raio = math.hypot(x1 - cx, y1 - cy)
        inicio = math.atan2(y1 - cy, x1 - cx)
        partes = max(2, math.ceil(abs(theta) / passo))
        for j in range(1, partes):
            angulo = inicio + theta * j / partes
            saida.append((cx + raio * math.cos(angulo), cy + raio * math.sin(angulo)))
    if not fechado and pts:
        saida.append((pts[-1][0], pts[-1][1]))
    return saida


def _orientacao(a, b, c):
    valor = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return 0 if valor == 0 else (1 if valor > 0 else -1)


def _no_segmento(a, b, p):
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])


def _cruzam(a, b, c, d):
    o1, o2, o3, o4 = _orientacao(a, b, c), _orientacao(a, b, d), _orientacao(c, d, a), _orientacao(c, d, b)
    if o1 != o2 and o3 != o4:
        return True
    return ((o1 == 0 and _no_segmento(a, b, c)) or (o2 == 0 and _no_segmento(a, b, d))
            or (o3 == 0 and _no_segmento(c, d, a)) or (o4 == 0 and _no_segmento(c, d, b)))


def _autointersecoes(pontos, limite=5):
    n = len(pontos)
    segmentos = [(pontos[i], pontos[(i + 1) % n]) for i in range(n)]
    caixas = [(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in segmentos]
    achados = []
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            ci, cj = caixas[i], caixas[j]
            if ci[2] < cj[0] or cj[2] < ci[0] or ci[3] < cj[1] or cj[3] < ci[1]:
                continue
            if _cruzam(*segmentos[i], *segmentos[j]):
                achados.append((i, j))
                if len(achados) >= limite:
                    return achados
    return achados


def validar(vertices, fechado=True, tol=1e-9):
    """Confere vértices repetidos, autointerseção, quantidade de vértices e orientação."""
    pts = _normalizar(vertices, fechado)
    problemas = []
    tem_arco = any(p[2] for p in pts)
    if fechado and (len(pts) < 3 and not (len(pts) == 2 and tem_arco)):
        problemas.append("menos de três vértices")
    repetidos = [i for i in range(len(pts) - (0 if fechado else 1))
                 if len(pts) > 1 and _iguais(pts[i], pts[(i + 1) % len(pts)], tol)]
    if repetidos:
        problemas.append(f"vértices repetidos consecutivos nas posições {repetidos[:10]}")
    sinal = area_assinada(pts) if fechado else 0.0
    orientacao = "anti-horario" if sinal > 0 else ("horario" if sinal < 0 else "degenerado")
    if fechado and len(pts) >= 3 and sinal == 0:
        problemas.append("área nula")
    if fechado and len(pts) >= 3 and not repetidos:
        cruzamentos = _autointersecoes(achatar(pts, True))
        if cruzamentos:
            problemas.append(f"autointerseção entre segmentos {cruzamentos}")
    return {"valido": not problemas, "problemas": problemas, "orientacao": orientacao, "vertices": len(pts)}


def _dentro(ponto, anel):
    x, y = ponto
    dentro = False
    n = len(anel)
    for i in range(n):
        x1, y1 = anel[i]
        x2, y2 = anel[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                dentro = not dentro
    return dentro


def area_por_paridade(aneis):
    """Soma anéis não ordenados pela profundidade de aninhamento (par soma, ímpar desconta)."""
    planos = [achatar(a, True) for a in aneis]
    niveis = []
    for i, anel in enumerate(planos):
        (x1, y1), (x2, y2) = anel[0], anel[1 % len(anel)]
        amostra = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        niveis.append(sum(1 for j, outro in enumerate(planos) if j != i and _dentro(amostra, outro)))
    total = sum(area(a) * (1 if n % 2 == 0 else -1) for a, n in zip(aneis, niveis))
    return total, niveis


def area_arestas(arestas):
    """Soma da integral de borda sobre arestas orientadas, sem fechar nada."""
    return sum((a[0] * b[1] - b[0] * a[1]) / 2.0 for a, b in arestas)


def invariante_translacao(arestas, dx=1000.0, dy=1000.0, tol_rel=1e-9):
    """Verdadeiro quando transladar a origem não muda a área (cadeia fechada)."""
    a0 = area_arestas(arestas)
    a1 = area_arestas([((a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy)) for a, b in arestas])
    return abs(a1 - a0) <= tol_rel * max(1.0, abs(a0))


def reconstruir_ciclos(arestas, tol=1e-9):
    """Encadeia arestas soltas pelas extremidades, sem mover vértices nem ligar componentes.

    Devolve ciclos fechados, cadeias abertas, lacunas (distância entre extremidades unidas
    pela tolerância ou entre as pontas de uma cadeia aberta) e a área por paridade.
    """
    celula = max(tol, 1e-12) * 2.0
    grade, nos = {}, []

    def no_de(ponto):
        gx, gy = math.floor(ponto[0] / celula), math.floor(ponto[1] / celula)
        for ix in (gx - 1, gx, gx + 1):
            for iy in (gy - 1, gy, gy + 1):
                for indice in grade.get((ix, iy), ()):
                    if _iguais(nos[indice], ponto, tol):
                        return indice
        nos.append(ponto)
        grade.setdefault((gx, gy), []).append(len(nos) - 1)
        return len(nos) - 1

    ligacoes = []
    incidentes = {}
    for k, (a, b) in enumerate(arestas):
        a, b = (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))
        na, nb = no_de(a), no_de(b)
        ligacoes.append((a, b, na, nb))
        incidentes.setdefault(na, []).append(k)
        incidentes.setdefault(nb, []).append(k)

    usadas = [False] * len(ligacoes)
    lacunas = []

    def caminhar(inicio_no, primeira):
        caminho, atual, aresta = [], inicio_no, primeira
        while aresta is not None:
            usadas[aresta] = True
            a, b, na, nb = ligacoes[aresta]
            orientada = (a, b) if na == atual else (b, a)
            if caminho and not _iguais(caminho[-1][1], orientada[0], 0.0):
                distancia = math.dist(caminho[-1][1], orientada[0])
                lacunas.append({"ponto": list(orientada[0]), "distancia": distancia})
            caminho.append(orientada)
            atual = nb if na == atual else na
            if atual == inicio_no:
                break
            aresta = next((k for k in incidentes[atual] if not usadas[k]), None)
        return caminho, atual

    ciclos, abertas = [], []
    pontas = [n for n, ks in incidentes.items() if len(ks) % 2 == 1]
    for no in pontas:
        primeira = next((k for k in incidentes[no] if not usadas[k]), None)
        if primeira is None:
            continue
        caminho, fim = caminhar(no, primeira)
        abertas.append([s[0] for s in caminho] + [caminho[-1][1]])
        lacunas.append({"ponto": list(caminho[-1][1]), "distancia": math.dist(caminho[0][0], caminho[-1][1]),
                        "tipo": "cadeia aberta"})
    for k in range(len(ligacoes)):
        if usadas[k]:
            continue
        a, b, na, nb = ligacoes[k]
        caminho, fim = caminhar(na, k)
        if fim == na:
            if not _iguais(caminho[-1][1], caminho[0][0], 0.0):
                lacunas.append({"ponto": list(caminho[0][0]), "distancia": math.dist(caminho[-1][1], caminho[0][0])})
            ciclos.append([s[0] for s in caminho])
        else:
            abertas.append([s[0] for s in caminho] + [caminho[-1][1]])
            lacunas.append({"ponto": list(caminho[-1][1]), "distancia": math.dist(caminho[0][0], caminho[-1][1]),
                            "tipo": "cadeia aberta"})

    total, niveis = area_por_paridade(ciclos) if ciclos else (0.0, [])
    irregulares = sum(1 for ks in incidentes.values() if len(ks) != 2)
    return {"ciclos": ciclos, "abertas": abertas, "lacunas": lacunas, "area": total,
            "niveis": niveis, "nos_irregulares": irregulares}


def _poligono(parte, passo):
    from shapely.geometry import Polygon
    if parte.get("aneis"):
        resultado = None
        for anel in parte["aneis"]:
            poligono = Polygon(achatar(anel, True, passo)).buffer(0)
            resultado = poligono if resultado is None else resultado.symmetric_difference(poligono)
        return resultado
    return Polygon(achatar(parte["contorno"], True, passo),
                   [achatar(f, True, passo) for f in parte.get("furos") or ()]).buffer(0)


def uniao(partes, passo=PASSO_ANGULAR, subtrair=()):
    """União de polígonos menos os de `subtrair`, via shapely; arcos discretizados.

    Cada parte é {"contorno", "furos"} ou {"aneis"} (anéis soltos de hachura, preenchidos por paridade).
    """
    try:
        from shapely.ops import unary_union
    except ImportError as erro:
        raise RuntimeError("uniao precisa de shapely: python3 -m pip install shapely") from erro
    resultado = unary_union([_poligono(p, passo) for p in partes])
    if subtrair:
        resultado = resultado.difference(unary_union([_poligono(p, passo) for p in subtrair]))
    geometrias = getattr(resultado, "geoms", [resultado])
    return [{"contorno": list(g.exterior.coords)[:-1], "furos": [list(i.coords)[:-1] for i in g.interiors]}
            for g in geometrias if g.geom_type == "Polygon" and not g.is_empty]


# ---------------------------------------------------------------- linha de comando

def _ler(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


AVISO_K = ("k não validado por cotas: confirme a escala com duas cotas conhecidas em direções diferentes e "
           "informe --k (04 §3)")


def _fator(argumentos, dados):
    """(k, validado): --k informado conta como validado; k do arquivo vale o que diz unidade.validada."""
    if argumentos.k is not None:
        return argumentos.k, True
    unidade = dados.get("unidade") or {}
    if unidade.get("k"):
        return float(unidade["k"]), bool(unidade.get("validada"))
    codigo = argumentos.insunits if argumentos.insunits is not None else unidade.get("insunits")
    return fator_insunits(codigo), False


def _parte(regiao):
    if regiao.get("aneis"):
        return {"aneis": regiao["aneis"]}
    return {"contorno": regiao["vertices"], "furos": regiao.get("furos") or []}


def _emitir(resultado, saida):
    texto = json.dumps(resultado, ensure_ascii=False, indent=2)
    if saida:
        Path(saida).write_text(texto + "\n", encoding="utf-8")
    print(texto if not saida else json.dumps({k: v for k, v in resultado.items() if not isinstance(v, list)},
                                             ensure_ascii=False, indent=2))


def _cmd_calcular(argumentos):
    dados = _ler(argumentos.regioes)
    k, validado = _fator(argumentos, dados)
    if not k:
        sys.exit("Unidade não definida: informe --k (metros por unidade) depois de validar a escala, "
                 "ou registre unidade.k no arquivo de regiões.")
    filtro = set(argumentos.ids.split(",")) if argumentos.ids else None
    saida, area_total, comprimento_total = [], 0.0, 0.0
    for regiao in dados.get("regioes", []):
        if filtro and regiao.get("id") not in filtro:
            continue
        registro = {chave: regiao[chave] for chave in ("id", "camada", "handle", "tipo", "aproximado") if chave in regiao}
        if not regiao.get("fechada", True):
            registro["comprimento_m"] = perimetro(regiao["vertices"], fechado=False) * k
            comprimento_total += registro["comprimento_m"]
        else:
            if regiao.get("aneis"):
                bruta, niveis = area_por_paridade(regiao["aneis"])
                registro["niveis"] = niveis
                aneis = regiao["aneis"]
            else:
                bruta = area_com_furos(regiao["vertices"], regiao.get("furos"))
                aneis = [regiao["vertices"], *(regiao.get("furos") or [])]
            registro["area_m2"] = bruta * k * k
            registro["perimetro_m"] = perimetro(aneis[0]) * k
            registro["perimetro_furos_m"] = sum(perimetro(a) for a in aneis[1:]) * k
            registro["validacao"] = validar(aneis[0])
            problemas_furos = [p for a in aneis[1:] for p in validar(a)["problemas"]]
            if problemas_furos:
                registro["validacao"]["valido"] = False
                registro["validacao"]["problemas"] += [f"furo: {p}" for p in problemas_furos]
            area_total += registro["area_m2"]
        saida.append(registro)
    resultado = {"k_m_por_unidade": k, "k_validado": validado, "area_total_m2": area_total,
                 "comprimento_total_m": comprimento_total, "regioes": saida}
    if not validado:
        resultado["aviso"] = AVISO_K
        print(f"Aviso: {AVISO_K}", file=sys.stderr)
    _emitir(resultado, argumentos.saida)


def _cmd_ciclos(argumentos):
    dados = _ler(argumentos.arestas)
    k = _fator(argumentos, dados)[0] or 1.0
    arestas = [(tuple(a), tuple(b)) for a, b in dados["arestas"]]
    resultado = reconstruir_ciclos(arestas, argumentos.tol)
    orientadas = [(c[i], c[(i + 1) % len(c)]) for c in resultado["ciclos"] for i in range(len(c))]
    _emitir({"k_m_por_unidade": k, "area_m2": resultado["area"] * k * k, "ciclos": len(resultado["ciclos"]),
             "cadeias_abertas": len(resultado["abertas"]), "nos_irregulares": resultado["nos_irregulares"],
             "invariante_translacao": invariante_translacao(orientadas) if orientadas else False,
             "lacunas": [{**lacuna, "distancia_m": lacuna["distancia"] * k} for lacuna in resultado["lacunas"]],
             "areas_ciclos_m2": [area(c) * k * k for c in resultado["ciclos"]], "niveis": resultado["niveis"]},
            argumentos.saida)


def _cmd_uniao(argumentos):
    dados = _ler(argumentos.regioes)
    k, validado = _fator(argumentos, dados)
    if not k:
        sys.exit("Unidade não definida: informe --k.")
    regioes = {r.get("id"): r for r in dados.get("regioes", [])}
    ids = argumentos.ids.split(",")
    retirar = argumentos.subtrair.split(",") if argumentos.subtrair else []
    faltando = [i for i in ids + retirar if i not in regioes]
    if faltando:
        sys.exit(f"Regiões inexistentes no arquivo: {', '.join(faltando)}")
    try:
        resultado = uniao([_parte(regioes[i]) for i in ids], subtrair=[_parte(regioes[i]) for i in retirar])
    except RuntimeError as erro:
        sys.exit(str(erro))
    saida = {"k_m_por_unidade": k, "k_validado": validado, "partes": len(resultado),
             "area_m2": sum(area_com_furos(p["contorno"], p["furos"]) for p in resultado) * k * k,
             "pgeom_m": sum(perimetro(p["contorno"]) + sum(perimetro(f) for f in p["furos"]) for p in resultado) * k,
             "aproximado": True, "observacao": f"união de {', '.join(ids)}" + (f" menos {', '.join(retirar)}" if retirar
                                                                              else "")
             + "; arcos discretizados para a operação booleana",
             "unidade": {"k": k, "validada": validado},
             "regioes": [{"id": f"U{n:02d}", "fechada": True, "vertices": [list(p) for p in parte["contorno"]],
                          "furos": [[list(p) for p in furo] for furo in parte["furos"]], "aproximado": True}
                         for n, parte in enumerate(resultado, start=1)]}
    if not validado:
        saida["aviso"] = AVISO_K
    _emitir(saida, argumentos.saida)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome, ajuda in (("calcular", "áreas, perímetros e comprimentos de regiões"),
                        ("uniao", "união (e subtração) de regiões: polígonos resultantes, área e Pgeom (shapely)")):
        p = sub.add_parser(nome, help=ajuda)
        p.add_argument("regioes")
        p.add_argument("--k", type=float, help="metros por unidade de desenho (escala validada)")
        p.add_argument("--insunits", type=int, help="código $INSUNITS, se k não for informado")
        p.add_argument("--ids", help="IDs separados por vírgula" + (" (obrigatório)" if nome == "uniao" else ""),
                       required=nome == "uniao")
        if nome == "uniao":
            p.add_argument("--subtrair", help="IDs a descontar da união, separados por vírgula")
        p.add_argument("--saida", help="JSON completo; na união, as regiões resultantes servem para calcular e render")
    p = sub.add_parser("ciclos", help="reconstrói ciclos a partir de arestas soltas")
    p.add_argument("arestas")
    p.add_argument("--tol", type=float, default=1e-9, help="tolerância para unir extremidades (unidades do desenho)")
    p.add_argument("--k", type=float)
    p.add_argument("--insunits", type=int)
    p.add_argument("--saida")
    argumentos = parser.parse_args()
    {"calcular": _cmd_calcular, "ciclos": _cmd_ciclos, "uniao": _cmd_uniao}[argumentos.comando](argumentos)


if __name__ == "__main__":
    main()
