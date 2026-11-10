# 08 — Conferência, comparação e entrega

## 1. Validação automática

Depois de gerar a planilha, na pasta da execução (`$SKILL` é a pasta da skill):

```bash
python3 $SKILL/scripts/recalcular.py planilha/<entrega>.xlsx --saida conferencia/recalculado.xlsx --pdf conferencia/caderno.pdf
python3 $SKILL/scripts/validar_entrega.py --levantamento dados/levantamento.json --recalculado conferencia/recalculado.xlsx
```

O `--pdf` exporta o caderno de memórias (uma página de largura por memória, em paisagem).

O validador confere:
- originais (projetos e planilha) com o mesmo hash do inventário inicial;
- células da planilha recebida idênticas ao snapshot (valores, fórmulas e vazios), além de abas, visibilidade, mesclagens e recursos (imagens, gráficos, macros, vínculos);
- **cobertura**: toda linha das listas com descrição e unidade tem item no `levantamento.json` ou motivo em `linhas_ignoradas`;
- `QTD LEVANTADA` e `ESTADO` ligados à memória certa, sem `IFERROR`/`SEERRO` e sem apontar para a quantidade recebida;
- regras do [ESQUEMA_LEVANTAMENTO](../assets/ESQUEMA_LEVANTAMENTO.md): estados, pendências e premissas referenciadas, motivos, unidades das parcelas;
- prints incorporados em cada item físico, com todas as parcelas, ou justificativa;
- valores gravados (cache) iguais aos calculados a partir das parcelas e aos do LibreOffice;
- dimensões gravadas como número, nomes de aba e tamanho do arquivo.

Erro do validador é corrigido antes da entrega, ou o item e a limitação são declarados. Sem LibreOffice, registrar "recálculo independente não executado".

## 2. Conferência física

O validador prova consistência, não que o universo físico esteja completo. Para cada família:
- escopo, estado físico, faces e alturas, vãos e interfaces, duplicações (vistas repetidas, legendas, faces), exclusões justificadas;
- **itens curva A:** segunda medição por outro caminho (envelope × decomposição, coordenadas × cotas, contagem por ambiente × por família, comando nativo);
- serviços associados, pela [matriz](../assets/MATRIZ_SERVICOS_ASSOCIADOS.md).

## 3. Testes de razoabilidade

São alertas para investigar, nunca motivo para ajustar a conta.

| Relação | Esperado |
|---|---|
| Soma das áreas de piso × quadro de áreas do projeto | iguais, ou diferença explicada |
| Forro × piso, por ambiente | iguais, ou diferença explicada (sem forro, rebaixos, shafts) |
| Rodapé × (`Pfaces` − vãos) | rodapé menor ou igual |
| Pintura de parede × Σ (face × altura) − vãos | mesma ordem de grandeza |
| Contrapiso × piso novo | mesmo contorno, salvo motivo |
| Demolição × superfície existente | demolição menor ou igual |
| Contagens | IDs = soma por família = soma por ambiente |
| Ordem de grandeza | valor incompatível com o tamanho da obra indica erro de unidade (mm × m) |

## 4. Comparação com outra quantidade

Só quando o usuário pedir. A coluna de quantidade recebida existe em quase toda planilha e, sozinha, não dispara comparação. O resultado vai para o campo `comparacao` do `levantamento.json`, que vira a aba Comparação.

1. Mapear por chave, ID, descrição e unidade; identificar a coluna de referência pelo cabeçalho e pela fórmula.
2. Classificar cada par: **comparável**; **comparável com ressalva** (critério incerto); **não comparável** (escopo, unidade, estado ou subtotal contra total); **sem correspondência**.
3. Calcular só nos comparáveis: `Δ = Q_levantada − Q_referência` e `Δ% = Δ ÷ Q_referência × 100` (base zero: "não calculável").
4. Investigar quando `|Δ%|` passar do limite combinado no checkpoint (padrão: 5%) ou o item for curva A. Separar fato demonstrado, hipótese e informação ausente; nunca afirmar erro da outra fonte sem prova.
5. A referência nunca é corrigida para coincidir. Nossas correções vão para o `levantamento.json`, com antes, depois e motivo.

Igualdade numérica, inclusive `1 VB`, não prova igualdade de escopo.

## 5. Revisão visual

Abrir ou renderizar a entrega e percorrer as memórias: IDs legíveis nos prints, legenda coerente, nada encobrindo tabelas, vírgula decimal por formato. Se o destino for Google Sheets, importar o arquivo completo e conferir a localidade em amostras. Teste no Excel ou no Sheets só é afirmado se o arquivo foi aberto nesse aplicativo.

## 6. Entrega

Arquivos: a planilha de entrega, o relatório do validador e o caderno em PDF, quando houver. Limitações (recálculo não executado, arquivo sem acesso, teste não feito no Excel) vão para o campo `limitacoes` do JSON e aparecem no Resumo.

Mensagem final, curta:
- link da planilha e alcance (abas e listas levantadas);
- contagem de itens por estado;
- pendências de maior impacto, como perguntas prontas para enviar;
- premissas principais e exclusões;
- verificações executadas e as que não foram possíveis;
- limitações de acesso ou de ferramenta.

Entregar o que está validado mesmo com pendências, sem apresentar parcial como completo.
