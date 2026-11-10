# 04 — Áreas

Objetivo: uma área reproduzível para um contorno e uma finalidade declarados. Antes de qualquer conta, saber se o pedido é transcrever, calcular ou conferir; em pedido de catálogo, só transcrever.

## 1. Método e rótulo

| Método usado | Rótulo junto ao valor | Evidência mínima |
|---|---|---|
| Etiqueta, quadro ou memorial | Área indicada no projeto — transcrita | arquivo, revisão, localizador |
| Cotas explícitas | Área calculada pelas cotas | vista, cotas usadas, parcelas e fórmulas |
| Coordenadas de DXF ou PDF vetorial | Área calculada pelas coordenadas | entidades ou handles, unidade validada, saída do `geometria.py` |
| Comando nativo executado | Área medida por comando nativo (nomear o comando) | objeto, comando e resultado legível |
| Medição gráfica em imagem ou PDF raster | Área estimada por medição gráfica (estado PREMISSA) | calibração e limitação |
| Modelo BIM | Área extraída do modelo, com a propriedade identificada | modelo e revisão, IDs, propriedade, bruta ou líquida |

Etiqueta não substitui medição independente. Cálculo por script continua sendo "pelas coordenadas", mesmo quando coincide com o CAD.

## 2. Contorno antes da conta

A ferramenta mede os limites escolhidos; quem decide quais limites representam o serviço é o critério. Declarar a finalidade (piso, forro, projeção, superfície desenvolvida…) e mostrar o contorno com IDs (`A01`, `A02`, deduções `D01`) no print antes de calcular.

| Elemento | Decisão a registrar |
|---|---|
| Paredes do limite | face nominal, face acabada ou eixo |
| Paredes e divisórias internas | projeção incluída ou excluída |
| Portas e passagens | linha de fechamento e a quem pertence a faixa sob a porta |
| Pilares, bonecas, reentrâncias | sólido excluído; piso ao lado incluído |
| Shafts, poços, vazios | contorno e inclusão ou exclusão |
| Bancadas, móveis fixos, equipamentos | área sob o elemento descontada ou não, conforme o serviço |
| Louças e símbolos | descontam só quando há exclusão física real |
| Hachuras existentes | limites e ilhas reais; hachura não equivale automaticamente ao ambiente |

Percorrer todo o limite (avanços, recuos, pilares, bonecas, batentes); nunca ligar dois cantos com uma reta que corte uma reentrância. Contorno externo e vazios internos são tratados separadamente. Superfície inclinada declara se a área é projetada ou desenvolvida: com inclinação constante α, `A_desenvolvida = A_projetada ÷ cos α`; com várias águas ou dobras, decompor por plano.

## 3. Unidade e escala

- **CAD:** distinguir Model e Paper Space; ler `$INSUNITS` e confirmar com pelo menos duas cotas conhecidas em direções diferentes. Registrar `k`, os metros por unidade de desenho: área × k², comprimento × k. A escala impressa da prancha não converte a geometria do Model.
- **PDF vetorial:** validar a escala com duas cotas (ou a escala escrita confirmada por uma cota) antes de `pdf.py medir`; registrar a diferença encontrada.
- **PDF raster ou imagem:** priorizar cotas legíveis; somar cotas parciais só quando consecutivas e do mesmo trecho. Sem cota, medição gráfica: `pdf.py render --grade 50` desenha coordenadas sobre a página, os vértices são lidos na imagem e `pdf.py medir --poligono "x1,y1;x2,y2;..." --calibrar ...` calcula com a escala calibrada por uma cota conhecida. O resultado é PREMISSA.

Escala incompatível vira pendência, e as demais medições seguem.

## 4. Vãos e soleiras

Auditar todas as portas e passagens, inclusive cabines e acessos secundários. Para cada vão, registrar: ambientes ligados; largura usada (vão, entre batentes ou passagem livre, nunca a folha sem prova); profundidade da faixa; linha onde a área termina; dono da faixa; e se ela já está dentro do polígono. O arco de abertura da porta não é limite de piso. Faixa compartilhada tem um único dono: conferir o conjunto dos ambientes para que nenhuma faixa fique duplicada ou sem dono.

## 5. Cálculo

- **Pelas cotas:** parcelas sem lacuna nem sobreposição, cada dimensão com sua fonte; `Total = Σ parcelas − deduções ainda não aplicadas`.
- **Pelas coordenadas:** `cad.py extrair` ou `pdf.py medir`, depois `geometria.py calcular`. O script trata arcos (bulge) analiticamente, desconta furos e valida fechamento, autointerseção e vértices repetidos.
- **Uniões e diferenças:** `geometria.py uniao --ids … --subtrair …` (aceita hachuras) devolve polígonos com furos já ordenados, prontos para `calcular` e para `render`.
- **Arestas soltas** (resultado de outro programa ou de extração por segmentos) passam por `geometria.py ciclos`. As arestas são encadeadas pelas extremidades, componentes separadas nunca são ligadas, só ciclos fechados são preenchidos (ilhas descontadas) e a área precisa ser a mesma depois de transladar a origem. Uma lista de arestas válida para somar área não é, por si só, uma sequência válida de vértices para desenhar.
- **Escala:** `geometria.py calcular` avisa quando o `k` veio do arquivo sem validação; depois de conferir as duas cotas, informar `--k`.
- **Lacunas:** distância entre extremidades que deveriam coincidir é registrada, com a aresta de fechamento adotada; vértice nunca é movido para fechar. Resíduo numérico e abertura física não resolvida são coisas diferentes.
- Cotas arredondadas e coordenadas não se misturam no mesmo total sem declarar a origem de cada trecho.

## 6. Medição nativa no CAD

Opcional: quando pedida ou para conferir item crítico, sempre numa cópia. Auditar a entidade (fechada, plano, arcos, sem cruzamentos), executar o comando (no AutoCAD, `AREA` → `Objeto`) e registrar objeto, handle, resultado e unidade. O AutoCAD calcula área de polilinha aberta com fechamento implícito: área retornada não prova que a polilinha é fechada. Ler a variável `AREA` ou uma propriedade é leitura, não nova medição. Operação em [07](07_ferramentas_e_aplicativos.md).

## 7. Conferência

Comparar com a etiqueta: `Δ = A_calculada − A_indicada`; `Δ% = Δ ÷ A_indicada × 100` (base zero: "não calculável"). Em divergência, revisar fonte, revisão, unidade, faces, vãos, vazios, sobreposições e aritmética; o contorno nunca é movido para coincidir. Manter a precisão interna e arredondar só na apresentação, com duas casas.

## 8. Exemplo fictício

Ambiente fictício: região de 3,20 × 2,40 m; faixa de porta de 0,80 × 0,18 m fora do retângulo; shaft de 0,30 × 0,40 m dentro dele.

| Parcela | Expressão | m² | Tratamento |
|---|---|---:|---|
| A01 região | 3,20 × 2,40 | 7,6800 | inclui a projeção do shaft |
| A02 porta | 0,80 × 0,18 | 0,1440 | faixa atribuída a este ambiente |
| D01 shaft | 0,30 × 0,40 | −0,1200 | dedução ainda não aplicada |
| Total | A01 + A02 − D01 | 7,7040 ≈ 7,70 | calculada pelas cotas |
