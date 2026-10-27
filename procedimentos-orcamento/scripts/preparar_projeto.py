#!/usr/bin/env python3
"""Prepara fontes e cópias de trabalho; não lê projetos nem calcula quantitativos."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from datetime import datetime


SUBPASTAS = (
    "01_catalogo", "02_bases_ambientes", "03_memorias_servicos", "04_evidencias",
    "05_planilhas", "06_conferencia", "07_backups", "08_dados_tecnicos",
)
EXTENSOES = {
    ".pdf", ".dwg", ".dxf", ".ifc", ".ifczip", ".rvt", ".rfa", ".nwd", ".nwc",
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".ods", ".csv", ".tsv",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".doc", ".docx",
    ".txt", ".md", ".zip", ".rar", ".7z",
}
PLANILHAS = {".xlsx", ".xls", ".xlsm", ".xlsb", ".ods", ".csv", ".tsv"}
IGNORAR = {".git", ".agents", ".codex", ".beads", ".aws", "node_modules", "__pycache__", ".venv", "venv"}


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
    registro = {
        "caminho": str(caminho), "relativo_ao_projeto": relativo(caminho, projeto),
        "extensao": caminho.suffix.lower(), "leitura": "nao_examinado",
    }
    try:
        antes = caminho.stat()
        registro.update(tamanho_bytes=antes.st_size, mtime_ns=antes.st_mtime_ns, sha256=sha256(caminho))
        depois = caminho.stat()
        if (antes.st_size, antes.st_mtime_ns) != (depois.st_size, depois.st_mtime_ns):
            registro["alerta"] = "Arquivo mudou durante o inventario; conferir e gerar nova identidade."
    except OSError as erro:
        registro["erro_acesso"] = str(erro)
    return registro


def criar_execucao(projeto, destino):
    if destino is not None:
        destino = destino.expanduser().resolve()
        if destino == projeto or dentro(projeto, destino):
            raise ValueError("A saida deve ser uma pasta nova, sem conter a pasta de origem.")
        destino.mkdir(parents=True, exist_ok=False)
        return destino
    pai = projeto / "levantamento-orcamento" / "execucoes"
    # Evitar redirecionamento inesperado da saida padrao por links simbolicos.
    for caminho in (projeto / "levantamento-orcamento", pai):
        if caminho.is_symlink():
            raise ValueError("A saida padrao usa link simbolico; indique --saida explicitamente.")
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


def preparar(projeto, planilha=None, saida=None):
    projeto = projeto.expanduser().resolve()
    if not projeto.is_dir():
        raise ValueError("A pasta de projetos nao existe ou nao e uma pasta.")
    destino = criar_execucao(projeto, saida)
    for nome in SUBPASTAS:
        (destino / nome).mkdir()
    execucoes = projeto / "levantamento-orcamento" / "execucoes"
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
        registro["id"] = f"F{indice:04d}"

    copias = {"estado": "nao_fornecida", "validacao_de_conteudo": "nao_realizada"}
    if planilha is None:
        alertas.append({"natureza": "planilha_ausente", "motivo": "Continuar catalogo; falta indicar planilha de servicos."})
    else:
        indicado = planilha.expanduser().absolute()
        original = indicado.resolve()
        copias.update(caminho_indicado=str(indicado), origem_resolvida=str(original))
        if not original.is_file() or original.suffix.lower() not in PLANILHAS:
            copias["estado"] = "indisponivel_ou_formato_nao_reconhecido"
            alertas.append({"natureza": "planilha_indisponivel", "caminho": str(indicado), "motivo": "Conferir caminho/formato; inventario dos demais arquivos preservado."})
        else:
            registro = next((item for item in fontes if item["caminho"] == str(original)), None)
            if registro is None:
                registro = dados_fonte(original, projeto)
                registro["id"] = f"F{len(fontes) + 1:04d}"
                registro["fornecido_explicitamente"] = True
                fontes.append(registro)
            backup = destino / "07_backups" / original.name
            trabalho = destino / "05_planilhas" / f"{original.stem}_TRABALHO{original.suffix}"
            try:
                shutil.copy2(original, backup)
                shutil.copy2(backup, trabalho)
                copias.update(backup=str(backup), trabalho=str(trabalho))
                hashes = [registro.get("sha256"), sha256(original), sha256(backup), sha256(trabalho)]
                if len(set(hashes)) == 1 and hashes[0]:
                    copias.update(estado="copias_identicas_a_origem", sha256=hashes[0])
                else:
                    copias["estado"] = "conferir_origem_alterada_ou_falha_de_identidade"
                    alertas.append({"natureza": "identidade_das_copias", "motivo": "Hashes nao coincidem; nao considerar copia de trabalho validada."})
            except OSError as erro:
                copias["estado"] = "falha_na_copia"
                alertas.append({"natureza": "copia_planilha", "motivo": str(erro)})

    duplicatas = {}
    for registro in fontes:
        if registro.get("sha256"):
            duplicatas.setdefault(registro["sha256"], []).append(registro["id"])
        if registro.get("erro_acesso") or registro.get("alerta"):
            alertas.append({"natureza": "fonte_a_conferir", "fonte_id": registro["id"], "motivo": registro.get("erro_acesso") or registro["alerta"]})
    manifesto = {
        "schema": "preparacao-levantamento/1", "criado_em": datetime.now().astimezone().isoformat(),
        "projeto": str(projeto), "execucao": str(destino),
        "alcance": "Somente inventario e copias. Projetos nao examinados, celulas nao lidas e nenhum quantitativo calculado.",
        "planilha": copias, "fontes": fontes, "exclusoes": exclusoes,
        "duplicatas_exatas": [ids for ids in duplicatas.values() if len(ids) > 1],
        "alertas_tecnicos": alertas,
    }
    manifesto_path = destino / "08_dados_tecnicos" / "inventario_preparacao.json"
    manifesto_path.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"execucao": str(destino), "inventario": str(manifesto_path), "fontes_listadas": len(fontes), "alertas": len(alertas), "planilha": copias["estado"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projeto", type=Path, required=True, help="Pasta da obra; originais nao sao alterados.")
    parser.add_argument("--planilha", type=Path, help="Excel/planilha recebida, opcional para iniciar somente o inventario.")
    parser.add_argument("--saida", type=Path, help="Pasta nova da execucao; deve ainda nao existir.")
    args = parser.parse_args()
    try:
        resultado = preparar(args.projeto, args.planilha, args.saida)
    except (OSError, ValueError) as erro:
        parser.exit(2, f"Preparacao nao concluida: {erro}\n")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
