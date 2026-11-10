#!/usr/bin/env python3
"""Prepara uma execução: pastas, inventário das fontes, cópias e snapshot da planilha, mapa e esqueleto do JSON.

Não lê o conteúdo dos projetos nem calcula quantitativos: todo arquivo começa como
`nao_examinado`. Os originais nunca são alterados nem movidos. XLS, XLSB, ODS e CSV são
convertidos para XLSX com o LibreOffice, quando disponível.

Cria levantamento-orcamento/execucoes/AAAAMMDD_HHMMSS/ com fontes/, dados/, evidencias/,
planilha/ e conferencia/.
"""

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

SUBPASTAS = ("fontes", "dados", "evidencias", "planilha", "conferencia")
EXTENSOES = {
    ".pdf", ".dwg", ".dxf", ".ifc", ".ifczip", ".rvt", ".rfa", ".nwd", ".nwc", ".skp",
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".ods", ".csv", ".tsv",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".doc", ".docx",
    ".txt", ".md", ".zip", ".rar", ".7z",
}
PLANILHAS_DIRETAS = {".xlsx", ".xlsm"}
PLANILHAS_CONVERTIDAS = {".xls", ".xlsb", ".ods", ".csv", ".tsv"}
IGNORAR = {".git", ".agents", ".codex", ".beads", "node_modules", "__pycache__", ".venv", "venv"}


def sha256(caminho):
    resultado = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            resultado.update(bloco)
    return resultado.hexdigest()


def relativo(caminho, base):
    try:
        return str(caminho.relative_to(base))
    except ValueError:
        return str(caminho)


def dentro(caminho, base):
    return caminho == base or base in caminho.parents


def dados_fonte(caminho, projeto):
    registro = {"caminho": str(caminho), "relativo_ao_projeto": relativo(caminho, projeto),
                "extensao": caminho.suffix.lower(), "leitura": "nao_examinado"}
    try:
        antes = caminho.stat()
        registro.update(tamanho_bytes=antes.st_size, mtime_ns=antes.st_mtime_ns, sha256=sha256(caminho))
        depois = caminho.stat()
        if (antes.st_size, antes.st_mtime_ns) != (depois.st_size, depois.st_mtime_ns):
            registro["alerta"] = "Arquivo mudou durante o inventário; conferir e gerar nova identidade."
    except OSError as erro:
        registro["erro_acesso"] = str(erro)
    return registro


def criar_execucao(projeto, destino):
    if destino is not None:
        destino = destino.expanduser().resolve()
        if destino == projeto or dentro(projeto, destino):
            raise ValueError("A saída deve ser uma pasta nova, sem conter a pasta de origem.")
        destino.mkdir(parents=True, exist_ok=False)
        return destino
    pai = projeto / "levantamento-orcamento" / "execucoes"
    for caminho in (projeto / "levantamento-orcamento", pai):
        if caminho.is_symlink():
            raise ValueError("A saída padrão usa link simbólico; indique --saida explicitamente.")
    pai.mkdir(parents=True, exist_ok=True)
    nome = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    numero = 0
    while True:
        candidato = pai / (nome if numero == 0 else f"{nome}_{numero:02d}")
        try:
            candidato.mkdir()
            return candidato
        except FileExistsError:
            numero += 1


def inventariar(projeto, destino):
    execucoes = projeto / "levantamento-orcamento"
    fontes, exclusoes, alertas = [], [], []

    def falha_percurso(erro):
        alertas.append({"natureza": "acesso_ao_inventario", "caminho": erro.filename, "motivo": str(erro)})

    for raiz, pastas, arquivos in os.walk(projeto, followlinks=False, onerror=falha_percurso):
        raiz = Path(raiz)
        for nome in list(pastas):
            caminho = raiz / nome
            motivo = None
            if caminho.is_symlink():
                motivo = "link_simbolico_nao_percorrido"
            elif nome in IGNORAR:
                motivo = "diretorio_de_sistema_ou_dependencias"
            elif dentro(caminho, destino) or caminho == execucoes:
                motivo = "execucoes_derivadas; consultar separadamente se forem fontes autorizadas"
            if motivo:
                pastas.remove(nome)
                exclusoes.append({"caminho": relativo(caminho, projeto), "motivo": motivo})
        for nome in sorted(arquivos):
            caminho = raiz / nome
            if caminho.is_symlink():
                exclusoes.append({"caminho": relativo(caminho, projeto), "motivo": "arquivo_link_simbolico_nao_lido"})
            elif not caminho.is_file():
                exclusoes.append({"caminho": relativo(caminho, projeto), "motivo": "nao_e_arquivo_regular"})
            elif caminho.suffix.lower() in EXTENSOES:
                fontes.append(dados_fonte(caminho, projeto))
    fontes.sort(key=lambda item: item["relativo_ao_projeto"])
    for indice, registro in enumerate(fontes, 1):
        registro["id"] = f"F{indice:03d}"
    return fontes, exclusoes, alertas


def copiar_planilha(indicado, projeto, destino, fontes, alertas):
    """Backup, referência legível em XLSX e cópia de trabalho; devolve os caminhos relativos à execução."""
    original = indicado.expanduser().resolve()
    estado = {"caminho_indicado": str(indicado), "origem_resolvida": str(original)}
    extensao = original.suffix.lower()
    if not original.is_file() or extensao not in PLANILHAS_DIRETAS | PLANILHAS_CONVERTIDAS:
        alertas.append({"natureza": "planilha_indisponivel", "caminho": str(indicado),
                        "motivo": "Conferir caminho e formato; inventário dos demais arquivos preservado."})
        return {**estado, "estado": "indisponivel_ou_formato_nao_reconhecido"}, None
    registro = next((item for item in fontes if item["caminho"] == str(original)), None)
    if registro is None:
        registro = dados_fonte(original, projeto)
        registro["id"] = f"F{len(fontes) + 1:03d}"
        registro["fornecido_explicitamente"] = True
        fontes.append(registro)
    pasta = destino / "planilha"
    backup = pasta / f"ORIGINAL_{original.name}"
    shutil.copy2(original, backup)
    if sha256(backup) != registro.get("sha256"):
        alertas.append({"natureza": "identidade_das_copias", "motivo": "Hash do backup difere da origem."})
    if extensao in PLANILHAS_DIRETAS:
        recebida, trabalho = backup, pasta / f"{original.stem}_TRABALHO{extensao}"
        shutil.copy2(backup, trabalho)
        situacao = "copias_identicas_a_origem" if sha256(trabalho) == sha256(backup) else "conferir_copias"
    else:
        from recalcular import converter
        recebida = pasta / f"{original.stem}_RECEBIDA_CONVERTIDA.xlsx"
        try:
            converter(backup, recebida)
        except Exception as erro:  # noqa: BLE001 - sem LibreOffice, registrar e seguir com o inventário
            alertas.append({"natureza": "conversao_planilha", "motivo": f"{erro}; converter para XLSX e repetir."})
            return {**estado, "estado": "conversao_necessaria", "backup": str(backup)}, None
        trabalho = pasta / f"{original.stem}_TRABALHO.xlsx"
        shutil.copy2(recebida, trabalho)
        situacao = "convertida_para_xlsx_pelo_libreoffice"
    return {**estado, "estado": situacao, "backup": str(backup), "recebida": str(recebida),
            "trabalho": str(trabalho)}, (recebida, trabalho, backup)


def esqueleto(destino, projeto, fontes, copias, mapa):
    listas, ocultas = [], []
    for aba in (mapa or {}).get("abas", []):
        cabecalho = aba.get("cabecalho")
        if not (cabecalho and aba.get("itens_provaveis")):
            continue
        if aba.get("estado", "visible") != "visible":
            ocultas.append(aba["nome"])
            continue
        colunas = dict(cabecalho["colunas"])
        quantidades = colunas.get("quantidade") or []
        quantidades = quantidades if isinstance(quantidades, list) else [quantidades]
        colunas["quantidade"] = quantidades[0] if len(quantidades) == 1 else None
        registro = {"aba": aba["nome"], "linha_cabecalho": cabecalho["linha"],
                    "colunas": {k: colunas.get(k) for k in ("item", "descricao", "unidade", "quantidade")}}
        if len(quantidades) > 1:
            registro["_quantidades_candidatas"] = quantidades
        listas.append(registro)
    planilha = {"listas": listas, "modo": "auto"}
    if ocultas:
        planilha["_listas_ocultas_detectadas"] = ocultas
    if copias:
        recebida, trabalho, backup = copias
        rel = lambda caminho: relativo(caminho, destino)  # noqa: E731
        stem = trabalho.name.replace("_TRABALHO", "_LEVANTAMENTO")
        planilha.update(recebida=rel(recebida), trabalho=rel(trabalho), entrega=f"planilha/{stem}",
                        snapshot="fontes/snapshot_planilha.json.gz")
        if recebida != backup:
            planilha["recebida_original"] = rel(backup)
    return {
        "versao": "levantamento/1", "obra": projeto.name, "planilha": planilha,
        "_observacao": "Listas sugeridas pelo mapa da planilha (só abas visíveis); confirmar no checkpoint de escopo. "
                       "Com mais de uma coluna de quantidade, escolher pelo cabeçalho e pela fórmula.",
        "criterios": [],
        "fontes": [{"id": f["id"], "arquivo": f["relativo_ao_projeto"], "revisao": None, "sha256": f.get("sha256"),
                    "representacoes": []} for f in fontes],
        "premissas": [], "pendencias": [], "itens": [],
    }


def preparar(projeto, planilha=None, saida=None):
    projeto = projeto.expanduser().resolve()
    if not projeto.is_dir():
        raise ValueError("A pasta de projetos não existe ou não é uma pasta.")
    destino = criar_execucao(projeto, saida)
    for nome in SUBPASTAS:
        (destino / nome).mkdir()
    fontes, exclusoes, alertas = inventariar(projeto, destino)
    estado_planilha, copias, mapa = {"estado": "nao_fornecida"}, None, None
    if planilha is None:
        alertas.append({"natureza": "planilha_ausente", "motivo": "Continuar o catálogo; falta indicar a planilha de serviços."})
    else:
        estado_planilha, copias = copiar_planilha(planilha, projeto, destino, fontes, alertas)
    if copias:
        import planilha as pl
        recebida, trabalho, _ = copias
        pl.salvar_snapshot(pl.snapshot(recebida), destino / "fontes" / "snapshot_planilha.json.gz")
        mapa = pl.mapear(trabalho)
        (destino / "fontes" / "mapa_planilha.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=2) + "\n",
                                                               encoding="utf-8")
        (destino / "fontes" / "mapa_planilha.md").write_text(pl.mapa_markdown(mapa), encoding="utf-8")
        if mapa["riscos_de_gravacao"]:
            alertas.append({"natureza": "recursos_da_planilha", "motivo": "A planilha tem recursos que a gravação "
                            "perderia; a entrega irá para arquivo separado: " + "; ".join(mapa["riscos_de_gravacao"])})
    duplicatas = {}
    for registro in fontes:
        if registro.get("sha256"):
            duplicatas.setdefault(registro["sha256"], []).append(registro["id"])
        if registro.get("erro_acesso") or registro.get("alerta"):
            alertas.append({"natureza": "fonte_a_conferir", "fonte_id": registro["id"],
                            "motivo": registro.get("erro_acesso") or registro["alerta"]})
    manifesto = {
        "schema": "preparacao-levantamento/2", "criado_em": datetime.now().astimezone().isoformat(),
        "projeto": str(projeto), "execucao": str(destino),
        "alcance": "Somente inventário e cópias. Projetos não examinados e nenhum quantitativo calculado.",
        "planilha": estado_planilha, "fontes": fontes, "exclusoes": exclusoes,
        "duplicatas_exatas": [ids for ids in duplicatas.values() if len(ids) > 1], "alertas_tecnicos": alertas,
    }
    (destino / "fontes" / "inventario.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
                                                        encoding="utf-8")
    from ambiente import diagnosticar
    (destino / "fontes" / "ambiente.json").write_text(json.dumps(diagnosticar(), ensure_ascii=False, indent=2) + "\n",
                                                      encoding="utf-8")
    levantamento = destino / "dados" / "levantamento.json"
    levantamento.write_text(json.dumps(esqueleto(destino, projeto, fontes, copias, mapa), ensure_ascii=False, indent=2)
                            + "\n", encoding="utf-8")
    return {"execucao": str(destino), "inventario": str(destino / "fontes" / "inventario.json"),
            "levantamento": str(levantamento), "fontes_listadas": len(fontes), "alertas": len(alertas),
            "planilha": estado_planilha["estado"],
            "listas_sugeridas": [f"{l['aba']} (cabeçalho na linha {l['linha_cabecalho']})"
                                 for l in json.loads(levantamento.read_text(encoding="utf-8"))["planilha"]["listas"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--projeto", type=Path, required=True, help="Pasta da obra; originais não são alterados.")
    parser.add_argument("--planilha", type=Path, help="Planilha de serviços recebida (opcional para só inventariar).")
    parser.add_argument("--saida", type=Path, help="Pasta nova da execução; não pode existir.")
    args = parser.parse_args()
    try:
        resultado = preparar(args.projeto, args.planilha, args.saida)
    except (OSError, ValueError) as erro:
        parser.exit(2, f"Preparação não concluída: {erro}\n")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
