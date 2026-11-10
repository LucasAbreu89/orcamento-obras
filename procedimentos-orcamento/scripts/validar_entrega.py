#!/usr/bin/env python3
"""Valida a planilha de entrega contra o levantamento.json, o snapshot e o manifesto.

Confere, sem depender de bibliotecas externas:
  - regras do levantamento.json (estados, pendências, premissas, evidências);
  - planilha recebida intacta (valores, fórmulas, vazios, abas, mesclagens, recursos);
  - QTD LEVANTADA e ESTADO ligados à memória certa, sem IFERROR/SEERRO;
  - fórmulas e valores gravados da memória iguais aos calculados pelas parcelas;
  - dimensões gravadas como número e prints incorporados em cada item físico;
  - com --recalculado, os valores de um motor independente (LibreOffice);
  - tamanho do arquivo.
Grava o relatório em JSON e Markdown (padrão: conferencia/validacao.*) e sai com 1 se houver erro.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import gerar_planilha as gp
import levantamento as lv
import planilha as pl


def _igual(esperado, celula):
    if celula is None:
        return esperado in (None, "")
    valor = celula.valor
    if esperado is None or esperado == "":
        return valor in (None, "")
    if isinstance(esperado, (int, float)) and not isinstance(esperado, bool):
        return isinstance(valor, (int, float)) and not isinstance(valor, bool) and \
            math.isclose(float(valor), float(esperado), rel_tol=1e-9, abs_tol=1e-9)
    return str(valor) == str(esperado)


def _preenchida(registro):
    return bool(registro) and (registro[1] not in (None, "") or registro[2] is not None)


def _cobertura(dados, foto, erros, avisos):
    """Toda linha das listas com descrição e unidade precisa de item no JSON ou de motivo em linhas_ignoradas."""
    listas = dados["planilha"].get("listas") or []
    chaves = {item["chave"] for item in dados.get("itens") or []}
    abas = {a["nome"]: a["celulas"] for a in foto["abas"]}
    for indice, lista in enumerate(listas):
        colunas = lista.get("colunas") or {}
        descricao, unidade = colunas.get("descricao"), colunas.get("unidade")
        celulas = abas.get(lista.get("aba"), {})
        if not descricao or not unidade:
            avisos.append(f"lista {lista.get('aba')} (linha {lista.get('linha_cabecalho')}): sem colunas de descrição "
                          "e unidade; a cobertura dos itens não foi verificada")
            continue
        ignoradas = {registro["linha"] for registro in lista.get("linhas_ignoradas") or []}
        ultima = lista.get("linha_final") or max((pl.separar_ref(r)[1] for r in celulas), default=0)
        for linha in range(lista["linha_cabecalho"] + 1, ultima + 1):
            if lv.lista_do_item(listas, lista["aba"], linha) != indice or linha in ignoradas:
                continue
            if (_preenchida(celulas.get(f"{descricao}{linha}")) and _preenchida(celulas.get(f"{unidade}{linha}"))
                    and f"{lista['aba']}!{linha}" not in chaves):
                erros.append(f"{lista['aba']}!{linha}: linha com descrição e unidade sem item no levantamento.json "
                             "(item omitido? se não for item, registrar em linhas_ignoradas com o motivo)")


def _conferir_fontes(raiz, erros, avisos):
    """Os originais (projetos e planilha) precisam continuar com o hash do inventário inicial."""
    inventario = raiz / "fontes" / "inventario.json"
    if not inventario.is_file():
        avisos.append("fontes/inventario.json ausente: os originais não foram reconferidos")
        return
    for fonte in json.loads(inventario.read_text(encoding="utf-8")).get("fontes", []):
        if not fonte.get("sha256"):
            continue
        caminho = Path(fonte["caminho"])
        if not caminho.is_file():
            erros.append(f"fonte original ausente: {caminho}")
        elif pl.sha256(caminho) != fonte["sha256"]:
            erros.append(f"fonte original alterada durante o levantamento: {caminho}")


def validar_entrega(caminho_json, recalculado=None, limite_mb=25.0, conferir_fontes=True):
    dados, raiz = lv.carregar(caminho_json)
    erros, avisos = lv.validar(dados, raiz)
    if conferir_fontes:
        _conferir_fontes(raiz, erros, avisos)
    planilha = dados["planilha"]
    # O manifesto tem o mesmo nome para .xlsx e .xlsm e guarda o caminho real da entrega.
    manifesto_caminho = gp.caminho_manifesto(lv.resolver(raiz, planilha["entrega"]))
    manifesto = (json.loads(manifesto_caminho.read_text(encoding="utf-8"))
                 if manifesto_caminho.is_file() else None)
    entrega = Path(manifesto["entrega"]) if manifesto else lv.resolver(raiz, planilha["entrega"])
    if manifesto is None or not entrega.is_file():
        resumo = {"recalculo": "não executado"}
        return {"ok": False, "erros": erros + [f"entrega ou manifesto inexistente: {entrega}"], "avisos": avisos,
                "resumo": resumo}
    foto = pl.carregar_snapshot(lv.resolver(raiz, planilha["snapshot"]))

    if manifesto["modo"] == "mesmo_arquivo":
        integridade = pl.verificar(foto, entrega, colunas_novas=manifesto["colunas_novas"],
                                   abas_novas=set(manifesto["abas_criadas"]))
    else:
        integridade = pl.verificar(foto, lv.resolver(raiz, planilha["recebida"]))
    erros += [f"planilha recebida: {e}" for e in integridade["erros"]]
    if integridade["total_erros"] > len(integridade["erros"]):
        erros.append(f"planilha recebida: mais {integridade['total_erros'] - len(integridade['erros'])} diferenças")
    avisos += integridade["avisos"]
    _cobertura(dados, foto, erros, avisos)

    contagem = dict.fromkeys(lv.ESTADOS, 0)
    with pl.ler_pasta(entrega) as pasta:
        abas = {a["nome"] for a in pasta.abas}
        recursos = pasta.recursos()["por_aba"]
        cache_abas = {}

        def celulas(aba):
            if aba not in cache_abas:
                cache_abas[aba] = pasta.ler(aba) if aba in abas else {}
            return cache_abas[aba]

        for item in dados.get("itens") or []:
            chave = item["chave"]
            registro = manifesto["itens"].get(chave)
            rotulo = f"item {item['id']} ({chave})"
            if not registro:
                erros.append(f"{rotulo}: não aparece no manifesto da entrega")
                continue
            esperado = lv.calcular_item(item)
            contagem[esperado["estado"]] += 1
            memoria, principal = registro["memoria"], celulas(registro["aba"])
            ref_qtd, ref_estado = registro["celulas"]["qtd"], registro["celulas"]["estado"]
            for ref, formula in ((ref_qtd, gp.formula_qtd(memoria)), (ref_estado, gp.formula_estado(memoria))):
                atual = principal.get(ref)
                if atual is None or atual.formula is None:
                    erros.append(f"{registro['aba']}!{ref}: fórmula ausente ({rotulo})")
                    continue
                if "IFERROR" in atual.formula.upper() or "SEERRO" in atual.formula.upper():
                    erros.append(f"{registro['aba']}!{ref}: usa IFERROR/SEERRO ({rotulo})")
                if pl.normalizar_formula(atual.formula) != pl.normalizar_formula(formula):
                    erros.append(f"{registro['aba']}!{ref}: fórmula {atual.formula} difere da esperada {formula[1:]} "
                                 f"({rotulo})")
            if not _igual(esperado["total"], principal.get(ref_qtd)):
                erros.append(f"{registro['aba']}!{ref_qtd}: valor gravado difere de {esperado['total']} ({rotulo})")
            if not _igual(esperado["estado"], principal.get(ref_estado)):
                erros.append(f"{registro['aba']}!{ref_estado}: estado gravado difere de {esperado['estado']} ({rotulo})")

            if memoria not in abas:
                erros.append(f"{rotulo}: aba de memória {memoria} inexistente")
                continue
            mem = celulas(memoria)
            parcelas = item.get("parcelas") or []
            formulas = gp.formulas_resultado(len(parcelas))
            valores = {"G8": esperado["total"], "G9": esperado["estado"], "G10": esperado["subtotal"],
                       "G12": esperado["faltantes"]}
            for ref, formula in formulas.items():
                atual = mem.get(ref)
                if atual is None or pl.normalizar_formula(atual.formula) != pl.normalizar_formula(formula):
                    erros.append(f"{memoria}!{ref}: fórmula diferente do esquema ({rotulo})")
                elif not _igual(valores[ref], atual):
                    erros.append(f"{memoria}!{ref}: valor gravado {atual.valor!r} difere de {valores[ref]!r} ({rotulo})")
            if not _igual(item["estado"], mem.get("G13")):
                erros.append(f"{memoria}!G13: estado declarado difere do levantamento.json ({rotulo})")
            for deslocamento, parcela in enumerate(parcelas):
                linha = gp.PRIMEIRA_PARCELA + deslocamento
                entradas = ([(f"{c}{linha}", v) for c, v in zip("EFG", parcela["dimensoes"])]
                            if parcela.get("dimensoes") is not None else [(f"H{linha}", parcela.get("valor"))])
                for ref, valor in entradas:
                    atual = mem.get(ref)
                    if valor is None:
                        if atual is not None and atual.valor not in (None, ""):
                            erros.append(f"{memoria}!{ref}: deveria estar vazio ({rotulo})")
                    elif atual is None or atual.tipo != "n" or not _igual(valor, atual):
                        erros.append(f"{memoria}!{ref}: esperado o número {valor} ({rotulo})")
                if not _igual(esperado["valores"][deslocamento], mem.get(f"K{linha}")):
                    erros.append(f"{memoria}!K{linha}: resultado da parcela difere ({rotulo})")
            fisico = item["natureza"] == "medivel" and item["estado"] in ("CONFIRMADO", "PREMISSA", "SUBTOTAL")
            imagens = recursos.get(memoria, {}).get("imagens", 0)
            esperadas = sum(1 for ev in item.get("evidencias") or []
                            if Path(ev["arquivo"]).suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif",
                                                                      ".tif", ".tiff", ".webp"))
            if fisico and not item.get("sem_representacao_grafica") and imagens < max(1, esperadas):
                erros.append(f"{memoria}: {imagens} imagem(ns) incorporada(s), esperado {max(1, esperadas)} ({rotulo})")

    recalculo = "não executado"
    if recalculado:
        recalculo = "executado"
        with pl.ler_pasta(recalculado) as outra:
            nomes = {a["nome"] for a in outra.abas}
            lidas = {}
            for item in dados.get("itens") or []:
                registro = manifesto["itens"].get(item["chave"])
                if not registro:
                    continue
                esperado = lv.calcular_item(item)
                verificacoes = [(registro["aba"], registro["celulas"]["qtd"], esperado["total"]),
                                (registro["aba"], registro["celulas"]["estado"], esperado["estado"]),
                                (registro["memoria"], "G8", esperado["total"]),
                                (registro["memoria"], "G9", esperado["estado"]),
                                (registro["memoria"], "G10", esperado["subtotal"]),
                                (registro["memoria"], "G12", esperado["faltantes"])]
                for aba, ref, valor in verificacoes:
                    if aba not in nomes:
                        erros.append(f"recálculo: aba {aba} ausente no arquivo recalculado")
                        continue
                    if aba not in lidas:
                        lidas[aba] = outra.ler(aba)
                    if not _igual(valor, lidas[aba].get(ref)):
                        atual = lidas[aba].get(ref)
                        erros.append(f"recálculo independente: {aba}!{ref} = {getattr(atual, 'valor', None)!r}, "
                                     f"esperado {valor!r}")
    else:
        avisos.append("recálculo independente não executado (rode recalcular.py e passe --recalculado)")

    tamanho = entrega.stat().st_size / 1e6
    if tamanho > limite_mb:
        avisos.append(f"entrega com {tamanho:.1f} MB (limite sugerido {limite_mb:.0f} MB)")
    resumo = {"entrega": str(entrega), "modo": manifesto["modo"], "itens": len(dados.get("itens") or []),
              "por_estado": contagem, "imagens": manifesto.get("imagens", 0), "tamanho_mb": round(tamanho, 2),
              "recalculo": recalculo}
    return {"ok": not erros, "erros": erros, "avisos": avisos, "resumo": resumo}


def relatorio_markdown(relatorio):
    r = relatorio["resumo"]
    linhas = [f"# Validação da entrega — {'OK' if relatorio['ok'] else 'COM ERROS'}", ""]
    for chave in ("entrega", "modo", "itens", "imagens", "tamanho_mb", "recalculo"):
        if chave in r:
            linhas.append(f"- **{chave}:** {r[chave]}")
    if r.get("por_estado"):
        linhas.append("- **por estado:** " + ", ".join(f"{k} {v}" for k, v in r["por_estado"].items()))
    linhas += ["", f"## Erros ({len(relatorio['erros'])})", ""] + [f"- {e}" for e in relatorio["erros"]]
    linhas += ["", f"## Avisos ({len(relatorio['avisos'])})", ""] + [f"- {a}" for a in relatorio["avisos"]]
    return "\n".join(linhas) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--levantamento", required=True)
    parser.add_argument("--recalculado", help="cópia recalculada pelo recalcular.py")
    parser.add_argument("--saida", help="relatório JSON (padrão: conferencia/validacao.json)")
    parser.add_argument("--limite-mb", type=float, default=25.0)
    parser.add_argument("--sem-hash-fontes", action="store_true",
                        help="não reconferir o hash dos originais (projetos muito grandes)")
    a = parser.parse_args()
    relatorio = validar_entrega(a.levantamento, a.recalculado, a.limite_mb, not a.sem_hash_fontes)
    _, raiz = lv.carregar(a.levantamento)
    saida = Path(a.saida) if a.saida else raiz / "conferencia" / "validacao.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    saida.with_suffix(".md").write_text(relatorio_markdown(relatorio), encoding="utf-8")
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    sys.exit(0 if relatorio["ok"] else 1)


if __name__ == "__main__":
    main()
