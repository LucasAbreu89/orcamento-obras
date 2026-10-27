# Esquema adaptável da planilha de levantamento

Este é um modelo de campos, não uma exigência de refazer o layout existente. Não é uma planilha calculada. O agente cria/adapta o arquivo real seguindo a habilidade de planilhas disponível e os procedimentos técnicos.

## Principal

| Campo | Tipo e regra |
|---|---|
| Item | Texto original; conservar zeros, subitens e ordem |
| Serviço | Descrição integral recebida |
| Unidade | Unidade original; conversões só com justificativa |
| Quantidade recebida | Preservar nome, valores, fórmulas e vazios originais; não substituir pelo novo levantamento |
| QTD LEVANTADA | Coluna própria, com fórmula para o resultado de nossa memória independente; estado explícito se incompleta |
| Estado | CONFIRMADO, ESTIMATIVA, SUBTOTAL, PENDENTE ou NÃO APLICÁVEL |
| Memória | Nome da aba/célula e link funcional quando suportado |
| Observação / dúvidas | Explicação curta e IDs da aba Pendências |

Se a comparação foi solicitada: `QTD <fonte de terceiro>`, `Diferença absoluta`, `Diferença %`, `Comparável?`, `Explicação da diferença`. Guardar os números de terceiro como transcrições de sua coluna correta, com fonte. Percentual deve ter denominador declarado; base zero ou alcance incompatível não gera percentual enganoso.

Uma planilha pode conter várias principais/listas. Inventariar todas as abas, inclusive ocultas; identificar função, tabelas/intervalos, alcance examinado e relação entre resumo, fonte, memória, revisão e lista independente. Não adotar automaticamente a aba ativa e não somar resumos às parcelas que já os alimentam.

Mapa de abas: `arquivo | aba | visibilidade | função | tabelas/intervalos | pavimento/setor/fase/revisão | relações/dependências | cobertura | inclusão/exclusão/pendência e motivo`.

Mapa de itens: `chave arquivo+aba+tabela/seção+item/linha | ID original | descrição | unidade | célula de quantidade original | célula QTD LEVANTADA | memória/resultado | estado`. Distinguir códigos repetidos sem alterar o ID recebido. As quantidades originais não dispensam medir e não alimentam nossa memória como atalho. Conservar também as fórmulas originais de custos/totais, sem redirecioná-las para nossa coluna por conta própria.

## Bases de ambientes/elementos

| Campos essenciais |
|---|
| ID, nome, pavimento/setor, estado físico, fonte/revisão/vista |
| Área indicada no projeto, área calculada e método em campos distintos |
| Contorno, parcelas, vãos e critério de atribuição das soleiras |
| Perímetro geométrico e comprimento efetivo do serviço em campos distintos |
| Altura de forro, altura até laje, cota absoluta/referência de nível e zonas |
| Elementos/trechos/faces, IDs e vínculos às evidências |
| Critério, estado, dúvidas e dependências |

Não pressupor uma única altura ou um mesmo contorno para todos os serviços do ambiente.

## Memória por item

Cabeçalho: ID original, descrição, unidade, estado físico, alcance, critério, fontes, resultado e estado. Preferir resultado em endereço padronizado quando possível, mantendo mapa explícito; `G8` é uma convenção possível, não obrigatória.

Tabela de parcelas: `ID | ambiente/elemento/face | fonte/vista | origem do dado | dimensões | unidade | fórmula | multiplicidade | acréscimo/desconto | resultado | estado`.

Incorporar prints reais marcados, legíveis e correspondentes a todas as áreas, faces, trechos ou ocorrências considerados. Mostrar inclusões/deduções e, para exclusão ou pendência, destacar a indicação ou a informação faltante nas fontes. Registrar por item quais imagens cobrem quais parcelas, com verificação de legibilidade, ou o motivo de não haver representação gráfica aplicável. Explicar junto à conta o que entrou, o que ficou fora e o que falta. Arquivo/hash ou imagem genérica sem vínculo não atendem à auditoria. Manter subtotal, ajustes e total separados. O resultado final verifica todas as dependências essenciais. Usar o [modelo de memória](MODELO_MEMORIA_SERVICO.md) e o [contrato de evidência visual](../references/06_quantitativos_e_memorias.md#evidencias-visuais-por-item).

Relatório de diagnóstico em cada memória: `descrição integral/escopo | constatação no projeto | problemas/categorias | evidências | soluções | base da resolução | estado por problema | informação específica faltante | impacto quantitativo | ressalva de execução | ação de revisão`. A consolidação central é complementar. Distinguir resolução demonstrada, viabilidade orçamentária por premissa e definição executiva pendente, conforme seção 7 da referência 06.

## Pendências

`ID | natureza | item(s) | ambiente/elemento | dúvida | fonte/revisão/vista consultada | evidência | dado necessário | parcela comprovada | alternativa/hipótese autorizada | impacto ou não determinado | células/dependências | estado | resolução/origem/data`.

A principal e a memória exibem o estado junto ao valor. Comentários complementam, mas não substituem esta aba. Campos numéricos desconhecidos não recebem zero fictício.

## Fontes

`ID | caminho | hash quando disponível | revisão | ID da representação | prancha/página ou Model/região ou layout/viewport | vista | layers/estado de visibilidade pertinente | cobertura examinada | método de leitura/medição | arquivo de evidência | limitações`.

## Registro técnico de aplicativos

Em dados técnicos da execução, manter `aplicativo | documento/caminho/ID | já estava aberto? | aberto pela tarefa? | original/cópia | alterações da tarefa | salvo em | evidência | fechado? | limitação`.

Esse registro serve à preservação e ao fechamento correto dos documentos, sem capturar conteúdo alheio ao trabalho. Não é uma lista Markdown de tarefas ou memória de sessão.

## Tipos e validação

Quantidades são números nativos; unidades e observações são campos próprios. Exibição brasileira é formatação/localidade. Fórmulas de subtotal não comprovam completude: testar entradas e estados essenciais antes do resultado final. A entrega deve ser salva e reaberta, com verificação real de valores, vínculos, imagens e recursos preservados.
