# 01 — Inventário e catálogo dos projetos

## 1. Inventariar sem presumir leitura

Percorrer a pasta selecionada, incluindo disciplinas, pavimentos e revisões. Listar PDF, DWG/DXF, IFC, imagens, memoriais e planilhas relevantes. Registrar caminho relativo, extensão, tamanho, data do arquivo e hash quando acessível. Data de modificação não substitui revisão técnica.

Separar originais, revisões anteriores, cópias e saídas derivadas. Mesmo nome não comprova igualdade; mesmo hash permite reconhecer duplicata exata. Não excluir revisões antigas sem registrar a razão de sua não utilização. Pastas chamadas `output` podem conter evidências úteis; classificá-las antes de ignorá-las. Pacotes compactados ou arquivos inacessíveis entram no inventário com a condição de acesso, sem alegar inspeção do conteúdo.

O auxiliar de preparação não segue links simbólicos para fora da árvore nem abre arquivos; registra essas limitações. Conferir se há fontes externas explicitamente fornecidas pelo usuário e adicioná-las ao catálogo.

## 2. Examinar e localizar o conteúdo

Para cada PDF pertinente, percorrer as páginas e identificar prancha, título, revisão, escala, pavimento, fase e vistas. Usar extração/OCR para busca, seguida de inspeção visual dos números e detalhes que sustentam o levantamento. Texto extraído não comprova cor, hachura, limite ou estado de demolição. Se a cobertura visual for parcial, indicar exatamente quais páginas foram examinadas.

Para CAD, identificar model space/layouts, unidades, escalas, referências externas, blocos e camadas pertinentes. Examinar os layouts e regiões necessários ao conteúdo do arquivo; verificar referências ausentes, camadas desligadas ou recortes que possam ocultar informação. Abrir, examinar e fechar conforme [07](07_computer_use_e_encerramento.md). Não deixar o arquivo aberto apenas para manter um cache.

### 2.1. Um arquivo pode conter várias plantas e vistas

**Não presumir que um DWG/DXF corresponde a uma única planta ou que a vista inicial mostra todo o projeto.** Um mesmo arquivo pode reunir pavimentos, disciplinas, fases, cortes, fachadas e detalhes: em regiões diferentes do Model, em vários layouts, em viewports ou sobrepostos e separados por camadas/estados de visibilidade. Uma página de PDF também pode conter várias dessas representações.

Mapear a estrutura interna antes de declarar a cobertura da leitura:

1. **Model:** localizar as regiões desenhadas, quadros, títulos, carimbos e vistas nomeadas disponíveis. Verificar regiões afastadas da vista inicial. Uma visão geral ajuda a localizar, mas não prova que conteúdo oculto foi examinado.
2. **Layouts e viewports:** listar os layouts e identificar as vistas de cada um, seus recortes e vínculos ao Model. Distinguir conteúdo desenhado no papel de conteúdo exibido por uma viewport. A mesma geometria pode aparecer em mais de uma prancha.
3. **Camadas e estados:** examinar nomes, agrupamentos e estados salvos pertinentes, relacionando-os a plantas, disciplinas, pavimentos ou fases quando essa relação for comprovada. Uma layer não é necessariamente uma planta; seu nome sozinho não comprova o conteúdo ou a fase.
4. **Visibilidade:** verificar desligamento, congelamento global e por viewport, isolamento e recortes que possam esconder informação. Model e viewports podem ter configurações distintas. Referências externas descarregadas, ausentes ou recortadas também limitam a leitura.
5. **Combinações interpretáveis:** consultar as combinações relevantes ao escopo e as vistas organizadas pelo projetista. Ligar todas as camadas simultaneamente não substitui essa investigação: pode sobrepor existente, demolição e proposta. Não exigir todas as combinações possíveis de layers; identificar as que representam conteúdo distinto e registrar o que permaneceu incerto.
6. **Preservação:** registrar o estado inicial e realizar alterações de visibilidade necessárias em cópia identificada, quando houver risco de gravá-las. Não salvar mudanças de inspeção sobre o original. Seguir o ciclo de salvar/fechar da referência 07.

Dar um ID a cada representação, por exemplo `F001.V01`, e registrar título/assunto, pavimento, disciplina, fase e revisão próprios quando identificáveis. Não impor o carimbo de uma região a todo o arquivo sem conferir as demais. Se faltarem nomes, usar uma imagem geral com regiões identificadas e um localizador reproduzível, como vista nomeada ou limites/coordenadas da região.

Para retornar à informação, o localizador CAD deve informar, conforme aplicável:

```text
arquivo/revisão → ID da representação → Model/região ou layout/viewport
→ layers/estado de visibilidade → vista/detalhe → evidência
```

Usar a matriz por representação do [modelo de catálogo](../assets/MODELO_CATALOGO.md). Distinguir `identificada, não examinada`, `examinada parcialmente`, `examinada` e `fora do escopo, com motivo`. Consultar um layout ou uma combinação de camadas não permite marcar o arquivo inteiro como examinado. Se uma configuração não puder ser verificada, registrar a limitação e continuar as outras representações.

**Representação não é ocorrência física adicional.** Relacionar planta no Model, viewports, ampliações e detalhes que mostram o mesmo universo físico. Catalogá-los como fontes complementares, sem somar novamente seus elementos. Separar revisões e alternativas: não somar soluções mutuamente exclusivas. Uma biblioteca de blocos, legenda ou detalhe típico não comprova peças instaladas.

O controle de visibilidade por viewport é documentado pela [Autodesk](https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT-MAC/files/GUID-188DCF15-A258-4549-821F-9BCBFBCBB407.htm); confirmar recursos e comandos no aplicativo disponível, sem transportar atalhos de outra versão.

### 2.2. Compatibilidade e outros formatos

PDF e DWG com nomes semelhantes não são necessariamente sincronizados. Comparar carimbo, revisão, cotas e detalhes antes de intercambiar fontes. Havendo conflito, registrar as duas fontes e as parcelas afetadas; não escolher a versão que faz a conta coincidir.

Para BIM/IFC, se houver ferramenta compatível, identificar disciplina, versão/esquema, fase, pavimento, elementos e propriedades úteis. Registrar se a quantidade é propriedade exportada ou cálculo próprio, unidade, método e nível de agregação. Conferir o alcance antes de somar elementos ou modelos; [10](10_boas_praticas_e_fontes.md) explica os limites semânticos. A ausência de ferramenta BIM não impede catalogar os demais arquivos.

## 3. Conteúdo mínimo por arquivo

Usar o [modelo de catálogo](../assets/MODELO_CATALOGO.md), adaptando o tamanho ao documento. Registrar:

| Informação | Exemplo de conteúdo, sem valores inventados |
|---|---|
| Identidade | Arquivo, revisão do carimbo, disciplina, pavimento e fase |
| Cobertura da leitura | Plantas/vistas identificadas e examinadas, por página, região do Model, layout/viewport e configuração pertinente de camadas; texto extraído e inspeção visual distinguíveis |
| Do que trata | Planta de demolição, ampliação de sanitários, iluminação, detalhes de marcenaria etc. |
| O que contém | Cotas, etiquetas de área, níveis, alturas, acabamentos, legendas, especificações, detalhes |
| Onde procurar | ID da representação, prancha/página/layout/viewport, região/vista/detalhe, camadas/estado e ambiente ou setor |
| Utilidade no levantamento | Serviços e grandezas que esta fonte pode sustentar |
| Limites | Informações ausentes, ambiguidades, divergências e referências externas faltantes |
| Evidência | Recorte e localizador persistentes, quando necessários |

Fazer também um índice inverso: assunto/serviço → fontes e vistas. Esse índice evita reabrir todos os projetos para cada item. Separar indicação de projeto de qualquer cálculo solicitado depois. Uma etiqueta `A=...` entra como **área indicada**; não como área conferida.

## 4. Compatibilizar as fontes

Relacionar planta geral, planta por disciplina, cortes, elevações e detalhes do mesmo elemento. Identificar a fonte que informa cada dimensão, sem presumir que uma ampliação substitua todas as outras vistas. Propostas, existentes e demolições devem ter estados separados.

Quando a informação estiver em um memorial ou quadro, registrar sua relação com a ocorrência física. Um detalhe típico descreve uma solução; sua quantidade depende da implantação. Uma legenda define famílias; seus símbolos ilustrativos não são peças instaladas.

Não converter ausência de desenho em ausência de serviço. Para situações ocultas de reforma, indicar se o dado vem de projeto cadastral, vistoria ou hipótese autorizada. Não inferir que toda parede tracejada será demolida sem ler a legenda.

## 5. Saída, cache e atualização

Salvar o catálogo técnico em `01_catalogo/` e os identificadores/hashes em `08_dados_tecnicos/`. Usar links relativos dentro da execução, com referência à fonte original. Não depender de caminho temporário de screenshot no resultado final.

O cache de extração ou recortes deve informar hash e revisão da fonte. Ao mudar o arquivo, invalidar o conteúdo afetado, verificar a nova revisão e recalcular as dependências. Não reutilizar uma evidência de outra obra ou revisão apenas por nome semelhante.

Arquivo corrompido, bloqueado ou sem acesso gera registro na aba `Pendências` quando houver planilha; enquanto ela não estiver disponível, conservar o dado no inventário técnico para importação. Continuar a leitura das demais fontes e a quantificação independente. Usar [03](03_duvidas_e_continuidade.md).
