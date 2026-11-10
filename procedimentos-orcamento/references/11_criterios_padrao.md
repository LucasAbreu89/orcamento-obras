# 11 — Critérios padrão de medição

Perfil padrão do pacote. Vale quando o contrato, o caderno de encargos, a composição indicada na planilha ou o usuário não definirem outra regra ([10](10_boas_praticas_e_fontes.md) traz a ordem de precedência). O critério adotado em cada obra vai para a aba Critérios com a sua fonte. Os parâmetros marcados com ★ mudam muito a quantidade e são confirmados no checkpoint.

A geometria fica guardada em parcelas (faces, vãos, retornos separados), para que outro critério possa ser aplicado sem medir de novo. Para mudar o padrão da empresa, editar este arquivo.

## Regras gerais

- Quantidade geométrica líquida, sem perdas: perdas pertencem ao coeficiente da composição ([06 §4](06_quantitativos_e_memorias.md)).
- Precisão total nas contas; apresentação com duas casas decimais; compra e embalagem só quando pedidas.
- Um elemento pode entrar em vários serviços, cada um com sua grandeza; dentro do mesmo serviço, nenhuma parcela entra duas vezes.
- Demolição e retirada são medidas na condição existente; serviço novo, na condição de projeto.
- Item sem projeto da disciplina não é estimado pela arquitetura: fica PENDENTE ou recebe estimativa autorizada.

## Pisos e superfícies horizontais

| Serviço | Unidade | Regra padrão | Parâmetros |
|---|---|---|---|
| Piso, contrapiso, regularização, impermeabilização horizontal, proteção de piso | m² | Projeção horizontal do contorno interno entre as faces das paredes como desenhadas. Desconta pilares, shafts, alvenarias e bancadas de alvenaria que interrompem o piso; não desconta móveis soltos, louças e equipamentos apoiados. | ★ Faixa sob portas: entra no ambiente para onde o piso continua; havendo item de soleira, sai do piso |
| Soleira, peitoril | m (ou un, conforme o item) | Comprimento igual à largura do vão | Largura da peça conforme projeto |
| Rodapé | m | Comprimento das faces que recebem rodapé, menos a largura dos vãos de porta | ★ Retornos nas ombreiras: só se especificados |
| Subida de impermeabilização | m² | Perímetro da área impermeabilizada × altura de subida | Altura conforme projeto ou especificação; sem fonte, PREMISSA |

## Paredes e superfícies verticais

| Serviço | Unidade | Regra padrão | Parâmetros |
|---|---|---|---|
| Alvenaria, drywall, divisórias | m² | Comprimento pelo eixo, sem sobrepor encontros, × altura do piso à face inferior da laje ou viga (ou à cota de projeto) | ★ Vãos: descontar todos (área líquida) |
| Demolição de alvenaria ou divisória | m² ou m³ | Geometria existente efetivamente removida | Espessura existente para m³ |
| Chapisco, emboço, reboco, massa, gesso | m² | Área por face revestida: comprimento da face × altura do revestimento | ★ Vãos: descontar todos; ★ requadros (ombreiras, vergas, peitoris): incluir só se o item ou a composição pedir |
| Revestimento cerâmico ou pedra em parede | m² | Área por face até a altura especificada | Como o anterior |
| Pintura de paredes | m² | Área por face pintada, até a altura de pintura (forro, teto ou faixa) | ★ Vãos e requadros: como o revestimento |
| Verga e contraverga | m | Largura do vão + transpasse de cada lado | Transpasse conforme projeto; sem fonte, PREMISSA |

Cada face da mesma parede é uma parcela própria, com material, altura e acabamento. Quando o contrato ou a composição adotar outra regra de vãos (por exemplo, não descontar vãos menores que um limite e descontar só o excedente), ela é aplicada sobre as mesmas parcelas de vão.

## Forros e tetos

| Serviço | Unidade | Regra padrão |
|---|---|---|
| Forro (gesso, mineral, madeira, metálico) | m² | Projeção horizontal por material e nível. Não desconta luminárias embutidas, grelhas e recortes menores que um módulo do forro. |
| Tabica, sanca, cortineiro, testeira | m (ou m² desenvolvido, conforme o item) | Percurso real; para m², altura desenvolvida |
| Pintura de forro ou teto | m² | Área pintada; superfícies verticais de sancas e rebaixos somadas como parcelas próprias |

## Coberturas

| Serviço | Unidade | Regra padrão |
|---|---|---|
| Telhamento, impermeabilização de cobertura | m² | Área desenvolvida (real, com a inclinação), por água |
| Estrutura de telhado | m² | Projeção horizontal, salvo outra unidade no item |
| Rufos, calhas, cumeeiras, rincões | m | Comprimento real |

## Esquadrias, vidros, marcenaria, louças e equipamentos

| Serviço | Unidade | Regra padrão |
|---|---|---|
| Portas, janelas, grades, portões | un (por tipo) ou m² | Contagem pelo quadro de esquadrias, conferida na planta; em m², largura × altura do vão do tipo |
| Vidros e espelhos | m² ou un | Área de cada peça ou módulo; duas lâminas não dobram a área de um módulo, salvo item por lâmina |
| Bancadas, tampos, saias, frontões | m², m ou un (conforme o item) | Cada peça separada; recorte de cuba não descontado |
| Marcenaria | un ou m² (conforme o item) | Por peça do detalhamento |
| Louças, metais, acessórios, equipamentos, luminárias | un | Ocorrências físicas únicas, por tipo |

## Instalações

| Serviço | Unidade | Regra padrão | Parâmetros |
|---|---|---|---|
| Pontos (tomadas, interruptores, água, esgoto, dados) | un | Contagem por tipo na planta da disciplina | — |
| Eletrodutos, tubos, dutos | m (por diâmetro ou seção) | Trechos horizontais medidos na planta + trechos verticais (diferença entre a altura do ponto e o nível da rede) | Subida ou descida sem cota: PREMISSA |
| Cabos e fios | m (por seção) | Soma dos trechos do circuito × número de condutores do circuito + sobras nas extremidades | Sobras conforme especificação; sem fonte, PREMISSA |
| Conexões, caixas, curvas | un | Contagem no projeto; sem desenho, regra declarada como PREMISSA | — |
| Dutos de ar em chapa | m² ou kg | Área desenvolvida da chapa (perímetro da seção × comprimento) | — |

## Estrutura, fundações e movimento de terra

| Serviço | Unidade | Regra padrão |
|---|---|---|
| Concreto | m³ | Volume geométrico por elemento, sem duplicar interseções: cada encontro entra uma vez, no elemento que o quadro do projeto indicar ou, na falta dele, na ordem pilar, viga, laje |
| Formas | m² | Superfície de contato com o concreto; faces contra o solo só se o item pedir |
| Armadura | kg (por bitola e categoria) | Quadro de ferragem do projeto, conferido por amostragem; sem quadro, PENDENTE |
| Estacas | m (por diâmetro) ou un | Comprimento × quantidade, pela locação e pela tabela de estacas |
| Escavação, aterro, reaterro | m³ | Volume geométrico in situ; empolamento e compactação só com fator de fonte declarada |
| Bota-fora e transporte | m³ ou m³×km | Volume solto = volume in situ × fator de empolamento declarado; distância conforme o item |

## Serviços gerais

| Serviço | Unidade | Regra padrão |
|---|---|---|
| Limpeza final de obra | m² | Área de piso construída ou reformada; fachadas e vidros só se o item pedir |
| Proteções provisórias | m² ou un | Superfícies ou elementos a proteger definidos no escopo |
| Tapume, andaime | m ou m² | Perímetro ou área do canteiro ou da fachada, conforme o item |
| Administração local, mobilização, equipe, consumos, ART, seguros | — | `NÃO APLICÁVEL` (custo indireto — definir pela engenharia), salvo pedido. Vale mesmo quando a unidade é mês |
| Outros itens em meses (aluguel de equipamento, vigilância contratada) | mês | Prazo da fonte (cronograma ou contrato); sem prazo, PENDENTE |
| Verbas | vb | 1 somente para pacote com escopo definido; o pacote é descrito |
