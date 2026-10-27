# 03 — Dúvidas, dependências e continuidade

## 1. Regra operacional

Falta de uma definição técnica não exige devolver o trabalho ao usuário antes de terminar o restante. Consultar fontes e decisões existentes; se a dúvida persistir, registrá-la na planilha, sinalizar as parcelas dependentes e continuar os serviços independentes. Ao final, entregar o trabalho possível e as perguntas localizadas para resolução posterior.

Essa regra não permite inventar medidas, contornar permissões ou afirmar conclusão integral. Uma limitação real de acesso ou ferramenta pode impedir uma operação; registrar exatamente o que ela afeta, fazer o restante e entregar o alcance possível.

## 2. Resolver com evidência antes de registrar a falta

1. Localizar no catálogo a fonte provável: planta, ampliação, corte, elevação, detalhe, quadro, memorial ou decisão do usuário.
2. Conferir revisão, unidade e estado físico; verificar se a aparente dúvida é conflito entre existente/proposto, medição/compra ou duas vistas do mesmo elemento.
3. Inspecionar a região e suas referências. Em falha de leitura/UI, adaptar a abordagem de forma limitada; não repetir indefinidamente o mesmo clique, exportação ou extração. Após até três tentativas com a mesma falha, registrar o impedimento e seguir outra parte.
4. Havendo mais de uma interpretação tecnicamente possível, não escolher pela proximidade com um total desejado. Registrar alternativas e seus efeitos quando calculáveis.
5. Continuar o lote. Não enviar perguntas repetidas durante o processo por dúvidas que podem ficar registradas. Respostas espontâneas do usuário devem ser incorporadas sem refazer o que não mudou.

## 3. Registro obrigatório na planilha

A aba `Pendências` contém uma linha por informação necessária, com IDs estáveis como `D001`. Vários itens podem depender da mesma dúvida.

| Campo | Conteúdo |
|---|---|
| ID e natureza | Falta de dado, conflito, critério, acesso ou validação não disponível |
| Itens/ambientes/elementos | IDs afetados e células de resultado |
| Dúvida objetiva | O que falta decidir ou comprovar |
| Fonte consultada | Caminho, revisão, prancha/página, vista/detalhe e evidência |
| Dado necessário | Dimensão, altura, prazo, material, estado, alcance ou critério |
| Parcela comprovada | O que já se pode afirmar e onde está sua memória |
| Alternativas/hipótese | Cenários separados; indicar se algum foi autorizado |
| Impacto | Quantidade/diferença calculável ou `não determinado`, sem precisão inventada |
| Dependências | Itens, bases, fórmulas, imagens e comparações a atualizar |
| Estado/resolução | Aberta, respondida ou resolvida por fonte; decisão, origem e data |

Se o Excel ainda não puder ser aberto, guardar o registro estruturado em `08_dados_tecnicos/` e integrá-lo à aba quando a ferramenta permitir. Se o acesso permanecer impossível, entregar o registro ao lado do arquivo disponível e declarar a limitação; não dizer que a aba foi criada.

Não esconder a falta somente em comentário. Principal e memória mostram o estado junto à quantidade, com referência a `D001` etc. O comentário pode complementar a explicação curta.

## 4. Significado dos resultados

| Estado | Uso correto |
|---|---|
| CONFIRMADO | Todas as entradas e critérios necessários ao resultado do alcance estão demonstrados |
| ESTIMATIVA | Método aproximado autorizado ou compatível com o pedido preliminar, com premissas e limite explícitos |
| SUBTOTAL | Parcelas comprovadas conhecidas, mas falta parte do mesmo item |
| PENDENTE | Não há base suficiente para resultado final; dúvida e dependências identificadas |
| NÃO APLICÁVEL | Exclusão comprovada do alcance, com justificativa; diferente de informação ausente |

`0` só significa ausência medida/comprovada pelo critério do item. `1 VB` só significa pacote contratualmente definido. Texto `a definir` isolado não é registro suficiente: mostrar motivo, fonte consultada e dado necessário.

Não somar cenários alternativos. Um total conhecido de uma família sem distribuição por tipo deve ficar na base da família; os itens de tipo ficam dependentes, sem repetir esse total em cada linha. Prazo desconhecido impede quantidade final em mês, mas não a medição das proteções por área. Altura ausente de um pano não impede contar portas ou medir piso em outro setor.

## 5. Dependências e atualização

Representar o vínculo técnico, por exemplo:

```text
D001: altura da divisória P03
→ base P03.H
→ área de divisória ITEM X
→ acabamento ITEM Y
→ principal e comparação dos itens X/Y
```

As fórmulas devem propagar incompletude. Uma soma que ignora texto não pode fazer uma memória pendente parecer completa. Conservar subtotal em campo próprio e sinalizar o alcance dos totais gerais. Não somar unidades diferentes para criar um total de quantidades sem significado.

Quando chegar a definição, registrar a decisão e sua origem, atualizar as bases, recalcular os dependentes e verificar as imagens/explicações. Manter o vínculo à dúvida resolvida para auditoria. Não apagar a evidência do conflito para fazer a versão final parecer que sempre esteve definida.

## 6. Fechamento do lote

Conferir que todos os itens solicitados receberam resultado e estado, ou pendência explícita. Consolidar as dúvidas que realmente alteram o levantamento, com a indicação de quais projetos/vistas o usuário precisa consultar. Entregar primeiro as partes validadas; não transformar a consolidação em uma exigência de resposta antes da entrega.

Continuidade refere-se ao trabalho autorizado durante a sessão. Não criar agendamento, prometer execução infinita ou atividade após o turno sem solicitação. Usar [09](09_agentes_e_retomada.md) para retomar depois com as fontes e dependências preservadas.
