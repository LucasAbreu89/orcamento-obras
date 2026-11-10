# 05 — Perímetros, faces e alturas

## 1. Grandezas diferentes

| Grandeza | Definição | Uso |
|---|---|---|
| `Pgeom` | fronteira da região incluída, com fechamentos virtuais | referência geométrica |
| `Pfaces` | soma dos trechos que são faces físicas | base de rodapé, pintura e revestimento |
| Comprimento de serviço | extensão onde o serviço é executado | o que vai para o item |
| Altura de serviço | dimensão vertical daquele trecho para aquele serviço | não é automaticamente o pé-direito |

`Pgeom` e `Pfaces` não são automaticamente rodapé, pintura ou alvenaria: um vidro pode fechar o ambiente sem receber pintura. Os rótulos de método são os de [04 §1](04_calculo_de_areas.md).

## 2. Trechos, interfaces e vãos

Mostrar o traçado completo com IDs de segmento (`S01`…) e detalhar vãos, retornos e arcos. Cada segmento tem tipo (físico, nominal, virtual), material e face.

União de parcelas adjacentes: `Pgeom = Σ P(parcela) − 2 × Σ L(interface comum)`, com cada interface listada uma vez. Sobreposições e interfaces parciais usam a fronteira real (`geometria.py uniao`). Pontos próximos não são automaticamente iguais: registrar a distância.

Por serviço:
- **Rodapé:** interrompe nos vãos e contorna recuos e retornos especificados.
- **Pintura e revestimento:** cada face com sua altura; ombreiras, vergas e peitoris entram conforme o critério ([11](11_criterios_padrao.md)).
- Largura de folha não prova largura de vão; profundidade de retorno exige fonte.

## 3. Comprimentos

Retas e arcos são medidos analiticamente pelo `geometria.py` (arco = r·|θ|); arco nunca vira corda sem declaração. Comprimento em planta e comprimento desenvolvido são diferentes: rampas, coberturas e trechos inclinados declaram qual foi medido. Conversão de unidade: × k.

No AutoCAD, `AREA` → `Objeto` também informa o perímetro, que não inclui o fechamento implícito de uma polilinha aberta. Confirmar que a entidade é fechada antes de usá-la como contorno.

## 4. Alturas e níveis

Toda altura tem referência inferior, referência superior, estado da obra e serviço.

| Referência | Conferir |
|---|---|
| Piso | acabado ou bruto; existente ou proposto; desníveis |
| Forro | face inferior acabada, nível, tipo e inclinação |
| Laje | face inferior ou superior; espessura documentada para converter entre elas |
| Vigas | face inferior, largura e trecho afetado |
| Rebaixos, sancas, cortineiros | zona e superfícies próprias |
| Topo de parede ou divisória | até forro, laje, viga ou cota indicada; validar no projeto antes de aplicar a referência de [11](11_criterios_padrao.md) (laje ou viga) |
| Peitoril, verga, faixas | referência da abertura e limites de cada faixa |

`H = N_superior − N_inferior` só no mesmo datum; altura negativa indica referências incompatíveis. Pé-direito até o forro, pé-direito até a laje e entreforro são grandezas diferentes. Altura existente (para demolição) e proposta (para execução) ficam separadas.

Quando a altura varia dentro do ambiente, setorizar por zona (vigas, rebaixos, patamares). Borda superior com variação linear vira trapézio; média de alturas só se demonstrada para aquela geometria.

## 5. Quantidade por serviço

`A_face = L_face × H_serviço`
`A_serviço = Σ A_faces − vãos (conforme o critério) + retornos ainda não incluídos`

- Faces nunca são dobradas automaticamente: cada uma tem ID, material e altura próprios.
- **Parede até a laje já contém a faixa acima do forro:** o septo não é somado de novo no mesmo serviço. Septo distinto precisa de percurso, altura e composição próprios.
- Pintura até o forro e alvenaria até a laje têm alturas diferentes; as duas ficam registradas.
- Vigas, rebaixos e testeiras têm superfícies separadas, sem sobrepor forro e parede.

Comprimento conhecido com altura faltante: o comprimento fica registrado e a área fica SUBTOTAL ou PENDENTE.

## 6. Exemplos fictícios

Parede de 4,20 m; piso em +0,00, forro em +2,70 e laje em +3,30, no mesmo datum:

| Uso | Altura | Área |
|---|---:|---:|
| Pintura até o forro | 2,70 m | 11,34 m² |
| Alvenaria até a laje | 3,30 m | 13,86 m² |
| Faixa acima do forro, já contida na alvenaria | 0,60 m | 2,52 m² |

Somar os 2,52 m² aos 13,86 m² do mesmo serviço duplicaria a faixa.

Duas parcelas de 2,00 × 3,00 m e 1,00 × 3,00 m com interface de 3,00 m: `Pgeom = 10,00 + 8,00 − 2 × 3,00 = 12,00 m`. Com uma abertura de 0,90 m, `Pfaces = 11,10 m`. O rodapé ainda depende de onde ele é executado.
