"""Conversão DWG → DXF pelo AcCoreConsole do AutoCAD, com um executável falso no lugar dele."""

import contextlib
import hashlib
import io
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from apoio import accoreconsole_falso, chamadas, rodar, tem

import ambiente
import cad

ROTEIRO_2018 = ["FILEDIA", "0", "DXFOUT", "<saida>", "V", "2018", "16", "QUIT", "Y"]
ROTEIRO_AUDIT_2013 = ["FILEDIA", "0", "AUDIT", "Y", "DXFOUT", "<saida>", "V", "2013", "16", "QUIT", "Y"]


def sha(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def roteiro(chamada):
    """Linhas do .scr recebido, com o caminho do DXF (entre aspas) trocado por <saida>."""
    return ["<saida>" if linha.startswith('"') else linha for linha in chamada["script"]]


def opcao(chamada, nome):
    argv = chamada["argv"]
    chave = next(c for c in ("-" + nome, "/" + nome) if c in argv)
    return argv[argv.index(chave) + 1]


def termina_com_eof(caminho):
    return Path(caminho).read_text(encoding="ascii").split()[-2:] == ["0", "EOF"]


class ConversaoAcCoreConsole(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.projetos = self.dir / "projetos"
        self.projetos.mkdir()
        self.dwg = self.projetos / "ARQ-01.dwg"
        self.dwg.write_bytes(b"AC1032 desenho sintetico")
        self.saida = self.dir / "dxf"

    def tearDown(self):
        self.pasta.cleanup()

    def converter(self, modo, *opcoes, entrada=None, env=None):
        falso, registro = accoreconsole_falso(self.dir / "falso", modo)
        processo = rodar("cad.py", "converter", entrada or self.projetos, "--saida", self.saida,
                         "--via", "accoreconsole", *opcoes, env={"ACCORECONSOLE": str(falso), **(env or {})})
        self.assertEqual(processo.returncode, 0, processo.stderr)
        return json.loads(processo.stdout), chamadas(registro)

    def manifesto(self):
        return json.loads((self.saida / "conversao_dxf.json").read_text(encoding="utf-8"))

    def test_converte_uma_copia_e_registra_hashes_no_manifesto(self):
        original = sha(self.dwg)
        resultado, feitas = self.converter("ok")
        destino = self.saida / "ARQ-01.dxf"
        [chamada] = feitas
        self.assertEqual(roteiro(chamada), ROTEIRO_2018)
        self.assertEqual(opcao(chamada, "l"), "en-US")
        copia = Path(opcao(chamada, "i"))
        self.assertNotEqual(copia.resolve(), self.dwg.resolve())
        self.assertFalse(copia.parent.exists(), "a pasta temporária da cópia ficou para trás")
        self.assertEqual(sha(self.dwg), original, "o falso altera o desenho que abre; o original não pode mudar")
        self.assertTrue(termina_com_eof(destino))
        manifesto = self.manifesto()
        self.assertEqual(manifesto["falhas"], [])
        [registro] = manifesto["convertidos"]
        self.assertEqual(Path(registro["dwg"]), self.dwg.resolve())
        self.assertEqual(Path(registro["dxf"]), destino.resolve())
        self.assertEqual(registro["sha256_dwg"], original)
        self.assertEqual(registro["sha256_dxf"], sha(destino))
        self.assertIn("AcCoreConsole", registro["ferramenta"])
        self.assertEqual(registro["tentativas"], 1)
        self.assertEqual(registro["falhas_tentativas"], [])
        self.assertNotIn("alertas", registro)
        self.assertEqual(resultado["convertidos"], manifesto["convertidos"])

    def test_caminhos_com_acento_passam_por_pasta_ascii(self):
        pasta = self.projetos / "BASE PRÉDIO"
        pasta.mkdir()
        (pasta / "CLIMATIZAÇÃO 16º PAVTO.dwg").write_bytes(b"AC1032 outro desenho")
        temporaria = self.dir / "temporária do usuário"
        temporaria.mkdir()
        self.saida = self.dir / "saída DXF"
        resultado, feitas = self.converter("ok", env={"TMPDIR": str(temporaria), "TEMP": str(temporaria),
                                                      "TMP": str(temporaria)})
        acentuado = self.saida / "BASE PRÉDIO" / "CLIMATIZAÇÃO 16º PAVTO.dxf"
        self.assertEqual(resultado["falhas"], [])
        self.assertEqual({Path(r["dxf"]) for r in resultado["convertidos"]},
                         {(self.saida / "ARQ-01.dxf").resolve(), acentuado.resolve()})
        self.assertTrue(termina_com_eof(acentuado))
        self.assertEqual(len(feitas), 2)
        for chamada in feitas:
            self.assertTrue(opcao(chamada, "i").isascii(), chamada)
            self.assertTrue(opcao(chamada, "s").isascii(), chamada)
            self.assertTrue(all(linha.isascii() for linha in chamada["script"]), chamada)

    def test_dxf_truncado_refaz_com_audit_e_versao_2013(self):
        resultado, feitas = self.converter("trunca_primeira")
        self.assertEqual([roteiro(c) for c in feitas], [ROTEIRO_2018, ROTEIRO_AUDIT_2013])
        [registro] = resultado["convertidos"]
        self.assertEqual((registro["tentativas"], registro["versao_dxf"], registro["audit"]), (2, "2013", True))
        [falha] = registro["falhas_tentativas"]
        self.assertEqual((falha["tentativa"], falha["versao_dxf"], falha["audit"]), (1, "2018", False))
        self.assertIn("EOF", falha["erro"])
        self.assertTrue(termina_com_eof(self.saida / "ARQ-01.dxf"))
        self.assertEqual(registro["sha256_dxf"], sha(self.saida / "ARQ-01.dxf"))
        self.assertEqual(registro["auditoria"], {"erros": 3, "corrigidos": 3, "apagados": 1})
        self.assertEqual(len(registro["alertas"]), 2, "objetos personalizados e objetos apagados pelo AUDIT")

    def test_duas_tentativas_sem_dxf_completo_viram_falha(self):
        resultado, feitas = self.converter("sempre_trunca")
        self.assertEqual([roteiro(c) for c in feitas], [ROTEIRO_2018, ROTEIRO_AUDIT_2013])
        self.assertEqual(resultado["convertidos"], [])
        [falha] = resultado["falhas"]
        self.assertEqual(falha["tentativas"], 2)
        self.assertEqual([(f["versao_dxf"], f["audit"]) for f in falha["falhas_tentativas"]],
                         [("2018", False), ("2013", True)])
        self.assertEqual(falha["sha256_dwg"], sha(self.dwg))
        self.assertFalse((self.saida / "ARQ-01.dxf").exists(), "DXF truncado não pode chegar ao destino")
        self.assertEqual(self.manifesto()["falhas"], resultado["falhas"])

    @unittest.skipIf(os.name == "nt", "o .cmd do falso não repassa o encerramento ao Python")
    def test_tempo_esgotado_registra_falha_sem_esperar_o_programa(self):
        inicio = time.monotonic()
        resultado, feitas = self.converter("demora", "--tempo-limite", "1")
        self.assertLess(time.monotonic() - inicio, 20)
        self.assertEqual(len(feitas), 1, "tempo esgotado pede --tempo-limite maior, não AUDIT")
        [falha] = resultado["falhas"]
        [tentativa] = falha["falhas_tentativas"]
        self.assertIn("tempo", tentativa["erro"])

    def test_versao_pedida_vai_para_o_dxfout(self):
        _, feitas = self.converter("ok", "--versao", "R2010")
        self.assertEqual(roteiro(feitas[0]), ["FILEDIA", "0", "DXFOUT", "<saida>", "V", "2010", "16", "QUIT", "Y"])
        falso, registro = accoreconsole_falso(self.dir / "falso_r14", "ok")
        processo = rodar("cad.py", "converter", self.projetos, "--saida", self.saida, "--via", "accoreconsole",
                         "--versao", "R14", env={"ACCORECONSOLE": str(falso)})
        self.assertNotEqual(processo.returncode, 0)
        self.assertEqual(chamadas(registro), [])

    def test_manifesto_acumula_rodadas_e_troca_falha_por_conversao(self):
        self.converter("sempre_trunca", entrada=self.dwg)
        self.assertEqual(len(self.manifesto()["falhas"]), 1)
        self.converter("ok", entrada=self.dwg)
        outro = self.dir / "outros" / "EST-01.dwg"
        outro.parent.mkdir()
        outro.write_bytes(b"AC1032 estrutura")
        self.converter("ok", entrada=outro)
        self.converter("ok", entrada=outro)
        manifesto = self.manifesto()
        self.assertEqual(manifesto["falhas"], [])
        self.assertEqual(sorted(Path(r["dxf"]).name for r in manifesto["convertidos"]), ["ARQ-01.dxf", "EST-01.dxf"])

    def test_destino_igual_ao_original_nao_e_gravado(self):
        planta = self.projetos / "planta.dxf"
        planta.write_text("conteúdo original", encoding="utf-8")
        falso, registro = accoreconsole_falso(self.dir / "falso", "ok")
        processo = rodar("cad.py", "converter", planta, "--saida", self.projetos, "--via", "accoreconsole",
                         env={"ACCORECONSOLE": str(falso)})
        self.assertEqual(processo.returncode, 0, processo.stderr)
        resultado = json.loads(processo.stdout)
        self.assertEqual(resultado["convertidos"], [])
        self.assertEqual(len(resultado["falhas"]), 1)
        self.assertEqual(planta.read_text(encoding="utf-8"), "conteúdo original")
        self.assertEqual(chamadas(registro), [])


class EscolhaDoConversor(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.dwg = self.dir / "ARQ-01.dwg"
        self.dwg.write_bytes(b"AC1032 desenho sintetico")

    def tearDown(self):
        self.pasta.cleanup()

    def sem_oda(self):
        if not tem("ezdxf"):
            return contextlib.nullcontext()  # sem ezdxf, a rota ODA já é indisponível
        return mock.patch("ezdxf.addons.odafc.is_installed", return_value=False)

    def test_sem_oda_converte_pelo_accoreconsole(self):
        falso, registro = accoreconsole_falso(self.dir / "falso")
        with self.sem_oda(), mock.patch.dict(os.environ, {"ACCORECONSOLE": str(falso)}), \
                contextlib.redirect_stderr(io.StringIO()):
            resultado = cad.converter(self.dwg, self.dir / "dxf")
        self.assertEqual(len(chamadas(registro)), 1)
        [registro_dxf] = resultado["convertidos"]
        self.assertIn("AcCoreConsole", registro_dxf["ferramenta"])

    @unittest.skipUnless(tem("ezdxf"), "ezdxf não instalado")
    def test_oda_instalado_tem_preferencia(self):
        def oda(origem, destino, **_):
            Path(destino).write_text("  0\nEOF\n", encoding="ascii")

        falso, registro = accoreconsole_falso(self.dir / "falso")
        with mock.patch("ezdxf.addons.odafc.is_installed", return_value=True), \
                mock.patch("ezdxf.addons.odafc.convert", side_effect=oda), \
                mock.patch.dict(os.environ, {"ACCORECONSOLE": str(falso)}), contextlib.redirect_stderr(io.StringIO()):
            resultado = cad.converter(self.dwg, self.dir / "dxf")
        self.assertEqual(chamadas(registro), [])
        [registro_dxf] = resultado["convertidos"]
        self.assertEqual(registro_dxf["ferramenta"], "ODA File Converter")
        self.assertEqual(registro_dxf["sha256_dwg"], sha(self.dwg))
        self.assertEqual(registro_dxf["sha256_dxf"], sha(self.dir / "dxf" / "ARQ-01.dxf"))

    def test_sem_conversor_explica_as_rotas(self):
        with self.sem_oda(), mock.patch.object(cad, "localizar_accoreconsole", return_value=None):
            with self.assertRaises(SystemExit) as saida:
                cad.converter(self.dwg, self.dir / "dxf")
        mensagem = str(saida.exception.code)
        for termo in ("ODA", "AcCoreConsole", "DXF"):
            self.assertIn(termo, mensagem)


class RotaDwgNoAmbiente(unittest.TestCase):
    def test_sem_oda_indica_o_accoreconsole(self):
        with tempfile.TemporaryDirectory() as pasta:
            falso, _ = accoreconsole_falso(pasta)
            with mock.patch.dict(os.environ, {"ACCORECONSOLE": str(falso)}), \
                    mock.patch.object(ambiente, "_oda", return_value=None):
                dados = ambiente.diagnosticar()
        self.assertEqual(dados["programas"]["accoreconsole"], str(falso))
        self.assertIn("AcCoreConsole", dados["rotas"]["dwg"])

    @unittest.skipUnless(tem("ezdxf"), "ezdxf não instalado")
    def test_oda_tem_preferencia_sobre_o_accoreconsole(self):
        with tempfile.TemporaryDirectory() as pasta:
            falso, _ = accoreconsole_falso(pasta)
            with mock.patch.dict(os.environ, {"ACCORECONSOLE": str(falso)}), \
                    mock.patch.object(ambiente, "_oda", return_value="/opt/oda/ODAFileConverter"):
                dados = ambiente.diagnosticar()
        self.assertIn("ODA", dados["rotas"]["dwg"])
        self.assertNotIn("AcCoreConsole", dados["rotas"]["dwg"])


if __name__ == "__main__":
    unittest.main()
