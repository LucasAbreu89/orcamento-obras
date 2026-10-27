# Áreas: consulta, cálculo e conferência

Aplicar a qualquer projeto e pasta de trabalho. O objetivo é obter uma área reproduzível para um contorno e uma finalidade declarados, com fonte, método e critério junto ao valor. Nenhum ambiente, valor, revisão, unidade ou regra de dedução de outro empreendimento constitui padrão para o atual.

## Índice

1. [Escopo, fontes e continuidade](#1-escopo-fontes-e-continuidade)
2. [Critério e contorno](#2-critério-e-contorno)
3. [Unidade, escala e plano](#3-unidade-escala-e-plano)
4. [Vãos, soleiras e elementos internos](#4-vãos-soleiras-e-elementos-internos)
5. [Cálculo e medição](#5-cálculo-e-medição)
6. [Conferência e apresentação](#6-conferência-e-apresentação)
7. [Modelos para a planilha e exemplo fictício](#7-modelos-para-a-planilha-e-exemplo-fictício)

## 1. Escopo, fontes e continuidade

Primeiro reconhecer se o pedido é transcrever, calcular ou conferir. Em catálogo ou rastreamento, registrar o que está no projeto; não acrescentar cálculos não solicitados. Uma etiqueta não substitui uma medição independente.

| Método efetivamente utilizado | Rótulo junto ao resultado | Evidência mínima |
|---|---|---|
| Leitura de etiqueta, quadro ou memorial | Área indicada no projeto — transcrita | Arquivo, revisão e localizador da indicação |
| Operações com cotas explícitas | Área calculada pelas cotas | Vista, referências das cotas, parcelas e fórmulas |
| Operações com coordenadas extraídas | Área calculada pelas coordenadas | Geometria, sistema de coordenadas, unidade e algoritmo |
| Execução do comando nativo do CAD | Área medida por comando nativo, nomeando-o | Objeto, execução, resultado e unidade registrados |
| Medição gráfica em PDF calibrado | Área estimada por medição gráfica | Calibração, vista, limites e limitação da estimativa |
| Quantidade extraída de modelo BIM | Área extraída do modelo — propriedade e critério identificados | Modelo/revisão, IDs dos objetos, unidade, propriedade, bruto/líquido e filtros |

Registrar projeto, disciplina, ambiente ou região, finalidade, arquivo-fonte, prancha, revisão, página/vista/espaço, data e referência da memória. Identificar separadamente a fonte da etiqueta e a da geometria. Conferir se plantas, detalhes e cortes se referem ao mesmo lugar e a revisões compatíveis; a revisão mais recente de uma prancha não atualiza automaticamente as demais.

Preservar originais. Qualquer criação ou ajuste de polilinha, camada, hachura ou outro objeto ocorre em cópia identificada de conferência, relacionada à fonte. Não apresentar contornos reconstruídos como entidades preexistentes do original.

Quando a fonte for BIM, o nome de uma propriedade não comprova seu critério de medição. Confirmar se a área é bruta ou líquida, projetada ou desenvolvida, quais vazios foram retirados e a fase/revisão do modelo. Registrar objetos, filtros e unidades; impedir duplicação entre objetos, modelos vinculados, arquivos federados e exportações repetidas. Uma área de objeto não equivale automaticamente à área de ambiente ou de serviço.

Na organização padrão do pacote, guardar as evidências em `levantamento-orcamento/execucoes/<data>/04_evidencias`, as memórias de serviços em `03_memorias_servicos`, a planilha em `05_planilhas` e os dados geométricos de apoio em `08_dados_tecnicos`, sempre sob a mesma execução. Manter os vínculos entre esses registros; nomes são adaptáveis ao destino definido pelo usuário.

### Dúvida é um registro, não uma pausa do lote

Se faltar cota, unidade, critério, revisão compatível ou leitura confiável, criar um ID na aba **Pendências**, associá-lo às linhas afetadas e continuar todos os ambientes, parcelas e serviços independentes. Ver [Dúvidas e continuidade](03_duvidas_e_continuidade.md).

- Não inventar medidas nem usar zero para ausência de informação. Manter o campo numérico sem valor e um campo de situação explícito, por exemplo, `Não determinado — PD-...`.
- Se só parte da área estiver determinada, apresentar o subtotal conhecido com cobertura e itens excluídos identificados. Uma soma de células vazias não pode ser rotulada como área completa.
- Se houver alternativas sustentadas pelas fontes, registrar cenários identificados, cada qual com critério, origem e efeito. Não escolher silenciosamente um cenário nem somar alternativas entre si.
- Um impedimento de medição afeta aquela grandeza; não invalida a transcrição de uma etiqueta legível, nem interrompe outros itens.
- Consolidar dúvidas na planilha para revisão posterior. Não transformar cada descoberta em pergunta bloqueante ao usuário.

## 2. Critério e contorno

**Definir e mostrar o contorno antes de calcular.** Uma ferramenta mede os limites selecionados; não decide quais limites representam a finalidade arquitetônica ou o serviço.

Declarar se a área é interna, útil, bruta, de piso, de circulação livre, de forro, de cobertura, projeção horizontal ou superfície desenvolvida, conforme o pedido. Uma área interna em planta não é automaticamente a área de qualquer serviço. Piso inclinado, rampa, escada e superfície curva exigem declarar se a quantidade é projetada ou desenvolvida e como foi obtida.

Em coberturas, rampas e outras superfícies inclinadas, verificar a composição ou especificação do serviço: impermeabilização ou revestimento pode exigir superfície desenvolvida, enquanto uma comparação arquitetônica pode pedir projeção. Se a superfície for plana com inclinação constante `α` em relação à horizontal e houver base geométrica suficiente, `A_desenvolvida = A_projetada ÷ cos(α)`; não aplicar essa relação a conjunto de planos, dobras ou inclinação variável sem decomposição. Incluir encontros, sobreposições e perdas apenas quando o critério do serviço os exigir e mantê-los separados da área geométrica.

Para práticas de reforma, construção nova e convenções de medição dependentes de fonte, consultar [Boas práticas e fontes](10_boas_praticas_e_fontes.md). Uma convenção externa não se torna regra do contrato sem verificar sua aplicabilidade.

| Elemento | Decisão a documentar |
|---|---|
| Paredes de limite | Face nominal, acabada, eixo ou outra referência identificável |
| Paredes e divisórias internas | Projeção incluída ou excluída e motivo conforme a finalidade |
| Portas e transições | Linha exata de fechamento, faixa de piso atribuída e interface entre ambientes |
| Bonecas, pilares e reentrâncias | Geometria sólida e faixas de piso aberto ao lado |
| Shafts, poços e vazios | Contorno interno, inclusão/exclusão e fonte |
| Ilhas, bancadas, móveis e equipamentos | Área sob o elemento e eventual projeção descontada |
| Louças, acessórios e símbolos | Confirmar se existe exclusão física pertinente; símbolo não cria desconto |
| Revestimentos | Face já acabada ou espessura considerada, evitando dedução repetida |
| Hachuras existentes | Limites, ilhas e recortes efetivos; não presumir equivalência com o ambiente |

Desenhar ou identificar o percurso completo em vista geral, por exemplo `IMG01`, com parcelas `A01`, `A02` etc. Detalhar portas, recortes e pequenos degraus em ampliações. A imagem precisa permitir seguir o traçado e localizar cada parcela; não basta uma captura do número final.

Toda área lançada na memória deve estar demarcada em print real incorporado à própria memória, com os mesmos IDs das parcelas, inclusões e deduções. Para superfícies verticais, relacionar a localização em planta à face/corte e à altura usada; uma planta genérica do ambiente não demonstra a área da parede. Aplicar o [contrato de evidência por item](06_quantitativos_e_memorias.md#evidencias-visuais-por-item), inclusive para áreas estimadas ou parciais.

Percorrer todos os limites e conferir avanços, recuos, pilares, bonecas, paredes internas, divisórias, batentes e descontinuidades. Não ligar cantos com uma reta que atravesse uma reentrância ou corte piso pertencente à área. Usar pontos e faces identificáveis; coordenadas aproximadas obtidas de uma captura não equivalem à geometria do desenho.

Tratar contorno externo e vazios internos separadamente. Uma única polilinha externa não desconta automaticamente ilhas ou shafts. Descrever a topologia e as operações de adição/subtração necessárias. Uma hachura pode descontar louças, bancadas ou piso oculto segundo outra finalidade; auditar antes de usar sua propriedade de área.

## 3. Unidade, escala e plano

### DWG e outros desenhos CAD

1. Localizar a vista correta e distinguir planta, corte, elevação, detalhe, Model e Paper Space. A distância no papel não comprova a dimensão real do ambiente.
2. Conferir camadas, referências externas e disponibilidade dos limites completos.
3. Ler a configuração de unidades e verificar pelo menos duas distâncias conhecidas, preferencialmente em direções distintas. Uma variável de unidades ou uma etiqueta isolada não comprova a escala da geometria.
4. Registrar a relação validada entre uma unidade do desenho e metros. Não redimensionar a fonte para obter um resultado esperado.
5. Conferir plano, coordenada Z e sistemas de coordenadas utilizados. Distinguir WCS, UCS e coordenadas do objeto quando houver extração ou automação. Área em planta exige projeção coerente no plano declarado.

Se uma unidade do desenho corresponde a `k` metros:

```text
A_m² = A_unidades² × k²
```

| Unidade geométrica validada | k, em metros por unidade | Conversão de área |
|---|---:|---|
| Metro | 1 | Manter o valor |
| Centímetro | 0,01 | Dividir por 10.000 |
| Milímetro | 0,001 | Dividir por 1.000.000 |

A escala impressa da prancha não é fator automático de conversão da geometria no Model. Se as verificações forem incompatíveis, registrar a inconsistência em Pendências e continuar outras medições confiáveis.

### PDF e imagem

Priorizar cotas explícitas da vista correta. Conferir unidade, linhas de extensão e faces de referência. Somar cotas parciais somente quando consecutivas e cobrindo o mesmo trecho; não somar uma total às suas parcelas.

Conferir a cota na imagem quando OCR ou extração de texto for usado para localizar informação. Não usar pixels, tamanho da tela ou escala de impressão presumida como medida exata. Medição gráfica exige calibração por referências válidas, avaliação de distorção e identificação como estimativa. Sem informação suficiente, registrar a medida não determinada; não inferir dimensão pela aparência.

## 4. Vãos, soleiras e elementos internos

Auditar a entrada principal e **todas as portas internas**, inclusive cabines e acessos secundários. Para cada uma, documentar:

1. Identificação e ligação entre ambientes ou parcelas.
2. Largura efetivamente usada: vão bruto, entre paredes, entre batentes ou passagem livre.
3. Profundidade da faixa de piso, medida nas referências aplicáveis.
4. Linha ou face em que a área termina.
5. Existência de batentes, degraus ou mudanças de seção.
6. Inclusão da faixa no polígono ou em parcela anterior.
7. Atribuição exclusiva da soleira quando dois ambientes serão totalizados.

Não substituir largura do vão por largura da folha sem evidência. O arco de giro da porta não é limite de piso e não gera área a somar ou descontar.

Para faixa comprovadamente retangular:

```text
A_vão = largura considerada × profundidade considerada
```

Somar apenas quando a faixa pertence ao critério e ainda está fora das outras parcelas e do polígono. Se já foi contornada, não somar novamente. Usar contorno real ou decomposição quando houver batentes, recortes ou variação de largura; uma aproximação retangular deve permanecer identificada como aproximação.

A boneca é parte sólida da parede. O piso aberto entre bonecas pode pertencer à área; isso não autoriza incluir a projeção da alvenaria. Mostrar separadamente os dois objetos geométricos.

Para soleiras compartilhadas, estabelecer um limite comum verificável e um ID de interface. Conferir o agregado dos ambientes para impedir duplicação e faixa sem atribuição. Se o critério não estiver definido, criar cenários e Pendência mantendo o processamento independente.

Aplicar a mesma disciplina às ilhas e paredes internas: uma dedução já incorporada ao polígono não volta à coluna de descontos. Identificar se a dedução está aplicada na geometria, na parcela ou apenas no total, e permitir uma única ocorrência.

## 5. Cálculo e medição

### Parcelas pelas cotas

Dividir a região em parcelas que cubram integralmente o critério sem lacunas nem sobreposição. Mostrar localização, dimensões, fonte de cada dimensão, expressão, resultado intermediário e tratamento dos vãos.

```text
Retângulo: A = largura × comprimento
Triângulo: A = base × altura perpendicular ÷ 2
Área em L: soma de parcelas disjuntas
Região com vazios: área externa − vazios identificados
Total: Σ parcelas incluídas − deduções ainda não aplicadas
```

Não misturar silenciosamente cotas arredondadas do PDF com coordenadas mais precisas do CAD no mesmo total. Uma memória híbrida excepcional deve declarar a origem de cada trecho, a compatibilidade entre fontes e a limitação resultante.

### Coordenadas e curvas

Para um polígono simples de segmentos retos, com vértices ordenados e fechamento `n+1 = 1`, pode-se usar:

```text
A = |Σ(x_i × y_(i+1) − x_(i+1) × y_i)| ÷ 2
```

Registrar a sequência, unidade, plano e extração. A fórmula de vértices não representa automaticamente arcos: preservar sua geometria analítica, bulges ou parcelas de setor/segmento circular conforme o caso. Não trocar arco por corda sem declarar aproximação, resolução e efeito. Validar orientação e tratamento de contornos internos; somar valores absolutos de todas as ilhas produz área errada quando deveriam ser subtraídas.

Conferir autointerseções, segmentos repetidos, laços acidentais e fechamento. Um algoritmo que retorna número para um contorno inválido não valida a região arquitetônica.

### Medição nativa no CAD

Consultar as capacidades e a interface disponíveis no momento; nomes, opções e variáveis variam por aplicativo e versão. Os passos abaixo descrevem a evidência desejada. Não afirmar que um comando foi executado apenas porque existe uma fórmula, um script ou um resultado anterior.

Na cópia identificada:

1. Criar camada de conferência legível e auditar a entidade existente ou reconstruir o contorno pelos pontos reais.
2. Confirmar fechamento explícito, plano, unidade, arcos, ausência de cruzamentos e tratamento dos vazios.
3. Se usar AutoCAD e a opção estiver disponível, executar `AREA` → `Object` no objeto conferido. Em outro aplicativo, registrar o comando equivalente realmente utilizado.
4. Capturar o resultado, unidade, objeto e execução. Converter com `k²` quando necessário.
5. Medir vazios separadamente ou usar entidade que os preserve corretamente; mostrar a operação final.
6. Salvar a cópia e evidências que mostrem tanto o contorno inteiro quanto o resultado nativo legível.

Registrar, quando acessíveis, camada, handle/ID, quantidade de vértices, propriedade de fechamento e perímetro. O AutoCAD pode calcular área com fechamento implícito de polilinha aberta; receber uma área não comprova `Closed = Yes`. Polilinhas largas podem medir pela linha central; auditar a referência geométrica.

Leitura de uma propriedade ou da variável que armazena o último resultado deve ser identificada como leitura. Confirmar o comportamento na versão em uso e a correspondência com o objeto recém-medido. Ler a variável `AREA` não executa uma nova medição.

Se o aplicativo, arquivo ou recurso necessário não estiver disponível, registrar essa limitação em Pendências, entregar os métodos confiáveis efetivamente usados e continuar o lote. Para operação e evidência de interface, ver [Computer use e encerramento](07_computer_use_e_encerramento.md).

## 6. Conferência e apresentação

Comparar a soma das parcelas com o contorno completo, preferencialmente por método independente. Se ambos usam os mesmos pontos e limites, a diferença deve ser explicável pela precisão numérica. Se usam cotas arredondadas e coordenadas, registrar essa distinção; proximidade não demonstra identidade de critério.

Em divergências, revisar fonte/revisão, unidade/plano, faces de limite, todos os vãos, soleiras, paredes e vazios, soma de cotas, sobreposições, deduções, arredondamentos e aritmética. Não escolher medidas nem mover contorno para fazer a conta coincidir com a etiqueta. Não usar tolerância percentual arbitrária para encerrar causa desconhecida.

```text
Δ_etiqueta = A_calculada − A_indicada
Δ_% = Δ_etiqueta ÷ A_indicada × 100
```

Calcular percentual somente com referência determinada e diferente de zero; caso contrário registrar `Não aplicável` ou `Não determinado`, com motivo. Identificar o denominador em qualquer comparação entre memórias. Sem a memória ou o contorno de outro total, quantificar a divergência quando possível, mas não afirmar sua causa.

Manter precisão intermediária e arredondar no resultado apresentado, de acordo com a fonte e a finalidade. Usar `≈` quando mostrar arredondamento. Casas adicionais do CAD não significam precisão física equivalente. Distinguir área indicada, calculada pelas cotas, calculada pelas coordenadas, medida nativamente e cenários, inclusive nos resumos do Excel.

Vincular resultados à memória e à finalidade do serviço conforme [Quantitativos e memórias](06_quantitativos_e_memorias.md). Conferir fórmulas, referências, cobertura e entrega conforme [Conferência, comparação e entrega](08_conferencia_comparacao_e_entrega.md).

## 7. Modelos para a planilha e exemplo fictício

Adaptar às abas e convenções do arquivo do usuário; preservar a estrutura existente quando ela já atender à rastreabilidade. IDs ligam valor, memória, imagem, fonte e eventual Pendência.

### Registro da área

| ID | Ambiente/região | Finalidade | Cenário/critério | Valor | Unidade | Método e origem | Fonte/localizador | Contorno/evidência | Situação | Pendência |
|---|---|---|---|---:|---|---|---|---|---|---|
| AR-... | Identificação do projeto | Uso da área | Limites e deduções | Campo numérico | m² | Método efetivo | Arquivo, revisão, vista | IMG/objeto | Completo, parcial ou não determinado | ID, se houver |

### Memória de parcelas

| ID área/cenário | Parcela | Região/imagem | Dimensões | Fonte de cada medida | Fórmula | Inclusão/dedução | Já aplicada no contorno? | Resultado em m² | Situação/Pendência |
|---|---|---|---|---|---|---|---:|---|
| AR-.../C... | A... | Referência gráfica | Medidas e unidade | Cotas ou coordenadas identificadas | Expressão reproduzível | Motivo e sinal | Sim/não | Campo numérico | Estado explícito |

### Auditoria dos vãos

| ID do vão/interface | Ambientes | Largura e referência | Profundidade e referência | Linha de fechamento | Faixa atribuída a | Já incluída em | Evidência | Situação/Pendência |
|---|---|---|---|---|---|---|---|---|
| V... | Identificações | Não usar folha sem prova | Fonte da espessura/faixa | Face/eixo identificado | Um ambiente ou cenário | Polígono/parcela | IMG... | Estado explícito |

### Registro na aba Pendências

| ID | Informação não resolvida | Fonte consultada | Linhas afetadas | Efeito | Tratamento adotado | Ação necessária para resolver |
|---|---|---|---|---|---|---|
| PD-... | Cota, limite ou critério faltante | Arquivo e vista | IDs de área/serviço | Quantidade, comparação ou cobertura | Campo sem valor, subtotal ou cenários separados | Documento ou decisão específica |

### Exemplo inteiramente fictício — não é dado de projeto

Para demonstrar somente o controle das parcelas, suponha um ambiente fictício com região retangular de `3,20 × 2,40 m`, piso aberto de entrada de `0,80 × 0,18 m` ainda fora do retângulo e shaft fechado de `0,30 × 0,40 m` dentro dele. O critério demonstrativo inclui a entrada, exclui o shaft e não serve como regra de outro ambiente.

| Parcela fictícia | Expressão | Resultado fictício | Tratamento |
|---|---|---:|---|
| A01 — região principal | `3,20 × 2,40` | 7,6800 m² | Inclui inicialmente a projeção do shaft |
| A02 — piso de entrada | `0,80 × 0,18` | 0,1440 m² | Adição única; soleira atribuída a este ambiente |
| D01 — shaft | `0,30 × 0,40` | 0,1200 m² | Dedução única, ainda não aplicada em A01 |
| Total do cenário demonstrativo | `A01 + A02 − D01` | 7,7040 m² ≈ 7,70 m² | Área calculada por dimensões fictícias |

Se a projeção de uma ilha não estiver dimensionada, registrar a falta em Pendências. Uma alternativa que dependa desse desconto permanece sem total determinado até obter sua dimensão; o cenário demonstrativo que mantém o piso sob a ilha pode continuar identificado, caso essa alternativa seja pertinente. Não inserir zero na dimensão da ilha, não alterar o critério para fechar uma conta e não apresentar nenhum desses números como medição de CAD executada.
