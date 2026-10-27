# 09 — Agentes, resultados isolados e retomada

Usar esta referência quando houver divisão do levantamento entre agentes ou necessidade de retomar uma execução. A coordenação deve permitir reproduzir resultados sem concorrência na interface ou gravações conflitantes da planilha, conservando fontes, critérios, dependências e limites comprovados.

## Índice

1. [Dividir por unidades verificáveis](#1-dividir-por-unidades-verificáveis)
2. [Controlar autoria e operação](#2-controlar-autoria-e-operação)
3. [Receber e integrar resultados](#3-receber-e-integrar-resultados)
4. [Reutilizar extrações com identidade verificável](#4-reutilizar-extrações-com-identidade-verificável)
5. [Registrar dependências e retomar](#5-registrar-dependências-e-retomar)
6. [Encerrar no alcance real](#6-encerrar-no-alcance-real)

## 1. Dividir por unidades verificáveis

Delegar quando houver trabalho independente que possa reduzir tempo ou melhorar a conferência. Particionar por ambiente, zona, disciplina, família de elementos ou etapa de verificação, conforme a geometria e as fontes. Cada pacote precisa de fronteira clara e de saída utilizável pelo responsável pela integração.

Exemplos de unidades independentes: contagem de uma família de luminárias em todas as vistas pertinentes; levantamento dos panos de um conjunto de ambientes; extração de esquadrias; conferência de fórmulas e imagens de uma cópia já consolidada. Não dividir um mesmo universo por imagens sobrepostas sem definir como reconhecer os mesmos elementos.

### Contrato mínimo da delegação

| Informação | Definição a transmitir |
|---|---|
| Objetivo e alcance | Ambientes, famílias, itens e condição física incluídos |
| Exclusões e interfaces | O que pertence a outro agente e os IDs das interfaces comuns |
| Fontes autorizadas | Arquivos, revisões, páginas/vistas e modelo de referência |
| Critério aplicável | Grandeza, unidade, faces, alturas e deduções quando já definidos |
| IDs | Prefixo ou namespace que evite colisões entre agentes |
| Saída isolada | Caminho próprio e formato dos resultados técnicos |
| Evidências | Imagens, marcações, coordenadas, fórmulas e localização da fonte |
| Dependências | Entradas compartilhadas e resultados exigidos de outros pacotes |
| Limites de atuação | Sem gravar a planilha final ou operar a UI fora da coordenação |

Não enviar apenas uma meta numérica. O agente deve devolver medidas ou contagens sustentadas, não ajustar o resultado a quantidade de orçamento ou etiqueta prévia.

### Dúvidas durante a execução

Aplicar [03 — Dúvidas e continuidade](03_duvidas_e_continuidade.md): não pausar o lote por indefinição técnica. O agente devolve a dúvida como registro estruturado para a aba `Pendências`, com item, fonte consultada, informação faltante, dependências e efeito. Continua os ambientes, famílias, parcelas e serviços independentes.

Não inventar números, não usar zero para ausência e não ocultar trechos não quantificados. Cenários ficam identificados e não são somados entre si. O responsável pela planilha integra os registros de dúvida e o estado técnico de cada resultado.

## 2. Controlar autoria e operação

### Um único autor do workbook final

Designar um responsável por gravar a planilha principal e consolidada. Os demais agentes produzem dados técnicos, propostas de fórmulas, imagens, mapas e relatórios em saídas separadas. Não permitir gravações simultâneas no mesmo workbook, mesmo quando os agentes pretendam editar abas diferentes; uma regravação de arquivo pode eliminar alterações alheias.

Se outro agente precisar validar a planilha, fornecer cópia identificada para leitura ou teste. Seus ajustes retornam como dados ou proposta com localização exata; a integração ocorre pelo autor responsável. Troca de autoria exige terminar a gravação atual, identificar a versão entregue e confirmar o ponto de partida do sucessor.

Antes de integrar sobre um destino existente, verificar se ele foi alterado pelo usuário ou por outro processo desde a leitura inicial. Não sobrescrever trabalho recente com cópia antiga. Preservação e validação seguem [08 — Conferência, comparação e entrega](08_conferencia_comparacao_e_entrega.md).

### Um único operador da interface compartilhada

Nomear um operador para CAD, Excel, browser e demais superfícies UI compartilhadas. Outros agentes trabalham com arquivos, extrações e cálculos sem mudar foco, clicar, digitar ou acionar comandos nessa interface.

Uma necessidade de UI pode ser atendida por pedido técnico ao operador: arquivo/revisão, vista, ação pretendida, objeto e evidência exigida. O operador devolve o resultado observado, não a promessa de que a ação funcionaria. A troca de operador segue a passagem de estado da referência [07 — Computer use e encerramento](07_computer_use_e_encerramento.md).

Também evitar mutação concorrente de cópias CAD, imagens marcadas ou tabelas de resultados. Cada agente recebe destino próprio; o responsável integra após conferir. Leitura paralela de fontes imutáveis pode ocorrer quando a ferramenta utilizada permitir.

## 3. Receber e integrar resultados

Na estrutura padrão, cada execução fica em `levantamento-orcamento/execucoes/<data>/`, usando `01_catalogo`, `02_bases_ambientes`, `03_memorias_servicos`, `04_evidencias`, `05_planilhas`, `06_conferencia`, `07_backups` e `08_dados_tecnicos`. Respeitar destinos existentes ou os definidos pelo usuário.

Guardar saídas de agentes em subpastas identificadas dentro das categorias pertinentes, por exemplo dados do agente em `08_dados_tecnicos/agentes/<id>/` e suas imagens em `04_evidencias/agentes/<id>/`. Não duplicar a planilha final em várias pastas sem distinguir cópias de conferência da versão de entrega.

### Resultado mínimo por pacote

| Campo | Conteúdo esperado |
|---|---|
| Identidade | Execução, pacote, agente e versão do resultado |
| Universo | Ambientes/elementos realmente examinados, com exclusões |
| Fontes | Caminhos, revisões, vistas e hashes quando disponíveis |
| Método e critério | Transcrição, cotas, coordenadas, contagem, estimativa ou execução nativa real |
| Parcelas | IDs, dimensões, expressões, unidades e resultados sem arredondamento prematuro |
| Estado técnico | Confirmado, parcial, estimado, cenário ou não determinado, com motivo |
| Evidências | IDs e caminhos que permitam localizar cada elemento/contorno |
| Pendências | Registros técnicos ligados às linhas afetadas |
| Dependências | Entradas compartilhadas, resultados consumidos e consequências de alteração |
| Verificações | O que foi conferido e quais verificações não foram possíveis |

O integrador verifica duplicações, lacunas e interfaces entre pacotes antes de somar. Prefixos distintos evitam colisões de nomes, mas não impedem que dois agentes tenham contado o mesmo objeto. Usar identidade física: modelo/ID, vista de origem, localização, família, face e estado da obra conforme o caso.

Para elementos vistos em planta e detalhe, identificar que se trata da mesma ocorrência. Para paredes compartilhadas, distinguir a mesma face contada duas vezes de duas faces físicas legitimamente incluídas em serviços diferentes. Não somar `Pgeom`, `Pfaces` e quantidade de serviço como se fossem parcelas equivalentes.

Integrar conforme [06 — Quantitativos e memórias](06_quantitativos_e_memorias.md), mantendo vínculos à memória. Conferir resultados e cobertura pela referência 08. A mensagem final do agente não substitui os arquivos e evidências necessários para reproduzir a quantidade.

## 4. Reutilizar extrações com identidade verificável

Evitar reabrir e reextrair a mesma fonte quando já existir resultado válido para o mesmo conteúdo, método e critério. O cache serve a extrações e cálculos técnicos; não torna revisões distintas equivalentes nem substitui conferência da fonte.

Uma chave técnica de reutilização deve considerar, conforme a operação:

```text
hash do conteúdo-fonte
+ revisão/fase confirmadas
+ página/vista/espaço, região ou IDs dos objetos
+ método, parâmetros e versão relevante do extrator
+ unidade, plano e sistema de coordenadas
+ critério, cenário e filtros aplicados
```

Usar hash de conteúdo, como SHA-256, quando houver acesso ao arquivo e isso for possível. Nome e data de modificação ajudam a localizar, mas não provam identidade. Para fonte remota, usar identificador de versão comprovado quando disponível; se não houver identidade suficiente, não afirmar que o resultado armazenado corresponde à fonte atual.

Uma extração de geometria pode ser reutilizada em cálculos novos quando sua unidade, plano e origem estiverem confirmados. Um resultado final de área, comprimento ou serviço exige também compatibilidade de contorno, altura, deduções e critério; igualdade de arquivo não basta.

### Invalidar o que foi afetado

| Mudança observada | Reavaliação necessária |
|---|---|
| Conteúdo/revisão da fonte | Reextrair ou comprovar as partes invariantes; recalcular dependentes afetados |
| Unidade ou sistema de coordenadas | Revisar geometrias, conversões e cálculos derivados |
| Limite, face, altura ou cenário | Atualizar bases, memórias, imagens e totais que dependem da escolha |
| Família, estado físico ou classificação | Reconciliar contagens e categorias, sem manter ocorrência em duas classes exclusivas |
| Mapeamento de item/célula | Refazer vínculo e comparação correspondentes |
| Fórmula, método ou ferramenta com efeito material | Revalidar resultados e cache calculado |

Preservar a versão técnica anterior quando necessária para explicar a alteração. Não usar arquivo antigo porque seu valor é conveniente nem alterar o hash registrado para fazê-lo parecer atual.

## 5. Registrar dependências e retomar

### Dados técnicos são o ponto de partida

Manter em `08_dados_tecnicos` os registros que permitem reconstruir o levantamento: manifesto de fontes/versões, objetos e geometrias, parâmetros, resultados de extração, dependências entre registros, logs nativos e inventário operacional dos documentos da referência 07. Podem ser tabelas, CSV ou JSON, de acordo com o uso real.

Esses arquivos descrevem dados, resultados e proveniência. Não criar uma memória informal, diário de status ou Markdown TODO como substituto de rastreamento do projeto. As dúvidas sobre quantidades continuam na aba `Pendências`, junto dos itens e efeitos técnicos.

Modelo de dependência técnica:

| ID resultado | Entradas/IDs | Fonte e identidade | Critério/cenário | Saída consumida por | Situação técnica | Evidência |
|---|---|---|---|---|---|---|
| Resultado identificável | Geometria, altura, contagem ou parâmetro | Arquivo/revisão/hash | Regra aplicada | Memória/serviço/célula | Válido, afetado ou não determinado | Caminho/ID |

Uma mudança em altura, por exemplo, pode afetar pintura, revestimento e alvenaria de maneiras distintas. Registrar esses vínculos para recalcular somente os itens dependentes e conferir os respectivos resumos, imagens e comparações.

### Beads quando houver workspace ativo

Se o projeto usa Beads, aplicar a habilidade `beads` disponível e usar `bd` como fonte durável de tarefas, dependências e continuidade. Carregar contexto com `bd prime` quando ausente ou desatualizado e verificar o workspace quando necessário. Inspecionar a tarefa antes de assumir ou alterar seu estado.

Usar os recursos documentados do `bd` para registrar escopo ainda necessário, dependências e referências aos artefatos técnicos. Persistir memória de projeto por `bd remember` quando o fluxo local assim estabelecer. Fechar uma tarefa somente quando seu alcance tiver sido realmente atendido; entregar subtotal não implica conclusão do levantamento integral.

Não criar listas Markdown paralelas. Não inicializar workspace ou migrar o rastreamento sem necessidade ou autorização do contexto. Na ausência de Beads ativo, respeitar o rastreador já existente; se não houver, a planilha e os dados técnicos sustentam a reprodução do que foi produzido, sem inventar um novo sistema de memória ad hoc.

### Procedimento de retomada

1. Ler o pedido vigente, as instruções do projeto e o rastreamento durável aplicável; identificar o alcance autorizado e as definições posteriores do usuário.
2. Localizar a execução e a planilha efetivamente entregues ou em uso, com backup e versões. Não escolher a versão apenas pelo nome ou pela maior data.
3. Conferir identidade das fontes e resultados armazenados; invalidar dependentes quando conteúdo, revisão, critério ou ferramenta tiverem mudado.
4. Ler `Pendências` e o mapa técnico de dependências. Distinguir informação ausente, hipótese, cenário e falha de ferramenta.
5. Revalidar os recursos atuais da interface se ela for necessária. O inventário de janelas de uma sessão anterior é evidência histórica, não garantia do que está aberto agora.
6. Reutilizar resultados comprovados, resolver o que a nova evidência permitir e seguir pelos itens independentes. Integrar e conferir as células afetadas.

Não refazer medições válidas apenas porque o turno ou contexto mudou. Também não considerar uma conclusão antiga automaticamente válida depois de revisão do projeto. A retomada segue identidade e dependências, não lembrança textual do agente.

## 6. Encerrar no alcance real

Terminar a execução atual com resultados preservados, autoria consolidada, registros de dúvidas integrados e documentos da tarefa encerrados conforme a referência 07. Informar os limites materiais: trechos sem altura, arquivos indisponíveis, cenários sem definição, falta de comando nativo ou recálculo não confirmado, quando afetarem a entrega.

Não descrever uma tarefa como integralmente concluída se restarem itens necessários sem quantidade determinada. Entregar as partes independentes já verificadas com cobertura explícita, conforme a referência 08.

Não criar agendamento, automação, execução futura, monitoramento ou promessa de continuidade após o turno sem pedido do usuário. Registrar dependências para permitir retomada não significa que o agente continuará trabalhando sozinho depois de encerrar a resposta. Se houver pedido de continuidade futura, usar o mecanismo autorizado e descrever o alcance real dessa configuração.

**Exemplo fictício:** um agente entrega contagem identificada de tomadas de uma zona; outro entrega luminárias por família. A altura de um pano permanece sem fonte. O autor único integra as contagens e a pendência, sem converter a altura em zero. Na retomada, uma nova seção resolve a altura: recalculam-se os serviços daquele pano, preservando as contagens cujas fontes e critérios permanecem válidos.
