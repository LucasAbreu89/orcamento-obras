#!/usr/bin/env python3
"""Mapeia, fotografa e verifica planilhas XLSX/XLSM usando só a biblioteca padrão.

  mapear     abas (inclusive ocultas), cabeçalho provável, colunas de item/descrição/
             unidade/quantidade/preço, itens prováveis, recursos e riscos de gravação
  snapshot   guarda valores e fórmulas de todas as células, mesclagens, nomes e recursos
  verificar  compara um arquivo com o snapshot: nada da planilha recebida pode mudar;
             são aceitas apenas colunas novas à direita e abas novas

Fórmulas compartilhadas são expandidas como o Excel/openpyxl as interpretam.
"""

import argparse
import gzip
import hashlib
import json
import math
import posixpath
import re
import sys
import unicodedata
import zipfile
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_XDR = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
NS_CHART = "http://schemas.openxmlformats.org/drawingml/2006/chart"

Celula = namedtuple("Celula", "tipo valor formula")

RECURSOS_ABA = ("imagens", "graficos", "formas", "controles", "objetos", "tabelas", "comentarios", "extensoes")
RECURSOS_PASTA = ("vba", "vinculos_externos", "tabelas_dinamicas", "segmentacoes", "linhas_do_tempo",
                  "conexoes", "modelo_dados")
# Recursos que a gravação com openpyxl descarta.
PERDIDOS_NA_GRAVACAO = {"imagens", "graficos", "formas", "controles", "objetos", "extensoes", "segmentacoes",
                        "linhas_do_tempo", "modelo_dados"}
# Extensões x14 (validação, formatação condicional e minigráficos avançados) que o openpyxl não regrava.
EXTENSOES_X14 = (b":dataValidations", b":conditionalFormattings", b":sparklineGroups", b":slicerList")


# ---------------------------------------------------------------- referências

def col_numero(letras):
    numero = 0
    for c in letras.upper():
        numero = numero * 26 + ord(c) - 64
    return numero


def col_letra(numero):
    letras = ""
    while numero > 0:
        numero, resto = divmod(numero - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def separar_ref(ref):
    m = re.fullmatch(r"\$?([A-Za-z]{1,3})\$?(\d+)", ref)
    if not m:
        raise ValueError(f"referência inválida: {ref}")
    return col_numero(m.group(1)), int(m.group(2))


def _segmentar(formula):
    """Divide a fórmula em trechos: textos "...", nomes de aba '...' e o restante."""
    partes, atual, i = [], [], 0
    while i < len(formula):
        c = formula[i]
        if c in "\"'":
            if atual:
                partes.append(("outro", "".join(atual)))
                atual = []
            j = i + 1
            while j < len(formula):
                if formula[j] == c:
                    if j + 1 < len(formula) and formula[j + 1] == c:
                        j += 2
                        continue
                    break
                j += 1
            partes.append(("texto" if c == '"' else "aba", formula[i:j + 1]))
            i = j + 1
            continue
        atual.append(c)
        i += 1
    if atual:
        partes.append(("outro", "".join(atual)))
    return partes


_REF = re.compile(
    r"(?P<colunas>(?<![A-Za-z0-9_.$])(\$?)([A-Z]{1,3}):(\$?)([A-Z]{1,3})(?![A-Za-z0-9_(]))"
    r"|(?P<linhas>(?<![A-Za-z0-9_.$:])(\$?)(\d+):(\$?)(\d+)(?![\d.]))"
    r"|(?P<celula>(?<![A-Za-z0-9_.$])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![A-Za-z0-9_(]))")


def traduzir_formula(formula, dlin, dcol):
    """Desloca referências relativas (sem $) por dlin linhas e dcol colunas."""

    def coluna(ancora, letras):
        if ancora:
            return ancora + letras
        n = col_numero(letras) + dcol
        return col_letra(n) if n >= 1 else None

    def linha(ancora, numero):
        if ancora:
            return ancora + numero
        n = int(numero) + dlin
        return str(n) if n >= 1 else None

    def trocar(m):
        g = m.groups()
        if m.group("colunas"):
            a, b = coluna(g[1], g[2]), coluna(g[3], g[4])
            return f"{a}:{b}" if a and b else "#REF!"
        if m.group("linhas"):
            a, b = linha(g[6], g[7]), linha(g[8], g[9])
            return f"{a}:{b}" if a and b else "#REF!"
        c, lin = coluna(g[11], g[12]), linha(g[13], g[14])
        return f"{c}{lin}" if c and lin else "#REF!"

    return "".join(_REF.sub(trocar, t) if tipo == "outro" else t for tipo, t in _segmentar(formula))


def normalizar_formula(formula):
    if formula is None:
        return None
    formula = formula[1:] if formula.startswith("=") else formula
    saida = []
    for tipo, trecho in _segmentar(formula):
        if tipo == "outro":
            trecho = re.sub(r"_xl(?:fn|ws|pm)\.", "", trecho, flags=re.IGNORECASE).upper()
        elif tipo == "aba":
            trecho = trecho.upper()
        saida.append(trecho)
    return "".join(saida)


# ---------------------------------------------------------------- leitura

def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _resolver(base, alvo):
    if alvo.startswith("/"):
        return alvo[1:]
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), alvo))


class Pasta:
    """Leitura de uma pasta de trabalho XLSX sem dependências externas."""

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.zip = zipfile.ZipFile(self.caminho)
        self.nomes_partes = set(self.zip.namelist())
        self._strings = None
        rels = self._rels("xl/workbook.xml")
        raiz = ET.fromstring(self.zip.read("xl/workbook.xml"))
        self.abas = []
        for el in raiz.iter(f"{{{NS_MAIN}}}sheet"):
            rid = el.get(f"{{{NS_REL}}}id")
            self.abas.append({"nome": el.get("name"), "estado": el.get("state", "visible"),
                              "parte": rels.get(rid, {}).get("alvo")})
        self.nomes_definidos = {}
        for el in raiz.iter(f"{{{NS_MAIN}}}definedName"):
            chave = el.get("name") + (f"@{el.get('localSheetId')}" if el.get("localSheetId") else "")
            self.nomes_definidos[chave] = el.text or ""
        self._cache = {}

    def fechar(self):
        self.zip.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()

    def _rels(self, parte):
        caminho = posixpath.join(posixpath.dirname(parte), "_rels", posixpath.basename(parte) + ".rels")
        if caminho not in self.nomes_partes:
            return {}
        raiz = ET.fromstring(self.zip.read(caminho))
        return {el.get("Id"): {"tipo": el.get("Type", "").rsplit("/", 1)[-1],
                               "alvo": el.get("Target") if el.get("TargetMode") == "External"
                               else _resolver(parte, el.get("Target", ""))}
                for el in raiz.iter(f"{{{NS_PKG}}}Relationship")}

    @property
    def strings(self):
        if self._strings is None:
            self._strings = []
            if "xl/sharedStrings.xml" in self.nomes_partes:
                raiz = ET.fromstring(self.zip.read("xl/sharedStrings.xml"))
                for si in raiz.iter(f"{{{NS_MAIN}}}si"):
                    direto = si.find(f"{{{NS_MAIN}}}t")
                    if direto is not None:
                        self._strings.append(direto.text or "")
                    else:
                        self._strings.append("".join(t.text or "" for r in si.iter(f"{{{NS_MAIN}}}r")
                                                     for t in r.iter(f"{{{NS_MAIN}}}t")))
        return self._strings

    def _parte(self, nome):
        for aba in self.abas:
            if aba["nome"] == nome:
                return aba["parte"]
        raise KeyError(f"aba inexistente: {nome}")

    def _ler_aba(self, nome):
        if nome in self._cache:
            return self._cache[nome]
        parte = self._parte(nome)
        celulas, mescladas, mestres, pendentes = {}, [], {}, []
        with self.zip.open(parte) as fluxo:
            for _, el in ET.iterparse(fluxo, events=("end",)):
                tag = _local(el.tag)
                if tag == "c":
                    ref = el.get("r")
                    tipo = el.get("t", "n")
                    f = el.find(f"{{{NS_MAIN}}}f")
                    v = el.find(f"{{{NS_MAIN}}}v")
                    formula = None
                    if f is not None:
                        if f.get("t") == "shared":
                            si = f.get("si")
                            if f.text:
                                formula = f.text
                                mestres[si] = (f.text, ref)
                            elif si in mestres:
                                formula = self._compartilhada(mestres[si], ref)
                            else:
                                pendentes.append((ref, si))
                        else:
                            formula = f.text or ""
                    if tipo == "inlineStr":
                        texto = "".join(t.text or "" for t in el.iter(f"{{{NS_MAIN}}}t"))
                        celulas[ref] = Celula("s", texto, formula)
                    else:
                        bruto = None if v is None else (v.text if v.text is not None or tipo != "str" else "")
                        celulas[ref] = Celula(*self._valor(tipo, bruto), formula)
                    el.clear()
                elif tag == "mergeCell":
                    mescladas.append(el.get("ref"))
                elif tag == "row":
                    el.clear()
        for ref, si in pendentes:
            if si in mestres:
                anterior = celulas[ref]
                celulas[ref] = Celula(anterior.tipo, anterior.valor, self._compartilhada(mestres[si], ref))
        self._cache[nome] = (celulas, mescladas)
        return self._cache[nome]

    @staticmethod
    def _compartilhada(mestre, ref):
        texto, ref_mestre = mestre
        c0, l0 = separar_ref(ref_mestre)
        c1, l1 = separar_ref(ref)
        return traduzir_formula(texto, l1 - l0, c1 - c0)

    def _valor(self, tipo, texto):
        if texto is None:
            return (None, None)
        if tipo == "s":
            return ("s", self.strings[int(texto)])
        if tipo == "str":
            return ("s", texto)
        if tipo == "b":
            return ("b", texto.strip() in ("1", "true"))
        if tipo in ("e", "d"):
            return (tipo, texto)
        try:
            numero = float(texto)
        except ValueError:
            return ("s", texto)
        if numero.is_integer() and re.fullmatch(r"-?\d+", texto.strip()):
            return ("n", int(numero))
        return ("n", numero)

    def ler(self, nome):
        """Células da aba: {ref: Celula(tipo, valor, formula)} com fórmulas sem '='."""
        return self._ler_aba(nome)[0]

    def mescladas(self, nome):
        return self._ler_aba(nome)[1]

    def recursos(self):
        por_aba = {}
        for aba in self.abas:
            contagem = dict.fromkeys(RECURSOS_ABA, 0)
            bruto = self.zip.read(aba["parte"])
            fim = bruto[bruto.rfind(b"<extLst"):] if b"<extLst" in bruto else b""
            contagem["extensoes"] = sum(fim.count(b"<x14" + marca) for marca in EXTENSOES_X14)
            for rel in self._rels(aba["parte"]).values():
                tipo, alvo = rel["tipo"], rel["alvo"]
                if tipo == "drawing" and alvo in self.nomes_partes:
                    with self.zip.open(alvo) as fluxo:
                        for _, el in ET.iterparse(fluxo, events=("end",)):
                            nome = _local(el.tag)
                            if nome == "pic" and el.tag.startswith(f"{{{NS_XDR}}}"):
                                contagem["imagens"] += 1
                            elif nome == "chart" and el.tag.startswith(f"{{{NS_CHART}}}"):
                                contagem["graficos"] += 1
                            elif nome in ("sp", "cxnSp") and el.tag.startswith(f"{{{NS_XDR}}}"):
                                contagem["formas"] += 1
                elif tipo == "ctrlProp":
                    contagem["controles"] += 1
                elif tipo in ("oleObject", "package"):
                    contagem["objetos"] += 1
                elif tipo == "table":
                    contagem["tabelas"] += 1
                elif tipo == "comments":
                    contagem["comentarios"] += 1
            por_aba[aba["nome"]] = contagem
        partes = self.nomes_partes
        pasta = {
            "vba": int("xl/vbaProject.bin" in partes),
            "vinculos_externos": sum(1 for p in partes if re.fullmatch(r"xl/externalLinks/externalLink\d+\.xml", p)),
            "tabelas_dinamicas": sum(1 for p in partes if re.fullmatch(r"xl/pivotTables/pivotTable\d+\.xml", p)),
            "segmentacoes": sum(1 for p in partes if re.fullmatch(r"xl/slicers/slicer\d+\.xml", p)),
            "linhas_do_tempo": sum(1 for p in partes if re.fullmatch(r"xl/timelines/timeline\d+\.xml", p)),
            "conexoes": int("xl/connections.xml" in partes),
            "modelo_dados": int(any(p.startswith("xl/model/") for p in partes)),
        }
        return {"por_aba": por_aba, "pasta": pasta}


def ler_pasta(caminho):
    return Pasta(caminho)


def riscos_de_gravacao(recursos):
    """Recursos que seriam perdidos se o arquivo fosse regravado pelo openpyxl."""
    riscos = []
    for aba, contagem in recursos["por_aba"].items():
        for chave in RECURSOS_ABA:
            if chave in PERDIDOS_NA_GRAVACAO and contagem.get(chave):
                riscos.append(f"{aba}: {contagem[chave]} {chave}")
    for chave in RECURSOS_PASTA:
        if chave in PERDIDOS_NA_GRAVACAO and recursos["pasta"].get(chave):
            riscos.append(f"pasta: {recursos['pasta'][chave]} {chave}")
    return riscos


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------- mapa

PADROES = {
    "unidade": re.compile(r"^(un|und|unid|unidade|u\s?m)\.?$"),
    "quantidade": re.compile(r"^(qt|qtd|qtde|qte|quant|quantidade)\b"),
    "preco_unitario": re.compile(r"(unit|^p\.?\s?u\.?$|^pu$)"),
    "preco_total": re.compile(r"(?<!sub)total"),
    "item": re.compile(r"^(item|itens|n|no|n[ºo°]|num|numero|cod|codigo|ref|referencia)\b"),
    "descricao": re.compile(r"(descri|discrimina|servico|especifica|denomina)"),
}


def _texto_normal(valor):
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto).strip().lower()


def _classificar(texto):
    for chave in ("unidade", "quantidade", "preco_unitario", "preco_total", "item", "descricao"):
        if PADROES[chave].search(texto):
            return chave
    return None


def _cabecalho(celulas, max_linha_busca=80):
    linhas = {}
    for ref, cel in celulas.items():
        if cel.tipo != "s" or cel.formula is not None:
            continue
        col, lin = separar_ref(ref)
        if lin <= max_linha_busca:
            linhas.setdefault(lin, []).append((col, _texto_normal(cel.valor)))
    melhor = None
    for lin in sorted(linhas):
        achados = {}
        for col, texto in sorted(linhas[lin]):
            categoria = _classificar(texto)
            if categoria:
                achados.setdefault(categoria, []).append((col, texto))
        nucleo = sum(1 for c in ("item", "descricao", "unidade", "quantidade") if c in achados)
        if nucleo >= 3 and (melhor is None or nucleo > melhor[0]):
            melhor = (nucleo, lin, achados)
    if not melhor:
        return None
    _, lin, achados = melhor
    colunas = {}
    for categoria, lista in achados.items():
        if categoria == "quantidade":
            colunas[categoria] = [col_letra(c) for c, _ in lista]
        elif categoria == "item":
            exatos = [c for c, t in lista if t in ("item", "itens")]
            colunas[categoria] = col_letra(exatos[0] if exatos else lista[0][0])
        else:
            colunas[categoria] = col_letra(lista[0][0])
    return {"linha": lin, "colunas": colunas}


def _max_coluna(celulas):
    return max((separar_ref(ref)[0] for ref, c in celulas.items() if c.valor is not None or c.formula is not None),
               default=0)


def mapear(caminho):
    pasta = ler_pasta(caminho)
    try:
        recursos = pasta.recursos()
        abas = []
        for aba in pasta.abas:
            celulas = pasta.ler(aba["nome"])
            preenchidas = {r: c for r, c in celulas.items() if c.valor is not None or c.formula is not None}
            max_col = _max_coluna(preenchidas)
            max_lin = max((separar_ref(r)[1] for r in preenchidas), default=0)
            registro = {"nome": aba["nome"], "estado": aba["estado"], "linhas": max_lin, "colunas": max_col,
                        "celulas": len(preenchidas), "formulas": sum(1 for c in preenchidas.values() if c.formula),
                        "mescladas": len(pasta.mescladas(aba["nome"])),
                        "primeira_coluna_livre": col_letra(max_col + 1), "cabecalho": None,
                        "itens_provaveis": 0, "agrupadores_provaveis": 0, "amostra": []}
            cab = _cabecalho(preenchidas)
            if cab:
                registro["cabecalho"] = cab
                cols = cab["colunas"]

                def texto(col, lin):
                    cel = preenchidas.get(f"{col}{lin}") if col else None
                    return None if cel is None or cel.valor in (None, "") else str(cel.valor)

                for lin in range(cab["linha"] + 1, max_lin + 1):
                    desc = texto(cols.get("descricao"), lin)
                    if not desc:
                        continue
                    if texto(cols.get("unidade"), lin):
                        registro["itens_provaveis"] += 1
                        if len(registro["amostra"]) < 5:
                            registro["amostra"].append({"linha": lin, "item": texto(cols.get("item"), lin),
                                                        "descricao": desc, "unidade": texto(cols.get("unidade"), lin)})
                    else:
                        registro["agrupadores_provaveis"] += 1
            abas.append(registro)
        return {"arquivo": str(caminho), "sha256": sha256(caminho), "abas": abas, "recursos": recursos,
                "nomes_definidos": len(pasta.nomes_definidos), "riscos_de_gravacao": riscos_de_gravacao(recursos)}
    finally:
        pasta.fechar()


def mapa_markdown(mapa):
    linhas = [f"# Mapa da planilha — {Path(mapa['arquivo']).name}", "",
              "| Aba | Estado | Linhas × colunas | Fórmulas | Cabeçalho | Itens prováveis | Agrupadores | Coluna livre |",
              "|---|---|---|---:|---|---:|---:|---|"]
    for a in mapa["abas"]:
        cab = a["cabecalho"]
        descricao_cab = (f"linha {cab['linha']}: " + ", ".join(f"{k}={v}" for k, v in cab["colunas"].items())
                         if cab else "não detectado")
        linhas.append(f"| {a['nome']} | {a['estado']} | {a['linhas']} × {a['colunas']} | {a['formulas']} | "
                      f"{descricao_cab} | {a['itens_provaveis']} | {a['agrupadores_provaveis']} | "
                      f"{a['primeira_coluna_livre']} |")
    linhas += ["", "Riscos de gravação (recursos que o openpyxl descartaria): "
               + ("; ".join(mapa["riscos_de_gravacao"]) or "nenhum")]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- snapshot e verificação

def snapshot(caminho):
    pasta = ler_pasta(caminho)
    try:
        abas = []
        for ordem, aba in enumerate(pasta.abas):
            celulas = {}
            for ref, c in pasta.ler(aba["nome"]).items():
                if c.valor is None and c.formula is None:
                    continue
                celulas[ref] = [c.tipo, c.valor, normalizar_formula(c.formula)]
            abas.append({"nome": aba["nome"], "estado": aba["estado"], "ordem": ordem,
                         "max_coluna": _max_coluna(pasta.ler(aba["nome"])), "celulas": celulas,
                         "mescladas": sorted(pasta.mescladas(aba["nome"]))})
        return {"versao": "snapshot-planilha/1", "arquivo": str(caminho), "sha256": sha256(caminho),
                "criado_em": datetime.now().astimezone().isoformat(), "abas": abas,
                "nomes_definidos": {k: normalizar_formula(v) for k, v in pasta.nomes_definidos.items()},
                "recursos": pasta.recursos()}
    finally:
        pasta.fechar()


def salvar_snapshot(dados, saida):
    texto = json.dumps(dados, ensure_ascii=False).encode("utf-8")
    saida = Path(saida)
    saida.write_bytes(gzip.compress(texto) if saida.suffix == ".gz" else texto)
    return saida


def carregar_snapshot(caminho):
    bruto = Path(caminho).read_bytes()
    if bruto[:2] == b"\x1f\x8b":
        bruto = gzip.decompress(bruto)
    return json.loads(bruto.decode("utf-8"))


def _mesmo_valor(tipo, valor, atual):
    if atual.tipo != tipo:
        return False
    if tipo == "n":
        return math.isclose(float(valor), float(atual.valor), rel_tol=1e-12, abs_tol=1e-12)
    return valor == atual.valor


def verificar(foto, caminho, colunas_novas=None, abas_novas=None, limite=200):
    """Compara o arquivo com o snapshot. colunas_novas = {aba: primeira coluna (número) liberada}."""
    erros, avisos = [], []
    pasta = ler_pasta(caminho)
    try:
        nomes_novos = [a["nome"] for a in pasta.abas]
        estados_novos = {a["nome"]: a["estado"] for a in pasta.abas}
        for aba in foto["abas"]:
            nome = aba["nome"]
            if nome not in estados_novos:
                erros.append(f"aba removida ou renomeada: {nome}")
                continue
            if estados_novos[nome] != aba["estado"]:
                erros.append(f"visibilidade da aba {nome} mudou: {aba['estado']} → {estados_novos[nome]}")
            atuais = pasta.ler(nome)
            originais = aba["celulas"]
            for ref, (tipo, valor, formula) in originais.items():
                atual = atuais.get(ref)
                if atual is None or (atual.valor is None and atual.formula is None):
                    erros.append(f"{nome}!{ref}: célula apagada (era {formula or valor!r})")
                elif formula is not None:
                    if normalizar_formula(atual.formula) != formula:
                        erros.append(f"{nome}!{ref}: fórmula mudou ({formula} → {atual.formula})")
                elif atual.formula is not None:
                    erros.append(f"{nome}!{ref}: valor virou fórmula ({valor!r} → {atual.formula})")
                elif not _mesmo_valor(tipo, valor, atual):
                    erros.append(f"{nome}!{ref}: valor mudou ({valor!r} → {atual.valor!r})")
            liberada = (colunas_novas or {}).get(nome)
            for ref, atual in atuais.items():
                if ref in originais or (atual.valor is None and atual.formula is None):
                    continue
                if liberada is None or separar_ref(ref)[0] < liberada:
                    erros.append(f"{nome}!{ref}: célula acrescentada dentro da área original")
            for intervalo in set(aba["mescladas"]) - set(pasta.mescladas(nome)):
                erros.append(f"{nome}: mesclagem {intervalo} desfeita")
        ordem_original = [a["nome"] for a in sorted(foto["abas"], key=lambda a: a["ordem"]) if a["nome"] in nomes_novos]
        if [n for n in nomes_novos if n in ordem_original] != ordem_original:
            avisos.append("a ordem das abas originais mudou")
        originais_nomes = {a["nome"] for a in foto["abas"]}
        for nome in nomes_novos:
            if nome not in originais_nomes and abas_novas is not None and nome not in abas_novas:
                avisos.append(f"aba nova não prevista: {nome}")
        for chave, valor in foto.get("nomes_definidos", {}).items():
            atual = pasta.nomes_definidos.get(chave)
            # Nomes internos do Excel (_xlnm.*) podem ser regravados de outra forma sem perda de conteúdo.
            destino = avisos if chave.startswith("_xlnm.") else erros
            if atual is None:
                destino.append(f"nome definido removido: {chave}")
            elif normalizar_formula(atual).replace("'", "") != (valor or "").replace("'", ""):
                destino.append(f"nome definido {chave} mudou: {valor} → {atual}")
        recursos = pasta.recursos()
        for aba, contagem in foto["recursos"]["por_aba"].items():
            agora = recursos["por_aba"].get(aba, {})
            for chave, quantidade in contagem.items():
                if agora.get(chave, 0) < quantidade:
                    erros.append(f"recurso perdido na aba {aba}: {chave} {quantidade} → {agora.get(chave, 0)}")
        for chave, quantidade in foto["recursos"]["pasta"].items():
            if recursos["pasta"].get(chave, 0) < quantidade:
                erros.append(f"recurso perdido na pasta: {chave} {quantidade} → {recursos['pasta'].get(chave, 0)}")
    finally:
        pasta.fechar()
    return {"ok": not erros, "total_erros": len(erros), "erros": erros[:limite], "avisos": avisos}


# ---------------------------------------------------------------- linha de comando

def _colunas_cli(valores):
    resultado = {}
    for item in valores or []:
        aba, _, coluna = item.rpartition("=")
        resultado[aba] = int(coluna) if coluna.isdigit() else col_numero(coluna)
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("mapear")
    p.add_argument("arquivo")
    p.add_argument("--saida")
    p.add_argument("--md", help="também grava um resumo em Markdown")
    p = sub.add_parser("snapshot")
    p.add_argument("arquivo")
    p.add_argument("--saida", required=True, help=".json ou .json.gz")
    p = sub.add_parser("verificar")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--arquivo", required=True)
    p.add_argument("--colunas-novas", nargs="*", metavar="ABA=COLUNA",
                   help="primeira coluna liberada por aba, ex.: 'Orçamento=G'")
    p.add_argument("--saida")
    a = parser.parse_args()

    if a.comando == "mapear":
        mapa = mapear(a.arquivo)
        if a.md:
            Path(a.md).write_text(mapa_markdown(mapa), encoding="utf-8")
        if a.saida:
            Path(a.saida).write_text(json.dumps(mapa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(mapa_markdown(mapa))
        else:
            print(json.dumps(mapa, ensure_ascii=False, indent=2))
    elif a.comando == "snapshot":
        foto = snapshot(a.arquivo)
        salvar_snapshot(foto, a.saida)
        print(json.dumps({"snapshot": a.saida, "abas": len(foto["abas"]),
                          "celulas": sum(len(x["celulas"]) for x in foto["abas"])}, ensure_ascii=False))
    else:
        relatorio = verificar(carregar_snapshot(a.snapshot), a.arquivo, _colunas_cli(a.colunas_novas))
        texto = json.dumps(relatorio, ensure_ascii=False, indent=2)
        if a.saida:
            Path(a.saida).write_text(texto + "\n", encoding="utf-8")
        print(texto)
        sys.exit(0 if relatorio["ok"] else 1)


if __name__ == "__main__":
    main()
