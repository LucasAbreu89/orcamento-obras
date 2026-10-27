# Procedimento reutilizável para levantamento de obras

Esta pasta contém uma **skill local do Codex**, procedimentos técnicos e modelos para transformar uma pasta de projetos e uma lista de serviços em quantitativos com memória de cálculo. O mesmo fluxo atende reforma e construção nova, conforme as disciplinas e informações disponíveis.

## Como pedir uma nova execução

Envie uma mensagem como esta, substituindo os dois caminhos:

```text
Use $procedimentos-orcamento.
Projetos: /caminho/da/obra
Planilha de serviços: /caminho/da/obra/servicos.xlsx

Faça o levantamento dos itens da planilha, com memória por item,
imagens reais dos projetos marcadas e fórmulas na principal.
Registre dúvidas na planilha e continue o restante.
```

Também é possível indicar diretamente o arquivo `SKILL.md` desta pasta se a skill ainda não aparecer no seletor da sessão. Para uma tarefa menor, informe o alcance: por exemplo, apenas catalogar os documentos, medir os ambientes ou comparar os itens 1 a 10. Não é necessário preencher os modelos manualmente.

Neste workspace, a skill está registrada por um link em `.agents/skills/procedimentos-orcamento`, apontando para esta pasta. Há uma única cópia dos procedimentos. O registro é local a esta árvore de projetos; não foi feita instalação global.

Projetos e planilhas podem estar em qualquer pasta acessível ao agente. Cada obra conserva suas próprias fontes, evidências, decisões e entregas. Não reutilizar números da LCA em outra obra. Para um projeto fora deste workspace, indicar o caminho completo desta skill ou disponibilizar a pasta como skill naquele ambiente.

## O que acontece, em ordem

1. Identificar a pasta e o Excel corretos, preservar os originais, registrar as fontes e os documentos já abertos nos aplicativos.
2. Examinar os projetos e criar um catálogo: conteúdo de cada arquivo, revisão, plantas e vistas, inclusive regiões do Model, layouts e combinações pertinentes de camadas. Registrar o que foi examinado e onde encontrar cada informação.
3. Abrir a planilha e mapear todas as abas/listas. Preservar as quantidades recebidas, reconhecer itens, unidades e fórmulas, e definir os critérios de medição por serviço. Números já preenchidos não dispensam o levantamento independente.
4. Levantar as bases necessárias de ambientes: áreas, perímetros, alturas e elementos. Auditar vãos, faces e interfaces.
5. Quantificar cada serviço, produzir sua memória com imagem marcada, parcelas, fontes e fórmulas, e criar a coluna própria `QTD LEVANTADA`, vinculada ao resultado nas abas de origem. Manter a coluna original para eventual comparação.
6. Conferir cobertura, unidades, duplicações, fórmulas e resultados. Se houver uma base de terceiro, comparar alcances compatíveis e investigar divergências.
7. Salvar, recalcular e reabrir a planilha, verificar as imagens e a leitura dos valores, fechar os documentos abertos pelo trabalho e entregar os links.

As regras completas e os critérios de passagem de cada etapa estão em [00 — Fluxo mestre](references/00_fluxo_mestre.md). O índice técnico está no [SKILL.md](SKILL.md).

## Quando faltar uma informação

A execução continua nos itens independentes. A aba `Pendências` registra a dúvida, o item, o projeto/vista a consultar, a informação necessária e o efeito sobre a conta. A principal e a memória mostram se o resultado é completo, estimado, subtotal ou pendente. Não há preenchimento fictício de zero para fazer a planilha parecer completa.

O trabalho pode terminar como **entrega com pendências**: todas as partes possíveis foram feitas, e o restante está localizado para resolução posterior. A continuidade não significa que o agente possa operar sem permissões, medir sem ferramentas ou continuar trabalhando depois do encerramento da sessão por conta própria.

## Organização das saídas

Por padrão, a execução cria uma pasta dentro da obra:

```text
levantamento-orcamento/execucoes/<data_hora>/
  01_catalogo/          conteúdo e índice das fontes
  02_bases_ambientes/   medidas e elementos dos ambientes
  03_memorias_servicos/ dados e memórias por item
  04_evidencias/        recortes reais e marcações
  05_planilhas/         arquivo de trabalho e entrega
  06_conferencia/       comparação e validação técnica
  07_backups/           cópias dos arquivos recebidos
  08_dados_tecnicos/    inventário, critérios e dependências
```

A planilha final contém a principal preservada, memórias por item, bases utilizadas, fontes e pendências. Os modelos são adaptáveis: não é necessário remodelar uma planilha boa apenas para imitar um layout.

## Preparação opcional por script

O agente pode executar, com Python 3, o auxiliar desta pasta:

```bash
python3 scripts/preparar_projeto.py --projeto "/caminho/da/obra" --planilha "/caminho/servicos.xlsx"
```

Esse comando inventaria arquivos, registra hashes e cria cópias da planilha. Ele **não calcula quantitativos**, não verifica células e não controla CAD. Essas atividades seguem os procedimentos e usam as ferramentas disponíveis na sessão. A planilha copiada inicialmente é apenas uma base de trabalho.

## Computer use e fechamento de arquivos

Ao usar CAD, PDF ou Excel, o agente identifica o documento, opera em cópias quando houver alterações de conferência, salva e fecha o que abriu assim que concluir o uso. Mantém os documentos que você já tinha abertos e não descarta alterações suas. No fim pode deixar somente a entrega aberta para revisão, se isso for útil.

## Pesquisa incorporada

As referências incluem TCU, CAIXA/SINAPI, RICS e buildingSMART. Elas ajudam a definir rastreabilidade, cobertura e critérios; não impõem automaticamente a uma obra privada regras de contratação pública ou convenções britânicas. As fontes, edições, locais de consulta e limitações de acesso estão em [10 — Boas práticas e fontes](references/10_boas_praticas_e_fontes.md).

Esta pasta é um pacote de skill portátil; não depende de publicar um plugin ou instalar um aplicativo CAD novo. A descoberta local por `.agents/skills` e os links simbólicos são documentados pelo [guia oficial de skills](https://learn.chatgpt.com/docs/build-skills). A disponibilidade dos aplicativos e ferramentas deve ser conferida em cada execução.
