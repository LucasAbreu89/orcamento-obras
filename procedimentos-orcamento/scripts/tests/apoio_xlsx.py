"""Construtor mínimo de XLSX só com a biblioteca padrão, para montar casos de teste.

Especificação de célula:
  ("n", 10)                         número
  ("s", "texto")                    texto em sharedStrings
  ("inline", "texto")               texto inline
  ("b", True)                       booleano
  ("e", "#N/A")                     erro
  ("f", "B5*C5", 20)                fórmula com valor em cache (None = sem cache)
  ("fs", "B5*C5", 0, "D5:D7", 20)   fórmula compartilhada mestre (texto, si, ref, cache)
  ("fs", None, 0, None, 30)         dependente de fórmula compartilhada
"""

import zipfile
from xml.sax.saxutils import escape

NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" ' \
     'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


def _ordenar(ref):
    letras = "".join(c for c in ref if c.isalpha())
    numero = int("".join(c for c in ref if c.isdigit()))
    coluna = 0
    for c in letras:
        coluna = coluna * 26 + ord(c) - 64
    return numero, coluna


def _celula(ref, spec, strings):
    tipo = spec[0]
    if tipo == "n":
        return f'<c r="{ref}"><v>{spec[1]!r}</v></c>'
    if tipo == "s":
        if spec[1] not in strings:
            strings.append(spec[1])
        return f'<c r="{ref}" t="s"><v>{strings.index(spec[1])}</v></c>'
    if tipo == "inline":
        return f'<c r="{ref}" t="inlineStr"><is><t>{escape(spec[1])}</t></is></c>'
    if tipo == "b":
        return f'<c r="{ref}" t="b"><v>{int(bool(spec[1]))}</v></c>'
    if tipo == "e":
        return f'<c r="{ref}" t="e"><v>{escape(spec[1])}</v></c>'
    if tipo == "f":
        cache = "" if spec[2] is None else f"<v>{spec[2]!r}</v>"
        return f'<c r="{ref}"><f>{escape(spec[1])}</f>{cache}</c>'
    if tipo == "fs":
        texto, si, alcance, cache = spec[1], spec[2], spec[3], spec[4]
        atributos = f't="shared" si="{si}"' + (f' ref="{alcance}"' if alcance else "")
        corpo = escape(texto) if texto else ""
        f = f"<f {atributos}>{corpo}</f>" if corpo else f"<f {atributos}/>"
        return f'<c r="{ref}">{f}' + ("" if cache is None else f"<v>{cache!r}</v>") + "</c>"
    raise ValueError(tipo)


def criar_xlsx(caminho, abas, imagem_na_aba=None):
    strings = []
    partes = {}
    for indice, aba in enumerate(abas, 1):
        linhas = {}
        for ref, spec in sorted(aba.get("celulas", {}).items(), key=lambda kv: _ordenar(kv[0])):
            linhas.setdefault(_ordenar(ref)[0], []).append(_celula(ref, spec, strings))
        dados = "".join(f'<row r="{n}">{"".join(c)}</row>' for n, c in sorted(linhas.items()))
        mescladas = aba.get("mescladas") or []
        merge = (f'<mergeCells count="{len(mescladas)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in mescladas)
                 + "</mergeCells>") if mescladas else ""
        desenho = '<drawing r:id="rId1"/>' if imagem_na_aba == indice - 1 else ""
        partes[f"xl/worksheets/sheet{indice}.xml"] = (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet {NS}>'
            f"<sheetData>{dados}</sheetData>{merge}{desenho}</worksheet>")
    sheets = "".join(
        f'<sheet name="{escape(a["nome"])}" sheetId="{i}" r:id="rId{i}"'
        + (f' state="{a["estado"]}"' if a.get("estado", "visible") != "visible" else "") + "/>"
        for i, a in enumerate(abas, 1))
    partes["xl/workbook.xml"] = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook {NS}>'
                                 f"<sheets>{sheets}</sheets></workbook>")
    rels = "".join(
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(abas) + 1))
    rels += (f'<Relationship Id="rId{len(abas) + 1}" '
             'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
             'Target="sharedStrings.xml"/>')
    partes["xl/_rels/workbook.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
    partes["xl/sharedStrings.xml"] = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><sst {NS.split(" ")[0]} count="{len(strings)}" '
        f'uniqueCount="{len(strings)}">' + "".join(f"<si><t>{escape(s)}</t></si>" for s in strings) + "</sst>")
    partes["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>')
    overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(1, len(abas) + 1))
    if imagem_na_aba is not None:
        n = imagem_na_aba + 1
        partes[f"xl/worksheets/_rels/sheet{n}.xml.rels"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" '
            'Target="../drawings/drawing1.xml"/></Relationships>')
        partes["xl/drawings/drawing1.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<xdr:oneCellAnchor><xdr:from><xdr:col>0</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>0</xdr:row>'
            '<xdr:rowOff>0</xdr:rowOff></xdr:from><xdr:ext cx="9525" cy="9525"/><xdr:pic><xdr:nvPicPr>'
            '<xdr:cNvPr id="1" name="Imagem 1"/><xdr:cNvPicPr/></xdr:nvPicPr><xdr:blipFill>'
            '<a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill><xdr:spPr>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic><xdr:clientData/>'
            '</xdr:oneCellAnchor></xdr:wsDr>')
        partes["xl/drawings/_rels/drawing1.xml.rels"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            'Target="../media/image1.png"/></Relationships>')
        partes["xl/media/image1.png"] = PNG_1PX
        overrides += ('<Override PartName="/xl/drawings/drawing1.xml" '
                      'ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>')
    partes["[Content_Types].xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        f"{overrides}</Types>")
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as pacote:
        for nome, conteudo in partes.items():
            pacote.writestr(nome, conteudo)
    return caminho


def lista_exemplo(quantidade_item_1=10):
    """Aba de orçamento típica: título, cabeçalho na linha 4, agrupador e dois itens."""
    return {
        "nome": "Orçamento",
        "celulas": {
            "A1": ("s", "PLANILHA ORÇAMENTÁRIA"),
            "A4": ("s", "ITEM"), "B4": ("s", "DESCRIÇÃO DOS SERVIÇOS"), "C4": ("s", "UNID."),
            "D4": ("s", "QUANT."), "E4": ("s", "PREÇO UNIT."), "F4": ("s", "TOTAL"),
            "A5": ("s", "1"), "B5": ("s", "PISOS"),
            "A6": ("s", "1.1"), "B6": ("s", "Piso cerâmico"), "C6": ("s", "m²"),
            "D6": ("n", quantidade_item_1), "E6": ("n", 50.0), "F6": ("fs", "D6*E6", 0, "F6:F7", quantidade_item_1 * 50.0),
            "A7": ("s", "1.10"), "B7": ("s", "Rodapé cerâmico"), "C7": ("s", "m"),
            "D7": ("n", 20), "E7": ("n", 12.5), "F7": ("fs", None, 0, None, 250.0),
        },
        "mescladas": ["A1:F1"],
    }
