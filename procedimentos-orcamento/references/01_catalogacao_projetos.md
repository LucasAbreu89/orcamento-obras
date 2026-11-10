# 01 — Inventário e catálogo das fontes

O catálogo diz o que existe em cada arquivo e onde está cada informação, para que nenhuma prancha precise ser relida a cada item. Ele registra o que está nos projetos; cálculos só entram quando pedidos.

## 1. Inventário

`preparar_projeto.py` lista os arquivos (caminho, tamanho, hash) com estado `nao_examinado`; inventário não prova leitura. Separar originais, revisões anteriores, cópias e saídas derivadas: mesmo nome não prova igualdade, mesmo hash prova duplicata exata. Arquivo compactado, protegido ou corrompido entra com sua condição de acesso e vira pendência se afetar itens. Fontes fornecidas fora da pasta pelo usuário também entram.

| Formato | Rota | Cuidado |
|---|---|---|
| DWG | `cad.py converter` para DXF, depois as rotas de DXF | sem conversor, ver [07 §2](07_ferramentas_e_aplicativos.md) |
| DXF | `cad.py inventario`, `extrair`, `render` | validar a unidade (§3) |
| PDF vetorial | `pdf.py inventario`, `texto`, `medir`, `render` | validar a escala antes de medir |
| PDF escaneado ou imagem | leitura visual; medição gráfica com `pdf.py render --grade` e `medir --poligono`, como PREMISSA | cotas legíveis têm prioridade |
| IFC | o kit não lê IFC: usar ferramenta IFC disponível (ex.: IfcOpenShell) ou pedir DWG/PDF ou quantitativos exportados do modelo | nome de propriedade não define critério ([10](10_boas_praticas_e_fontes.md)) |
| RVT, SKP, NWD e outros proprietários | pedir exportação em IFC, DWG ou PDF | pendência de acesso |
| Memorial, caderno de encargos, quadros | ler e citar | fonte de especificação e de critério |

## 2. Leitura de reconhecimento

Vale para todas as fontes. Para cada arquivo, uma linha por **representação** (página, prancha, layout, região do Model ou vista) com: ID (`F003.V02`), título, disciplina, pavimento, fase (existente, demolir, novo), revisão do carimbo, escala, localizador e estado de leitura (`não examinada`, `parcial`, `examinada` ou `fora do escopo` com motivo).

- **CAD:** `cad.py inventario` lista layouts e viewports, camadas (ligada, congelada, travada), blocos com contagem, textos, cotas, hachuras, referências externas e as regiões desenhadas no Model. Um arquivo pode ter várias plantas no Model, vários layouts e conteúdos separados por camada; a vista inicial não representa o arquivo.
- **PDF:** `pdf.py inventario` informa, por página, se ela é vetorial ou raster, o texto de maior destaque (carimbo, títulos) e as escalas escritas. Uma página pode ter várias vistas.
- **Quadros úteis:** áreas, esquadrias, acabamentos por ambiente, cargas, aço e concreto, estacas. Eles costumam ser a fonte primária e ganham linha própria.

Representação não é ocorrência: a mesma geometria em planta, ampliação e viewport é uma coisa só. Legenda, biblioteca de blocos e detalhe típico não são peças instaladas.

## 3. Aprofundamento sob demanda

Quando uma representação vai sustentar uma quantidade, conferir:

1. **Visibilidade:** camadas desligadas ou congeladas (no Model e por viewport), recortes e referências externas ausentes. Ligar todas as camadas de uma vez pode sobrepor existente, demolição e proposta; investigar as combinações que o projetista organizou e registrar as consultadas.
2. **Unidade e escala:** `$INSUNITS` e pelo menos duas cotas conhecidas em direções diferentes ([04 §3](04_calculo_de_areas.md)).
3. **Estado físico:** legenda de existente, demolir e construir; hachura ou tracejado só valem com legenda.
4. **Compatibilidade:** PDF e DWG de mesmo nome não são necessariamente a mesma revisão; comparar carimbo, cotas e detalhes. Conflito vira pendência com as duas fontes, e a escolha nunca é a versão que fecha a conta.

Mudanças de visibilidade e marcações acontecem em cópia identificada.

## 4. Índice assunto → fonte

Montar o índice inverso: piso → quadro de acabamentos F002.V05 e planta F002.V01; forro → F005.V01; esquadrias → quadro F002.V07; e assim por diante. É ele que evita reabrir todos os projetos para cada item. Etiqueta `A=...` entra como **área indicada no projeto**, nunca como área conferida.

## 5. Saídas

`fontes/catalogo.md` ([modelo](../assets/MODELO_CATALOGO.md)) e a lista `fontes` do `levantamento.json`, que vira a aba Fontes. Conversões e extrações guardam o hash da fonte; se o arquivo mudar, o que depende dele é refeito ([09 §3](09_agentes_retomada_e_revisoes.md)).
