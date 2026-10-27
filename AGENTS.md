# Instruções para trabalhar nesta pasta

## Procedimentos documentados

### Fluxo reutilizável para qualquer obra

Para levantamento completo ou retomada a partir de projetos e Excel, usar a skill [procedimentos-orcamento](procedimentos-orcamento/SKILL.md), começando pelo [fluxo mestre](procedimentos-orcamento/references/00_fluxo_mestre.md). O [guia de uso](procedimentos-orcamento/LEIA_PRIMEIRO.md) explica as entradas e as saídas. Ler as demais referências por etapa, sem carregar todo o pacote desnecessariamente.

Antes de consultar, transcrever, calcular ou conferir áreas, aplicar a [referência generalizada de áreas](procedimentos-orcamento/references/04_calculo_de_areas.md). Para perímetros e alturas, aplicar a [referência correspondente](procedimentos-orcamento/references/05_perimetros_e_alturas.md). Para quantitativos e memórias por serviço, aplicar a [referência de serviços](procedimentos-orcamento/references/06_quantitativos_e_memorias.md).

O pacote generalizado é a referência operacional para novas obras. Históricos, catálogos, quantitativos e exemplos específicos permanecem nas pastas locais das respectivas obras, fora do repositório de procedimentos. Esses arquivos continuam preservados no workspace; seus valores e critérios não são padrões para outro projeto. Cada nova obra recebe seu próprio catálogo.

Dúvidas técnicas devem ser registradas na aba `Pendências`, com fonte e dependências, sem interromper os itens independentes. Não inventar números para preencher campos. Ao usar aplicativos, identificar documentos preexistentes e fechar somente os abertos pela tarefa, logo após seu uso, preservando o trabalho do usuário.

Regras para as próximas tarefas:

- Distinguir área indicada no projeto, cálculo pelas cotas, cálculo pelas coordenadas e medição com comando nativo. Identificar a origem junto ao valor.
- Em pedidos apenas de catálogo ou rastreamento, registrar o que consta nos projetos; não acrescentar cálculos sem solicitação.
- Definir e mostrar o contorno antes de calcular. Auditar todos os vãos de portas, suas profundidades e seus limites, evitando omissões e contagens duplicadas.
- Incorporar à memória de cada item físico prints reais marcados que mostrem todas as áreas, faces, trechos ou ocorrências considerados, com os mesmos IDs das parcelas. Exclusões e pendências precisam mostrar a indicação, conflito ou informação faltante nas fontes quando houver representação aplicável; explicar os demais casos. Aplicar o [contrato de evidência visual por item](procedimentos-orcamento/references/06_quantitativos_e_memorias.md#evidencias-visuais-por-item), sem aceitar imagem genérica ou nome/hash de arquivo como justificativa.
- Preservar os arquivos originais; criar os contornos de conferência em cópias identificadas.
- Um arquivo de projeto pode conter várias plantas/vistas no Model, em layouts e em combinações de camadas. Registrar a cobertura por representação, sem presumir que a vista inicial mostre tudo.
- Um Excel pode conter várias abas e listas de serviços, inclusive ocultas. Mapear seu conteúdo e relações antes de levantar, sem somar resumos novamente aos detalhes.
- Preservar intactas as colunas de quantidade recebidas, inclusive cabeçalhos, valores, fórmulas e vazios. Levantar os itens independentemente em coluna própria `QTD LEVANTADA`, vinculada às memórias, mesmo quando já houver quantidades preenchidas. Usar as quantidades originais como referência para comparação compatível.
- Não ajustar a conta para coincidir com uma etiqueta nem tratar resultados próximos como iguais.
- Aplicar as instruções atuais do usuário ao caso; se ele definir outro critério, documentar a escolha e os efeitos no resultado.
- Ao criar um novo procedimento solicitado pelo usuário, registrar sua referência neste índice.

Índice atual:

| Procedimento | Documento |
|---|---|
| Fluxo mestre do levantamento | [00 — Fluxo mestre](procedimentos-orcamento/references/00_fluxo_mestre.md) |
| Inventário e catálogo | [01 — Catalogação de projetos](procedimentos-orcamento/references/01_catalogacao_projetos.md) |
| Planilha e escopo | [02 — Planilha, escopo e mapeamento](procedimentos-orcamento/references/02_planilha_escopo_e_mapeamento.md) |
| Dúvidas e continuidade | [03 — Dúvidas e continuidade](procedimentos-orcamento/references/03_duvidas_e_continuidade.md) |
| Áreas — generalizado | [04 — Áreas](procedimentos-orcamento/references/04_calculo_de_areas.md) |
| Perímetros e alturas — generalizado | [05 — Perímetros e alturas](procedimentos-orcamento/references/05_perimetros_e_alturas.md) |
| Quantitativos — generalizado | [06 — Quantitativos e memórias](procedimentos-orcamento/references/06_quantitativos_e_memorias.md) |
| Prints marcados e auditoria visual por item | [06, seção 5 — Evidências vinculadas às parcelas e aos estados](procedimentos-orcamento/references/06_quantitativos_e_memorias.md#evidencias-visuais-por-item) |
| Operação e fechamento dos aplicativos | [07 — Computer use e encerramento](procedimentos-orcamento/references/07_computer_use_e_encerramento.md) |
| Conferência e entrega | [08 — Conferência, comparação e entrega](procedimentos-orcamento/references/08_conferencia_comparacao_e_entrega.md) |
| Agentes e retomada | [09 — Agentes e retomada](procedimentos-orcamento/references/09_agentes_e_retomada.md) |
| Pesquisa técnica e fontes | [10 — Boas práticas e fontes](procedimentos-orcamento/references/10_boas_praticas_e_fontes.md) |

## Rastreamento de tarefas

Usar Beads (`bd`) para rastreamento durável quando houver um workspace Beads nesta pasta, conforme as instruções do usuário e a habilidade `beads`. Não criar listas Markdown de tarefas como substituto desse rastreamento.

Procedimentos e memórias de cálculo solicitados pelo usuário são documentação técnica. Não usá-los como arquivos de status ou listas de tarefas pendentes.
