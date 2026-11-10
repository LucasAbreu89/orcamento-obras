#!/usr/bin/env python3
"""Confere as ferramentas disponíveis e indica a rota de leitura de cada formato.

Lista bibliotecas Python, ODA File Converter, LibreOffice e AutoCAD instalados e resume
as rotas possíveis para DWG, PDF, geração da planilha, recálculo e uniões. Não instala
nada. Saída em JSON (stdout e, com --saida, em arquivo).
"""

import argparse
import glob
import importlib
import json
import os
import platform
import shutil
import sys
from pathlib import Path

from recalcular import localizar_soffice

BIBLIOTECAS = {"ezdxf": "ezdxf", "shapely": "shapely", "pymupdf": "pymupdf", "openpyxl": "openpyxl",
               "pillow": "PIL", "matplotlib": "matplotlib"}
OPCIONAIS = {"ifcopenshell": "ifcopenshell"}
REQUISITOS = Path(__file__).resolve().parent / "requirements.txt"
VENV = Path(__file__).resolve().parents[1] / ".venv"
PYTHON_VENV = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _versao(modulo):
    try:
        importado = importlib.import_module(modulo)
    except Exception:  # noqa: BLE001 - qualquer falha de importação conta como ausente
        return None
    return str(getattr(importado, "__version__", getattr(importado, "VersionBind", "instalado")))


def _oda():
    candidatos = ["/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",
                  shutil.which("ODAFileConverter") or ""]
    candidatos += glob.glob("C:/Program Files/ODA/ODAFileConverter*/ODAFileConverter.exe")
    return next((c for c in candidatos if c and Path(c).exists()), None)


def _autocad():
    padroes = ["/Applications/Autodesk/AutoCAD*", "C:/Program Files/Autodesk/AutoCAD*"]
    return sorted(c for padrao in padroes for c in glob.glob(padrao))


def _instrucao(faltando):
    if not faltando:
        return None
    if PYTHON_VENV.exists() and Path(sys.executable).resolve() != PYTHON_VENV.resolve():
        return f"o ambiente virtual (venv) da skill já existe: rode os scripts com {PYTHON_VENV}"
    return (f"criar um ambiente virtual (venv) para a skill: python3 -m venv {VENV} && "
            f"{PYTHON_VENV} -m pip install -r {REQUISITOS}; depois rodar os scripts com {PYTHON_VENV}")


def diagnosticar():
    bibliotecas = {nome: _versao(modulo) for nome, modulo in BIBLIOTECAS.items()}
    opcionais = {nome: _versao(modulo) for nome, modulo in OPCIONAIS.items()}
    programas = {"oda_file_converter": _oda(), "libreoffice": localizar_soffice(), "autocad": _autocad()}
    tem = {nome: versao is not None for nome, versao in bibliotecas.items()}
    if tem["ezdxf"] and programas["oda_file_converter"]:
        dwg = "cad.py converter (ODA) e leitura do DXF por script"
    elif programas["autocad"]:
        dwg = "sem conversor: exportar DXF de uma cópia pelo AutoCAD (computer use) ou pedir DXF/PDF"
    else:
        dwg = "sem conversor nem CAD: pedir DXF ou PDF vetorial ao usuário"
    if not tem["ezdxf"]:
        dwg += "; instalar ezdxf para ler DXF"
    rotas = {
        "dwg": dwg,
        "dxf": "cad.py" if tem["ezdxf"] else "indisponível: instalar ezdxf",
        "prints_cad": "cad.py render" if tem["ezdxf"] and tem["matplotlib"] else "indisponível: instalar ezdxf e matplotlib",
        "pdf": "pdf.py" if tem["pymupdf"] else "indisponível: instalar PyMuPDF (leitura visual continua possível)",
        "planilha_gerar": "gerar_planilha.py" if tem["openpyxl"] and tem["pillow"] else "indisponível: instalar openpyxl e Pillow",
        "planilha_validar": "validar_entrega.py (biblioteca padrão)",
        "recalculo": "recalcular.py (LibreOffice)" if programas["libreoffice"] else "indisponível: registrar recálculo não executado",
        "unioes": "geometria.py uniao" if tem["shapely"] else "indisponível: instalar shapely (calcular por parcelas)",
        "ifc": ("IfcOpenShell instalado: ler quantidades e propriedades do modelo por script próprio"
                if opcionais["ifcopenshell"] else
                "o kit não inclui leitor IFC: usar ferramenta IFC disponível ou pedir DWG/PDF ou quantitativos "
                "exportados do modelo"),
    }
    faltando = [nome for nome, ok in tem.items() if not ok]
    return {
        "python": platform.python_version(), "sistema": platform.platform(), "executavel": sys.executable,
        "bibliotecas": bibliotecas, "opcionais": opcionais, "programas": programas, "rotas": rotas,
        "instalar": _instrucao(faltando),
        "observacao": "Instalação é feita uma vez pelo usuário (ou pelo agente com autorização dele). O agente não "
                      "instala programas nem aceita licenças; ODA File Converter e LibreOffice são instalados pelo "
                      "usuário.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--saida")
    a = parser.parse_args()
    texto = json.dumps(diagnosticar(), ensure_ascii=False, indent=2)
    if a.saida:
        Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
