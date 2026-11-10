# 09 — Agentes, retomada e revisões de projeto

## 1. Quando delegar

Padrão: um agente só. Cada subagente relê contexto e fontes; vale a pena quando o ganho é claro:
- contagem volumosa e independente (por exemplo, uma família de luminárias em todas as vistas);
- segunda medição, sem acesso à primeira, dos itens curva A;
- verificação independente de uma entrega já gerada.

O pedido ao subagente traz: objetivo e alcance, fontes e revisões, critério, prefixo de IDs, pasta de saída própria e formato de retorno (parcelas com origem, evidências, pendências). Nunca uma meta numérica. Subagente não grava a planilha nem o `levantamento.json` e não opera a interface.

**Um autor** grava o `levantamento.json` e a planilha; **um operador** usa a interface. Ao integrar, o autor confere duplicações pela identidade física (local, família, face, estado), não só pelo prefixo do ID.

## 2. Retomada

O estado do trabalho está no `dados/levantamento.json`, no `fontes/inventario.json` (hashes), no snapshot e na última entrega.

1. Ler o pedido atual e as decisões posteriores do usuário.
2. Localizar a execução e a entrega em uso, conferindo o conteúdo (nunca escolher pela data ou pelo nome).
3. Conferir os hashes das fontes: o que mudou invalida as extrações, bases e itens que dependem dele.
4. Ler Pendências e Premissas e incorporar as respostas.
5. Reaproveitar as medições válidas, medir o que falta, gerar e validar de novo.

Medição válida não é refeita só porque a sessão mudou; resultado antigo não vale depois de nova revisão de projeto.

## 3. Nova revisão de projeto

1. Inventariar os arquivos novos e comparar os hashes.
2. Para DXF, `cad.py comparar` lista, por camada, as entidades acrescentadas e removidas e a região afetada; para PDF, comparar carimbo e páginas.
3. Achar as bases e os itens afetados pelas referências de fonte no `levantamento.json`.
4. Remedir só o afetado e registrar antes e depois por item, com o motivo.
5. Gerar a planilha, validar e entregar um resumo das alterações.

## 4. Rastreamento

Se houver workspace Beads na pasta, usar `bd` para tarefas e dependências. Listas de tarefas em Markdown não substituem esse rastreamento; pendências técnicas ficam na aba Pendências.
