# Esquema da planilha de entrega

Gerada por `gerar_planilha.py` a partir de `levantamento.json` ([ESQUEMA_LEVANTAMENTO](ESQUEMA_LEVANTAMENTO.md)). As fórmulas aparecem abaixo como o Excel em português as exibe; o arquivo as guarda em inglês.

## 1. Listas recebidas (principais)

Nenhuma célula existente é alterada. À direita do conteúdo da aba, na linha de cabeçalho da lista, entram quatro colunas:

| Coluna | Conteúdo |
|---|---|
| `QTD LEVANTADA` | `=SE('ITEM 2.1'!$G$8="";"";'ITEM 2.1'!$G$8)`, vazia quando o item não tem total |
| `ESTADO` | `='ITEM 2.1'!$G$9` |
| `MEMÓRIA` | link para a aba da memória |
| `OBS LEVANTAMENTO` | motivo curto, com IDs `D###`/`P###` |

Só as linhas de itens recebem as colunas; títulos e agrupadores ficam vazios. As colunas de quantidade recebidas continuam como estavam, inclusive fórmulas e vazios.

## 2. Aba de memória `ITEM <id>`

Nome: `ITEM ` + ID, sem `[ ] : * ? / \`, com até 31 caracteres; um código repetido recebe o sufixo ` (2)`. O mapa chave → aba fica no Resumo.

| Célula | Conteúdo |
|---|---|
| A1 | título |
| B3, B4, B5, B6 | ID, descrição integral, unidade, chave (`aba!linha`) |
| B8 a B12 | critério, premissas, pendências, fontes e natureza |
| **G8** | **resultado**: o subtotal (G10) quando o estado efetivo é CONFIRMADO ou PREMISSA; vazio nos demais |
| **G9** | **estado efetivo**: o declarado (G13), rebaixado para SUBTOTAL se alguma parcela estiver sem valor |
| G10 | subtotal conhecido: soma das parcelas com valor |
| G11 | unidade |
| G12 | número de parcelas sem valor |
| G13 | estado declarado no `levantamento.json` |
| B14, B15, B16 | o que entrou, o que ficou fora, o que falta |
| linha 18 | cabeçalho das parcelas; parcelas a partir da linha 19 |

Fórmulas do bloco de resultado:

```text
G8  =SE(OU(G9="CONFIRMADO";G9="PREMISSA");G10;"")
G9  =SE(E(OU(G13="CONFIRMADO";G13="PREMISSA");G12>0);"SUBTOTAL";G13)
G10 =SE(CONT.NÚM(K19:K30)=0;"";SOMA(K19:K30))
G12 =LINS(K19:K30)-CONT.NÚM(K19:K30)
```

Tabela de parcelas:

| Coluna | Campo |
|---|---|
| A | ID da parcela |
| B | descrição |
| C | local ou face |
| D | estado físico |
| E, F, G | dimensões 1 a 3 |
| H | valor direto |
| I | multiplicidade |
| J | sinal (1 ou −1) |
| K | resultado: `=SE(CONT.NÚM(E19:F19)<2;"";E19*F19*I19*J19)` para duas dimensões (ajustado a 1 ou 3) ou `=SE(CONT.NÚM(H19)<1;"";H19*I19*J19)` para valor direto |
| L | unidade |
| M | origem |
| N | fonte ou localizador |
| O | premissas e pendências da parcela |

Depois das parcelas vêm o diagnóstico (quando houver) e os prints, cada um com sua legenda.

## 3. Abas do levantamento

| Aba | Conteúdo |
|---|---|
| Pendências | campos de [03 §4](../references/03_pendencias_premissas_e_estados.md), ordenados por impacto |
| Premissas | campos de [03 §3](../references/03_pendencias_premissas_e_estados.md), incluindo premissas de escopo |
| Critérios | ID, família, regra, parâmetros e fonte |
| Fontes | ID, arquivo, revisão, hash, representações e estado de leitura |
| Sugestões | serviços que faltam na lista (campo `sugestoes`), fora da principal; só existe se houver sugestão |
| Comparação | quantidade levantada × referência, classe, Δ e Δ% (campo `comparacao`); só existe quando pedida |
| Resumo do levantamento | contagem por estado, mapa chave → aba de memória, modo de gravação e limitações (campo `limitacoes`) |

Se o arquivo já tiver uma aba com o mesmo nome, a nova recebe o sufixo ` (levantamento)`.

## 4. Tipos e valores

Quantidades e dimensões são números nativos; a vírgula decimal é formato de exibição. IDs são texto. As fórmulas são gravadas com os valores já calculados (cache), para que visualizadores sem motor de cálculo mostrem os números; o validador confere esses valores contra o JSON e contra o LibreOffice.

## 5. Arquivo separado

Se o arquivo recebido tiver recursos que a gravação perderia (imagens, gráficos, controles, objetos incorporados, extensões), o modo `auto` cria `<nome>_LEVANTAMENTO.xlsx`. Cada lista vira uma aba `<aba> (cópia)` (`(cópia 2)` para a segunda lista da mesma aba) com o bloco da lista copiado como valores, agrupadores incluídos: colunas item, descrição, unidade e quantidade recebida, as colunas do §1 nas linhas de itens e `LINHA ORIGINAL`. Seguem as memórias e as abas do §3. O arquivo recebido fica intocado (o validador confere o hash) e o motivo vai para o Resumo. Arquivo `.xlsm` vira `.xlsx` nesse modo.
