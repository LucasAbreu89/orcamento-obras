# 00 — Fluxo mestre

## 1. Entradas e saídas

**Entradas:** pasta de projetos (DWG/DXF, PDF, IFC, imagens, memoriais, cadernos de encargos, quadros) e planilha de serviços (XLSX, XLSM, XLS, ODS ou CSV). Os caminhos vêm na mensagem. Tipo de obra, pavimentos e disciplinas são deduzidos dos documentos.

- Sem planilha: fazer catálogo e bases, registrar a ausência e não inventar a lista de serviços.
- Com mais de um arquivo candidato: usar o indicado pelo usuário ou o de evidência inequívoca; nunca sobrescrever um deles por tentativa.

**Saída:** a planilha de [ESQUEMA_PLANILHA](../assets/ESQUEMA_PLANILHA.md), gerada a partir de `dados/levantamento.json` ([ESQUEMA_LEVANTAMENTO](../assets/ESQUEMA_LEVANTAMENTO.md)), mais o relatório do validador.

## 2. Etapas e critério de passagem

| Etapa | O que fazer | Pronto quando |
|---|---|---|
| 0. Preparar | `ambiente.py` e `preparar_projeto.py` ([07](07_ferramentas_e_aplicativos.md)) | Rotas de leitura definidas; planilha com backup, snapshot e mapa |
| 1. Catalogar | Leitura de reconhecimento e índice assunto → fonte ([01](01_catalogacao_projetos.md)) | Toda representação está no catálogo com estado de leitura; faltas listadas |
| 2. Mapear | Abas, listas, natureza dos itens, mapa de especificações ([02](02_planilha_escopo_e_mapeamento.md)) | Todo item tem chave, natureza e fonte provável |
| 3. Checkpoint | Apresentar o escopo proposto (§3) | Escopo confirmado, ou registrado como premissa de escopo |
| 4. Bases | Ambientes, paredes e faces, vãos, forros, pontos, equipamentos ([04](04_calculo_de_areas.md), [05](05_perimetros_e_alturas.md)) | Cada base tem contorno ou IDs, método e origem |
| 5. Quantificar | Critério ([11](11_criterios_padrao.md)), parcelas, estados ([03](03_pendencias_premissas_e_estados.md)), serviços associados ([06](06_quantitativos_e_memorias.md)) | Todo item tem estado, parcelas ou motivo, e evidência ou justificativa |
| 6. Gerar | Prints com `cad.py render`/`pdf.py render`; `gerar_planilha.py` | Planilha gerada sem erro de esquema |
| 7. Conferir e entregar | `recalcular.py`, `validar_entrega.py`, razoabilidade, mensagem final ([08](08_conferencia_comparacao_e_entrega.md)) | Validador sem erro, ou limitações declaradas item a item |

Uma pendência não segura a etapa seguinte para os itens independentes.

## 3. Checkpoint de escopo

Depois das etapas 1 e 2, e antes de medir, enviar **uma** mensagem com:

1. Fontes encontradas, cobertura da leitura e documentos faltantes que afetam itens.
2. Abas e listas que serão levantadas, com o número de itens; abas excluídas e o motivo.
3. Itens por natureza ([02 §3](02_planilha_escopo_e_mapeamento.md)): mensuráveis, por parâmetro, indiretos/verbas, fora do escopo.
4. Disciplinas cobertas e não cobertas (por exemplo, instalações sem projeto).
5. Critérios de maior impacto, marcados com ★ em [11](11_criterios_padrao.md), o nível de premissas e o limite de 10% para premissa ([03 §2](03_pendencias_premissas_e_estados.md)).
6. Se houver comparação pedida, a quantidade de referência e o limite de 5% para investigar diferenças ([08 §4](08_conferencia_comparacao_e_entrega.md)).

Depois, aguardar a resposta.

Seguir sem esperar quando o pedido já definir abas, disciplinas e critérios, quando o usuário disser para não confirmar, ou quando o pedido for parcial e inequívoco ("levante os itens 3.1 a 3.8"). Nesses casos, registrar as escolhas na aba Premissas como **premissas de escopo** e prosseguir. Pedido só de catálogo não tem checkpoint.

## 4. Ordem de trabalho

- **Por elemento, depois por item.** Medir uma vez as bases (ambientes, trechos de parede com faces e alturas, vãos do quadro de esquadrias, forros, pontos, equipamentos) e apropriar cada item como filtro e fórmula sobre elas. Uma correção na base chega a todos os itens que a usam.
- **Serviços associados.** Ao fechar cada família, passar a [matriz](../assets/MATRIZ_SERVICOS_ASSOCIADOS.md) para achar omissões na lista; o que faltar vai para o campo `sugestoes` do JSON (aba Sugestões), fora da principal.
- **Critério registrado uma vez por família** na aba Critérios; os itens apontam para ele.

## 5. Reforma e construção nova

**Reforma:** separar existente, a demolir ou retirar, a manter, a reaproveitar e novo. Planta nova não prova o que existe escondido nem a extensão da demolição; dado de vistoria ausente vira pendência localizada. Conferir proteção, retirada, transporte, descarte e recomposição sempre que houver item.

**Construção nova:** conferir a cobertura das disciplinas (terreno, fundações, estrutura, vedações, cobertura, impermeabilização, acabamentos, instalações, equipamentos, áreas externas). Cada sistema é medido pelo seu projeto; arquitetura não substitui estrutura, fundações ou instalações. Sem o projeto da disciplina, o item fica pendente ou recebe estimativa autorizada, identificada como tal.

Preços e quantidades já preenchidas na planilha são ignorados, salvo comparação pedida ([02 §4](02_planilha_escopo_e_mapeamento.md)).

## 6. Pastas da execução

`preparar_projeto.py` cria, dentro da obra ou no destino indicado:

```text
levantamento-orcamento/execucoes/AAAAMMDD_HHMMSS/
  fontes/       inventário, ambiente, catálogo, snapshot e mapa da planilha, DXF convertidos
  dados/        levantamento.json, geometrias e extrações
  evidencias/   prints marcados e plantas de levantamento
  planilha/     backup do original, cópia de trabalho e entrega
  conferencia/  relatórios do validador, recálculo e comparação
```

Nada da entrega depende de diretório temporário. Originais nunca são movidos nem renomeados.

## 7. Encerramento

| Situação | Significado |
|---|---|
| Concluído no alcance | Todos os itens com estado final, memória e validação |
| Entregue com pendências | Lote processado; itens SUBTOTAL e PENDENTE identificados, com as perguntas |
| Entrega limitada | Parte viável feita; limitação de acesso ou ferramenta, itens afetados e validação não executada descritos |

A mensagem final segue [08 §6](08_conferencia_comparacao_e_entrega.md). Não prometer trabalho depois do fim da sessão.
