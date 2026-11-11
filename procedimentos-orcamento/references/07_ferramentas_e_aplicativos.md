# 07 — Ferramentas e aplicativos

## 1. Kit de scripts

Rodar sempre pelo interpretador; `python3 scripts/<nome>.py --help` mostra as opções. `scripts/` fica na pasta da skill: a partir da pasta da execução, usar o caminho completo (`python3 <pasta da skill>/scripts/<nome>.py`), e os demais caminhos (`dados/`, `planilha/`…) ficam relativos à execução.

| Tarefa | Comando | Depende de |
|---|---|---|
| Checar o ambiente e as rotas disponíveis | `ambiente.py` | — |
| Preparar a execução (pastas, inventário, cópias, snapshot, mapa, esqueleto do JSON) | `preparar_projeto.py --projeto … --planilha …` | — |
| Mapear, fotografar e verificar a planilha | `planilha.py mapear`, `snapshot`, `verificar` | — |
| Converter DWG em DXF (arquivo ou pasta, preservando subpastas), com manifesto `conversao_dxf.json` na pasta de saída | `cad.py converter` (`--via auto`, `oda` ou `accoreconsole`) | ODA File Converter (com ezdxf) ou AcCoreConsole do AutoCAD (§2) |
| Inventário (inclusive blocos aninhados), extração (`--blocos` lê dentro de blocos), prints e comparação de DXF | `cad.py inventario`, `extrair`, `render`, `comparar` | ezdxf, matplotlib |
| Inventário, busca de texto, medição (vetores ou `--poligono` marcado à mão) e prints de PDF (`--grade` para ler coordenadas) | `pdf.py inventario`, `texto`, `medir`, `render` | PyMuPDF |
| Áreas, perímetros, ciclos, uniões e subtrações | `geometria.py calcular`, `ciclos`, `uniao` | — (uniões: shapely) |
| Gerar a planilha de entrega | `gerar_planilha.py --levantamento dados/levantamento.json` | openpyxl, Pillow |
| Recalcular num motor independente, converter XLS/ODS/CSV e exportar o caderno em PDF | `recalcular.py` | LibreOffice |
| Validar a entrega | `validar_entrega.py --levantamento dados/levantamento.json` | — |

`cad.py render` e `pdf.py render` desenham marcas (polígonos, linhas, pontos e rótulos, no formato de `geometria.py`) sobre o desenho real, nas coordenadas do próprio desenho.

As bibliotecas ficam num ambiente virtual da skill (`<pasta da skill>/.venv`), instalado uma vez pelo usuário (ou pelo agente, com autorização dele): `ambiente.py` mostra o comando exato. Quando esse ambiente existir, os scripts rodam com `<pasta da skill>/.venv/bin/python` no lugar de `python3`. O ODA File Converter e o LibreOffice são instalados pelo usuário; o AcCoreConsole vem com o AutoCAD. O agente não instala programas nem aceita licenças: se faltar algo, informa e segue pela melhor rota disponível.

## 2. Rotas, por ordem de preferência

1. **Dados estruturados:** DXF (convertido do DWG) e PDF vetorial lidos pelos scripts; IFC com ferramenta IFC instalada, porque o kit não inclui leitor IFC. Precisos e reproduzíveis.
2. **Aplicativo pela interface (computer use):** DWG sem conversor (exportar DXF de uma cópia), medição nativa pedida, conferência visual no Excel.
3. **Medição gráfica** em imagem ou PDF raster, com estado PREMISSA.

**DWG → DXF**, nesta ordem (`ambiente.py` mostra qual está disponível):

1. **ODA File Converter**, por `cad.py converter`.
2. **AcCoreConsole do AutoCAD**, sem interface: `cad.py converter` passa a ele quando falta o ODA (ou com `--via accoreconsole`). O executável é procurado nas pastas do AutoCAD no macOS e no Windows; a variável `ACCORECONSOLE` indica outro.
3. **AutoCAD pela interface**: exportar DXF de uma cópia (§3).
4. **Pedir** DXF ou PDF vetorial ao usuário.

Pelo AcCoreConsole, cada DWG é copiado para uma pasta temporária de caminho ASCII, porque o console lê o `.scr` em cp1252 e não abre caminhos com acento. O `.scr` traz uma resposta por linha: `FILEDIA`, `0`, `DXFOUT`, `"<saída>.dxf"`, `V`, `2018`, `16`, `QUIT`, `Y`. A exportação pode sair truncada sem nenhum erro, então o DXF só vale se terminar em `0`/`EOF`. Sem DXF completo, a segunda tentativa roda `AUDIT` e `Y` antes do `DXFOUT` e grava na versão 2013. Tempo esgotado (`--tempo-limite`, padrão 600 s por tentativa) não se resolve com AUDIT: refazer só aquele arquivo com um limite maior. O DXF completo é movido para o destino; o console só abre a cópia, nunca o original. O `conversao_dxf.json` da pasta de saída acumula, por DXF, o hash do DWG e do DXF, a ferramenta, as tentativas e as falhas; uma nova conversão do mesmo DXF substitui o registro anterior. Quando o registro traz `alertas` (objetos personalizados, que podem faltar no DXF, ou exportação depois do AUDIT, que pode apagar objetos, com o resumo em `auditoria`), conferir o DXF contra o PDF da prancha antes de medir.

Resultado de script, XML ou renderizador nunca é descrito como "testado no Excel" ou "medido no AutoCAD".

## 3. Operar aplicativos pela interface

- Ler a documentação atual da ferramenta de computer use da sessão antes de operar; coordenadas, atalhos e IDs de janela de outra sessão não valem.
- Um único agente opera a interface.
- Registrar os documentos que já estavam abertos; eles não são fechados nem alterados.
- Trabalhar em cópia identificada e conferir o caminho depois de "Salvar como".
- Confirmar aplicativo, documento, aba ou vista e objeto antes de cada grupo de ações; reler o estado depois de cada diálogo.
- Salvar e fechar cada documento aberto pela tarefa logo que seu uso terminar. Num diálogo de alterações não salvas, identificar o conteúdo antes de escolher; na dúvida, preservar a janela.
- Depois de uma falha, preservar o que já foi obtido, fechar só o que é da tarefa e registrar o que ficou aberto.
- Relatar só o observado: `salvo e fechado`, `salvo, fechamento não confirmado`, `preservado aberto` ou `aplicativo indisponível`.

## 4. Medição nativa

Para afirmar medição nativa, registrar juntos: arquivo ou cópia e vista; objeto e handle; contorno visível; comando e opção executados, com o resultado legível; unidade e conversão. Captura só do número não reproduz a medição. Se o comando falhar, registrar a falha; o cálculo alternativo segue com o próprio rótulo.

## 5. Falhas de ferramenta

No máximo três tentativas da mesma abordagem. Depois, registrar o impedimento em Pendências (natureza "acesso ou ferramenta") com os itens afetados e seguir pelos itens independentes.
