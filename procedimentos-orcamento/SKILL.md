---
name: procedimentos-orcamento
description: Levantar quantitativos de reforma ou construção a partir de uma pasta de projetos e uma planilha de serviços, com catálogo, cálculos rastreáveis, imagens marcadas e memórias vinculadas por item. Usar também para conferir ou retomar esse levantamento.
---

# Levantamento de quantitativos de obras

Transforme os projetos e a lista de serviços fornecidos em uma planilha conferível. Receba os caminhos da pasta do projeto e do Excel pela mensagem; não exija formulário, configuração manual ou questionário inicial quando o contexto permitir começar.

Leia primeiro [00 — Fluxo mestre](references/00_fluxo_mestre.md). Carregue as demais referências quando entrar na etapa correspondente, sem ler todos os projetos ou procedimentos novamente a cada item.

## Invariantes

- Catalogue o conteúdo efetivamente examinado antes de calcular. Inventário de arquivos não comprova leitura. Em pedido apenas de catálogo, não acrescente cálculos.
- Um arquivo de projeto pode conter várias plantas/vistas, distribuídas no Model, layouts e combinações de camadas. Um Excel pode conter várias abas e listas de serviços. Mapear essa estrutura e registrar a cobertura por representação/aba; não presumir que a primeira vista ou aba represente todo o arquivo.
- Preserve originais e revisões. Separe dados de cada obra; exemplos e resultados de outra obra não definem medidas, perdas, alturas ou critérios desta.
- Identifique junto ao valor: indicação do projeto, cálculo por cotas, coordenadas, contagem, estimativa ou comando nativo realmente executado. Mostre contorno, faces e vãos antes da conta.
- Incorpore à memória de cada item físico um print real do projeto, marcado para mostrar exatamente as áreas, panos, percursos ou ocorrências considerados, com os mesmos IDs das parcelas. Exclusões, conflitos e pendências também precisam de evidência visual vinculada à decisão quando a fonte permitir; arquivo, hash ou imagem genérica não substituem essa explicação. Aplique o [contrato de evidência por item](references/06_quantitativos_e_memorias.md#evidencias-visuais-por-item) e confira sua cobertura em [08](references/08_conferencia_comparacao_e_entrega.md).
- Trabalhe nos itens autorizados. Cada serviço original recebe sua memória e fórmula de vínculo à principal; sugestões ficam separadas e só entram se solicitadas.
- Preserve intactas as colunas de quantidade recebidas, inclusive fórmulas e vazios. Faça o levantamento independente mesmo quando já houver números; crie `QTD LEVANTADA` para nossos resultados e vínculos. Quantidades originais servem de referência para comparação compatível, sem substituir a medição.
- Dúvida técnica não encerra o lote: registre-a na aba `Pendências`, sinalize resultados dependentes e continue os itens independentes. Não preencha desconhecidos com zero, nem apresente subtotal como quantidade completa. Aplique [03](references/03_duvidas_e_continuidade.md).
- Use computer use para inspeção/operação nativa quando solicitado ou necessário, conforme as ferramentas e aplicativos realmente disponíveis. Um operador controla a UI; um autor consolida a planilha. Salve e feche documentos abertos pela tarefa logo após usá-los; preserve os que já estavam abertos. Aplique [07](references/07_computer_use_e_encerramento.md).
- Para operações reais com PDF e planilhas, aplique as habilidades disponíveis correspondentes. Escolha ferramentas que preservem os recursos do arquivo. Se o usuário exigir execução exclusivamente pela interface, respeite essa escolha. Não invente acesso, medição CAD, recálculo ou teste no Excel.
- Entregue o trabalho validado mesmo com pendências técnicas explícitas. Limitação de acesso, permissão ou ferramenta não autoriza contorná-la; continue o que for possível e descreva o alcance entregue.

## Rotas

| Etapa | Ler quando |
|---|---|
| [01 — Catalogação](references/01_catalogacao_projetos.md) | Receber/revisar as fontes, identificar plantas, detalhes e revisões |
| [02 — Planilha e escopo](references/02_planilha_escopo_e_mapeamento.md) | Abrir o Excel e mapear itens, unidades e abas |
| [03 — Dúvidas e continuidade](references/03_duvidas_e_continuidade.md) | Uma informação faltar ou conflitar |
| [04 — Áreas](references/04_calculo_de_areas.md) | Consultar, calcular ou conferir superfícies |
| [05 — Perímetros e alturas](references/05_perimetros_e_alturas.md) | Medir contornos, comprimentos, forro, laje e panos |
| [06 — Quantitativos e memórias](references/06_quantitativos_e_memorias.md) | Medir serviços; marcar prints por item, inclusive exclusões/pendências; vincular parcelas |
| [07 — Computer use e encerramento](references/07_computer_use_e_encerramento.md) | Abrir ou controlar aplicativos/documentos |
| [08 — Conferência e entrega](references/08_conferencia_comparacao_e_entrega.md) | Comparar bases, recalcular, salvar e reabrir a entrega |
| [09 — Agentes e retomada](references/09_agentes_e_retomada.md) | Delegar, reduzir releituras ou retomar uma execução |
| [10 — Boas práticas e fontes](references/10_boas_praticas_e_fontes.md) | Definir critérios, consultar referências e avaliar seus limites |

Os modelos em `assets/` são bases de saída, a adaptar ao arquivo recebido. O auxiliar [preparar_projeto.py](scripts/preparar_projeto.py) cria uma execução isolada, inventário e cópias do Excel; não lê projetos, mede geometria nem substitui as etapas da skill. Use `--help` antes da primeira execução. O guia humano é [LEIA_PRIMEIRO.md](LEIA_PRIMEIRO.md).
