# 07 — Ferramentas e aplicativos

## 1. Kit de scripts

Rodar sempre pelo interpretador; `python3 scripts/<nome>.py --help` mostra as opções. `scripts/` fica na pasta da skill: a partir da pasta da execução, usar o caminho completo (`python3 <pasta da skill>/scripts/<nome>.py`), e os demais caminhos (`dados/`, `planilha/`…) ficam relativos à execução.

| Tarefa | Comando | Depende de |
|---|---|---|
| Checar o ambiente e as rotas disponíveis | `ambiente.py` | — |
| Preparar a execução (pastas, inventário, cópias, snapshot, mapa, esqueleto do JSON) | `preparar_projeto.py --projeto … --planilha …` | — |
| Mapear, fotografar e verificar a planilha | `planilha.py mapear`, `snapshot`, `verificar` | — |
| Converter DWG em DXF (arquivo ou pasta, preservando subpastas) | `cad.py converter` | ezdxf e ODA File Converter |
| Inventário (inclusive blocos aninhados), extração (`--blocos` lê dentro de blocos), prints e comparação de DXF | `cad.py inventario`, `extrair`, `render`, `comparar` | ezdxf, matplotlib |
| Inventário, busca de texto, medição (vetores ou `--poligono` marcado à mão) e prints de PDF (`--grade` para ler coordenadas) | `pdf.py inventario`, `texto`, `medir`, `render` | PyMuPDF |
| Áreas, perímetros, ciclos, uniões e subtrações | `geometria.py calcular`, `ciclos`, `uniao` | — (uniões: shapely) |
| Gerar a planilha de entrega | `gerar_planilha.py --levantamento dados/levantamento.json` | openpyxl, Pillow |
| Recalcular num motor independente, converter XLS/ODS/CSV e exportar o caderno em PDF | `recalcular.py` | LibreOffice |
| Validar a entrega | `validar_entrega.py --levantamento dados/levantamento.json` | — |

`cad.py render` e `pdf.py render` desenham marcas (polígonos, linhas, pontos e rótulos, no formato de `geometria.py`) sobre o desenho real, nas coordenadas do próprio desenho.

As bibliotecas ficam num ambiente virtual da skill (`<pasta da skill>/.venv`), instalado uma vez pelo usuário (ou pelo agente, com autorização dele): `ambiente.py` mostra o comando exato. Quando esse ambiente existir, os scripts rodam com `<pasta da skill>/.venv/bin/python` no lugar de `python3`. O ODA File Converter e o LibreOffice são instalados pelo usuário. O agente não instala programas nem aceita licenças: se faltar algo, informa e segue pela melhor rota disponível.

## 2. Rotas, por ordem de preferência

1. **Dados estruturados:** DXF (convertido do DWG) e PDF vetorial lidos pelos scripts; IFC com ferramenta IFC instalada, porque o kit não inclui leitor IFC. Precisos e reproduzíveis.
2. **Aplicativo pela interface (computer use):** DWG sem conversor (exportar DXF de uma cópia), medição nativa pedida, conferência visual no Excel.
3. **Medição gráfica** em imagem ou PDF raster, com estado PREMISSA.

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
