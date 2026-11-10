# 02 — Planilha, escopo e mapeamento

## 1. Preservar e fotografar

`preparar_projeto.py` faz o backup, a cópia de trabalho e roda `planilha.py snapshot` e `planilha.py mapear`. O snapshot guarda valores e fórmulas de todas as células: é contra ele que o validador prova, no fim, que nada da planilha recebida mudou. XLS, ODS e CSV são convertidos para XLSX com o LibreOffice, e a conversão é registrada. Macros nunca são habilitadas. Se o usuário pedir gravação no próprio arquivo, conferir antes da gravação final se ele mudou desde o snapshot.

## 2. Mapear abas e listas

`planilha.py mapear` lista todas as abas (inclusive ocultas), dimensões, células mescladas, fórmulas, cabeçalho provável com as colunas de item, descrição, unidade, quantidade e preço, e os recursos do arquivo (imagens, gráficos, macros, vínculos externos). Conferir e completar:

- **Função de cada aba:** lista de serviços, outro pavimento ou etapa, resumo, composição, memória, comparação, revisão anterior. Aba não é excluída pelo nome; o motivo de inclusão ou exclusão fica registrado. O esqueleto do JSON só sugere abas visíveis; listas em abas ocultas aparecem em `_listas_ocultas_detectadas` para decisão.
- **Relações:** um resumo e as abas que o alimentam não são quantidades a somar. Rastrear as fórmulas para separar repetição de lista independente.
- **Várias listas na mesma aba:** cada uma entra em `planilha.listas` com sua `linha_cabecalho` e uma `linha_final`; o item pertence à lista cujo intervalo contém a sua linha.
- **Linhas:** título ou agrupador não é item. Linha com descrição e unidade que não seja item (subtotal informativo, observação) vai para `linhas_ignoradas` com o motivo; o validador acusa as demais que ficarem sem item.
- **Colunas de quantidade:** podem ser várias (original, revisada, de terceiro); cada uma é identificada pelo cabeçalho e pela fórmula, nunca pela posição. Com mais de uma, o esqueleto deixa `quantidade` vazia e lista as candidatas.

**Chave do item:** `aba!linha` (por exemplo, `Orçamento!37`). O ID original é texto (`1.10` ≠ `1.1`) e nunca é alterado; códigos repetidos se distinguem pela chave.

## 3. Natureza de cada item

| Natureza | Exemplos | Tratamento |
|---|---|---|
| `medivel` | piso, parede, forro, esquadria, ponto, tubo | medir nos projetos |
| `parametro` | tapume (perímetro do canteiro), limpeza final (área), proteções | calcular por regra declarada; parâmetro faltante, como o prazo, vira pendência |
| `indireto` | administração local, mobilização, equipe, consumos, ART, seguros | `NÃO APLICÁVEL` com o motivo "custo indireto — definir pela engenharia", salvo pedido |
| `fora_escopo` | disciplina ou aba excluída pelo usuário; projeto não fornecido e não contratado | `NÃO APLICÁVEL` com o motivo |

Agrupadores e títulos não entram no `levantamento.json`. Unidade `VB` com quantidade 1 só representa pacote definido; desconhecido não vira verba.

## 4. Preços e quantidades recebidas

Não há curva ABC. Preços e quantidades já preenchidas na planilha são ignorados: não ordenam o trabalho, não entram em memória, não servem de conferência e não indicam que o serviço existe na obra. A planilha pode ser um modelo padrão, com valores de outra obra. As colunas ficam intactas (§1) e só são lidas se o usuário pedir uma comparação ([08 §4](08_conferencia_comparacao_e_entrega.md)).

## 5. Mapa de especificações

Ligar cada item à forma como o projeto o identifica:

```text
item (chave, ID, descrição) → código ou tipo no projeto (PI-01, PT-03, P1, L4…)
→ onde aparece (quadro de acabamentos, legenda, quadro de esquadrias, camada, hachura, bloco)
→ ambientes ou elementos
```

Especificação divergente (marca, dimensão, material) é registrada no diagnóstico do item. Especificação do projeto sem item na lista vai para `sugestoes` (aba Sugestões). Item sem correspondência no projeto vira pendência ou `NÃO APLICÁVEL` comprovado.

## 6. Unidades

Normalizar só unidades equivalentes (`m2` = `m²`). Nunca trocar `m` por `m²` para encaixar uma conta: a incompatibilidade vira pendência, com a parcela que já se pode medir.

## 7. Colunas e fórmulas

O layout está em [ESQUEMA_PLANILHA](../assets/ESQUEMA_PLANILHA.md) e é aplicado por `gerar_planilha.py`:

- As colunas novas entram à direita do conteúdo da aba. Inserir colunas no meio da lista só com Excel ou LibreOffice, que atualizam as referências, e com validação depois.
- `QTD LEVANTADA` puxa a memória, nunca a quantidade recebida. Fórmulas originais de custo e totais não são redirecionadas para a nossa coluna sem pedido.
- Quantidades são números nativos; vírgula decimal é formato de exibição.
- Se a planilha recebida tiver recursos que a gravação perderia (imagens, gráficos, controles), a entrega vai para um arquivo separado e o motivo fica registrado.
