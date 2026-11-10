#!/usr/bin/env python3
"""Modelo do `levantamento.json`: carga, validação das regras e cálculo dos itens.

Usado por gerar_planilha.py e validar_entrega.py; só depende da biblioteca padrão.
Rodado direto, valida um arquivo:  python3 levantamento.py dados/levantamento.json
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ESTADOS = ("CONFIRMADO", "PREMISSA", "SUBTOTAL", "PENDENTE", "NÃO APLICÁVEL")
COM_TOTAL = ("CONFIRMADO", "PREMISSA")
NATUREZAS = ("medivel", "parametro", "indireto", "fora_escopo")
ORIGENS = ("indicado", "cotas", "coordenadas", "comando_nativo", "contagem", "medicao_grafica", "premissa",
           "criterio_usuario")
ORIGENS_APROXIMADAS = ("medicao_grafica", "premissa")
CATEGORIAS = ("ESCOPO_FASE", "ESPECIFICACAO", "GEOMETRIA_COTAS", "UNIDADE_CRITERIO", "COMPOSICAO_DUPLICIDADE",
              "DOCUMENTACAO_REVISAO", "DIMENSIONAMENTO_VISTORIA")
CLASSES_COMPARACAO = ("comparável", "comparável com ressalva", "não comparável", "sem correspondência")
PROIBIDOS_ABA = re.compile(r"[\[\]:*?/\\]")
SINONIMOS_UNIDADE = {"und": "un", "unid": "un", "unidade": "un", "unidades": "un", "pç": "pc", "peça": "pc",
                     "verba": "vb", "vba": "vb", "mes": "mês", "meses": "mês"}


def raiz_de(caminho_json, dados=None):
    """Pasta da execução: a que contém dados/ (ou o campo "raiz", se houver)."""
    if dados and dados.get("raiz"):
        return Path(dados["raiz"]).expanduser().resolve()
    pasta = Path(caminho_json).resolve().parent
    return pasta.parent if pasta.name == "dados" else pasta


def carregar(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return dados, raiz_de(caminho, dados)


def resolver(raiz, caminho):
    caminho = Path(caminho).expanduser()
    return caminho if caminho.is_absolute() else raiz / caminho


def normalizar_unidade(unidade):
    texto = unicodedata.normalize("NFKC", str(unidade or "")).strip().lower().replace(" ", "").replace(".", "")
    return SINONIMOS_UNIDADE.get(texto, texto)


def separar_chave(chave):
    m = re.fullmatch(r"(.+)!(\d+)", str(chave or ""))
    return (m.group(1), int(m.group(2))) if m else None


def lista_do_item(listas, aba, linha):
    """Índice da lista da aba cujo intervalo contém a linha (cabeçalho mais próximo acima)."""
    candidatas = [(indice, lista) for indice, lista in enumerate(listas)
                  if lista.get("aba") == aba and isinstance(lista.get("linha_cabecalho"), int)
                  and lista["linha_cabecalho"] < linha
                  and (lista.get("linha_final") is None or linha <= lista["linha_final"])]
    if not candidatas:
        return None
    return max(candidatas, key=lambda par: par[1]["linha_cabecalho"])[0]


def valor_parcela(parcela):
    """Resultado da parcela ou None quando falta algum dado (nunca zero por omissão)."""
    multiplicidade = parcela.get("multiplicidade", 1)
    sinal = parcela.get("sinal", 1)
    if "dimensoes" in parcela and parcela["dimensoes"] is not None:
        dimensoes = parcela["dimensoes"]
        if not dimensoes or any(d is None for d in dimensoes):
            return None
        produto = 1.0
        for d in dimensoes:
            produto *= float(d)
        return produto * multiplicidade * sinal
    if parcela.get("valor") is None:
        return None
    return float(parcela["valor"]) * multiplicidade * sinal


def calcular_item(item):
    """Mesma lógica das fórmulas da memória (ESQUEMA_PLANILHA §2)."""
    valores = [valor_parcela(p) for p in item.get("parcelas") or []]
    conhecidos = [v for v in valores if v is not None]
    subtotal = sum(conhecidos) if conhecidos else None
    faltantes = len(valores) - len(conhecidos)
    estado = item.get("estado")
    if estado in COM_TOTAL and faltantes > 0:
        estado = "SUBTOTAL"
    total = subtotal if estado in COM_TOTAL else None
    return {"valores": valores, "subtotal": subtotal, "faltantes": faltantes, "estado": estado, "total": total}


def sanear_nome_aba(nome):
    nome = PROIBIDOS_ABA.sub("-", str(nome)).strip().strip("'")
    return (nome or "ITEM")[:31]


def nomes_abas_memoria(itens, existentes=()):
    """Mapa chave → nome de aba válido e único (sem diferenciar maiúsculas)."""
    usados = {n.lower() for n in existentes}
    nomes = {}
    for item in itens:
        base = sanear_nome_aba(item.get("aba_memoria") or f"ITEM {item.get('id', '')}")
        nome, n = base, 1
        while nome.lower() in usados:
            n += 1
            sufixo = f" ({n})"
            nome = base[:31 - len(sufixo)] + sufixo
        usados.add(nome.lower())
        nomes[item["chave"]] = nome
    return nomes


def _validar_planilha(planilha, erros):
    for campo in ("recebida", "trabalho", "entrega", "snapshot"):
        if not planilha.get(campo):
            erros.append(f"planilha.{campo} ausente")
    if planilha.get("modo", "auto") not in ("auto", "mesmo_arquivo", "arquivo_separado"):
        erros.append("planilha.modo inválido")
    vistas = set()
    for lista in planilha.get("listas") or []:
        rotulo = f"lista {lista.get('aba')}"
        cabecalho, final = lista.get("linha_cabecalho"), lista.get("linha_final")
        if not isinstance(cabecalho, int) or cabecalho < 1:
            erros.append(f"{rotulo}: linha_cabecalho inválida")
            continue
        if final is not None and (not isinstance(final, int) or final <= cabecalho):
            erros.append(f"{rotulo}: linha_final deve ser maior que linha_cabecalho")
        if (lista.get("aba"), cabecalho) in vistas:
            erros.append(f"{rotulo}: lista repetida (mesma aba e cabeçalho)")
        vistas.add((lista.get("aba"), cabecalho))
        for ignorada in lista.get("linhas_ignoradas") or []:
            if not isinstance(ignorada.get("linha"), int) or not str(ignorada.get("motivo") or "").strip():
                erros.append(f"{rotulo}: linhas_ignoradas precisa de linha (número) e motivo")


def _validar_extras(dados, chaves, erros):
    for sugestao in dados.get("sugestoes") or []:
        if not all(str(sugestao.get(c) or "").strip() for c in ("id", "servico", "motivo")):
            erros.append(f"sugestão {sugestao.get('id', '?')}: id, servico e motivo são obrigatórios")
    for comparacao in dados.get("comparacao") or []:
        rotulo = f"comparação {comparacao.get('chave', '?')}"
        if comparacao.get("chave") not in chaves:
            erros.append(f"{rotulo}: chave não corresponde a nenhum item")
        if comparacao.get("classe") not in CLASSES_COMPARACAO:
            erros.append(f"{rotulo}: classe inválida (use {', '.join(CLASSES_COMPARACAO)})")
        referencia = comparacao.get("referencia")
        if referencia is not None and not isinstance(referencia, (int, float)):
            erros.append(f"{rotulo}: referencia deve ser número ou null")
    if not all(isinstance(t, str) and t.strip() for t in dados.get("limitacoes") or []):
        erros.append("limitacoes deve ser uma lista de frases")


def validar(dados, raiz, conferir_arquivos=True):
    """Devolve (erros, avisos) segundo as regras do ESQUEMA_LEVANTAMENTO."""
    erros, avisos = [], []
    if dados.get("versao") != "levantamento/1":
        erros.append('versao deve ser "levantamento/1"')
    planilha = dados.get("planilha") or {}
    _validar_planilha(planilha, erros)
    listas = list(planilha.get("listas") or [])
    abas_listas = {lista.get("aba") for lista in listas}
    premissas = {p.get("id") for p in dados.get("premissas") or []}
    pendencias = {p.get("id") for p in dados.get("pendencias") or []}
    criterios = {c.get("id") for c in dados.get("criterios") or []}
    vistos = set()

    for item in dados.get("itens") or []:
        rotulo = f"item {item.get('id', '?')} ({item.get('chave', 'sem chave')})"
        chave = separar_chave(item.get("chave"))
        if not chave:
            erros.append(f"{rotulo}: chave deve ser 'aba!linha'")
        elif chave[0] not in abas_listas:
            erros.append(f"{rotulo}: a aba {chave[0]} não está em planilha.listas")
        elif lista_do_item(listas, *chave) is None:
            erros.append(f"{rotulo}: linha fora do intervalo das listas da aba (confira linha_cabecalho e linha_final)")
        if item.get("chave") in vistos:
            erros.append(f"{rotulo}: chave repetida")
        vistos.add(item.get("chave"))
        for campo in ("id", "descricao", "unidade"):
            if not str(item.get(campo) or "").strip():
                erros.append(f"{rotulo}: campo {campo} ausente")
        estado, natureza = item.get("estado"), item.get("natureza")
        if estado not in ESTADOS:
            erros.append(f"{rotulo}: estado inválido {estado!r} (use {', '.join(ESTADOS)})")
        if natureza not in NATUREZAS:
            erros.append(f"{rotulo}: natureza inválida {natureza!r}")
        refs_p = set(item.get("premissas") or [])
        refs_d = set(item.get("pendencias") or [])
        parcelas = item.get("parcelas") or []
        for p in parcelas:
            refs_p |= {r for r in p.get("refs") or [] if str(r).startswith("P")}
            refs_d |= {r for r in p.get("refs") or [] if str(r).startswith("D")}
        for ref in sorted(refs_p - premissas):
            erros.append(f"{rotulo}: premissa {ref} não existe")
        for ref in sorted(refs_d - pendencias):
            erros.append(f"{rotulo}: pendência {ref} não existe")
        if item.get("criterio") and item["criterio"] not in criterios:
            avisos.append(f"{rotulo}: critério {item['criterio']} não está em criterios")

        ids_parcelas = []
        unidade_item = normalizar_unidade(item.get("unidade"))
        for p in parcelas:
            ids_parcelas.append(p.get("id"))
            if p.get("origem") not in ORIGENS:
                erros.append(f"{rotulo}: parcela {p.get('id')}: origem inválida {p.get('origem')!r}")
            if p.get("sinal", 1) not in (1, -1):
                erros.append(f"{rotulo}: parcela {p.get('id')}: sinal deve ser 1 ou -1")
            dims = p.get("dimensoes")
            if dims is not None and not (isinstance(dims, list) and 1 <= len(dims) <= 3):
                erros.append(f"{rotulo}: parcela {p.get('id')}: dimensoes deve ter de 1 a 3 valores")
            if dims is None and "valor" not in p:
                erros.append(f"{rotulo}: parcela {p.get('id')}: informe dimensoes ou valor")
            if p.get("unidade") and normalizar_unidade(p["unidade"]) != unidade_item:
                erros.append(f"{rotulo}: parcela {p.get('id')}: unidade {p['unidade']!r} difere da unidade do item "
                             f"{item.get('unidade')!r}")
        if len(set(ids_parcelas)) != len(ids_parcelas):
            erros.append(f"{rotulo}: IDs de parcela repetidos")

        calculo = calcular_item(item)
        aproximadas = any(p.get("origem") in ORIGENS_APROXIMADAS for p in parcelas)
        if estado in ("PENDENTE", "SUBTOTAL") and not refs_d:
            erros.append(f"{rotulo}: estado {estado} exige pendência (D###)")
        if estado == "SUBTOTAL" and calculo["subtotal"] is None:
            erros.append(f"{rotulo}: SUBTOTAL exige ao menos uma parcela com valor")
        if estado == "PREMISSA" and not refs_p and not aproximadas:
            erros.append(f"{rotulo}: PREMISSA exige premissa (P###) ou parcela de medicao_grafica")
        if estado == "CONFIRMADO" and (refs_p or aproximadas):
            erros.append(f"{rotulo}: CONFIRMADO não pode depender de premissa ou medição gráfica (use PREMISSA)")
        if estado == "NÃO APLICÁVEL" and not str(item.get("observacao") or "").strip():
            erros.append(f"{rotulo}: NÃO APLICÁVEL exige o motivo em observacao")
        if estado in COM_TOTAL:
            if not parcelas:
                erros.append(f"{rotulo}: {estado} exige parcelas")
            elif calculo["faltantes"]:
                erros.append(f"{rotulo}: {estado} com parcela sem valor (use SUBTOTAL e uma pendência)")

        evidencias = item.get("evidencias") or []
        exige_print = natureza == "medivel" or (natureza == "parametro" and estado != "NÃO APLICÁVEL")
        if exige_print and not evidencias and not item.get("sem_representacao_grafica"):
            erros.append(f"{rotulo}: falta evidência (print marcado) ou sem_representacao_grafica com o motivo")
        if (natureza == "medivel" and estado in ("CONFIRMADO", "PREMISSA", "SUBTOTAL") and not evidencias
                and item.get("sem_representacao_grafica")):
            avisos.append(f"{rotulo}: item físico sem print; confirme que não há representação gráfica aplicável")
        cobertas = set()
        for ev in evidencias:
            caminho = resolver(raiz, ev.get("arquivo", ""))
            if conferir_arquivos and not caminho.is_file():
                erros.append(f"{rotulo}: evidência não encontrada: {ev.get('arquivo')}")
            for pid in ev.get("parcelas") or []:
                if pid not in ids_parcelas:
                    avisos.append(f"{rotulo}: a evidência cita a parcela {pid}, que não existe")
                cobertas.add(pid)
        if evidencias:
            for pid in ids_parcelas:
                if pid not in cobertas:
                    erros.append(f"{rotulo}: parcela {pid} não aparece em nenhuma evidência")
        if natureza in ("medivel", "parametro") and estado != "NÃO APLICÁVEL" and not item.get("criterio"):
            avisos.append(f"{rotulo}: item mensurável sem critério")
        if natureza == "medivel" and estado in ("CONFIRMADO", "PREMISSA", "SUBTOTAL") and not item.get("texto"):
            avisos.append(f"{rotulo}: faltam os textos o que entrou / ficou fora / falta")
        for d in item.get("diagnostico") or []:
            if d.get("categoria") not in CATEGORIAS:
                avisos.append(f"{rotulo}: categoria de diagnóstico desconhecida {d.get('categoria')!r}")
    _validar_extras(dados, vistos, erros)
    return erros, avisos


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 2)
    dados, raiz = carregar(sys.argv[1])
    erros, avisos = validar(dados, raiz)
    print(json.dumps({"ok": not erros, "erros": erros, "avisos": avisos}, ensure_ascii=False, indent=2))
    sys.exit(0 if not erros else 1)


if __name__ == "__main__":
    main()
