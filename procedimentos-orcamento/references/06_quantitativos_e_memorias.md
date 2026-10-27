# 06 — Quantitativos e memórias por serviço

## Finalidade e posição no fluxo

Transformar o escopo mapeado em quantidades reproduzíveis: cada resultado deve indicar o serviço, a unidade, o critério, os elementos físicos, a origem das parcelas e o caminho até a coluna própria `QTD LEVANTADA`. Nesta referência, “principal” abrange todas as abas/listas de origem incluídas no mapeamento, não somente a aba ativa ou a primeira.

Aplicar esta referência depois de inventariar e catalogar os projetos e de abrir e mapear a planilha, conforme [00 — Fluxo mestre](00_fluxo_mestre.md), [01 — Catalogação de projetos](01_catalogacao_projetos.md) e [02 — Planilha, escopo e mapeamento](02_planilha_escopo_e_mapeamento.md). Usar as bases de [04 — Cálculo de áreas](04_calculo_de_areas.md) e [05 — Perímetros e alturas](05_perimetros_e_alturas.md) quando a grandeza for necessária. A base de um ambiente é uma fonte auxiliar; não determina, sozinha, a quantidade de todos os serviços nele executados.

O método serve a qualquer projeto e modelo de Excel. Nomes de arquivos, códigos de itens, valores, materiais e exemplos encontrados em uma obra são dados daquele caso, sem autoridade para alterar este fluxo ou definir critérios de outra obra. Ao executar, aplicar as habilidades de planilhas e de PDF disponíveis e adequadas ao arquivo; escolher ferramentas compatíveis com os recursos que precisam ser preservados. Não fixar biblioteca, versão ou aplicativo que não esteja disponível.

**Dúvida técnica não interrompe o lote.** Buscar a resposta nas fontes e nas decisões já registradas; se continuar faltando uma definição, registrar a pendência e prosseguir com os itens independentes. Não perguntar ao usuário durante o lote por mera indefinição técnica. Seguir [03 — Dúvidas e continuidade](03_duvidas_e_continuidade.md), manter os resultados dependentes identificados e entregar o alcance efetivamente concluído.

## 1. Fixar o contrato de medição de cada item

Preservar o ID e a descrição integral da lista autorizada, inclusive suas unidades. Tratar IDs como texto: `1.10` e `1.1` não são o mesmo item. Não ampliar uma descrição para acomodar material que não possui item, nem criar serviço adicional só para aproveitar uma medida disponível.

Trabalhar com todas as abas/listas abrangidas pelo mapa de [02](02_planilha_escopo_e_mapeamento.md). Identificar cada ocorrência pela chave `arquivo + aba + tabela/seção + item/linha`, necessária quando códigos se repetem. Quantidades orçamentárias já preenchidas são referências para comparação: não dispensam medir/calcular independentemente nem podem alimentar nossas memórias como atalho. Se faltar dado, registrar nossa pendência, sem copiar a quantidade original.

Antes da seleção geométrica, registrar o contrato de medição:

| Campo | Definição necessária |
|---|---|
| Chave de origem, item, descrição e unidade | Arquivo, aba, tabela/seção e item/linha de destino, alcance contratual e grandeza que será apurada |
| Estado físico | Existente, a demolir/retirar, a manter/preservar, reaproveitado ou proposto/a construir/instalar |
| Elementos e ambientes | Onde o serviço ocorre e quais peças ou regiões o compõem |
| Limite de medição | Face, eixo, projeção, superfície desenvolvida, módulo, peça ou conjunto |
| Alturas e níveis | Condição existente ou proposta, referência de nível, início e fim de cada pano |
| Inclusões e exclusões | Vãos, vergas, retornos, espessuras, interfaces e componentes de outros itens |
| Composição | Fornecimento, instalação, retirada, transporte, acabamento e o que já integra o pacote |
| Natureza da quantidade | Geometria física, quantidade de execução pelo critério da composição, consumo de insumos ou compra; perda e arredondamento, se autorizados |
| Evidência e origem | Arquivo, revisão, prancha/vista, método e informação que sustenta cada decisão |

Critérios usuais que exigem decisão explícita: parede completa por uma elevação ou acabamento de duas faces; forro em projeção ou desenvolvimento; vidro por módulo, lâmina, área ou extensão; pedra por tampo ou todas as peças; limpeza de uma face ou duas; conjunto com acessórios incluídos ou acessórios contados separadamente.

Não transportar a convenção de um item para outro. Uma região com piso preservado pode ter forro removido; a planta proposta não comprova a quantidade existente a retirar. A ausência de um material em uma vista não prova que foi mantido ou que não existe.

Se a unidade ou o critério estiver indefinido, registrar o que já é comprovado, criar a memória parcial e manter o resultado final dependente. Não converter unidade por conveniência nem escolher silenciosamente uma das alternativas.

## 2. Montar o inventário físico antes de somar

### 2.1. IDs, vistas e ocorrências

Dar um ID estável a cada elemento físico e às suas parcelas, por exemplo `P01` para pano, `V01` para verga, `S01` para trecho e `E01` para equipamento. Acrescentar ambiente ou prefixo de arquivo quando necessário para evitar colisões. Registrar explicitamente a relação entre elemento, face, estado e serviço.

Planta, elevação, corte, ampliação e detalhe podem mostrar a mesma peça. Relacionar essas vistas a um único elemento antes de contar. A repetição de um bloco em uma planta duplicada, de um símbolo na legenda ou de uma peça em detalhe típico não cria uma ocorrência física adicional.

Usar uma relação como:

```text
ID físico | ambiente/local | estado | família/tipo | vistas que o representam
          | item(s) relacionado(s) | face/parcela | fonte | observação
```

Um elemento pode participar legitimamente de itens distintos, como parede e pintura, desde que cada um tenha sua grandeza e critério. Dentro do mesmo alcance, não somar duas vezes a mesma parcela por aparecer em vistas diferentes. Famílias mutuamente exclusivas devem repartir o mesmo conjunto de peças sem duplicação.

Peças iguais só podem ser agrupadas por multiplicidade depois de confirmar dimensões, especificações e locais de todas elas. Uma chamada `×3` multiplica somente a parcela à qual está ligada; não toda a bancada, ambiente ou detalhe por proximidade gráfica.

### 2.2. Legendas, famílias e reconciliação

A legenda define tipos e convenções; o inventário identifica as ocorrências na implantação. Não contar amostras da legenda. Confrontar contagem por família, contagem por ambiente e relação de IDs; investigar diferenças, inclusive tipos decorativos, acessórios e famílias menos frequentes.

Se houver total de família comprovado e distribuição contratual desconhecida, conservar o total como referência. Não repetir o total em cada item de modelo/cor/ângulo nem distribuir por estimativa silenciosa. Guardar o universo conhecido em base comum e manter pendentes as classificações dependentes.

### 2.3. Origem de cada parcela

Identificar a origem junto do valor, inclusive em resumos e comparações:

| Origem | Registro que acompanha o valor |
|---|---|
| Indicado no projeto | Transcrição e localizador; não chamar de conferência independente |
| Cálculo pelas cotas | Dimensões, unidade, vista, fórmula e limites |
| Cálculo pelas coordenadas | Entidades/contornos, sistema de coordenadas, transformações, unidade e fórmula |
| Comando nativo | Aplicativo/comando realmente usado, objeto, unidade, resultado e evidência |
| Contagem | Lista de peças ou conjuntos físicos únicos e suas localizações |
| Medição gráfica estimada | Escala calibrada, fonte, aproximação e limite de precisão |
| Critério do usuário | Decisão registrada e itens afetados |
| Composição ou pacote | Unidade contratual e componentes incluídos |

Uma memória pode combinar origens, com parcelas e subtotais distinguíveis. Não afirmar execução de `AREA`, medição CAD nativa ou teste no Excel quando houve apenas cálculo por coordenadas, propriedade extraída ou renderização por outra ferramenta.

Validar unidades, cotas, planos e transformações pelas referências anteriores. OCR e texto extraído auxiliam a localização; conferir visualmente casas decimais, sinais e faces de referência. Arcos de giro de portas, símbolos de chamadas e projeções de espessura não são automaticamente parcelas do serviço.

## 3. Aplicar o critério da família de serviço

### 3.1. Pisos, remoções de piso e soleiras

Mostrar o contorno próprio do serviço antes da conta. Aplicar [04 — Cálculo de áreas](04_calculo_de_areas.md) aos vãos, faixas de portas, profundidades, batentes, bonecas, pilares, shafts, recortes e ilhas. Uma faixa já incluída no polígono não pode ser acrescentada novamente.

Separar existente, removido, mantido e novo; separar também materiais distintos. Definir a atribuição de soleiras compartilhadas e os limites entre ambientes. Conferir piso sob móveis, louças e bancadas conforme a condição e o trabalho descritos. Uma hachura pode representar apenas piso visível ou um material: não presumir que cobre toda a remoção.

Se o item combinar piso, soleiras e rodapés, discriminar as parcelas compatíveis com sua composição. Não somar diretamente metros de rodapé a metros quadrados de piso. Uma medição apenas do piso visível permanece subtotal quando o alcance exigir partes ainda não comprovadas.

### 3.2. Paredes, divisórias, fechamentos e demolições

Inventariar os panos físicos por material, sistema, estado, altura e face. Em encontros L/T, declarar como os limites são atribuídos para evitar sobreposição. Não assumir que a soma de panos corresponda a um eixo contínuo.

Para um critério de uma elevação:

```text
Área = soma(comprimento de cada pano × sua altura)
       + complementos não incluídos
       − aberturas ainda não descontadas
```

Se a decomposição já mede os panos laterais sem a porta, incluir a verga quando ela pertence ao serviço e não descontar o vão novamente. Separar folha, painel fixo, batente e verga conforme os itens. A folha retirada não vira painel fixo demolido.

Uma divisória com chapas em duas faces pode ser medida por uma elevação do sistema completo, conforme a composição. Não dobrar automaticamente sua área. Acabamentos de faces diferentes exigem parcelas próprias. Conservar a distinção entre alvenaria, drywall, MDF, vidro e sistemas mistos, ainda que a lista possua menos categorias.

Usar alturas existentes para demolição e limites previstos para elementos novos. Conferir trechos até o forro, até a laje, sob vigas e inclinados. Uma parede já medida até a laje contém a faixa acima do forro: não lançá-la novamente como septo. Um septo independente precisa de percurso, altura e item identificados.

### 3.3. Forros, sancas, tabicas e cortineiros

Medir o forro por seu próprio contorno e material. Não copiar a área do piso como total sem comprovar que os contornos coincidem. Conferir entradas, vãos, regiões junto à marcenaria, vazios, rebaixamentos, MDF, telas, chassis, sancas, cortineiros e tabicas.

Relacionar planta de forro, níveis, cortes e detalhes. Distinguir projeção horizontal, superfícies verticais e desenvolvimento de curvas. Declarar o que integra a composição e o que possui medição própria; não acrescentar um recorte ou superfície já incluídos no campo medido ou no pacote.

Um símbolo de luminária, recorte ou detalhe sem dimensão física não produz, por si só, área adicional ou dedução. Quando faltar o limite de uma sanca ou peça, registrar a falta e concluir os campos independentes comprovados.

### 3.4. Rodapés, pintura e revestimentos

Usar [05 — Perímetros e alturas](05_perimetros_e_alturas.md) para percursos e faces. Perímetro geométrico e soma de faces são referências; o serviço exige seu mapa de trechos e materiais.

No rodapé, auditar portas, retornos, curvas e continuidade atrás de móveis/louças. Excluir um trecho substituído por rodapé integrado em outro sistema apenas com comprovação. Na pintura e no revestimento, medir cada face com sua altura efetiva, limites, vãos, vergas, retornos e mudanças de material.

Distinguir material que substitui o acabamento de objeto que somente o oculta. Louça ou móvel diante da parede não justifica automaticamente desconto. `Perímetro × pé-direito` só se torna total após verificar todas as faces e suas condições. Medir curvas por seu desenvolvimento quando esse for o critério.

### 3.5. Vidros, espelhos, pedras e marcenaria

Identificar peças físicas e unidades. Distinguir módulo de divisória, lâmina e face: duas lâminas não dobram automaticamente a extensão contratual de um módulo. Para espelhos, identificar cristal e face efetiva; uma vista lateral da espessura não é um novo espelho.

Em pedras e marcenaria, conferir implantação, vistas, cortes e detalhes para discriminar tampo, saias, frontões, laterais, retornos, fundos, engrosso, cavidades e peças removíveis, conforme o alcance. Não inventar frontão a partir de cota de base ou rodapé. Registrar dimensões, quantidade de peças, acabamento e unidade de cada parcela.

Uma conta de tampo e saias é **subtotal** quando a descrição também exige faces internas de cuba ou outras peças ainda não medidas. Preservar esse subtotal como informação útil, sem apresentá-lo como total completo. Não completar a diferença por estimativa oculta.

Classificações mutuamente exclusivas devem conservar a quantidade física total quando uma peça muda de categoria. Se a espécie, espessura ou tipo não estiver definido, manter a medição geométrica conhecida em base compartilhada e sinalizar a distribuição pendente nos itens dependentes.

### 3.6. Louças, metais, acessórios e equipamentos

Contar equipamentos físicos únicos, confrontando planta, legenda e detalhes. Separar existente, retirado, reaproveitado e novo. Definir o conteúdo de cada conjunto para não multiplicar acessórios comuns ao ambiente pelo número de louças sem indicação.

Uma placa, kit ou acessório incluído por convenção deve declarar essa origem; não descrevê-lo como ocorrência contada no desenho. A quantidade de pontos não comprova extensões de redes, tubulações, cabos ou infraestrutura.

### 3.7. Iluminação, fitas LED e perfis

Fazer inventário completo de todas as famílias do projeto antes de distribuir os itens da lista. Conferir a implantação inteira, a legenda e os detalhes de forro e marcenaria, incluindo famílias decorativas, embutidas, sobrepostas, pendentes e especiais. Uma contagem correta de parte das famílias não comprova o total de iluminação.

Registrar para cada ocorrência: ID, ambiente, família/código, modelo, cor, ângulo/facho, montagem, estado e item candidato. Características ausentes permanecem ausentes; não inferir cor/facho pela aparência de uma perspectiva nem assumir que dois códigos pertencem ao mesmo produto.

Reconciliar o inventário por três leituras: ocorrências localizadas, subtotais por família e subtotais por ambiente. Retirar amostras da legenda e vistas repetidas da contagem. Se a lista contratar modelos que o projeto ainda não distribui, manter o universo físico conhecido e os itens de modelo pendentes, sem repetir a base em cada linha.

Medir fitas LED e perfis por seus percursos físicos, distinguindo sanca, marcenaria, espelho e demais sistemas. Usar comprimentos de retas e curvas reais; perímetro de chassis só serve quando corresponder ao percurso do produto. Evitar duplicação entre luminotécnico, planta de forro e detalhe local. Comprimento de fita, comprimento de perfil, fonte/driver e quantidade de luminárias são grandezas próprias.

### 3.8. Verbas, meses, limpeza, transporte e volumes

**Verba:** respeitar a grafia e o significado da unidade da lista, como `vb`, `VB` ou `VBA` quando a fonte definir essa convenção como verba. `1` representa um pacote somente quando a contratação define esse alcance. Descrever atividades, locais, componentes e exclusões. Não usar verba para esconder quantidade desconhecida de item contratado em m², m ou unidade.

**Meses:** obter prazo e regra de cobrança da fonte aplicável. Distinguir meses de um pacote, pessoa-mês, equipamento-mês e mobilizações. Não multiplicar equipe sem verificar a unidade. Manter prazo comum em uma entrada referenciada pelos itens dependentes; se o prazo faltar, preservar a memória e propagar a pendência. Não adotar automaticamente a duração de outra obra.

**Limpeza:** declarar superfícies, faces, altura e número de ciclos conforme o serviço. Área de piso não comprova fachada; duas faces de um campo não comprovam um módulo que ultrapassa seus limites.

**Transporte e descarte:** menção a bota-fora não comprova volume, massa, viagens ou caçambas. Conversões dependem de material, espessura, densidade, empolamento/capacidade e critério apropriados. Não transformar m² em m³ ou toneladas sem essas fontes. Para outros volumes, declarar geometria, dimensões e limites.

### 3.9. Rota complementar de construção nova

Usar as disciplinas e revisões correspondentes a cada sistema. A arquitetura pode localizar um elemento, mas não substitui projeto estrutural, fundações, instalações, topografia ou especificação de execução quando estes determinam sua quantidade.

| Família | Levantamento e controles |
|---|---|
| Terraplenagem, escavação e reaterro | Usar terreno, níveis, seções e geometrias de projeto pertinentes. Separar corte, escavação, aterro, reaterro e destinos; declarar material, profundidade e interferências quando comprovados. Distinguir volume **in situ**, solto e compactado: fatores de empolamento, contração ou compactação exigem fonte e base de incidência. Não transferir um volume diretamente entre esses estados nem adotar fator genérico sem declarar a origem. |
| Fundações e estrutura de concreto | Consultar projeto de fundações/estrutura e detalhes. Discriminar elementos e interfaces para não contar a mesma região em pilar, viga, laje e bloco. Medir concreto pela geometria e critério aplicáveis; não converter a área de piso em volume sem espessuras e limites comprovados. |
| Formas | Medir as superfícies de contato ou a grandeza prevista na composição, identificando faces e exclusões. Volume de concreto não comprova área de forma; superfície encostada no terreno, face livre e face moldada têm condições distintas. |
| Armaduras e aço | Usar detalhamento, tabelas e quantitativos do projeto correspondente, com revisão, posições, diâmetros, comprimentos e massas aplicáveis. Não inventar consumo em kg/m² ou kg/m³ para fechar um orçamento sem fonte. Transcrição de quadro e cálculo independente devem permanecer identificados. |
| Coberturas e impermeabilização | Distinguir projeção horizontal, superfície inclinada/desenvolvida e área de compra. Conferir inclinação, águas, beirais, platibandas, cumeeiras, rufos, calhas, encontros e aberturas. Sobreposições, remontes e perdas devem seguir especificação/composição, com aplicação uma única vez. Não usar área projetada como desenvolvida sem justificar a relação geométrica. |
| Redes e instalações | Medir percursos e peças pelos projetos correspondentes, distinguindo sistema, material, diâmetro/seção, nível, trecho horizontal/vertical, conexão e equipamento conforme os itens. Quantidade de pontos não comprova metros de rede. Não somar a mesma rede em planta geral, detalhe e isométrico; relacionar as vistas ao mesmo trecho físico. |

Se os projetos executivos necessários não estiverem disponíveis, registrar a parcela conhecida, a documentação faltante e o impacto; seguir com sistemas independentes. Uma estimativa autorizada deve ter método e fonte próprios, sem ser apresentada como levantamento executivo completo.

### 3.10. Rota complementar de reforma

Separar condição existente comprovada, condição aparente e elemento oculto ainda não verificado. Um desenho cadastral ou uma foto não demonstra automaticamente o que está atrás de revestimentos, acima do forro ou enterrado. Marcar a necessidade de verificação em campo quando ela alterar material, quantidade, método ou alcance; não afirmar que houve vistoria se ela não ocorreu. Registrar em `Pendências` e prosseguir com o que é comprovável.

Mapear preservação e proteção por sistema e região, incluindo interferências com elementos mantidos. Confrontar retirada/demolição, reaproveitamento, transporte interno, armazenamento e reinstalação quando fizerem parte do escopo. Não supor que retirar inclui fornecer novo, ou que preservar elimina proteção e limpeza.

Conferir recomposições decorrentes das intervenções, como fechamento de rasgos, regularização, arremates e acabamentos, usando o alcance autorizado e as composições para evitar omissão ou dupla inclusão. Se uma recomposição necessária não corresponder a item autorizado, registrar a lacuna; não aumentar silenciosamente outro serviço.

Logística, acesso, ocupação, faseamento, proteção provisória e interrupções podem alterar produtividade, contratação ou serviços auxiliares. Não transformá-los automaticamente em acréscimo geométrico ou percentual de perda. Documentar a condição, a fonte e o efeito pertinente; prazo e contratação faltantes seguem pendentes sem interromper a medição independente.

## 4. Separar geometria, execução, consumo e compra

Manter distinguíveis:

```text
Quantidade geométrica física, conforme contorno/peças medidos
Quantidade de execução segundo o critério de medição da composição adotada
Consumo dos insumos conforme coeficientes e sua fonte
Perdas já incorporadas nos coeficientes e eventual reserva adicional autorizada
Quantidade de compra e arredondamento por embalagem, chapa ou peça
```

Essas quantidades podem coincidir em um caso e diferir em outro. Um critério de quantificação de composição pode tratar vãos e superfícies de modo diferente do polígono físico; guardar a geometria base e mostrar a transformação aplicada à quantidade do serviço, sem alterar o desenho ou chamar a quantidade contratual de área física exata.

Consultar especificação da composição e critérios de quantificação aplicáveis antes de usar coeficientes de referência. Cadernos técnicos, como os do SINAPI, ajudam a identificar o alcance e as condições de uma composição; sua utilização não os torna especificação executiva universal nem imposição automática a uma obra privada. Identificar composição, versão/data e adequação ao caso. Ver [10 — Boas práticas e fontes](10_boas_praticas_e_fontes.md).

Não aplicar perda genérica para fazer a quantidade coincidir com outro orçamento. Verificar primeiro se as perdas já estão embutidas no coeficiente: acrescentar mais 10% ou outro percentual por hábito pode duplicá-las. Quando houver fator ou reserva adicional justificados, mostrar origem, base de incidência e aplicação uma única vez. Guardar a precisão disponível nas parcelas e arredondar na apresentação ou na regra de compra explicitamente adotada.

Não somar materiais ou unidades incompatíveis. Subtotais de famílias diferentes podem ser apresentados lado a lado sem formar um total sem significado físico.

<a id="evidencias-visuais-por-item"></a>

## 5. Produzir evidências visuais ligadas às parcelas

Usar imagens reais do projeto utilizado: captura do aplicativo, recorte/renderização de PDF ou exportação comprovada do desenho. Preservar geometria, informações e relação com a fonte. Não redesenhar um projeto presumido e apresentá-lo como imagem original.

### 5.1. Contrato de evidência por item

**Todo item físico cuja quantidade possa ser localizada no projeto precisa de print marcado incorporado à sua memória. Toda área considerada precisa ser demarcada.** A exigência abrange resultados confirmados, estimativas e subtotais; não se limita aos exemplos escolhidos para a entrega. A memória deve permitir reconhecer **o que foi considerado**, antes de conferir a conta.

Para cada item com levantamento físico:

1. Preparar uma vista geral que permita localizar todos os elementos considerados.
2. Marcar contornos, panos, peças, percursos e deduções com IDs iguais aos da tabela de parcelas.
3. Acrescentar detalhes legíveis dos vãos, cotas, curvas e pequenas parcelas que não possam ser auditados na geral.
4. Diferenciar inclusões, deduções e referências por legenda; preservar cotas essenciais e contexto de localização.
5. Identificar arquivo, prancha, revisão, página/vista e método das anotações. Distinguir cota transcrita de dimensão calculada.
6. Conferir alinhamento, escala e transformação entre coordenadas do desenho e pixels do recorte.
7. Verificar a correspondência nos dois sentidos: toda parcela aparece na imagem e toda marca de medição corresponde a parcela ou referência explicitada.

IDs são o vínculo entre desenho e conta. Se uma parcela é dividida, reclassificada ou excluída, atualizar sua marcação e as relações afetadas. Não manter imagem antiga ilustrando uma fórmula nova.

| Grandeza ou decisão | O print deve mostrar |
|---|---|
| Área de piso, forro, cobertura, proteção ou remoção | Contorno de cada região considerada, material/estado, recortes, vazios e deduções; distinguir regiões excluídas da soma |
| Parede, demolição, pintura ou revestimento vertical | Panos/faces localizados em planta e os cortes/elevações ou detalhes que sustentam alturas, faixas, vãos e retornos; marcar o que é existente, retirado ou novo |
| Comprimento e redes | Percursos e seus limites, trechos únicos, derivações, subidas/descidas e referências aos detalhes correspondentes; diferenciar trechos medidos de extensões assumidas |
| Luminárias, equipamentos e peças | Cada ocorrência considerada marcada e identificada; legenda/modelo correspondente e separação de amostras, vistas repetidas, existentes e novos |
| Área ou trecho estimado por premissa | Local e extensão adotados com anotação explícita de premissa; distinguir dimensões assumidas das indicadas no projeto |

Uma imagem pode atender mais de um item quando permitir identificar sem ambiguidade as parcelas de cada um e estiver incorporada às respectivas memórias. Uma planta inteira sem marcas específicas, um atlas de bases sem associação às parcelas ou a reutilização de um print genérico não atendem à exigência. Quando a redução para a planilha tornar IDs e limites ilegíveis, usar recortes por setor e detalhes; manter a geral para localização.

### 5.2. Exclusões, conflitos e informações faltantes

O estado do item também precisa ser compreensível visualmente quando houver fonte gráfica pertinente:

- **Não aplicável por material cancelado ou preservação:** destacar a especificação riscada/cancelada na legenda e a chamada correspondente na implantação, como o tipo de piso existente a manter. Explicar o efeito: sem compra nova integral daquele material, por exemplo. Mostrar e remeter a eventual serviço de reparo ou complemento, sem concluir que ele inexiste.
- **Alternativa ou composição já coberta:** localizar o mesmo elemento e citar o item que o atende, distinguindo fornecimento e instalação. A justificativa precisa mostrar por que duas linhas não geram duas ocorrências físicas.
- **Conflito entre fontes:** incorporar os recortes relevantes de cada fonte, marcar as indicações incompatíveis e explicar qual definição altera a quantidade. Identificar corretamente se a referência é nota de projeto, célula de planilha, legenda ou premissa.
- **Pendência ou subtotal:** marcar a região, o pano, o trajeto ou o equipamento conhecido e indicar objetivamente a entrada ausente, como altura existente, limite do percurso ou modelo não distribuído. Mostrar a parte comprovada e a parte não determinada em tratamentos distintos.

Ausência em uma vista parcial ou em um recorte não prova exclusão. Para concluir ausência ou cancelamento, documentar a cobertura examinada e a indicação que sustenta a decisão. Se não houver documento que permita localizar o elemento ou obter um print pertinente, registrar a fonte faltante e a limitação visual; não fabricar contorno ou marcação. A falta de print aplicável não pode ser ocultada por uma imagem sem relação com o item.

Em serviço administrativo, prazo, taxa ou verba sem representação física própria, declarar **“Sem representação gráfica aplicável”**, o motivo e a fonte do escopo/premissa. Quando um quadro ou texto contratual esclarecer o pacote, incorporar seu recorte real com o trecho destacado. Não produzir uma planta artificial para preencher esse campo.

Incorporar imagens à planilha como recursos de imagem suportados pelo formato, preservando-as no arquivo salvo; não depender exclusivamente de links temporários nem transformar a planilha inteira em um print. Manter fórmulas, números e tabelas como conteúdo nativo. Guardar também os arquivos técnicos necessários para reconstruir contornos e cálculos complexos.

Um esquema complementar pode explicar a conta, desde que seja identificado como derivado e acompanhado do recorte real de origem. Lista de coordenadas, nome de arquivo, revisão, hash, tamanho do DXF e referência a outro item são localizadores ou dados de rastreio; não substituem o print marcado nem explicam sozinhos uma exclusão ou pendência.

### 5.3. Verificação antes de considerar a memória auditável

Registrar, por item, `ID da evidência | fonte/vista | parcelas/ocorrências cobertas | inclusões/deduções/exclusões ou dúvida demonstrada | imagem incorporada | verificação de legibilidade`. Para item sem representação gráfica aplicável, registrar a justificativa no mesmo controle. Esse é um registro técnico de cobertura, não uma lista de tarefas.

Conferir o arquivo salvo: todas as parcelas físicas precisam ter correspondência visual; os IDs devem ser legíveis e a imagem deve representar o critério atual. Quantidade correta com print genérico ou desatualizado continua com auditoria visual incompleta. Corrigir antes da entrega ou identificar explicitamente o item e a limitação na memória e no quadro de cobertura; não declarar revisão visual integral por existir uma imagem na aba. Aplicar também o gate de [08 — Conferência e entrega](08_conferencia_comparacao_e_entrega.md).

## 6. Organizar as bases de ambientes e as memórias por ITEM

### 6.1. Bases de ambientes

Quando o arquivo comportar esse arranjo, manter abas/bases de ambientes com as grandezas já apuradas: nome/ID, área por origem, contorno, perímetros por critério, alturas e níveis, fontes, estado e revisões. Respeitar o mapeamento definido em [02](02_planilha_escopo_e_mapeamento.md).

Grandezas comuns devem ter uma fonte única referenciada pelos serviços. Uma alteração nessa fonte deve chegar às memórias dependentes. Evitar copiar números manualmente para múltiplas abas e perder o vínculo. Ao mesmo tempo, não obrigar um serviço a usar a base do ambiente quando seu contorno, estado, altura ou unidade forem diferentes: criar sua medição própria e explicar a diferença.

### 6.2. Uma aba por item

Criar uma memória por **ITEM de escopo identificado pela chave de origem**, e não somente por família de serviço ou ambiente. Nomear preferencialmente com o ID, como `1.2` ou `10.1.7`. Se houver repetição entre abas/listas, caracteres proibidos ou limites do aplicativo, usar nome válido e registrar a correspondência chave de origem → aba de memória. Preservar a descrição completa dentro da aba. Resumos e detalhamentos do mesmo universo devem compartilhar ou reconciliar a base medida, sem somar o resumo novamente aos seus detalhes.

| Bloco | Conteúdo mínimo |
|---|---|
| Identificação | Chave de origem, ID, descrição integral, unidade, ambientes/elementos e revisão/data |
| Resultado | Célula única de saída, estado e alcance do resultado |
| Critério | Grandeza, limites, faces, alturas, vãos, composição e perdas |
| Origem e fontes | Arquivos, revisões, localizadores e método por parcela |
| Parcelas | IDs, dimensões, multiplicidades, deduções, fórmulas e resultados |
| Evidências | Prints reais incorporados e marcados com os IDs das parcelas; inclusões/deduções e fontes da exclusão, conflito ou informação faltante, conforme seção 5 |
| Conferência | Método, subtotais, comparação e diferenças demonstráveis |
| Limitações | Pendências, exclusões, hipóteses e dependências |
| Dados auxiliares | Coordenadas, arcos, peças, classificação e entradas comuns necessárias |

Tabela de parcelas adaptável:

```text
ID | ambiente/elemento/face | estado | multiplicidade | dimensão 1 | dimensão 2
   | acréscimo/dedução | fórmula | resultado | unidade | fonte/método | estado
```

Adaptar nomes e unidades das colunas à conta: comprimento/altura, raio/ângulo, coordenadas ou contagem. Não colocar um raio em coluna intitulada largura. Explicitar se uma dedução já está incorporada à geometria; não subtraí-la novamente.

Junto à conta e aos prints, explicar em linguagem direta **“O que entrou”**, **“O que ficou fora”** e, quando aplicável, **“O que falta para concluir”**. Na aba principal, mostrar uma justificativa curta do estado e a referência à memória. Uma relação de nomes de arquivos ou hashes, sem a informação decisiva, não permite ao leitor entender a pendência.

### 6.3. Resultado padronizado e vínculo de QTD LEVANTADA

Manter **intactas todas as colunas originais de quantidade: cabeçalhos, valores, fórmulas e vazios**. Criar coluna própria `QTD LEVANTADA` nas abas/listas de origem abrangidas, vinculada às nossas memórias, conforme [02](02_planilha_escopo_e_mapeamento.md). Não preencher vazios originais nem substituir uma quantidade recebida por nosso resultado. Em revisão/retomada, atualizar uma coluna existente somente se sua autoria e origem como nosso levantamento estiverem comprovadas; o nome do cabeçalho ou a posição como primeira coluna numérica não bastam.

Adotar `G8` como célula de resultado quando o modelo permitir. Se o template tiver outra estrutura, preservar seu contrato e documentar a célula adotada. Manter o endereço consistente entre as memórias novas sempre que possível.

O resultado deve ser calculado pelas parcelas independentes, sem copiar nem referenciar como atalho as quantidades orçamentárias originais. O fluxo é:

```text
Medições/cálculos documentados → parcelas da memória → resultado do ITEM → QTD LEVANTADA
```

Para um resultado numérico completo, um vínculo típico na coluna `QTD LEVANTADA` da aba de origem correta é:

```excel
='1.2'!G8
```

Não criar circularidade fazendo a memória buscar como entrada a `QTD LEVANTADA` que ela própria alimenta. Medições comuns independentes podem ser compartilhadas por várias memórias; a dependência deve permanecer em um único sentido.

Manter estado, origem resumida e critério junto à nossa `QTD LEVANTADA` em cada aba de origem, conforme a estrutura disponível. Comentário pode complementar, mas não esconder limitação decisiva. Preservar descrição, unidade e todos os recursos existentes que integrem a entrega.

Se o resultado final depender de dado faltante, não exibir subtotal como total. Guardar o subtotal conhecido em campo próprio e propagar um marcador explícito e o estado à nossa `QTD LEVANTADA`, ou deixar esse campo vazio acompanhado de estado visível quando o template exigir coluna numérica. A quantidade original permanece intacta, mesmo quando estiver preenchida. **Não ligar diretamente uma célula vazia de memória sem proteção:** aplicativos podem exibir `0` para essa referência. Implementar e testar a proteção conforme o mecanismo de fórmulas disponível.

Totalizadores do nosso levantamento e cálculos de custos autorizados que dependam de `QTD LEVANTADA` devem verificar completude. Uma soma que ignora texto pode mostrar número aparentemente final enquanto itens estão pendentes; rotular o valor como parcial e manter a incompletude visível. Não usar `SEERRO/IFERROR(...;0)` ou equivalente para apagar ausência, erro de vínculo ou função não calculada. Não redirecionar fórmulas originais de custos ou totais para nossa coluna sem pedido específico.

### 6.4. Apresentação

Gravar medidas e quantidades como números nativos, com unidade em campo ou formato próprio. Formatar casas decimais/localidade sem transformar o número em texto. Destacar entradas, fórmulas e definições pendentes com legenda; congelar cabeçalhos quando útil. Organizar imagens sem cobrir resultados ou tabelas.

Atualizar simultaneamente nossas fórmulas, resumos, critérios, imagens e notas de comparação quando um cenário mudar. O texto deve descrever o cálculo que o arquivo efetivamente executa.

## 7. Estados e Pendências sem interromper o lote

### 7.1. Diagnóstico do serviço em relação ao projeto

Revisar cada item confrontando sua descrição integral e composição com o que o projeto efetivamente mostra. Registrar todos os problemas encontrados, sem criar uma dúvida fictícia quando houver compatibilidade. O relatório de cada memória deve conter:

```text
Item/descrição integral/unidade
Escopo do serviço → constatação do projeto e evidência
Problema(s)/categoria → solução aplicada ou proposta → base da resolução
Estado de cada problema → informação específica ainda necessária
Efeito na quantidade → ressalva de execução → ação de revisão realizada
```

Usar uma ou mais categorias quando necessário:

| Categoria | Questão tratada |
|---|---|
| ESCOPO_FASE | Existente, preservado, retirado ou novo; locais e etapas abrangidos |
| ESPECIFICACAO | Material, modelo, sistema, acabamento ou capacidade divergentes |
| GEOMETRIA_COTAS | Contorno, dimensões, alturas, níveis, vãos ou percurso |
| UNIDADE_CRITERIO | Unidade da linha, natureza da grandeza e regra de medição |
| COMPOSICAO_DUPLICIDADE | Fornecimento/instalação, componentes incluídos, agregadores e alternativas |
| DOCUMENTACAO_REVISAO | Fonte/revisão incompatível, documento ou vista necessária não disponível |
| PREMISSA_ORCAMENTO | Decisão ou reserva adotada para viabilizar o orçamento, com sua origem |
| DIMENSIONAMENTO_VISTORIA | Definição executiva ou verificação de campo que não pode ser comprovada pelo levantamento disponível |
| EVIDENCIA_RASTREABILIDADE | Print, identificação, legenda, vínculo ou explicação insuficientes para auditar |

Para cada problema, descrever a discrepância concreta, a evidência que a demonstra, a solução e quem/o que sustenta essa solução: projeto, critério contratual, decisão do usuário, premissa declarada ou definição técnica ainda necessária. Localizar e resolver nas fontes disponíveis antes de registrar falta de informação. Se a aproximação estiver autorizada, adotar e documentar o cenário de orçamento aplicável, mantendo seus parâmetros e limites visíveis.

Separar **solucionado por fonte/critério demonstrado**, **orçamento viável por premissa** e **executivo ou informação ainda pendente**. Uma estimativa não se transforma em solução executiva porque recebeu um número. Exclusão adotada no orçamento por conservação do imóvel também não comprova ausência física do elemento. Identificar a ressalva de execução sem reabrir como bloqueio de orçamento uma escolha usual já autorizada.

Explicar o impacto: quantidade alterada e antes/depois quando houver, parcela afetada, reserva de orçamento, exclusão de soma duplicada ou impacto não determinável com a informação atual. Não preencher apenas “a definir”: informar, por exemplo, qual altura, trecho de alimentação, interface, especificação ou documento falta e onde ele afeta a conta. Manter os prints e localizadores junto ao diagnóstico correspondente.

O relatório detalhado fica **em cada memória de item**, com a descrição completa preservada; a principal recebe uma conclusão curta e o vínculo. Um relatório central de revisão pode consolidá-los para filtrar problemas e pendências, mas não substitui a explicação e as evidências dentro de cada memória.

### 7.2. Estado do resultado e continuidade

Usar estados explícitos e coerentes entre base, memória e principal:

| Estado | Uso |
|---|---|
| CONFIRMADO | Resultado reproduzível para todo o alcance declarado |
| SUBTOTAL | Parte conhecida e delimitada; ainda não fecha o item completo |
| ESTIMATIVA | Aproximação expressa, com método e limitação |
| PENDENTE | Falta dado ou decisão que altera quantidade/classificação |
| NÃO APLICÁVEL | Fora do alcance por fonte ou premissa expressa, com justificativa; distinguir exclusão orçamentária adotada de ausência física comprovada |

Zero exige evidência. Falta de informação, quantidade não medida e ausência de especificação não equivalem a zero. Cenário calculado não equivale a decisão adotada.

Registrar em `Pendências`, na estrutura definida pelo fluxo:

```text
Item/elemento afetado | fonte(s) consultada(s) | informação faltante/conflito
                    | o que já está comprovado | impacto na quantidade/estado
                    | dependências | localização da memória/evidência
```

Documentar as alternativas e seus efeitos quando forem calculáveis, sem escolher arbitrariamente. Concluir as parcelas independentes, preparar imagens e fórmulas possíveis e continuar os demais itens. Não interromper o pipeline, nem abrir uma pergunta ao usuário a cada falta técnica encontrada. Consolidar as definições necessárias na entrega parcial identificada, segundo [03](03_duvidas_e_continuidade.md).

Para mudanças posteriores de critério ou revisão, registrar antes/depois, motivo/fonte, elementos e itens afetados e efeito nos resultados, preservando o histórico necessário à conferência. Não alterar cotas ou dados originais para coincidir com etiqueta, orçamento de referência ou expectativa.

## 8. Saída desta etapa

Ao passar para [08 — Conferência, comparação e entrega](08_conferencia_comparacao_e_entrega.md), cada item solicitado deve ter memória ou justificativa explícita de estado, vínculo rastreável em `QTD LEVANTADA` na aba de origem correta e evidência adequada ao que foi efetivamente levantado. As pendências não impedem essa passagem: delimitam o alcance da validação e da entrega.

Usar [07 — Computer use e encerramento](07_computer_use_e_encerramento.md) para operações em aplicativos e fechamento das cópias de trabalho, e [09 — Agentes e retomada](09_agentes_e_retomada.md) para divisão do lote e registro de continuidade. Não afirmar teste nativo que não tenha sido realizado.
