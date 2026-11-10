# 10 — Referências técnicas

As fontes orientam critérios; nenhuma vira regra do contrato sem verificar sua aplicabilidade. Ordem de precedência:

1. Instrução do usuário e documentos do contrato (caderno de encargos, memorial descritivo, especificações).
2. Critério da composição indicada na planilha (por exemplo, o caderno técnico SINAPI daquela composição).
3. Padrão do pacote ([11](11_criterios_padrao.md)).
4. Demais referências.

O critério usado e sua fonte ficam registrados na aba Critérios.

## Brasil

| Fonte | Para que serve |
|---|---|
| SINAPI — Cadernos Técnicos de composições (CAIXA) | critério de quantificação e itens incluídos em cada composição; conferir a versão usada |
| SINAPI — Metodologias e Conceitos (CAIXA) | diferença entre critério de quantificação e critério de aferição; coeficiente de insumo não é quantitativo físico |
| TCPO (Editora Pini) | composições e critérios de medição de uso corrente no mercado privado |
| TCU — Orientações para elaboração de planilhas orçamentárias de obras públicas (2014) | levantamento com critério declarado e memória reproduzível; princípios técnicos, sem presumir a atualidade das referências legais |
| ABNT NBR 12721 | definições das áreas da edificação (real, privativa, de uso comum) quando o item pedir área construída |
| DNIT — Manuais de custos do SICRO | infraestrutura: terraplenagem, pavimentação, drenagem; fatores de empolamento e compactação |

Links: [Livro SINAPI](https://www.caixa.gov.br/Downloads/sinapi-metodologia/Livro_SINAPI_Metodologias_Conceitos.pdf) · [Portal SINAPI](https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/paginas/default.aspx) · [TCU 2014](https://portal.tcu.gov.br/data/files/BF/21/7F/EE/965EC710D79E7EB7F18818A8/Orientacoes_elaboracao_planilhas_orcamentarias_obras_publicas.PDF)

## Internacionais (apoio)

| Fonte | Para que serve |
|---|---|
| [RICS NRM 2](https://www.rics.org/content/dam/ricsglobal/documents/standards/october_2021_nrm_2.pdf) | regras detalhadas por serviço; trabalhos em existente e demolições |
| buildingSMART IFC: [IfcElementQuantity](https://buildingsmart.or.kr/newsfile/ifc4_3/HTML/lexical/IfcElementQuantity.htm), [Qto_WallBaseQuantities](https://buildingsmart.or.kr/newsfile/ifc4_3/HTML/lexical/Qto_WallBaseQuantities.htm) | quantidades em modelos têm nome, método e unidade; `NetSideArea` de parede é do plano médio, não da pintura das duas faces |
| [Autodesk — comando AREA](https://help.autodesk.com/cloudhelp/2023/ENU/AutoCAD-LT-MAC/files/GUID-0591351F-8750-425C-9F1C-98B1C73D9D55.htm) | fechamento implícito de polilinha aberta e tratamento do perímetro |

## Decisões do pacote

- Não há regra universal de perda, desconto de vãos, altura padrão ou duplicação de faces. O padrão de [11](11_criterios_padrao.md) vale até o contrato ou o usuário dizerem outra coisa, e a geometria fica guardada para recalcular com outro critério.
- Preço não faz parte do pedido de quantitativos. Se for pedido, registrar fonte, data-base, localidade e encargos à parte da quantidade.
