"""Utilitários comuns aos testes: caminho dos scripts e detecção de bibliotecas opcionais."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def tem(modulo):
    return importlib.util.find_spec(modulo) is not None


def rodar(script, *args, cwd=None):
    """Executa um script do kit com o mesmo interpretador dos testes e devolve o processo."""
    comando = [sys.executable, str(SCRIPTS / script), *map(str, args)]
    return subprocess.run(comando, capture_output=True, text=True, cwd=cwd)


def pixels(imagem):
    """Tuplas RGB de uma imagem Pillow, sem depender de APIs depreciadas."""
    bruto = imagem.convert("RGB").tobytes()
    return (tuple(bruto[i:i + 3]) for i in range(0, len(bruto), 3))


def escrever_json(caminho, dados):
    Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return Path(caminho)
