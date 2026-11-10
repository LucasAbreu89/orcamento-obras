# 03 — Pendências, premissas e estados

Fonte única dos estados do resultado, da escada de resolução e das abas Pendências e Premissas.

## 1. Estados do resultado

| Estado | Quando usar | `QTD LEVANTADA` |
|---|---|---|
| `CONFIRMADO` | Todas as entradas vêm dos projetos e do critério acordado; a conta é reproduzível | valor |
| `PREMISSA` | Calculado, mas depende de premissa registrada (`P###`) ou de medição aproximada (imagem, PDF raster) | valor |
| `SUBTOTAL` | Parte do item medida; falta parte identificada (`D###`) | vazio; subtotal na memória |
| `PENDENTE` | Sem base para quantificar (`D###`) | vazio |
| `NÃO APLICÁVEL` | Não quantificado neste levantamento, com motivo: fora do escopo pedido, custo indireto, serviço comprovadamente inexistente na obra | vazio |

Zero nunca expressa ausência: ausência comprovada é `NÃO APLICÁVEL` com a evidência. "A definir" sozinho não é registro.

## 2. Escada de resolução

Para cada lacuna, subir a escada e parar no primeiro degrau que resolve:

1. Projeto da disciplina, em todas as representações catalogadas.
2. Outros projetos, cortes, detalhes, quadros, memorial e caderno de encargos.
3. Critério do usuário, do contrato ou da composição indicada na planilha; na falta deles, o padrão de [11](11_criterios_padrao.md) (precedência em [10](10_boas_praticas_e_fontes.md)).
4. **Premissa técnica usual** → estado `PREMISSA`, registrada na aba Premissas.
5. **Pendência** → `PENDENTE` ou `SUBTOTAL`, registrada na aba Pendências.

A escolha entre os degraus 4 e 5:

- **Pendência** sempre que a resposta depender de decisão do cliente ou do projetista: escopo, especificação, solução executiva.
- Nos demais casos, estimar a faixa plausível do dado e o efeito dela na quantidade do item:
  - efeito de até **10%** (limite ajustável no checkpoint) → **premissa**;
  - efeito acima do limite em item **curva A** → **pendência**;
  - efeito acima do limite em item **curva B ou C** → **premissa**, com a faixa registrada no campo Impacto.
- Sem preços na planilha (sem curva ABC), vale só o limite de 10%.

O **nível de premissas** é combinado no checkpoint:

| Nível | Regra |
|---|---|
| `conservador` | só degraus 1 a 3; o resto vira pendência |
| `padrão` | a regra acima (vale quando nada for dito) |
| `amplo` | premissa para tudo que for estimável; pendência só para decisões do cliente |

Entre interpretações plausíveis, nunca escolher pela proximidade com um total esperado: registrar os cenários e o efeito de cada um.

## 3. Aba Premissas

| Campo | Conteúdo |
|---|---|
| ID | `P001`… |
| Itens | IDs dos itens afetados |
| Parâmetro | o que foi adotado (ex.: altura da divisória até a laje) |
| Valor adotado | número e unidade |
| Base | por que esse valor: elemento vizinho, norma, prática usual, decisão do usuário |
| Impacto | efeito estimado na quantidade (ex.: ±0,30 m na altura = ±6 m²) |
| Confirmar com | projetista, cliente, engenharia ou vistoria |
| Situação | adotada, confirmada ou substituída (com data e origem) |

As premissas de escopo do checkpoint também entram aqui.

## 4. Aba Pendências

| Campo | Conteúdo |
|---|---|
| ID | `D001`… |
| Natureza | falta de dado, conflito entre fontes, decisão de escopo ou critério, acesso ou ferramenta |
| Itens | IDs dos itens afetados |
| Pergunta | pergunta objetiva, pronta para enviar ao projetista ou ao cliente |
| Fonte consultada | arquivo, revisão, prancha ou vista |
| Já comprovado | parcela medida e onde está |
| Opções e efeito | cenários com a quantidade de cada um, quando calculável |
| Impacto | quantidade ou "não determinado" |
| Responsável | quem responde |
| Situação | aberta, respondida ou resolvida (decisão, origem e data) |

Ordenar por impacto. Uma pendência pode afetar vários itens.

## 5. Propagação

- Parcela sem valor deixa o item em `SUBTOTAL`; as fórmulas da memória ([ESQUEMA_PLANILHA §2](../assets/ESQUEMA_PLANILHA.md)) fazem esse rebaixamento sozinhas.
- `SEERRO(…;0)` ou `IFERROR(…,0)` nunca escondem falta de dado. Soma que ignora texto não prova completude.
- O total conhecido de uma família sem distribuição por tipo fica na base da família; os itens por tipo ficam dependentes, sem repetir o total em cada linha.
- Quando chega uma resposta: registrar a decisão e a origem, atualizar bases e parcelas no `levantamento.json` e gerar de novo a planilha e os prints afetados. O histórico da pendência permanece.

## 6. Perguntas ao usuário

As paradas planejadas são o checkpoint de escopo e a entrega. Durante o lote, dúvidas técnicas vão para a aba Pendências, não para o chat. Respostas espontâneas do usuário são incorporadas sem refazer o que não mudou. Falha de leitura ou de interface: no máximo três tentativas da mesma abordagem; depois registrar e seguir com outra parte.
