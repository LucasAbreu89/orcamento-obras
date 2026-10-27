# 02 — Planilha, escopo e mapeamento

## 1. Identidade, preservação e leitura inicial

Abrir o arquivo indicado, confirmar caminho/nome e identificar as abas reais. Criar backup antes de editar; preferir cópia de trabalho na pasta da execução. Registrar hash/tamanho de entrada quando houver acesso ao arquivo. Se o usuário autorizou atualização no mesmo arquivo, conferir alterações concorrentes antes da gravação final; não sobrescrever trabalho feito depois do backup.

Aplicar a habilidade de planilhas disponível. Inventariar abas visíveis/ocultas, tabelas, fórmulas, nomes definidos, imagens, comentários, links externos e macros relevantes. Não converter formato ou salvar com ferramenta que remova silenciosamente recursos. Se a ferramenta não preserva o arquivo, usar rota nativa compatível ou entregar uma cópia separada com a limitação explícita. Não ativar macros por padrão.

Mapear as abas que contêm listas de serviços: linhas de cabeçalho, agrupadores, itens, unidades, quantidades, preços, subtotais e observações. Conferir células mescladas, tabelas separadas, filtros e linhas/colunas ocultas que possam conter itens. Uma linha de título não é serviço. Distinguir quantidade original, quantidade levantada, quantidade de empreiteiro e coeficiente de composição.

### 1.1. Um Excel pode conter várias abas e listas

Não presumir que a primeira aba, a aba ativa ou a aba chamada “Orçamento” contém todo o escopo. Inventariar **todas as abas**, inclusive as ocultas quando a ferramenta permitir leitura sem modificar a fonte. Registrar nome, visibilidade, conteúdo, tabelas/intervalos, relação com outras abas e alcance examinado.

Classificar cada aba pela função efetivamente comprovada: lista de serviços, lista de outro pavimento/setor/etapa, resumo consolidado, base de ambientes, memória de cálculo, composição/preços, comparação, revisão anterior ou outra função identificada. Não excluir uma aba apenas pelo nome; registrar o motivo de inclusão ou exclusão e respeitar as restrições do usuário. Identificar mais de uma lista/tabela na mesma aba quando houver.

| Arquivo/aba | Visibilidade | Função e tabelas/intervalos | Pavimento/setor/fase/revisão | Relação com outras abas | Cobertura da leitura | Tratamento no alcance |
|---|---|---|---|---|---|---|
| Identificação real | Visível/oculta/limitação de acesso | Conteúdo examinado | Quando comprovado | Fonte, resumo, detalhe, revisão ou independente | Examinada/parcial/não examinada | Incluída, excluída com motivo ou pendente |

O pedido de levantar os itens do Excel abrange as listas de serviços pertinentes ao alcance autorizado, mesmo que estejam distribuídas em várias abas. Um resumo e as abas que o alimentam não são quantidades adicionais a somar. Rastrear fórmulas e identidade dos itens para distinguir repetição do mesmo universo de listas independentes; igualdade de código ou descrição, sozinha, não resolve essa distinção.

Neste pacote, **“principal” significa cada aba de origem que recebe nossos resultados**, ou um resumo existente que os consolida. Não exigir que o arquivo possua apenas uma principal. Manter a organização recebida; uma consolidação nova, se útil, é adicional e não substitui ou apaga as listas originais. Se uma aba não puder ser lida, registrar a falta e continuar as demais, sem declarar cobertura integral.

### 1.2. Quantidades existentes são preservadas e levantadas novamente

O Excel pode já conter quantidades, inclusive em várias colunas. **Manter a coluna de quantidade recebida intacta:** cabeçalho, números, fórmulas e células vazias. Registrar seu endereço e conteúdo no inventário inicial para conferir a preservação ao final. Não renomeá-la, sobrescrevê-la, preenchê-la ou redirecionar suas fórmulas para nossos resultados apenas para acomodar o novo levantamento.

Criar em cada lista aplicável a coluna **`QTD LEVANTADA`**, com resultados próprios vinculados às memórias, e campos de estado/origem necessários. Localizá-la ao lado da quantidade de referência quando o layout permitir, preservando as referências existentes. Na retomada, uma coluna nossa pode ser atualizada somente se sua autoria/função estiver comprovada; caso haja dúvida de identidade ou colisão de nomes, usar uma nova coluna identificada, sem substituir dados alheios.

**Quantidade preenchida não dispensa o levantamento independente.** Medir/calcular/contar os itens autorizados a partir das fontes e critérios, sem copiar o número existente para a memória ou escolhê-lo como meta para ajustar o contorno. Se faltar informação, nossa coluna mostra pendência ou subtotal identificado; não usar o número recebido para completar a lacuna.

Conservar lado a lado a quantidade original e a levantada para eventual comparação. Deltas e explicações dependem de unidade, fase e alcance compatíveis, conforme [08](08_conferencia_comparacao_e_entrega.md). Divergência não comprova erro da entrada. Não redirecionar fórmulas originais de custos ou totais para a nossa coluna sem pedido específico; o levantamento de quantidades não altera silenciosamente o orçamento recebido.

## 2. Escopo por item

Preservar descrição, unidade, ordem e códigos recebidos. Tratar IDs como texto: `1.10` é diferente de `1.1`. Se o Excel já os transformou em número e perdeu informação, reconstruir apenas com fonte inequívoca; do contrário registrar a ambiguidade. IDs repetidos recebem chave interna por arquivo + aba + tabela/seção + item/linha, sem alterar silenciosamente o código do usuário. Não mesclar automaticamente dois itens de abas diferentes por terem o mesmo código.

Aplicar formato de texto aos códigos quando necessário e conferir tanto o valor armazenado quanto sua exibição depois de exportar/renderizar. Um renderizador pode interpretar o código textual como número sob formato Geral; o arquivo final precisa preservar a distinção visível entre os subitens.

Construir a relação:

```text
chave interna | ID original | arquivo/aba/tabela/linha | descrição | unidade original
| unidade normalizada | estado físico | critério | fontes
| quantidade original (coluna/célula preservada) | QTD LEVANTADA (coluna/célula)
| bases necessárias | memória de destino | dependências | estado
```

Normalizar para cálculo somente unidades equivalentes comprovadas. Não substituir `m` por `m²` para encaixar uma conta. Registrar incompatibilidade e obter a parcela comprovada enquanto a definição permanece pendente. Quantidade em verba (`VB`) igual a 1 só é apropriada quando o escopo foi definido como pacote; desconhecido não vira verba.

Itens sugeridos pelo agente ficam fora da principal, em seção/aba separada quando autorizados. Se o usuário pediu somente seus itens ou excluiu sugestões, respeitar a restrição. Não incluir serviços adicionais nos totais.

## 3. Estrutura da planilha de entrega

Adaptar a estrutura existente sem perder o vínculo rastreável. Usar o [esquema](../assets/ESQUEMA_PLANILHA.md) como referência:

- **Principal(is):** itens e quantidades recebidos preservados; nova coluna `QTD LEVANTADA` por fórmula, estado visível e link para a memória. Manter as colunas existentes. Quando solicitado, acrescentar quantidade de terceiro, diferenças e explicação.
- **Bases/ambientes:** valores indicados e calculados em campos distintos, unidades, alturas, critérios e fontes. Abas por ambiente quando úteis ou solicitadas.
- **Memória por item:** nome curto e estável, como `ITEM 1.2`, com descrição integral no cabeçalho, aba/tabela de origem, imagem marcada, parcelas e resultado vinculado. Se o código se repetir em listas independentes, distinguir as memórias por chave interna e nome válido. Limite de 31 caracteres e unicidade dos nomes do Excel precisam ser respeitados; conservar mapa chave do item → aba.
- **Fontes:** arquivo, revisão, prancha/vista, método, evidência e alcance examinado.
- **Pendências:** informações faltantes/conflitantes, itens afetados e dependências; estado também aparece na principal.
- **Comparação:** somente quando solicitada ou houver base explicitamente fornecida para isso.

É possível reservar `G8` como resultado padrão de cada memória nova, se isso couber no modelo. Não deslocar dados existentes para forçar essa célula. Manter o endereço real no mapa e referenciá-lo na principal: `='ITEM 1.2'!G8`. Nomes com apóstrofos precisam de escape correto.

## 4. Fórmulas e estados

Cada memória deve guardar os números de entrada separadamente das fórmulas. Unidades e descrições são campos próprios, não texto misturado ao valor. A coluna `QTD LEVANTADA` de cada principal puxa o resultado da memória, e a memória puxa bases compartilhadas quando apropriado. A quantidade original é referência preservada, não entrada que substitui a medição. Não lançar manualmente um segundo total independente.

Estados recomendados: `CONFIRMADO`, `ESTIMATIVA`, `SUBTOTAL`, `PENDENTE`, `NÃO APLICÁVEL`. Definir seu significado conforme [03](03_duvidas_e_continuidade.md). Uma indicação do projeto pode ser transcrita como referência confirmada da fonte, mas não recebe rótulo de cálculo independente.

Testar dependências essenciais antes de devolver número final. `SUM` ignora texto e células vazias; uma soma que retorna valor não comprova completude. Guardar subtotal conhecido em campo próprio e impedir que o total geral seja rotulado como completo quando houver itens pendentes.

Exemplo de lógica, a adaptar à ferramenta e à localidade:

```text
se todas as entradas obrigatórias forem numéricas e o critério estiver definido:
    resultado = fórmula completa
senão:
    resultado = "PENDENTE" ou "SUBTOTAL — ver memória"
    subtotal conhecido = soma apenas das parcelas comprovadas
```

Não usar `IFERROR(...,0)` para mascarar ausência de dado. Célula numérica pode ficar sem número quando acompanhada de estado explícito e motivo; nenhum campo relevante fica sem interpretação. Se o usuário quer tudo preenchido, preencher a informação de estado, não inventar uma quantidade.

## 5. Números, localidade e compatibilidade

Gravar quantidades como números nativos. Usar formato de exibição e localidade para vírgula decimal no Brasil; não substituir pontos dentro de fórmulas nem transformar valores em strings como `191,10 m²`. Distinguir separador de milhar, decimal e unidade na importação.

Ao importar para Google Sheets, verificar a localidade e a leitura de amostras: decimal, milhares, negativo, percentual e fórmula. Preferir importação do arquivo completo à colagem ambígua de texto. Não alegar teste no Sheets se houve apenas leitura do XLSX por biblioteca.

Seguir [08](08_conferencia_comparacao_e_entrega.md) para recálculo, caches, imagens, erros e reabertura do arquivo final. Validação de dados e aparência são verificações diferentes.
