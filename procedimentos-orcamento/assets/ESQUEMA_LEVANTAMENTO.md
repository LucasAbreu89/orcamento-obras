# Esquema do `levantamento.json`

`dados/levantamento.json` é a fonte de verdade do levantamento. O agente registra nele itens, parcelas, critérios, premissas, pendências e evidências; `gerar_planilha.py` monta a planilha a partir dele e `validar_entrega.py` confere a planilha contra ele. Para mudar um resultado, muda-se o JSON e gera-se de novo; não se edita a planilha à mão.

`preparar_projeto.py` cria um esqueleto já com os caminhos e as listas detectadas. Caminhos relativos são resolvidos a partir da pasta da execução (a pasta que contém `dados/`).

## Estrutura

| Campo | Obrigatório | Conteúdo |
|---|---|---|
| `versao` | sim | `"levantamento/1"` |
| `obra` | sim | nome da obra |
| `planilha` | sim | caminhos e listas (abaixo) |
| `criterios` | não | `[{id, familia, regra, parametros, fonte}]`, IDs `C01`… |
| `fontes` | não | `[{id, arquivo, revisao, sha256, representacoes: [{id, titulo, localizador, leitura}]}]` |
| `premissas` | não | campos da aba Premissas ([03 §3](../references/03_pendencias_premissas_e_estados.md)), IDs `P001`… |
| `pendencias` | não | campos da aba Pendências ([03 §4](../references/03_pendencias_premissas_e_estados.md)), IDs `D001`… |
| `itens` | sim | um registro por item de escopo (abaixo) |
| `sugestoes` | não | serviços que faltam na lista: `[{id, servico, motivo, local, fonte, unidade, quantidade, itens_relacionados}]`; viram a aba Sugestões |
| `comparacao` | não | só quando pedida: `[{chave, referencia, fonte, classe, explicacao}]`, classe `comparável`, `comparável com ressalva`, `não comparável` ou `sem correspondência`; vira a aba Comparação |
| `limitacoes` | não | frases sobre o que não pôde ser feito ou verificado; aparecem no Resumo |

### `planilha`

| Campo | Conteúdo |
|---|---|
| `recebida` | arquivo recebido (só leitura) |
| `trabalho` | cópia de trabalho, nunca editada à mão; base da geração |
| `entrega` | arquivo gerado |
| `snapshot` | snapshot da planilha recebida (`planilha.py snapshot`) |
| `modo` | `auto` (padrão), `mesmo_arquivo` ou `arquivo_separado` ([ESQUEMA_PLANILHA §5](ESQUEMA_PLANILHA.md)) |
| `listas` | `[{aba, linha_cabecalho, linha_final, colunas: {item, descricao, unidade, quantidade}, coluna_inicial_nova, linhas_ignoradas}]` |

Em cada lista, `linha_final` é opcional (obrigatória na prática quando há várias listas na mesma aba: o item pertence à lista cujo intervalo contém sua linha). `coluna_inicial_nova` é opcional (padrão: primeira coluna livre à direita do conteúdo da aba). `linhas_ignoradas` = `[{linha, motivo}]` para linhas com descrição e unidade que não são itens; as demais precisam de item.

### Item

| Campo | Obrigatório | Conteúdo |
|---|---|---|
| `chave` | sim | `aba!linha`, por exemplo `Orçamento!37`; a aba precisa estar em `listas` |
| `id` | sim | código original como texto (`"1.10"`) |
| `descricao`, `unidade` | sim | como recebidos |
| `natureza` | sim | `medivel`, `parametro`, `indireto` ou `fora_escopo` ([02 §3](../references/02_planilha_escopo_e_mapeamento.md)) |
| `estado` | sim | `CONFIRMADO`, `PREMISSA`, `SUBTOTAL`, `PENDENTE` ou `NÃO APLICÁVEL` ([03 §1](../references/03_pendencias_premissas_e_estados.md)) |
| `criterio` | não | ID em `criterios` |
| `premissas`, `pendencias`, `fontes` | não | listas de IDs |
| `parcelas` | conforme estado | tabela da conta (abaixo) |
| `evidencias` | conforme natureza | `[{arquivo, legenda, parcelas: [IDs]}]` |
| `sem_representacao_grafica` | não | motivo, quando o item não tem desenho aplicável |
| `texto` | recomendado | `{entrou, ficou_fora, falta}` em linguagem direta |
| `diagnostico` | não | `[{categoria, constatacao, solucao, base, estado, efeito}]`, só para problemas reais ([06 §6](../references/06_quantitativos_e_memorias.md)) |
| `observacao` | conforme estado | frase curta que aparece na principal |
| `aba_memoria` | não | nome da aba; se ausente, `ITEM <id>` |

### Parcela

| Campo | Conteúdo |
|---|---|
| `id` | `A01`, `D01`, `S03`, `E12`… (os mesmos IDs do print) |
| `descricao`, `local`, `estado_fisico` | texto |
| `dimensoes` | 1 a 3 números multiplicados entre si; `null` onde falta o dado |
| `valor` | alternativa a `dimensoes`: valor direto (coordenadas, comando nativo, transcrição, contagem); `null` se falta |
| `multiplicidade` | padrão 1 |
| `sinal` | `1` (soma) ou `-1` (dedução) |
| `unidade` | unidade do resultado da parcela |
| `origem` | `indicado`, `cotas`, `coordenadas`, `comando_nativo`, `contagem`, `medicao_grafica`, `premissa` ou `criterio_usuario` |
| `fonte` | ID da representação (`F002.V01`) ou localizador |
| `refs` | IDs de premissas/pendências ligados à parcela |

Resultado da parcela = produto das dimensões (ou valor) × multiplicidade × sinal. Parcela com `null` fica sem valor e rebaixa o item para `SUBTOTAL`, sem virar zero.

## Regras conferidas pelos scripts

Erros (impedem a geração):
- `chave` repetida, mal formada, de aba fora das listas ou de linha fora do intervalo das listas; `estado`, `natureza` ou `origem` inválidos;
- parcela sem `dimensoes` nem `valor`, com mais de 3 dimensões, com `sinal` diferente de 1 e −1, com ID repetido ou com unidade diferente da do item;
- `PENDENTE` ou `SUBTOTAL` sem pendência; `PREMISSA` sem premissa nem parcela de `medicao_grafica`; `CONFIRMADO` que dependa de premissa ou de medição gráfica; `NÃO APLICÁVEL` sem `observacao`;
- `CONFIRMADO` ou `PREMISSA` sem parcelas, ou com parcela sem valor;
- referência a premissa ou pendência inexistente;
- item `medivel` (em qualquer estado) ou `parametro` (fora de `NÃO APLICÁVEL`) sem evidência e sem `sem_representacao_grafica`; arquivo de evidência inexistente; parcela que não aparece em nenhuma evidência;
- sugestão sem id, serviço ou motivo; comparação com chave inexistente ou classe inválida; listas repetidas ou com `linha_final` menor que o cabeçalho.

Avisos: item mensurável sem critério; item físico com valor justificado só por `sem_representacao_grafica`; evidência citando parcela inexistente; texto "o que entrou/ficou fora/falta" ausente em item físico.

O validador da entrega ainda acusa linha das listas com descrição e unidade sem item no JSON e sem registro em `linhas_ignoradas`.

## Exemplo fictício

```json
{
  "versao": "levantamento/1",
  "obra": "Obra exemplo",
  "planilha": {
    "recebida": "planilha/ORIGINAL_servicos.xlsx",
    "trabalho": "planilha/servicos_TRABALHO.xlsx",
    "entrega": "planilha/servicos_LEVANTAMENTO.xlsx",
    "snapshot": "fontes/snapshot_planilha.json.gz",
    "modo": "auto",
    "listas": [{"aba": "Orçamento", "linha_cabecalho": 4,
                "colunas": {"item": "A", "descricao": "B", "unidade": "C", "quantidade": "D"}}]
  },
  "criterios": [{"id": "C01", "familia": "Pintura de paredes", "regra": "Área por face até o forro; vãos descontados",
                 "parametros": {"vaos": "descontar todos", "requadros": "não incluídos"}, "fonte": "Padrão do pacote (11), confirmado no checkpoint"}],
  "premissas": [{"id": "P001", "itens": ["2.1"], "parametro": "Altura do forro da sala", "valor": "2,70 m",
                 "base": "Corte BB indica 2,70 m no ambiente vizinho com o mesmo forro", "impacto": "±0,10 m = ±1,7 m²",
                 "confirmar_com": "Projetista", "situacao": "adotada"}],
  "pendencias": [],
  "itens": [{
    "chave": "Orçamento!12", "id": "2.1", "descricao": "Pintura acrílica em paredes internas", "unidade": "m²",
    "natureza": "medivel", "estado": "PREMISSA", "criterio": "C01", "premissas": ["P001"],
    "parcelas": [
      {"id": "S01", "descricao": "Parede norte, face interna", "local": "Sala", "dimensoes": [4.20, 2.70], "unidade": "m²", "origem": "cotas", "fonte": "F001.V01", "refs": ["P001"]},
      {"id": "S02", "descricao": "Parede leste, face interna", "local": "Sala", "dimensoes": [3.10, 2.70], "unidade": "m²", "origem": "cotas", "fonte": "F001.V01", "refs": ["P001"]},
      {"id": "V01", "descricao": "Porta P1", "local": "Sala", "dimensoes": [0.80, 2.10], "sinal": -1, "unidade": "m²", "origem": "indicado", "fonte": "quadro de esquadrias F001.V07"}
    ],
    "evidencias": [{"arquivo": "evidencias/item_2.1.png", "legenda": "Faces S01–S02 em azul; vão V01 hachurado", "parcelas": ["S01", "S02", "V01"]}],
    "texto": {"entrou": "Faces internas S01 e S02 até o forro", "ficou_fora": "Porta V01 (vão descontado)", "falta": "Confirmar altura do forro (P001)"},
    "observacao": "Altura do forro adotada (P001)"
  }]
}
```
