#!/usr/bin/env python3
"""Gera a planilha de entrega a partir do levantamento.json (layout em assets/ESQUEMA_PLANILHA.md).

Nenhuma célula da planilha recebida é alterada: as colunas QTD LEVANTADA, ESTADO, MEMÓRIA
e OBS LEVANTAMENTO entram à direita do conteúdo de cada lista, e as memórias por item, as
abas do levantamento e os prints são acrescentados. Se a planilha tiver recursos que a
gravação perderia (imagens, gráficos, controles, extensões), o modo auto grava um arquivo
separado. As fórmulas saem com os valores já calculados (cache), e um manifesto ao lado da
entrega registra o que foi gerado, para o validar_entrega.py conferir.

Precisa de openpyxl e Pillow (scripts/requirements.txt).
"""

import argparse
import io
import json
import math
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

import levantamento as lv
import planilha as pl

COLUNAS_NOVAS = ("QTD LEVANTADA", "ESTADO", "MEMÓRIA", "OBS LEVANTAMENTO")
ABAS_FIXAS = ("Resumo do levantamento", "Pendências", "Premissas", "Critérios", "Fontes", "Sugestões", "Comparação")
PRIMEIRA_PARCELA = 19
LARGURA_EXIBICAO = 980
CORES_ESTADO = {"CONFIRMADO": "C6EFCE", "PREMISSA": "FFEB9C", "SUBTOTAL": "F8CBAD", "PENDENTE": "FFC7CE",
                "NÃO APLICÁVEL": "D9D9D9"}


# ---------------------------------------------------------------- fórmulas (usadas também pelo validador)

def citar(nome):
    return "'" + nome.replace("'", "''") + "'"


def formula_qtd(memoria):
    return f'=IF({citar(memoria)}!$G$8="","",{citar(memoria)}!$G$8)'


def formula_estado(memoria):
    return f"={citar(memoria)}!$G$9"


def formula_parcela(linha, n_dimensoes):
    if n_dimensoes == 0:
        return f'=IF(COUNT(H{linha})<1,"",H{linha}*I{linha}*J{linha})'
    colunas = "EFG"[:n_dimensoes]
    faixa = f"E{linha}" if n_dimensoes == 1 else f"E{linha}:{colunas[-1]}{linha}"
    fatores = "*".join(f"{c}{linha}" for c in colunas)
    return f'=IF(COUNT({faixa})<{n_dimensoes},"",{fatores}*I{linha}*J{linha})'


def formulas_resultado(n_parcelas):
    if n_parcelas:
        faixa = f"K{PRIMEIRA_PARCELA}:K{PRIMEIRA_PARCELA + n_parcelas - 1}"
        g10, g12 = f'=IF(COUNT({faixa})=0,"",SUM({faixa}))', f"=ROWS({faixa})-COUNT({faixa})"
    else:
        g10, g12 = '=""', "=0"
    return {"G8": '=IF(OR(G9="CONFIRMADO",G9="PREMISSA"),G10,"")',
            "G9": '=IF(AND(OR(G13="CONFIRMADO",G13="PREMISSA"),G12>0),"SUBTOTAL",G13)',
            "G10": g10, "G12": g12}


def caminho_manifesto(entrega):
    return Path(entrega).with_suffix(".manifesto.json")


# ---------------------------------------------------------------- imagens

def preparar_imagem(caminho, largura_max):
    """Reduz a largura e a paleta; devolve (bytes, (largura, altura))."""
    from PIL import Image
    with Image.open(caminho) as original:
        original.load()
        if original.mode in ("RGBA", "LA", "P"):
            rgba = original.convert("RGBA")
            imagem = Image.new("RGB", rgba.size, "white")
            imagem.paste(rgba, mask=rgba.split()[-1])
        else:
            imagem = original.convert("RGB")
    if imagem.width > largura_max:
        imagem = imagem.resize((largura_max, round(imagem.height * largura_max / imagem.width)),
                               Image.Resampling.LANCZOS)
    png = io.BytesIO()
    imagem.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(png, format="PNG", optimize=True)
    dados = png.getvalue()
    if len(dados) > 600_000:
        jpg = io.BytesIO()
        imagem.save(jpg, format="JPEG", quality=85, optimize=True)
        if len(jpg.getvalue()) < len(dados):
            dados = jpg.getvalue()
    return dados, imagem.size


# ---------------------------------------------------------------- cache das fórmulas

_CELULA_FORMULA = re.compile(
    r'<c r="([A-Z]{1,3}\d+)"([^>]*)>(<f(?:\s[^>]*)?>.*?</f>|<f(?:\s[^>]*)?/>)(?:<v\s*/>|<v></v>)</c>', re.S)


def _serializar(valor):
    if isinstance(valor, pl.Celula):
        if valor.valor is None:
            return None
        if valor.tipo == "n":
            return "", repr(valor.valor)
        if valor.tipo == "b":
            return "b", "1" if valor.valor else "0"
        if valor.tipo == "e":
            return "e", escape(str(valor.valor))
        return "str", escape(str(valor.valor))
    if isinstance(valor, bool):
        return "b", "1" if valor else "0"
    if isinstance(valor, (int, float)):
        if isinstance(valor, float) and valor.is_integer():
            return "", str(int(valor))
        return "", repr(valor)
    return "str", escape(str(valor))


def _partes_das_abas(pacote):
    ns_main, ns_rel = pl.NS_MAIN, pl.NS_REL
    livro = ET.fromstring(pacote.read("xl/workbook.xml"))
    rels = ET.fromstring(pacote.read("xl/_rels/workbook.xml.rels"))
    alvos = {r.get("Id"): pl._resolver("xl/workbook.xml", r.get("Target")) for r in rels}
    return {s.get("name"): alvos[s.get(f"{{{ns_rel}}}id")] for s in livro.iter(f"{{{ns_main}}}sheet")}


def injetar_cache(caminho, calculados, originais):
    """Grava <v> nas fórmulas: valores calculados por nós e, nas abas originais, os da planilha recebida."""
    with zipfile.ZipFile(caminho) as pacote:
        infos = pacote.infolist()
        conteudo = {i.filename: pacote.read(i.filename) for i in infos}
        partes = _partes_das_abas(pacote)
    preenchidas = 0
    for aba, parte in partes.items():
        nossos = calculados.get(aba, {})
        deles = originais.get(aba, {})
        if not nossos and not deles:
            continue

        def trocar(m):
            nonlocal preenchidas
            ref, atributos, formula = m.groups()
            fonte = nossos[ref] if ref in nossos else deles.get(ref)
            serial = None if fonte is None else _serializar(fonte)
            if serial is None:
                return m.group(0)
            tipo, texto = serial
            atributos = re.sub(r'\s+t="[^"]*"', "", atributos) + (f' t="{tipo}"' if tipo else "")
            preenchidas += 1
            return f'<c r="{ref}"{atributos}>{formula}<v>{texto}</v></c>'

        conteudo[parte] = _CELULA_FORMULA.sub(trocar, conteudo[parte].decode("utf-8")).encode("utf-8")
    temporario = Path(caminho).with_suffix(".tmp_cache")
    with zipfile.ZipFile(temporario, "w") as saida:
        for info in infos:
            saida.writestr(info, conteudo[info.filename])
    temporario.replace(caminho)
    return preenchidas


# ---------------------------------------------------------------- montagem

class Gerador:
    def __init__(self, dados, raiz, saida, modo, largura_imagem):
        import openpyxl
        from openpyxl.styles import Alignment, Font, PatternFill
        self.openpyxl, self.Alignment, self.Font, self.PatternFill = openpyxl, Alignment, Font, PatternFill
        self.dados, self.raiz, self.saida = dados, raiz, saida
        self.largura_imagem = largura_imagem
        planilha = dados["planilha"]
        self.trabalho = lv.resolver(raiz, planilha["trabalho"])
        self.foto = pl.carregar_snapshot(lv.resolver(raiz, planilha["snapshot"]))
        with pl.ler_pasta(self.trabalho) as pasta:
            self.riscos = pl.riscos_de_gravacao(pasta.recursos())
            self.originais = {a["nome"]: {r: c for r, c in pasta.ler(a["nome"]).items() if c.formula is not None}
                              for a in pasta.abas}
        self.modo = modo or planilha.get("modo", "auto")
        if self.modo == "auto":
            self.modo = "arquivo_separado" if self.riscos else "mesmo_arquivo"
        self.calculados = {}
        self.manifesto = {"versao": "manifesto-planilha/1", "modo": self.modo, "riscos": self.riscos,
                          "colunas_novas": {}, "itens": {}, "abas_criadas": [], "imagens": 0, "bytes_imagens": 0}
        self.avisos = []

    # -- utilidades
    def _cache(self, ws, ref, valor):
        self.calculados.setdefault(ws.title, {})[ref] = "" if valor is None else valor

    @staticmethod
    def _texto(ws, ref, valor):
        celula = ws[ref]
        celula.value = valor
        if isinstance(valor, str) and valor.startswith("="):
            celula.data_type = "s"
        return celula

    def _cabecalho(self, ws, linha, coluna, titulos):
        for i, titulo in enumerate(titulos):
            celula = ws.cell(row=linha, column=coluna + i, value=titulo)
            celula.font = self.Font(bold=True)
            celula.fill = self.PatternFill("solid", fgColor="DDDDDD")
            celula.alignment = self.Alignment(wrap_text=True, vertical="center")

    def _cores_de_estado(self, ws, faixa):
        from openpyxl.formatting.rule import CellIsRule
        for estado, cor in CORES_ESTADO.items():
            ws.conditional_formatting.add(faixa, CellIsRule(operator="equal", formula=[f'"{estado}"'],
                                                            fill=self.PatternFill("solid", fgColor=cor)))

    def _nome_livre(self, base, usados):
        nome, n = base[:31], 1
        while nome.lower() in usados:
            n += 1
            sufixo = " (levantamento)" if n == 2 else f" (levantamento {n})"
            nome = base[:31 - len(sufixo)] + sufixo
        usados.add(nome.lower())
        return nome

    # -- etapas
    def montar(self):
        if self.modo == "mesmo_arquivo":
            self.wb = self.openpyxl.load_workbook(self.trabalho, keep_vba=self.trabalho.suffix.lower() == ".xlsm",
                                                  keep_links=True, rich_text=True)
        else:
            self.wb = self.openpyxl.Workbook()
            self.wb.remove(self.wb.active)
        usados = {n.lower() for n in self.wb.sheetnames}
        self.nomes_fixos = {nome: self._nome_livre(nome, usados) for nome in ABAS_FIXAS}
        itens = self.dados.get("itens") or []
        self.nomes_memoria = lv.nomes_abas_memoria(itens, usados)
        self.resultados = {item["chave"]: lv.calcular_item(item) for item in itens}
        self._principais(itens)
        self._abas_do_levantamento(itens)
        for item in itens:
            self._memoria(item)
        if self.wb.calculation is None:
            from openpyxl.workbook.properties import CalcProperties
            self.wb.calculation = CalcProperties()
        self.wb.calculation.fullCalcOnLoad = True
        return self.wb

    def _principais(self, itens):
        listas = self.dados["planilha"]["listas"]
        por_lista = {}
        for item in itens:
            aba, linha = lv.separar_chave(item["chave"])
            por_lista.setdefault(lv.lista_do_item(listas, aba, linha), []).append((linha, item))
        fotos = {a["nome"]: a for a in self.foto["abas"]}
        copias = {}
        for indice_lista, lista in enumerate(listas):
            aba = lista["aba"]
            if aba not in fotos:
                raise SystemExit(f"A aba {aba} não existe no snapshot da planilha recebida.")
            linhas = sorted(por_lista.get(indice_lista, []), key=lambda par: par[0])
            if self.modo == "mesmo_arquivo":
                ws = self.wb[aba]
                coluna = lista.get("coluna_inicial_nova")
                coluna = (pl.col_numero(coluna) if isinstance(coluna, str) else coluna) or fotos[aba]["max_coluna"] + 1
                ocupadas = {pl.separar_ref(r)[0] for r in fotos[aba]["celulas"]}
                if any(c in ocupadas for c in range(coluna, coluna + len(COLUNAS_NOVAS))):
                    raise SystemExit(f"coluna_inicial_nova da aba {aba} sobrepõe conteúdo da planilha recebida.")
                cabecalho = lista["linha_cabecalho"]
                destino = [(linha, linha, item) for linha, item in linhas]
            else:
                copias[aba] = copias.get(aba, 0) + 1
                sufixo = " (cópia)" if copias[aba] == 1 else f" (cópia {copias[aba]})"
                ws = self.wb.create_sheet(lv.sanear_nome_aba(aba[:31 - len(sufixo)] + sufixo))
                self.manifesto["abas_criadas"].append(ws.title)
                destino = self._copiar_lista(ws, lista, indice_lista, fotos[aba]["celulas"], dict(linhas))
                coluna, cabecalho = 5, 1
            letras = [pl.col_letra(coluna + i) for i in range(len(COLUNAS_NOVAS))]
            self._cabecalho(ws, cabecalho, coluna, COLUNAS_NOVAS)
            anterior = self.manifesto["colunas_novas"].get(ws.title)
            self.manifesto["colunas_novas"][ws.title] = coluna if anterior is None else min(anterior, coluna)
            for linha_saida, linha_origem, item in destino:
                memoria = self.nomes_memoria[item["chave"]]
                resultado = self.resultados[item["chave"]]
                qtd, estado, link, obs = (f"{letra}{linha_saida}" for letra in letras)
                ws[qtd] = formula_qtd(memoria)
                ws[qtd].number_format = "#,##0.00"
                self._cache(ws, qtd, resultado["total"])
                ws[estado] = formula_estado(memoria)
                self._cache(ws, estado, resultado["estado"])
                self._texto(ws, link, memoria)
                ws[link].hyperlink = self._link(link, memoria)
                ws[link].font = self.Font(color="0563C1", underline="single")
                self._texto(ws, obs, self._observacao(item))
                self.manifesto["itens"][item["chave"]] = {
                    "aba": ws.title, "linha": linha_saida, "memoria": memoria,
                    "celulas": {"qtd": qtd, "estado": estado, "memoria": link, "obs": obs}}
            if destino:
                self._cores_de_estado(ws, f"{letras[1]}{destino[0][0]}:{letras[1]}{destino[-1][0]}")
            ws.column_dimensions[letras[0]].width = 16
            ws.column_dimensions[letras[1]].width = 16
            ws.column_dimensions[letras[2]].width = 16
            ws.column_dimensions[letras[3]].width = 40

    def _copiar_lista(self, ws, lista, indice_lista, celulas, itens_por_linha):
        """Copia o bloco da lista (itens e agrupadores) como valores; devolve (linha de saída, linha original, item)."""
        colunas = lista.get("colunas") or {}
        campos = ("item", "descricao", "unidade", "quantidade")
        self._cabecalho(ws, 1, 1, ("ITEM", "DESCRIÇÃO", "UNIDADE", "QTD RECEBIDA (cópia)"))
        self._cabecalho(ws, 1, 9, ("LINHA ORIGINAL",))
        listas = self.dados["planilha"]["listas"]
        ultima = lista.get("linha_final") or max((pl.separar_ref(r)[1] for r in celulas), default=lista["linha_cabecalho"])
        destino, posicao = [], 2
        for linha in range(lista["linha_cabecalho"] + 1, ultima + 1):
            if lv.lista_do_item(listas, lista["aba"], linha) != indice_lista:
                continue
            valores = []
            for campo in campos:
                letra = colunas.get(campo)
                registro = celulas.get(f"{letra}{linha}") if letra else None
                valores.append(registro[1] if registro else None)
            if all(v in (None, "") for v in valores) and linha not in itens_por_linha:
                continue
            for coluna, valor in enumerate(valores, start=1):
                self._texto(ws, f"{pl.col_letra(coluna)}{posicao}", valor)
            ws[f"I{posicao}"] = linha
            if linha in itens_por_linha:
                destino.append((posicao, linha, itens_por_linha[linha]))
            posicao += 1
        ws.column_dimensions["B"].width = 50
        return destino

    @staticmethod
    def _link(ref, memoria):
        from openpyxl.worksheet.hyperlink import Hyperlink
        return Hyperlink(ref=ref, location=f"{citar(memoria)}!A1", display=memoria)

    @staticmethod
    def _observacao(item):
        texto = (item.get("observacao") or "").strip()
        ids = [*(item.get("pendencias") or []), *(item.get("premissas") or [])]
        faltando = [i for i in ids if i not in texto]
        return (texto + (" " if texto and faltando else "") + ", ".join(faltando)).strip()

    def _memoria(self, item):
        ws = self.wb.create_sheet(self.nomes_memoria[item["chave"]])
        self.manifesto["abas_criadas"].append(ws.title)
        resultado = self.resultados[item["chave"]]
        negrito = self.Font(bold=True)
        quebra = self.Alignment(wrap_text=True, vertical="top")
        ws["A1"] = f"MEMÓRIA DE CÁLCULO — ITEM {item['id']}"
        ws["A1"].font = self.Font(bold=True, size=13)
        rotulos = [
            ("A3", "Item", item["id"]), ("A4", "Descrição", item["descricao"]), ("A5", "Unidade", item["unidade"]),
            ("A6", "Chave na planilha", item["chave"]),
            ("A8", "Critério", self._criterio(item.get("criterio"))),
            ("A9", "Premissas", self._resumo_ids(item.get("premissas"), self.dados.get("premissas"), "parametro")),
            ("A10", "Pendências", self._resumo_ids(item.get("pendencias"), self.dados.get("pendencias"), "pergunta")),
            ("A11", "Fontes", ", ".join(item.get("fontes") or []) or self._fontes_das_parcelas(item)),
            ("A12", "Natureza", item.get("natureza")),
            ("A14", "O que entrou", (item.get("texto") or {}).get("entrou", "")),
            ("A15", "O que ficou fora", (item.get("texto") or {}).get("ficou_fora", "")),
            ("A16", "O que falta", (item.get("texto") or {}).get("falta", "")),
        ]
        for ref, rotulo, valor in rotulos:
            ws[ref] = rotulo
            ws[ref].font = negrito
            ws[ref].alignment = quebra
            linha = ref[1:]
            self._texto(ws, f"B{linha}", valor)
            ws[f"B{linha}"].alignment = quebra
        if item.get("sem_representacao_grafica"):
            ws["A17"] = "Sem representação gráfica"
            ws["A17"].font = negrito
            self._texto(ws, "B17", item["sem_representacao_grafica"])
            ws["B17"].alignment = quebra

        parcelas = item.get("parcelas") or []
        formulas = formulas_resultado(len(parcelas))
        bloco = [("F8", "QTD LEVANTADA", "G8", formulas["G8"], resultado["total"]),
                 ("F9", "Estado", "G9", formulas["G9"], resultado["estado"]),
                 ("F10", "Subtotal conhecido", "G10", formulas["G10"], resultado["subtotal"]),
                 ("F11", "Unidade", "G11", None, item["unidade"]),
                 ("F12", "Parcelas sem valor", "G12", formulas["G12"], resultado["faltantes"]),
                 ("F13", "Estado declarado", "G13", None, item["estado"])]
        for rotulo_ref, rotulo, ref, formula, valor in bloco:
            ws[rotulo_ref] = rotulo
            ws[rotulo_ref].font = negrito
            if formula:
                ws[ref] = formula
                self._cache(ws, ref, valor)
            else:
                self._texto(ws, ref, valor)
        ws["G8"].number_format = ws["G10"].number_format = "#,##0.00##"
        ws["G8"].font = self.Font(bold=True, size=12)
        self._cores_de_estado(ws, "G9")

        titulos = ("ID", "Descrição", "Local / face", "Estado físico", "Dim. 1", "Dim. 2", "Dim. 3", "Valor direto",
                   "Mult.", "Sinal", "Resultado", "Unid.", "Origem", "Fonte", "P / D")
        self._cabecalho(ws, PRIMEIRA_PARCELA - 1, 1, titulos)
        for deslocamento, parcela in enumerate(parcelas):
            linha = PRIMEIRA_PARCELA + deslocamento
            dimensoes = parcela.get("dimensoes")
            self._texto(ws, f"A{linha}", parcela.get("id"))
            self._texto(ws, f"B{linha}", parcela.get("descricao"))
            self._texto(ws, f"C{linha}", parcela.get("local"))
            self._texto(ws, f"D{linha}", parcela.get("estado_fisico"))
            if dimensoes is not None:
                for letra, valor in zip("EFG", dimensoes):
                    ws[f"{letra}{linha}"] = valor
                    ws[f"{letra}{linha}"].number_format = "0.00##"
                ws[f"K{linha}"] = formula_parcela(linha, len(dimensoes))
            else:
                ws[f"H{linha}"] = parcela.get("valor")
                ws[f"H{linha}"].number_format = "0.00##"
                ws[f"K{linha}"] = formula_parcela(linha, 0)
            ws[f"I{linha}"] = parcela.get("multiplicidade", 1)
            ws[f"J{linha}"] = parcela.get("sinal", 1)
            ws[f"K{linha}"].number_format = "#,##0.00##"
            self._cache(ws, f"K{linha}", resultado["valores"][deslocamento])
            self._texto(ws, f"L{linha}", parcela.get("unidade"))
            self._texto(ws, f"M{linha}", parcela.get("origem"))
            self._texto(ws, f"N{linha}", parcela.get("fonte"))
            self._texto(ws, f"O{linha}", ", ".join(parcela.get("refs") or []))
        linha = PRIMEIRA_PARCELA + max(len(parcelas), 1) + 1

        diagnostico = item.get("diagnostico") or []
        if diagnostico:
            ws[f"A{linha}"] = "Diagnóstico"
            ws[f"A{linha}"].font = negrito
            linha += 1
            campos = ("categoria", "constatacao", "solucao", "base", "estado", "efeito")
            self._cabecalho(ws, linha, 1, ("Categoria", "Constatação e evidência", "Solução", "Base", "Estado", "Efeito"))
            for registro in diagnostico:
                linha += 1
                for coluna, campo in enumerate(campos, start=1):
                    celula = self._texto(ws, f"{pl.col_letra(coluna)}{linha}", registro.get(campo))
                    celula.alignment = quebra
            linha += 2

        for evidencia in item.get("evidencias") or []:
            caminho = lv.resolver(self.raiz, evidencia["arquivo"])
            if caminho.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".webp"):
                self.avisos.append(f"{item['chave']}: {evidencia['arquivo']} não é imagem; não foi incorporado")
                continue
            legenda = f"{caminho.name} — {evidencia.get('legenda', '')}"
            if evidencia.get("parcelas"):
                legenda += f" (parcelas: {', '.join(evidencia['parcelas'])})"
            ws[f"A{linha}"] = legenda
            ws[f"A{linha}"].font = negrito
            dados, (largura, altura) = preparar_imagem(caminho, self.largura_imagem)
            from openpyxl.drawing.image import Image as ImagemExcel
            imagem = ImagemExcel(io.BytesIO(dados))
            escala = min(1.0, LARGURA_EXIBICAO / largura)
            imagem.width, imagem.height = round(largura * escala), round(altura * escala)
            ws.add_image(imagem, f"A{linha + 1}")
            self.manifesto["imagens"] += 1
            self.manifesto["bytes_imagens"] += len(dados)
            linha += 3 + math.ceil(imagem.height / 20)

        larguras = {"A": 22, "B": 52, "C": 18, "D": 13, "E": 10, "F": 19, "G": 14, "H": 12, "I": 7, "J": 7,
                    "K": 13, "L": 8, "M": 15, "N": 24, "O": 14}
        for letra, largura in larguras.items():
            ws.column_dimensions[letra].width = largura
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    def _criterio(self, cid):
        for c in self.dados.get("criterios") or []:
            if c.get("id") == cid:
                return f"{cid} — {c.get('regra', '')} (fonte: {c.get('fonte', '')})"
        return cid or ""

    @staticmethod
    def _resumo_ids(ids, registros, campo):
        por_id = {r.get("id"): r for r in registros or []}
        return "; ".join(f"{i}: {por_id.get(i, {}).get(campo, '')}".strip() for i in ids or [])

    @staticmethod
    def _fontes_das_parcelas(item):
        return ", ".join(sorted({p.get("fonte") for p in item.get("parcelas") or [] if p.get("fonte")}))

    def _tabela(self, nome, titulos, linhas):
        ws = self.wb.create_sheet(nome)
        self.manifesto["abas_criadas"].append(ws.title)
        self._cabecalho(ws, 1, 1, titulos)
        quebra = self.Alignment(wrap_text=True, vertical="top")
        for i, valores in enumerate(linhas, start=2):
            for j, valor in enumerate(valores, start=1):
                if isinstance(valor, (list, tuple)):
                    valor = ", ".join(map(str, valor))
                celula = self._texto(ws, f"{pl.col_letra(j)}{i}", valor)
                celula.alignment = quebra
        for j in range(1, len(titulos) + 1):
            ws.column_dimensions[pl.col_letra(j)].width = 28
        ws.freeze_panes = "A2"
        return ws

    def _abas_do_levantamento(self, itens):
        dados = self.dados
        resumo = self.wb.create_sheet(self.nomes_fixos["Resumo do levantamento"])
        self.manifesto["abas_criadas"].append(resumo.title)
        cabecalho = [("Obra", dados.get("obra")), ("Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")),
                     ("Planilha recebida", dados["planilha"]["recebida"]),
                     ("Modo de gravação", self.modo),
                     ("Motivo do arquivo separado", "; ".join(self.riscos) if self.modo == "arquivo_separado" else "—")]
        cabecalho += [("Limitação", texto) for texto in dados.get("limitacoes") or []]
        for i, (rotulo, valor) in enumerate(cabecalho, start=1):
            resumo[f"A{i}"] = rotulo
            resumo[f"A{i}"].font = self.Font(bold=True)
            self._texto(resumo, f"B{i}", valor)
        contagem = {e: sum(1 for r in self.resultados.values() if r["estado"] == e) for e in lv.ESTADOS}
        linha = len(cabecalho) + 2
        self._cabecalho(resumo, linha, 1, ("Estado", "Itens"))
        for estado, quantidade in contagem.items():
            linha += 1
            resumo[f"A{linha}"], resumo[f"B{linha}"] = estado, quantidade
        linha += 2
        self._cabecalho(resumo, linha, 1, ("Chave", "Item", "Descrição", "Estado", "QTD LEVANTADA", "Unidade", "Memória"))
        for item in itens:
            linha += 1
            resultado = self.resultados[item["chave"]]
            memoria = self.nomes_memoria[item["chave"]]
            for coluna, valor in zip("ABCDEF", (item["chave"], item["id"], item["descricao"], resultado["estado"],
                                                resultado["total"], item["unidade"])):
                self._texto(resumo, f"{coluna}{linha}", valor)
            resumo[f"E{linha}"].number_format = "#,##0.00"
            self._texto(resumo, f"G{linha}", memoria)
            resumo[f"G{linha}"].hyperlink = self._link(f"G{linha}", memoria)
        for letra, largura in zip("ABCDEFG", (24, 12, 50, 16, 16, 9, 18)):
            resumo.column_dimensions[letra].width = largura

        def linhas(registros, campos):
            return [[r.get(c) for c in campos] for r in registros or []]

        self._tabela(self.nomes_fixos["Pendências"],
                     ("ID", "Natureza", "Itens", "Pergunta", "Fonte consultada", "Já comprovado", "Opções e efeito",
                      "Impacto", "Responsável", "Situação"),
                     linhas(dados.get("pendencias"), ("id", "natureza", "itens", "pergunta", "fonte_consultada",
                                                      "comprovado", "opcoes", "impacto", "responsavel", "situacao")))
        self._tabela(self.nomes_fixos["Premissas"],
                     ("ID", "Itens", "Parâmetro", "Valor adotado", "Base", "Impacto", "Confirmar com", "Situação"),
                     linhas(dados.get("premissas"), ("id", "itens", "parametro", "valor", "base", "impacto",
                                                     "confirmar_com", "situacao")))
        criterios = [[c.get("id"), c.get("familia"), c.get("regra"),
                      json.dumps(c.get("parametros"), ensure_ascii=False) if isinstance(c.get("parametros"), dict)
                      else c.get("parametros"), c.get("fonte")] for c in dados.get("criterios") or []]
        self._tabela(self.nomes_fixos["Critérios"], ("ID", "Família", "Regra", "Parâmetros", "Fonte"), criterios)
        fontes = [[f.get("id"), f.get("arquivo"), f.get("revisao"), f.get("sha256"),
                   "\n".join(f"{r.get('id')} — {r.get('titulo', '')} — {r.get('localizador', '')} — {r.get('leitura', '')}"
                             for r in f.get("representacoes") or [])] for f in dados.get("fontes") or []]
        self._tabela(self.nomes_fixos["Fontes"], ("ID", "Arquivo", "Revisão", "SHA-256", "Representações"), fontes)
        if dados.get("sugestoes"):
            self._tabela(self.nomes_fixos["Sugestões"],
                         ("ID", "Serviço sugerido", "Motivo", "Local / elemento", "Fonte", "Unidade",
                          "Quantidade estimada", "Itens relacionados"),
                         linhas(dados["sugestoes"], ("id", "servico", "motivo", "local", "fonte", "unidade",
                                                     "quantidade", "itens_relacionados")))
        if dados.get("comparacao"):
            por_chave = {item["chave"]: item for item in itens}
            linhas_comparacao = []
            for registro in dados["comparacao"]:
                item = por_chave[registro["chave"]]
                resultado = self.resultados[registro["chave"]]
                total, referencia = resultado["total"], registro.get("referencia")
                delta = percentual = "—"
                if (registro.get("classe") in ("comparável", "comparável com ressalva")
                        and isinstance(total, (int, float)) and isinstance(referencia, (int, float))):
                    delta = total - referencia
                    percentual = delta / referencia * 100 if referencia else "não calculável — base zero"
                linhas_comparacao.append([registro["chave"], item["id"], item["descricao"], item["unidade"], total,
                                          resultado["estado"], referencia, registro.get("fonte"),
                                          registro.get("classe"), delta, percentual, registro.get("explicacao")])
            self._tabela(self.nomes_fixos["Comparação"],
                         ("Chave", "Item", "Descrição", "Unidade", "QTD LEVANTADA", "Estado", "Referência",
                          "Fonte da referência", "Classe", "Δ (levantada − referência)", "Δ% sobre a referência",
                          "Explicação"), linhas_comparacao)


def gerar(caminho_json, saida=None, modo=None, largura_imagem=1400):
    dados, raiz = lv.carregar(caminho_json)
    erros, avisos = lv.validar(dados, raiz)
    if erros:
        return {"ok": False, "erros": erros, "avisos": avisos}
    planilha = dados["planilha"]
    destino = Path(saida).resolve() if saida else lv.resolver(raiz, planilha["entrega"]).resolve()
    if raiz.resolve() not in destino.parents:
        return {"ok": False, "erros": [f"a entrega deve ficar dentro da pasta da execução ({raiz}); "
                                       "os arquivos originais nunca são sobrescritos"], "avisos": avisos}
    protegidos = {lv.resolver(raiz, planilha[c]).resolve() for c in ("recebida", "trabalho")}
    if destino in protegidos:
        return {"ok": False, "erros": [f"a entrega não pode sobrescrever {destino.name}"], "avisos": avisos}
    gerador = Gerador(dados, raiz, destino, modo, largura_imagem)
    trabalho_sufixo = gerador.trabalho.suffix.lower()
    if gerador.modo == "mesmo_arquivo" and destino.suffix.lower() != trabalho_sufixo:
        return {"ok": False, "erros": [f"a entrega deve ter a extensão {trabalho_sufixo}"], "avisos": avisos}
    if gerador.modo == "arquivo_separado" and destino.suffix.lower() != ".xlsx":
        destino = destino.with_suffix(".xlsx")
    workbook = gerador.montar()
    destino.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(destino)
    originais = gerador.originais if gerador.modo == "mesmo_arquivo" else {}
    preenchidas = injetar_cache(destino, gerador.calculados, originais)
    tamanho = destino.stat().st_size / 1e6
    avisos += gerador.avisos
    if tamanho > 25:
        avisos.append(f"planilha com {tamanho:.1f} MB: considere mover as plantas gerais para um caderno PDF")
    manifesto = {**gerador.manifesto, "entrega": str(destino), "gerado_em": datetime.now().astimezone().isoformat(),
                 "celulas_com_cache": preenchidas, "tamanho_mb": round(tamanho, 2)}
    caminho_manifesto(destino).write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "entrega": str(destino), "modo": gerador.modo, "riscos": gerador.riscos,
            "itens": len(dados.get("itens") or []), "imagens": manifesto["imagens"],
            "tamanho_mb": round(tamanho, 2), "avisos": avisos}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--levantamento", required=True, help="dados/levantamento.json")
    parser.add_argument("--saida", help="caminho da entrega (padrão: planilha.entrega do JSON)")
    parser.add_argument("--modo", choices=("auto", "mesmo_arquivo", "arquivo_separado"))
    parser.add_argument("--largura-imagem", type=int, default=1400, help="largura máxima dos prints, em pixels")
    a = parser.parse_args()
    try:
        import openpyxl  # noqa: F401
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("gerar_planilha.py precisa de openpyxl e Pillow: python3 -m pip install -r scripts/requirements.txt")
    resultado = gerar(a.levantamento, a.saida, a.modo, a.largura_imagem)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    sys.exit(0 if resultado["ok"] else 1)


if __name__ == "__main__":
    main()
