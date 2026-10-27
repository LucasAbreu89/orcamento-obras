# Perímetros, faces e alturas por serviço

Aplicar a qualquer projeto e pasta de trabalho. Registrar geometria, finalidade, fontes, método e critério antes de converter comprimentos e alturas em quantitativos. Não transportar dimensões, alturas, critérios de acabamento ou convenções de um empreendimento para outro.

## Índice

1. [Grandezas, fontes e continuidade](#1-grandezas-fontes-e-continuidade)
2. [Contornos, interfaces e vãos](#2-contornos-interfaces-e-vãos)
3. [Cálculo e medição de comprimentos](#3-cálculo-e-medição-de-comprimentos)
4. [Alturas, níveis e zonas](#4-alturas-níveis-e-zonas)
5. [Conversão em quantidade por serviço](#5-conversão-em-quantidade-por-serviço)
6. [Conferência e registros na planilha](#6-conferência-e-registros-na-planilha)
7. [Exemplos fictícios](#7-exemplos-fictícios)

## 1. Grandezas, fontes e continuidade

Não tratar grandezas diferentes como intercambiáveis:

| Grandeza | Definição operacional | Limite de uso |
|---|---|---|
| `Pgeom` | Comprimento da fronteira da união das regiões incluídas pelo critério, com contornos internos explicitamente declarados | Pode conter fechamento virtual ou limite operacional sem face física |
| `Pfaces` | Extensão dos trechos classificados como faces delimitadoras da região e finalidade descritas | Exclui linhas virtuais; um fechamento nominal pode ser vidro, painel ou caixilho |
| Comprimento de serviço | Extensão física onde o serviço será executado conforme especificação própria | Exige decidir faces, interrupções, retornos, inclusões e deduções |
| Altura de serviço | Distância vertical ou dimensão desenvolvida efetivamente aplicável ao trecho e serviço | Não é automaticamente pé-direito nem uma altura única por ambiente |

Para `Pgeom`, separar `Pexterno` e `Pinterno` quando existirem ilhas ou vazios excluídos; declarar se o total solicitado inclui ambos. Interfaces entre parcelas pertencentes à mesma união desaparecem da fronteira. Uma parede física interna, por sua vez, pode continuar exigindo serviço em suas faces mesmo que não participe da fronteira externa daquela união.

**`Pgeom` e `Pfaces` não são automaticamente rodapé, pintura, revestimento ou alvenaria.** Uma linha de vidro pode delimitar o espaço sem representar alvenaria a pintar. Uma quantidade de serviço não deve ser deduzida por convenção de outro serviço.

### Fonte e método junto ao valor

| Origem efetiva | Rótulo a usar |
|---|---|
| Quadro, etiqueta ou memorial | Perímetro/altura indicado no projeto — transcrito |
| Cotas explícitas | Perímetro/altura calculado pelas cotas |
| Coordenadas extraídas | Perímetro/altura calculado pelas coordenadas, com plano e geometria |
| Comando nativo realmente executado | Perímetro/altura medido por comando nativo, nomeando-o |
| Medição gráfica calibrada | Estimativa gráfica, com calibração e limitação |
| Modelo BIM | Comprimento/altura extraído do modelo — propriedade e critério identificados |

Em pedidos de catálogo, transcrever a informação existente sem criar cálculo não solicitado. Para cada grandeza registrar arquivo, disciplina, prancha, revisão, página/vista/espaço, região, data e evidência. Conferir compatibilidade entre planta, cortes, detalhes, esquadrias, estrutura, forro e memorial. Não combinar sem registro uma altura de existente com um comprimento de proposta.

Em BIM, registrar IDs, revisão/fase, unidade, propriedade e filtros. Não inferir critério apenas pelo nome da propriedade; distinguir extensão nominal, comprimento de eixo, face e altura calculada. Para áreas ou volumes derivados, confirmar bruto/líquido, aberturas e encontros. Evitar duplicatas de objetos, vínculos, federações e exportações repetidas antes de agregar.

Na organização padrão do pacote, relacionar memórias em `levantamento-orcamento/execucoes/<data>/03_memorias_servicos`, evidências em `04_evidencias`, planilhas em `05_planilhas` e dados de geometria/níveis em `08_dados_tecnicos`, todos dentro da mesma execução. Adaptar ao destino definido pelo usuário.

### Continuidade sem valores inventados

Falta de altura, diferença de revisão, dúvida de interface ou impossibilidade de executar CAD gera registro na aba **Pendências**, ligado aos trechos e serviços afetados. Continuar os demais ambientes, faces, serviços e documentos independentes. Ver [Dúvidas e continuidade](03_duvidas_e_continuidade.md).

- Não inventar altura ou comprimento e não substituir ausência por zero. Campo numérico sem valor deve ter situação e ID de Pendência em campos próprios.
- Conservar o comprimento conhecido mesmo quando a altura estiver indeterminada; a área de serviço dependente permanece não determinada.
- Se houver cenários documentáveis, manter versões identificadas e comparáveis. Não somar alternativas nem transformar hipótese em resultado confirmado.
- Um subtotal com trechos ainda não quantificados deve mostrar sua cobertura e os itens excluídos; não se apresenta como total concluído.
- Registrar dúvidas como dados para revisão, sem perguntas que parem o lote. Indisponibilidade de app ou arquivo limita o item correspondente e fica expressa na entrega.

## 2. Contornos, interfaces e vãos

Definir finalidade e faces antes da conta. Mostrar o traçado completo em imagem geral, por exemplo `IMG01`, com segmentos `S01`, `S02` etc. Criar detalhes para vãos, retornos, arcos, interfaces e segmentos curtos. Cada trecho da memória deve ser localizável na imagem.

| Elemento | Definição necessária |
|---|---|
| Paredes | Face interna nominal, acabada, eixo ou outra referência |
| Portas | Linha virtual, largura e sua referência, ombreiras, profundidade, retornos e batentes |
| Janelas, vidro e painéis | Linha nominal do fechamento, face de caixilho e superfícies realmente tratadas |
| Paredes/divisórias internas | Faces físicas existentes e interfaces geométricas das parcelas |
| Shafts, pilares e ilhas | Contorno interno, região excluída e participação em cada grandeza |
| Limites abertos/operacionais | Trechos virtuais que entram em `Pgeom`, quando o critério exigir, e não em `Pfaces` |
| Acabamentos | Referência nominal ou acabada, sem descontar espessura novamente |

Percorrer todas as reentrâncias, bonecas, recuos e mudanças de direção. Não transformar a linha de fechamento de um ambiente em parede física. Não ignorar um contorno interno apenas por estar dentro do envelope externo.

### União de parcelas

Para regiões disjuntas em área, com interfaces lineares comuns coincidentes e cada interface compartilhada por duas parcelas:

```text
Pgeom = Σ P(parcela_i) − 2 × Σ L(interface comum)
```

Listar cada interface uma vez, com parcelas, extremos e comprimento. O fator dois elimina a ocorrência da interface no perímetro de cada parcela. Não aplicar a fórmula cegamente a sobreposições, interfaces parciais, múltiplas incidências ou geometrias complexas; nesses casos determinar a fronteira real da união e documentar a operação.

Conferir coincidência real. Pontos próximos não são automaticamente iguais; registrar discrepância, tolerância usada e efeito. Não deslocar vértices para forçar igualdade. Preservar a origem de eventual ajuste de uma cópia e manter o resultado anterior rastreável.

Uma porta interna em interface já cancelada não é subtraída novamente de `Pgeom`. Para ambientes quantificados separadamente, definir como cada face física, abertura e soleira participa do agregado. Distinguir duplicação indevida de duas faces físicas distintas que recebem serviços legítimos.

### Auditoria de portas e retornos

Para cada vão, identificar sua imagem e segmento, largura usada, linha de fechamento, profundidade real, ombreiras, batentes, retornos e mudanças de plano. Registrar quais trechos já estão na polilinha e na quantidade do serviço.

- Em `Pgeom`, o critério pode manter o fechamento virtual da abertura.
- Em `Pfaces`, retirar a linha virtual e acompanhar somente as faces classificadas como delimitadoras, incluindo retornos quando pertinentes.
- No rodapé, definir interrupção na abertura, continuidade em recuos e retornos efetivamente especificados.
- Na pintura ou no revestimento, identificar aberturas, ombreiras, vergas, peitoris e faces internas com seu material e acabamento.

Largura de folha não prova largura de vão. O arco do giro da folha não compõe o perímetro arquitetônico. Profundidade de retorno exige fonte; não inferi-la pela espessura aparente em uma captura. Dedução de pintura, rodapé e revestimento tem critério próprio e não deve migrar automaticamente de um serviço para outro.

## 3. Cálculo e medição de comprimentos

### Segmentos e curvas

Para segmento reto no plano entre dois pontos:

```text
Δx = x2 − x1
Δy = y2 − y1
L_planta = √(Δx² + Δy²)
```

Para arco circular de raio `r` e ângulo central `θ` em radianos:

```text
L_arco = r × |θ|
```

Usar raio, ângulo, bulge ou outra representação analítica válida. Não substituir arco por corda ou segmentos sem identificar aproximação, resolução e efeito. Conferir unidade angular: graus devem ser convertidos antes de usar a fórmula em radianos.

Distinguir comprimento em planta de comprimento espacial ou desenvolvido. Se houver inclinação e a finalidade exigir comprimento 3D, usar método e fonte coerentes; não somar comprimento inclinado quando se pede projeção horizontal. Manter planos e níveis separados antes de totalizar.

Em rodapés de rampas, bordas de cobertura e outros percursos inclinados, conferir se o serviço exige extensão desenvolvida. Em superfícies, distinguir área em projeção e desenvolvida; não multiplicar indiscriminadamente um comprimento projetado pela altura vertical para representar uma face inclinada. As práticas e convenções documentadas devem ser verificadas conforme [Boas práticas e fontes](10_boas_praticas_e_fontes.md), sem adotar limiares externos como regras universais.

Se uma unidade do desenho corresponde a `k` metros:

```text
L_m = L_unidades × k
```

O fator é linear, `k`, e não `k²`. Conferir unidade configurada e pelo menos duas dimensões conhecidas, quando disponíveis; escala impressa ou variável de unidades isolada não comprova a geometria. Se a validação não for possível, registrar a limitação e prosseguir nos demais itens.

### Medição no CAD e uso da interface

Preservar o DWG original e trabalhar em cópia identificada. Auditar entidade, fechamento, plano XY/Z, sistema de coordenadas, unidade, arcos/bulges, segmentos repetidos, cruzamentos e interfaces. Contornos reconstruídos devem ser identificados como tal.

Ler as ferramentas, documentação e recursos atuais do aplicativo antes de operar. No AutoCAD, quando disponível, executar `AREA` → `Object` no objeto conferido e registrar o `Perimeter` reportado, a área da mesma execução, camada e handle/ID. Usar Properties, `LIST` ou recurso equivalente realmente disponível para verificar propriedades.

Confirmar `Closed = Yes` no objeto destinado a representar contorno fechado. O comando pode reportar área por fechamento implícito de polilinha aberta, enquanto seu perímetro não inclui a linha de fechamento imaginada; área retornada não prova perímetro fechado. Para medir uma face aberta, identificar deliberadamente a entidade aberta e seu objetivo, sem apresentá-la como contorno fechado.

Esse comportamento refere-se à opção de seleção do objeto. Na entrada direta de pontos, o fechamento implícito pode entrar no perímetro; registrar a opção usada. Em modos de adição/subtração, não presumir que o perímetro acumulado represente a fronteira da união: conferir interfaces pelo método da seção 2. Ver a referência Autodesk em [10](10_boas_praticas_e_fontes.md).

Uma variável como `PERIMETER` ou a leitura de uma propriedade só pode ser citada conforme disponibilidade e comportamento confirmados na versão usada. Registrar logo após medir o objeto correto e distinguir leitura armazenada de nova execução.

Salvar evidência do contorno completo e do resultado nativo legível, vinculada ao objeto. Cálculo por script ou coordenadas continua sendo cálculo por coordenadas, mesmo quando numericamente coincide com o CAD. Sem execução não afirmar `AREA executado`, `medido no AutoCAD` ou qualquer comando equivalente. Ver [Computer use e encerramento](07_computer_use_e_encerramento.md).

## 4. Alturas, níveis e zonas

Altura precisa de referência inferior, referência superior, estado da obra e serviço. Não adotar uma altura padrão pelo nome do ambiente, por outro projeto ou por uma única anotação de pé-direito.

### Existente, demolição e proposta

Registrar separadamente a condição **existente**, **a demolir/remover** e **proposta**, conforme a documentação disponível. Um levantamento cadastral pode medir o existente; um corte proposto pode definir a nova altura. Não substituir um pelo outro sem declarar o uso e a compatibilidade.

Quando houver altura existente e proposta diferentes, associar cada uma ao serviço correto: remoção, nova execução, complementação, manutenção ou acabamento. A diferença entre alturas só representa uma faixa de obra se a posição, continuidade e solução construtiva permitirem essa conclusão.

### Níveis e referências

| Referência | O que conferir |
|---|---|
| Piso | Acabado ou bruto; nível existente/proposto; eventual desnível e espessura de regularização |
| Forro | Face inferior acabada, cota de nível ou altura sobre o piso; inclinação e tipo de forro |
| Laje | Face inferior ou superior; não usar espessura implícita para converter entre as faces |
| Vigas | Cota da face inferior, largura/projeção, trecho afetado e eventual envelopamento |
| Rebaixos, sancas e cortineiros | Zona de abrangência e superfícies horizontais/verticais específicas |
| Topo de parede/divisória | Altura até forro, laje, viga ou outra referência expressa |
| Peitoril, verga e frisos | Referência da abertura e limites de faixas de revestimento |

Quando os níveis usam o mesmo datum e unidades compatíveis:

```text
H_entre_níveis = N_superior − N_inferior
```

Conferir a referência de cada nível antes da subtração. Uma altura negativa inesperada indica possível incompatibilidade de referência, não quantidade a aceitar automaticamente. Não somar cotas de nível a alturas já medidas sobre o piso sem analisar o significado.

Pé-direito livre até o forro, pé-direito até a face inferior da laje e distância no entreforro são grandezas diferentes. A cota de topo da laje não fornece sua face inferior sem espessura documentada. O nível de piso acabado não equivale ao piso bruto.

### Variação dentro do ambiente

Setorizar em zonas ou segmentos quando houver vigas, laje inclinada, forros em níveis diferentes, pisos em patamares ou paredes de altura variável. Associar cada comprimento à altura local aplicável. Uma única multiplicação `perímetro × altura média` só é admissível se a altura média estiver demonstrada para aquela geometria e finalidade.

Para trecho cuja borda superior varia linearmente e cuja base tem referência compatível, uma face simples pode ser decomposta em retângulo e triângulo, ou calculada como trapézio. Se a variação não for linear, decompor conforme as fontes. Não adotar média aritmética de alturas sem demonstrar a área representada.

Fonte ambígua gera Pendência por zona. Registrar separadamente as alturas conhecidas, mantendo os outros serviços e segmentos em andamento.

## 5. Conversão em quantidade por serviço

Usar comprimentos e alturas como insumos rastreáveis, com critério específico. Para levantar e vincular a memória ao Excel, aplicar [Quantitativos e memórias](06_quantitativos_e_memorias.md).

Na memória de cada serviço, incorporar prints reais marcando os trechos considerados e, para áreas de parede ou faixas, as faces e os limites verticais aplicados. Usar os mesmos IDs da conta e distinguir o que será demolido, construído, preservado ou apenas usado como referência. Uma linha em planta sem identificação da face/altura não comprova sozinha a superfície calculada. Seguir o [contrato de evidência por item](06_quantitativos_e_memorias.md#evidencias-visuais-por-item).

| Serviço ou finalidade | Definição necessária antes de quantificar |
|---|---|
| Rodapé | Trechos físicos executados, interrupções, retornos, material e unidade contratual |
| Pintura de paredes | Faces, substrato, limites verticais, aberturas e retornos tratados |
| Revestimento de paredes | Faixas, altura local, encontros, deduções e peças de acabamento |
| Alvenaria/divisória | Altura construtiva, limites até laje/viga/forro, aberturas e composição |
| Septo/fechamento no entreforro | Local, comprimento, limites inferior/superior e relação com a parede principal |
| Remoção/demolição | Geometria existente e extensão efetivamente removida |
| Sanca, testeira ou faixa vertical | Comprimento e altura desenvolvida próprios, sem confundir com área horizontal de forro |

Para face plana retangular de altura constante:

```text
A_bruta_face = L_face × H_serviço
A_líquida_serviço = Σ A_brutas − deduções aplicáveis + retornos ainda não incluídos
```

Cada parcela deve indicar face, material, serviço e origem das dimensões. A regra de dedução pode depender de contrato, composição ou instrução do usuário; registrá-la. Quando não estiver definida, registrar Pendência e cenários quando calculáveis, sem assumir limiar de dedução universal.

Não multiplicar por duas faces automaticamente. Uma parede pode ter comprimentos, alturas, materiais e acabamentos diferentes em cada lado. Representar as faces com IDs próprios e explicitar eventual agrupamento equivalente.

### Parede até a laje e septo: evitar dupla contagem

Representar as faixas verticais e sua participação no serviço:

- Se a quantidade da parede já vai do piso à laje, o trecho acima do forro já está dentro dessa área; não acrescentar o mesmo trecho novamente como septo do mesmo serviço.
- Se a parede foi medida somente até o forro e existe fechamento adicional acima, quantificar a faixa complementar somente com limites, extensão e solução documentados.
- Se o septo for um elemento distinto, indicar localização, faces e composição para demonstrar por que é quantidade adicional, mesmo quando se encontra próximo de uma parede.
- Pintura até o forro pode ter altura diferente da alvenaria até a laje. Conservar ambas, associadas aos serviços correspondentes.

O controle é por elemento, face, faixa vertical, extensão e serviço. Compartilhar comprimento não significa compartilhar altura, nem autoriza somar todas as áreas derivadas no mesmo serviço.

### Vigas, aberturas e retornos

Não descontar a projeção de uma viga da parede e somar o mesmo revestimento de volta sem mostrar superfícies e limites. Quando o serviço envolver faces inferiores/laterais de vigas, testeiras ou rebaixos, separar suas áreas e impedir sobreposição com forro e parede.

Para aberturas, registrar largura e altura do vão utilizado, base/peitoril, topo/verga, face e dedução aplicável. Ombreiras, vergas e peitoris podem gerar retornos próprios conforme a especificação. Não aplicar `largura × altura` a abertura irregular sem descrever a decomposição; não adicionar retornos já incluídos no contorno desenvolvido ou em outra parcela.

## 6. Conferência e registros na planilha

Somar comprimentos, cancelar interfaces e calcular áreas sem arredondar antecipadamente. Exibir precisão compatível com fontes, tolerâncias e finalidade; precisão do CAD não equivale à precisão física da obra.

Comparar métodos mantendo suas origens separadas. Diferença entre cotas arredondadas e coordenadas deve ser mostrada e investigada, sem mover pontos ou escolher altura para coincidir com outra memória. Registrar discrepâncias não resolvidas em Pendências e continuar o lote. Aplicar [Conferência, comparação e entrega](08_conferencia_comparacao_e_entrega.md).

Adaptar os modelos às abas existentes. As tabelas descrevem registros técnicos; não constituem lista de tarefas do projeto.

### Segmentos e finalidade

| ID região/cenário | Segmento | Tipo de linha | Geometria/fórmula | Medidas e fontes | Comprimento em m | Entra em Pgeom? | Entra em Pfaces? | Serviço/face | Imagem/objeto | Situação/Pendência |
|---|---|---|---|---|---:|---|---|---|---|---|
| REG-.../C... | S... | Física, nominal ou virtual | Reta, arco ou outra | Dimensões e origem | Campo numérico | Critério | Critério | ID específico | IMG/handle | Estado explícito |

### Interfaces e união

| ID interface | Parcelas envolvidas | Extremos/geometria | Comprimento comum | Coincidência/tolerância | Cancelamento aplicado | Evidência | Situação/Pendência |
|---|---|---|---:|---|---|---|---|
| IF-... | A... e A... | Referências verificáveis | Campo numérico | Verificação documentada | Quantas ocorrências foram removidas | IMG... | Estado explícito |

### Alturas e níveis

| ID altura | Estado da obra | Ambiente/zona/segmento | Serviço/face | Referência inferior | Referência superior | Níveis e datum | Altura em m | Método/fonte/localizador | Situação/Pendência |
|---|---|---|---|---|---|---|---:|---|---|
| H-... | Existente, remoção ou proposta | ID geométrico | Uso específico | Piso ou outra face identificada | Forro, laje, viga etc. | Mesma referência validada | Campo numérico | Transcrição, cotas ou medição efetiva | Estado explícito |

### Memória do serviço

| ID serviço | Elemento/face/faixa | Comprimento vinculado | Altura vinculada | Fórmula | Área bruta | Aberturas/deduções | Retornos não incluídos | Quantidade e unidade | Critério/cenário | Fonte/evidência | Situação/Pendência |
|---|---|---|---|---|---:|---|---|---|---|---|---|
| SV-... | Identificação única | S... | H... | Expressão auditável | Campo numérico | IDs e regra | IDs e fórmula | Campo numérico + unidade | Regra do serviço | Documento/imagem | Estado explícito |

### Pendências e cobertura dos totais

| ID | Informação faltante ou divergência | Registros afetados | Efeito sobre a quantidade | Tratamento atual | Informação necessária para resolver |
|---|---|---|---|---|---|
| PD-... | Altura, critério, unidade etc. | S..., H..., SV... | Item/subtotal/cenário afetado | Não determinado, parcial ou cenários separados | Fonte ou definição específica |

O resumo deve distinguir `Pgeom`, `Pfaces`, comprimentos por serviço e áreas por serviço. Não somar grandezas diferentes. Informar quais registros compõem cada subtotal e quais permanecem sem quantidade determinada. Um registro sem altura não pode entrar como área zero em um total apresentado como completo.

## 7. Exemplos fictícios

Todos os valores desta seção são inventados apenas para explicar o método. Não representam medição, comando executado ou regra de projeto real.

### União e comprimento de serviço

Suponha duas parcelas fictícias retangulares adjacentes, `2,00 × 3,00 m` e `1,00 × 3,00 m`, compartilhando interface coincidente de `3,00 m`. Não há vazios internos.

```text
P(A01) = 2 × (2,00 + 3,00) = 10,00 m
P(A02) = 2 × (1,00 + 3,00) = 8,00 m
Pgeom da união = 10,00 + 8,00 − 2 × 3,00 = 12,00 m
```

Uma abertura externa fictícia de `0,90 m` integra a linha virtual de fechamento desse cenário. Se, somente neste exemplo simplificado, não houver retornos adicionais a incluir, `Pfaces = 12,00 − 0,90 = 11,10 m`. A quantidade de rodapé ainda exige definir onde ele será executado e suas interrupções; não recebe automaticamente nem `12,00 m` nem `11,10 m`.

### Alturas distintas e faixa acima do forro

Para uma parede fictícia de `4,20 m`, suponha piso acabado no nível `+0,00 m`, face inferior do forro em `+2,70 m` e face inferior da laje em `+3,30 m`, todos no mesmo datum. Suponha, apenas para demonstrar faixas, uma face sem aberturas e alvenaria contínua até a laje.

| Uso demonstrativo | Altura fictícia | Cálculo por face | Área fictícia |
|---|---:|---|---:|
| Pintura da parede somente até o forro | 2,70 m | `4,20 × 2,70` | 11,34 m² |
| Parede até a laje | 3,30 m | `4,20 × 3,30` | 13,86 m² |
| Faixa acima do forro, já contida na parede até a laje | 0,60 m | `4,20 × (3,30 − 2,70)` | 2,52 m² |

Os `2,52 m²` demonstram a parte superior da parede; acrescentá-los aos `13,86 m²` da mesma face e serviço duplicaria a faixa. Se a solução real usar septo distinto, é necessário identificar esse elemento e sua composição antes de quantificá-lo.

Se outro trecho tiver somente altura de forro conhecida e faltar a cota da viga, manter a altura de pintura que estiver documentada, registrar a altura construtiva não determinada em Pendências e continuar os demais trechos. Não presumir que a viga coincide com o forro ou com a laje.
