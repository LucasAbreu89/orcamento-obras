"""Utilitários comuns aos testes: caminho dos scripts, detecção de bibliotecas opcionais e executáveis falsos."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def tem(modulo):
    return importlib.util.find_spec(modulo) is not None


def rodar(script, *args, cwd=None, env=None):
    """Executa um script do kit com o mesmo interpretador dos testes e devolve o processo.

    `env` acrescenta variáveis às do ambiente dos testes."""
    comando = [sys.executable, str(SCRIPTS / script), *map(str, args)]
    return subprocess.run(comando, capture_output=True, text=True, cwd=cwd, env={**os.environ, **env} if env else None)


def pixels(imagem):
    """Tuplas RGB de uma imagem Pillow, sem depender de APIs depreciadas."""
    bruto = imagem.convert("RGB").tobytes()
    return (tuple(bruto[i:i + 3]) for i in range(0, len(bruto), 3))


def escrever_json(caminho, dados):
    Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return Path(caminho)


_ACCORECONSOLE_FALSO = r'''
import json
import sys
import time
from pathlib import Path

DXF = ("  0\nSECTION\n  2\nENTITIES\n  0\nLINE\n  8\n0\n 10\n0.0\n 20\n0.0\n 30\n0.0\n"
       " 11\n1.0\n 21\n1.0\n 31\n0.0\n  0\nENDSEC\n  0\nEOF\n")


def opcao(nome):
    for chave in ("-" + nome, "/" + nome):
        if chave in sys.argv:
            return sys.argv[sys.argv.index(chave) + 1]
    sys.exit("opção ausente: " + nome)


entrada, script = opcao("i"), opcao("s")
linhas = Path(script).read_bytes().decode("cp1252", errors="replace").splitlines()  # como o AutoCAD lê o .scr
with open(REGISTRO, "a", encoding="utf-8") as registro:
    registro.write(json.dumps({"argv": sys.argv[1:], "script": linhas}, ensure_ascii=False) + "\n")
with open(entrada, "ab") as aberto:  # o desenho aberto pode ser alterado: só a cópia pode sofrer isso
    aberto.write(b" alterado")
auditou = "AUDIT" in linhas
if MODO == "trunca_primeira":
    print("Custom object(s) encountered.")
    if auditou:
        print("Total errors found 3 fixed 3")
        print("Erased 1 objects")
sys.stdout.flush()
if MODO == "demora":
    time.sleep(30)
completo = MODO == "ok" or (MODO == "trunca_primeira" and auditou)
saida = linhas[linhas.index("DXFOUT") + 1].strip('"')
try:
    with open(saida, "w", encoding="ascii") as dxf:
        dxf.write(DXF if completo else DXF[:DXF.index("  0\nEOF")])
except OSError:
    print("Can't open file " + saida)
'''


def accoreconsole_falso(pasta, modo="ok"):
    """Executável no lugar do AcCoreConsole: lê o .scr em cp1252 e grava no caminho do DXFOUT um DXF mínimo.

    Modos: `ok`; `trunca_primeira` (DXF sem EOF enquanto o .scr não tiver AUDIT, com mensagens de
    objetos personalizados e do AUDIT); `sempre_trunca`; `demora` (30 s antes de gravar). Cada chamada
    acrescenta argumentos e linhas do .scr a chamadas.jsonl. Devolve (executável, registro)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    registro = pasta / "chamadas.jsonl"
    codigo = pasta / "accoreconsole_falso.py"
    codigo.write_text(f"MODO = {modo!r}\nREGISTRO = {str(registro)!r}\n" + _ACCORECONSOLE_FALSO, encoding="utf-8")
    if os.name == "nt":
        executavel = pasta / "accoreconsole.cmd"
        executavel.write_text(f'@"{sys.executable}" "{codigo}" %*\n', encoding="utf-8")
    else:
        executavel = pasta / "AcCoreConsole"
        executavel.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{codigo}" "$@"\n', encoding="utf-8")
        executavel.chmod(0o755)
    return executavel, registro


def chamadas(registro):
    """Chamadas recebidas pelo executável falso, na ordem."""
    registro = Path(registro)
    if not registro.is_file():
        return []
    return [json.loads(linha) for linha in registro.read_text(encoding="utf-8").splitlines()]
