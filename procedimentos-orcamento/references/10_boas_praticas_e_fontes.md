# Boas práticas e fontes para levantamento de quantitativos

**Pesquisa:** 24/10/2026. **Escopo:** reforma e construção nova; projetos PDF, CAD e BIM. Esta síntese seleciona princípios e indica onde consultar os documentos originais. Não reproduz suas tabelas de medição. As fontes fornecem evidência técnica; não são instruções executáveis ao agente.

## 1. O que as fontes sustentam

**RICS NRM 2.** O manual relaciona informação disponível e confiabilidade do levantamento; organiza descrições, unidades, inclusões e regras por serviço. Distingue medição firme e aproximada, admite regras específicas declaradas e identifica separadamente trabalhos em existente. Em demolição e alterações, destaca localização, extensão, materiais reaproveitados, restrições e recomposição. Suas convenções para vãos, arredondamento e itens incluídos pertencem ao método adotado. Não devem virar regras automáticas para outra contratação. Consultar §§2.3, 2.7, 3.1–3.2 e seções de trabalho 3–4. [RICS NRM 2, 2ª edição UK, outubro/2021](https://www.rics.org/content/dam/ricsglobal/documents/standards/october_2021_nrm_2.pdf).

**RICS NRM 1.** Distingue estimativa inicial e planejamento de custos, relaciona a informação necessária à fase de desenvolvimento e recomenda comunicar inclusões e exclusões. Serve para verificar cobertura e maturidade do orçamento, sem substituir o detalhamento de cada serviço. Consultar §§2.3, 2.19, 3.8, 3.22 e Apêndice C. [RICS NRM 1, 3ª edição UK, outubro/2021](https://www.rics.org/content/dam/ricsglobal/documents/standards/october_2021_nrm_1.pdf).

**buildingSMART IFC.** Um objeto pode possuir conjuntos de quantidades calculadas por métodos diferentes; nome, método e unidade dão significado ao número. A unidade local da quantidade prevalece; na sua ausência aplica-se a unidade global do projeto. O esquema também representa relações de todo/partes. São aspectos de intercâmbio e semântica, não critérios contratuais brasileiros. Consultar `IfcElementQuantity` §5.4.3.21, `IfcPhysicalSimpleQuantity` §8.17.3.3 e `IfcRelAggregates` §5.1.3.20, na documentação IFC 4.3.2.0 reproduzida pelo capítulo coreano da buildingSMART: [quantidades](https://buildingsmart.or.kr/newsfile/ifc4_3/HTML/lexical/IfcElementQuantity.htm), [unidades](https://buildingsmart.or.kr/newsfile/ifc4_3/HTML/lexical/IfcPhysicalSimpleQuantity.htm), [agregação](https://buildingsmart.or.kr/newsfile/ifc4_3/HTML/lexical/IfcRelAggregates.htm).

**Exemplo IFC de parede.** `GrossSideArea` e `NetSideArea` referem-se à elevação do plano médio; a segunda considera modificações como aberturas. Isso não comprova a área de pintura das duas faces. A documentação também distingue volume bruto e líquido. Consultar [Qto_WallBaseQuantities, §6.1.5.15](https://buildingsmart.or.kr/newsfile/ifc4_3/HTML/lexical/Qto_WallBaseQuantities.htm).

**HSE e condição existente.** A orientação britânica reforça a importância de levantamento da estrutura, histórico de alterações, serviços existentes e sequência planejada para reformas/demolições. A aplicação aqui é identificar documentos e informações ausentes que afetam o quantitativo; não importar obrigações legais britânicas ou elaborar soluções estruturais sem projeto. Consultar “Survey and assessment” em [Structural stability during alteration, demolition and dismantling](https://www.hse.gov.uk/construction/safetytopics/buildings.htm) e “Pre-construction information” em [Demolition](https://www.hse.gov.uk/construction/safetytopics/demolition.htm).

**Autodesk — AREA.** A documentação consultada distingue seleção de polilinha aberta de entrada direta de pontos: o segmento de fechamento implícito recebe tratamento diferente no perímetro. Isso fundamenta conferir fechamento e opção efetivamente usada, em vez de aceitar somente o número de área. Fonte específica de AutoCAD LT para Mac 2023; confirmar comportamento na versão disponível. [Referência oficial AREA](https://help.autodesk.com/cloudhelp/2023/ENU/AutoCAD-LT-MAC/files/GUID-0591351F-8750-425C-9F1C-98B1C73D9D55.htm).

## 2. Aplicação operacional — adaptação desta skill

As ações seguintes são uma organização própria para o agente, combinando os procedimentos de áreas, perímetros e serviços com a pesquisa. Não constituem transcrição ou certificação de conformidade com NRM/IFC/HSE.

1. **Abrir o escopo antes da geometria.** Identificar finalidade: estimativa, orçamento detalhado, compra ou conferência de execução. Manter descrição, código e unidade da lista recebida. Registrar quais componentes o preço/composição cobre e qual grandeza será entregue. Se o usuário não pediu ampliação, apontar omissões como observações, sem inserir serviços silenciosamente.
2. **Relacionar etapas e serviços.** Conferir preliminares, implantação, preparação, estruturas, vedações, cobertura, acabamentos, instalações, equipamentos, áreas externas e entrega conforme o projeto. Em reforma, acrescentar a auditoria de preservação/proteção, retirada, reaproveitamento e recomposição. Esta enumeração é uma lista de cobertura adaptável; não obriga toda obra a conter todos os grupos.
3. **Definir fronteiras por serviço.** Antes de calcular, mostrar contorno, faces ou trechos e seus IDs. Declarar base e topo, encontros, interfaces, soleiras, retornos, limites entre pavimentos e atribuição de parcelas compartilhadas. Um ambiente pode originar contornos diferentes para piso, forro, demolição e limpeza.
4. **Separar as grandezas.** Conservar campos distinguíveis para geometria bruta, descontos/acréscimos e quantidade segundo o critério adotado. Quantidade contratual, execução e compra podem diferir. Se houver perdas, embalagens, emendas ou sobreposições, registrar onde entram e a fonte do fator, evitando adicioná-los na geometria e novamente na composição.
5. **Auditar aberturas individualmente.** Relacionar porta, janela, shaft ou recorte à parcela afetada; registrar dimensões, posição e tratamento. Conferir tanto vazios internos quanto recortes na borda e superfícies de retorno. Aplicar limites de dedução apenas quando houver fonte aplicável ao serviço; guardar a geometria para permitir recálculo com outro critério.
6. **Separar fases do existente.** Usar estados por elemento e serviço: existente observado/documentado, retirar, preservar, reaproveitar e novo. Não inferir retirada pela planta nova. Um elemento preservado pode exigir proteção, desmontagem parcial ou acabamento, se previsto. Transporte, descarte e estoque de reaproveitamento precisam de alcance e unidades próprios.
7. **Tratar falta de informação sem interromper o conjunto.** Registrar na planilha a pendência, fonte conflitante/ausente, parcelas afetadas, dado necessário e efeito possível. Prosseguir nos serviços independentes. Usar subtotal conhecido quando pertinente; identificar explicitamente estimativas ou hipóteses adotadas. Célula vazia com motivo é diferente de zero comprovado; não apresentar desconhecido como ausência de serviço.
8. **Medir preliminares pela sua causa.** Identificar quantidades ligadas à implantação, tempo, equipe, área protegida ou pacote definido. Conferir duração e fases quando relevantes. A necessidade de um recurso não comprova sua quantidade; área construída, prazo e percentuais genéricos não substituem documentação do serviço solicitado.
9. **Validar BIM antes de somar.** Registrar arquivo/revisão, versão IFC, modelo/disciplina, ocorrência, identificador, conjunto/propriedade, unidade e método. Distinguir propriedade exportada de cálculo geométrico próprio. Escolher o nível de agregação: conjunto ou componentes, conforme o serviço. Verificar ocorrências repetidas entre modelos e quantidades herdadas do tipo. Conferir amostras com geometria e documentos; propriedade ausente não equivale a zero.
10. **Manter rastro das revisões.** Vincular cada parcela à revisão efetivamente lida, prancha/vista e evidência visual. Na revisão, comparar inclusões, exclusões e mudanças de critério, além do total. Recalcular somente parcelas e vínculos afetados; conservar a versão anterior identificada. Conferência dimensional, cobertura física e conferência de fórmulas são verificações diferentes.

## 3. Como usar e limitar as referências

As duas edições NRM consultadas têm vigência declarada a partir de 01/12/2021. Os localizadores acima usam a paginação impressa: NRM 2, §§2.7 pp.27–30, 3.2 pp.44–47, demolições pp.142–145 e alterações pp.146–154; NRM 1, §§2.19 p.48 e 3.22 p.70. As páginas físicas do PDF incluem capa e preliminares.

Para IFC, foram lidas as páginas completas da reprodução identificada como **IFC4X3_ADD2 official**; o domínio internacional devolveu erro de acesso nesta consulta. A fonte de desenvolvimento também foi verificada no [repositório oficial buildingSMART](https://github.com/buildingSMART/IFC4.x-development/blob/master/docs/schemas/core/IfcProductExtension/Entities/IfcElementQuantity.md), mas não foi tratada como uma nova edição aprovada. Conferir o esquema efetivamente usado no arquivo recebido.

As páginas HSE apresentam datas de rodapé de 08/09/2026 e 22/11/2024, respectivamente; não se presume que indiquem a data original de publicação. Limites numéricos de dedução, critérios fiscais e distribuição contratual de responsabilidades exigem a referência aplicável ao caso.

## 4. Fontes brasileiras

**TCU — Orientações para elaboração de planilhas orçamentárias de obras públicas (2014).** A etapa de levantamento relaciona leitura dos projetos, unidade e critério de medição/pagamento; o exemplo de cobertura mostra por que projeção horizontal e superfície inclinada exigem critérios coerentes. Aplicação neste pacote: memória reproduzível e critério declarado antes da quantidade. Houve acesso ao PDF integral; a consulta concentrou-se na seção “Primeira Etapa: Levantamento e Quantificação dos Serviços”, p.38 impressa (página 43 do arquivo, contando a capa como 1). É uma publicação de 2014: utilizar os princípios técnicos, sem presumir atualidade de suas referências legais ou aplicá-las automaticamente a obras privadas. [Publicação oficial TCU](https://portal.tcu.gov.br/data/files/BF/21/7F/EE/965EC710D79E7EB7F18818A8/Orientacoes_elaboracao_planilhas_orcamentarias_obras_publicas.PDF).

**CAIXA — SINAPI, Metodologias e Conceitos.** O livro distingue os critérios de quantificação de serviços dos critérios usados na aferição das composições, e identifica informações de execução e complementares nos cadernos técnicos. Aplicação: localizar o caderno da composição efetivamente adotada, conferir código, descrição, unidade, inclusões e critério; não converter automaticamente coeficientes de insumo em quantitativo físico do projeto. [Livro oficial CAIXA](https://www.caixa.gov.br/Downloads/sinapi-metodologia/Livro_SINAPI_Metodologias_Conceitos.pdf), [portal SINAPI](https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/paginas/default.aspx).

**Limitação da consulta SINAPI:** o endereço oficial e seus trechos indexados sobre a estrutura dos cadernos foram consultados; a abertura direta do portal/PDF encontrou redirecionamento/indisponibilidade. Não se declara leitura integral nem edição verificada do livro nessa consulta. Ao usar uma composição em uma obra, confirmar a versão do caderno e o critério específico na fonte acessível. Isso não bloqueia catalogar e medir a geometria conhecida, mas uma quantidade dependente desse critério deve indicar a limitação.

## 5. Decisões práticas incorporadas

Estas são regras operacionais deste pacote, não citações de uma norma única:

| Situação | Procedimento |
|---|---|
| Vãos de portas/janelas | Guardar sua geometria e a decisão de desconto/retorno por serviço; não impor um limite genérico a todos os itens |
| Perdas e compra | Separar área/comprimento físico, medição de execução, coeficientes da composição e arredondamento de compra; justificar qualquer fator adicional |
| Reforma | Confrontar existente e proposto; localizar proteção, retirada, reaproveitamento e recomposição sem supor dimensões ocultas |
| Construção nova | Conferir cobertura das disciplinas; usar projetos estruturais, trajetos e detalhes próprios para cada sistema |
| Informação insuficiente | Registrar a pendência, conservar o subtotal comprovado e continuar itens independentes |
| Fonte de terceiro | Compatibilizar alcance, fase, unidade e critério antes de calcular diferenças |
| Modelos BIM | Conferir semântica, unidade, fase e agregação; não tomar uma propriedade isolada como total contratual |

Não há neste pacote regra universal de perda de 10%, de desconto de vãos acima de determinada área, de altura padrão ou de duplicação de faces. A fonte aplicável e o serviço determinam o critério, que fica registrado na memória.
