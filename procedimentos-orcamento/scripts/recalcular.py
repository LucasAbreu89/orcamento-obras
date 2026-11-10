#!/usr/bin/env python3
"""Recalcula uma planilha no LibreOffice e grava uma cópia em XLSX.

Serve de verificação independente das fórmulas (validar_entrega.py --recalculado) e de
conversão de XLS, ODS ou CSV para XLSX. O LibreOffice roda sem interface, com um perfil
temporário configurado para recalcular tudo ao abrir; o perfil do usuário e o arquivo
de entrada não são tocados.

  python3 recalcular.py planilha/entrega.xlsx --saida conferencia/recalculado.xlsx
  python3 recalcular.py servicos.xls --saida planilha/servicos_TRABALHO.xlsx
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATOS = (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "C:/Program Files/LibreOffice/program/soffice.exe",
    "C:/Program Files (x86)/LibreOffice/program/soffice.exe",
    "/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice", "/opt/libreoffice/program/soffice",
)
REGISTRO = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""


def localizar_soffice():
    for candidato in (os.environ.get("SOFFICE"), shutil.which("soffice"), shutil.which("libreoffice"), *CANDIDATOS):
        if candidato and Path(candidato).exists():
            return str(candidato)
    return None


def converter(entrada, saida, tempo_limite=600, formato="xlsx"):
    """Abre no LibreOffice (recalculando tudo) e grava em XLSX (ou PDF) no caminho de saída."""
    soffice = localizar_soffice()
    if not soffice:
        raise RuntimeError("LibreOffice não encontrado; instale-o ou defina a variável SOFFICE.")
    entrada, saida = Path(entrada).resolve(), Path(saida).resolve()
    if entrada == saida:
        raise ValueError("a saída precisa ser outro arquivo")
    if not entrada.is_file():
        raise FileNotFoundError(f"arquivo não encontrado: {entrada}")
    with tempfile.TemporaryDirectory() as perfil, tempfile.TemporaryDirectory() as destino:
        usuario = Path(perfil) / "user"
        usuario.mkdir()
        (usuario / "registrymodifications.xcu").write_text(REGISTRO, encoding="utf-8")
        filtro = "pdf:calc_pdf_Export" if formato == "pdf" else "xlsx:Calc MS Excel 2007 XML"
        comando = [soffice, f"-env:UserInstallation={Path(perfil).as_uri()}", "--headless", "--norestore",
                   "--nologo", "--nodefault", "--convert-to", filtro, "--outdir", destino, str(entrada)]
        processo = subprocess.run(comando, capture_output=True, text=True, timeout=tempo_limite)
        gerado = Path(destino) / f"{entrada.stem}.{formato}"
        if processo.returncode != 0 or not gerado.exists():
            raise RuntimeError("LibreOffice não converteu o arquivo: "
                               + (processo.stderr.strip() or processo.stdout.strip() or "sem mensagem"))
        saida.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(gerado), saida)
    return saida


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entrada")
    parser.add_argument("--saida", required=True, help="cópia recalculada em XLSX")
    parser.add_argument("--pdf", help="também exporta a planilha em PDF (caderno de memórias)")
    a = parser.parse_args()
    try:
        saida = converter(a.entrada, a.saida)
        if a.pdf:
            converter(a.entrada, a.pdf, formato="pdf")
    except (RuntimeError, ValueError, FileNotFoundError, subprocess.TimeoutExpired) as erro:
        print(json.dumps({"ok": False, "erro": str(erro)}, ensure_ascii=False))
        sys.exit(1)
    import planilha as pl
    with pl.ler_pasta(saida) as pasta:
        formulas = [c for aba in pasta.abas for c in pasta.ler(aba["nome"]).values() if c.formula is not None]
    print(json.dumps({"ok": True, "saida": str(saida), "formulas": len(formulas),
                      "formulas_sem_valor": sum(1 for c in formulas if c.valor is None)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
