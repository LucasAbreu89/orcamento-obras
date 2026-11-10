# 06 — Quantitativos e memórias por item

## 1. Contrato de medição do item

Antes de selecionar geometria, fixar para cada item (ou para a família, com o item apontando para ela):

| Campo | Definição |
|---|---|
| Item | chave, ID, descrição integral, unidade |
| Estado físico | existente, demolir ou retirar, manter, reaproveitar, novo |
| Onde | ambientes, elementos, faces |
| Limite de medição | face, eixo, projeção, superfície desenvolvida, peça, conjunto |
| Alturas e níveis | existente ou proposto; início e fim de cada pano |
| Inclusões e exclusões | vãos, vergas, retornos, interfaces, componentes de outros itens |
| Composição | fornecimento, instalação, retirada, transporte e acabamento incluídos |
| Natureza da quantidade | geométrica, de execução (critério da composição), consumo ou compra |

O critério vem do usuário, do contrato ou da composição indicada na planilha; na falta deles, de [11](11_criterios_padrao.md) (precedência em [10](10_boas_praticas_e_fontes.md)). A descrição do item não é ampliada para acomodar material sem item, e a convenção de um item não é transportada para outro.

## 2. Inventário físico e origem dos valores

Cada elemento e cada parcela têm ID estável (`P01` pano, `V01` vão, `S01` trecho, `E01` equipamento), com prefixo de ambiente ou de arquivo quando necessário. Planta, corte, ampliação e detalhe que mostram a mesma peça apontam para um ID só. Multiplicidade (`×3`) só depois de confirmar dimensões, especificação e local de todas as peças.

**Contagens** são reconciliadas por três leituras: lista de IDs, total por família e total por ambiente. Amostras de legenda e vistas repetidas saem da contagem. Em CAD, peças costumam estar dentro de outros blocos: `cad.py inventario` conta também os blocos aninhados, e `cad.py extrair --blocos` lê a geometria de dentro dos blocos. Conteúdo de referência externa só é lido com o arquivo referenciado.

| Origem | Registro junto ao valor |
|---|---|
| Indicado no projeto | transcrição e localizador |
| Cotas | dimensões, vista e fórmula |
| Coordenadas | entidades ou handles, unidade validada, script |
| Comando nativo | aplicativo, comando, objeto e resultado |
| Contagem | lista de peças e locais |
| Medição gráfica | calibração e limitação (PREMISSA) |
| Premissa | ID `P###` |
| Critério do usuário | decisão registrada |

## 3. Critérios por família

As regras padrão estão em [11](11_criterios_padrao.md), e os serviços que costumam acompanhar cada elemento estão na [matriz](../assets/MATRIZ_SERVICOS_ASSOCIADOS.md). Pontos que mais geram erro:

- **Pisos:** contorno próprio do serviço ([04](04_calculo_de_areas.md)); existente, removido, mantido e novo separados, assim como cada material; hachura pode mostrar só o piso visível; rodapé (m) nunca soma com piso (m²).
- **Paredes, divisórias, demolições:** panos por material, sistema, estado, altura e face; encontros em L e T sem sobreposição; altura existente para demolição e prevista para o novo; divisória de duas faces medida por uma elevação quando a composição inclui as duas.
- **Forros:** contorno próprio, nunca cópia da área do piso sem prova; sancas, tabicas e cortineiros com medida própria. Forro novo mostrado em ampliação abaixo de um forro existente é localizado na implantação e na ampliação que define material e nível, com os mesmos IDs nas duas vistas: a projeção transferida para a planta superior não prova o acabamento do plano inferior.
- **Rodapés, pintura, revestimentos:** mapa de trechos e faces ([05](05_perimetros_e_alturas.md)); objeto à frente da parede não justifica desconto; `perímetro × pé-direito` só depois de conferir todas as faces.
- **Vidros, espelhos, pedras, marcenaria:** peça física e unidade; duas lâminas não dobram um módulo; tampo, saias, frontões, laterais e cubas discriminados; conta parcial é SUBTOTAL.
- **Louças, metais, equipamentos, luminárias:** ocorrências físicas únicas; inventário de todas as famílias do projeto antes de distribuir pelos itens; característica ausente (cor, facho) não é deduzida da aparência.
- **Fitas LED e perfis:** percurso físico real, sem duplicar luminotécnico, forro e detalhe.
- **Verbas, meses, limpeza, transporte:** `1 VB` só para pacote definido; meses vêm do prazo da fonte; bota-fora exige volume, material e fator declarados.

### Construção nova e projetos complementares

- **Fundações e estrutura:** usar primeiro os quadros-resumo do projeto (concreto por elemento, formas, aço por bitola, estacas) como "indicado no projeto" e conferir por amostragem, recalculando ao menos um elemento de cada tipo pela geometria. Sem projeto estrutural, o item fica pendente; consumo por taxa (kg/m³) só como estimativa autorizada.
- **Terraplenagem:** volumes por seções ou malha; corte, aterro, reaterro e bota-fora separados; volume in situ, solto e compactado só se convertem com fator de fonte declarada.
- **Coberturas e impermeabilização:** área desenvolvida, rufos, calhas, cumeeiras e subidas conforme a especificação; perdas e sobreposições aplicadas uma vez só.
- **Instalações:** pontos e peças por contagem de blocos; tubos, eletrodutos e dutos por trecho e diâmetro, somando subidas e descidas (diferença entre a altura do ponto e o nível da rede); cabos por circuito (diagrama unifilar ou quadro de cargas) × trecho, com sobras declaradas; conexões por contagem ou regra declarada. Quantidade de pontos não prova metros de rede, e a mesma rede em planta, detalhe e isométrico é um trecho só.

### Reforma

Separar existente comprovado, existente aparente e oculto não verificado; vistoria não realizada nunca é afirmada. Mapear proteção, retirada, reaproveitamento, transporte e reinstalação quando houver item. Recomposição necessária sem item vira sugestão, e nenhum outro serviço é aumentado para cobri-la.

## 4. Geometria, execução, consumo e compra

Ficam separadas: a quantidade geométrica; a quantidade de execução pelo critério da composição; o consumo pelos coeficientes; as perdas já embutidas nos coeficientes; e a compra (embalagem, chapa, peça). Perda genérica (10% etc.) não entra por hábito: verificar se o coeficiente já a contém. Fator adicional só com fonte, base de incidência e aplicação única.

<a id="evidencias-visuais-por-item"></a>

## 5. Evidências visuais

**Todo item físico tem, na sua memória, um print real do projeto com as parcelas marcadas pelos mesmos IDs da tabela, e toda parcela aparece num print.** Vale para CONFIRMADO, PREMISSA e SUBTOTAL de itens mensuráveis e por parâmetro. Em PENDENTE e NÃO APLICÁVEL de item mensurável, o print mostra a indicação, o conflito ou a falta (tabela abaixo). Quando não houver representação gráfica aplicável, `sem_representacao_grafica` explica por quê.

Rota padrão:
1. Uma **planta de levantamento por família e pavimento** (pisos, forros, paredes e pintura, pontos…) gerada com `cad.py render` ou `pdf.py render` a partir das geometrias e dos IDs. Ela localiza tudo.
2. Para cada item, um **recorte gerado da mesma geometria**, com apenas as parcelas do item destacadas. Como print e conta saem da mesma geometria, a correspondência entre eles é garantida.
3. Legenda com cores, IDs e o que é incluído, descontado ou apenas referência, além de arquivo, revisão, vista e método.

Captura de tela marcada à mão só quando a geometria não pode ser extraída (PDF raster, DWG inacessível); registrar "marcação manual".

| Situação | O print mostra |
|---|---|
| Área | contornos, materiais e estados, recortes, vazios e deduções |
| Superfície vertical | faces localizadas em planta e o corte ou elevação com alturas, vãos e retornos |
| Comprimento e redes | trechos, derivações, subidas e descidas |
| Contagem | cada ocorrência marcada e a legenda ou modelo correspondente |
| Premissa | local e extensão adotados, com a premissa escrita no print |
| Exclusão ou cancelamento | a legenda, nota ou chamada que sustenta a decisão |
| Conflito | recortes das fontes conflitantes, marcados |
| Pendência ou subtotal | parte medida e parte faltante com tratamentos distintos |

Item sem representação gráfica (taxa, prazo, verba, custo indireto) registra `sem_representacao_grafica` com o motivo; se um quadro ou texto contratual define o pacote, recortar esse trecho. Nunca gerar planta fictícia nem usar imagem sem relação com o item. Uma mesma imagem pode servir a vários itens se identificar sem ambiguidade as parcelas de cada um.

**Tamanho:** `gerar_planilha.py` reduz as imagens (largura de até 1400 px e paleta reduzida). Se a planilha passar de cerca de 25 MB, manter nela os recortes por item e entregar as plantas gerais de levantamento como arquivos em `evidencias/`, citados nas memórias.

## 6. Memória por item

Uma aba por item de escopo, gerada a partir do `levantamento.json` com o layout do [ESQUEMA_PLANILHA](../assets/ESQUEMA_PLANILHA.md): identificação, resultado e estado, critério, premissas, pendências, fontes, os textos **"O que entrou" / "O que ficou fora" / "O que falta"**, a tabela de parcelas com fórmulas, os prints e o diagnóstico.

**Diagnóstico** só quando houver problema real entre o serviço e o projeto, com categoria, constatação e evidência, solução e base, estado e efeito na quantidade:

| Categoria | Questão |
|---|---|
| `ESCOPO_FASE` | existente, mantido, retirado ou novo; locais e etapas |
| `ESPECIFICACAO` | material, modelo, sistema ou acabamento divergente |
| `GEOMETRIA_COTAS` | contorno, dimensões, alturas, níveis, vãos, percurso |
| `UNIDADE_CRITERIO` | unidade da linha e regra de medição |
| `COMPOSICAO_DUPLICIDADE` | fornecimento e instalação, componentes incluídos, alternativas |
| `DOCUMENTACAO_REVISAO` | fonte incompatível ou vista faltante |
| `DIMENSIONAMENTO_VISTORIA` | definição executiva ou verificação de campo necessária |

Item compatível com o projeto não ganha problema inventado. A principal recebe apenas o estado, o link para a memória e uma observação curta.

## 7. Saída da etapa

Cada item do escopo está no `levantamento.json` com estado, parcelas (ou motivo) e evidência (ou justificativa). Pendências não impedem a passagem para [08](08_conferencia_comparacao_e_entrega.md).
