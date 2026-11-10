# 09 — Agentes, modelos, retomada e revisões de projeto

## 1. Agentes e modelos por tarefa

O agente que recebe o pedido é o **orquestrador**. Ele executa a primeira linha da tabela e delega as demais a subagentes criados com o modelo e o effort indicados. O Claude Fable não é usado.

| Tarefa | Nível | OpenAI | Anthropic |
|---|---|---|---|
| Orquestrar: escopo e checkpoint, critérios, premissa × pendência, integração do `levantamento.json`, geração, recálculo e validação da planilha com a correção dos erros apontados, conferência física ([08 §2](08_conferencia_comparacao_e_entrega.md)), operação de CAD ou Excel pela interface ([07 §3](07_ferramentas_e_aplicativos.md)) e mensagem final | topo | `gpt-6.1-sol` | `claude-opus-5-5` |
| Medir geometria e quantificar (etapas 4 e 5): áreas, comprimentos, alturas, faces, vãos, volumes, percursos | topo | `gpt-6.1-sol` | `claude-opus-5-5` |
| Segunda medição independente, sem acesso à primeira, quando a conferência pedir ([08 §2](08_conferencia_comparacao_e_entrega.md)) | topo | `gpt-6.1-sol` | `claude-opus-5-5` |
| Catalogar as fontes (etapa 1) | médio | `gpt-6.1-terra` | `claude-sonnet-5-5` |
| Mapear a planilha (etapa 2) | médio | `gpt-6.1-terra` | `claude-sonnet-5-5` |
| Contar peças por blocos, símbolos ou quadros: pontos, louças, luminárias, equipamentos, esquadrias | médio | `gpt-6.1-terra` | `claude-sonnet-5-5` |
| Revisar a entrega gerada: prints e memórias ([08 §5](08_conferencia_comparacao_e_entrega.md)) | médio | `gpt-6.1-terra` | `claude-sonnet-5-5` |
| Operar scripts em lote: preparação, conversões, inventários, extrações e renderização de prints já definidos | leve | `gpt-6-luna` | `claude-haiku-5-5` |

Effort por nível: topo, `ultra` na OpenAI e `xhigh` na Anthropic; médio, `high`; leve, `medium`. Para trocar um modelo, muda-se só esta tabela. Vale a coluna do fornecedor em que a chamada está rodando. Os nomes seguem o catálogo de cada fornecedor: o leve da OpenAI é `gpt-6-luna`, sem versão 6.1.

- **Modelo da chamada.** A chamada começa no modelo de topo. Se começar em outro, o agente segue como orquestrador e registra isso em `limitacoes`.
- **Contexto novo.** O subagente recebe o pedido completo e não herda a conversa do orquestrador: modelos diferentes não compartilham cache, e conversa herdada é relida a cada chamada. No Codex, `spawn_agent` com `model` e `reasoning_effort`, sem `fork_turns`; no Claude Code, agente novo com `model`, nunca `fork`.
- **Segunda medição.** Quando o ambiente dá acesso aos dois fornecedores, ela usa o que não fez a primeira.
- **Sem ferramenta de subagentes**, o agente executa todas as tarefas no modelo da chamada e registra isso em `limitacoes`.

O pedido ao subagente traz: objetivo e alcance, fontes e revisões, critério, prefixo de IDs, pasta de saída própria e formato de retorno (parcelas com origem, evidências, pendências). Nunca uma meta numérica. Subagente não grava a planilha nem o `levantamento.json` e não opera a interface.

O orquestrador é o único autor do `levantamento.json` e da planilha e o único operador da interface. Ao integrar, ele confere duplicações pela identidade física (local, família, face, estado), não só pelo prefixo do ID.

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
