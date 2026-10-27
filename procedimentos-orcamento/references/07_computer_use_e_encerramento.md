# 07 — Computer use, evidências e encerramento

Usar esta referência quando for necessário operar CAD, visualizador, Excel ou outro aplicativo pela interface. O objetivo é executar a ação autorizada no arquivo correto, comprovar o que ocorreu e encerrar cada documento aberto pela tarefa assim que seu uso terminar, preservando o trabalho do usuário.

## Índice

1. [Escolher e conhecer a ferramenta atual](#1-escolher-e-conhecer-a-ferramenta-atual)
2. [Controlar a sessão e identificar os documentos](#2-controlar-a-sessão-e-identificar-os-documentos)
3. [Operar CAD e comprovar medições](#3-operar-cad-e-comprovar-medições)
4. [Salvar e fechar a cada arquivo](#4-salvar-e-fechar-a-cada-arquivo)
5. [Tratar falhas e comprovar o encerramento](#5-tratar-falhas-e-comprovar-o-encerramento)
6. [Registro técnico mínimo](#6-registro-técnico-mínimo)

## 1. Escolher e conhecer a ferramenta atual

Preferir ferramentas de arquivo, conectores, APIs ou recursos específicos do aplicativo quando atenderem à tarefa com fidelidade. Usar computer use quando a interface for necessária para acessar, medir, recalcular, verificar visualmente ou comprovar um comportamento nativo.

Antes da primeira operação, ler as instruções e a documentação atual da ferramenta de computer use disponível naquela sessão. Respeitar o protocolo de inicialização e descoberta do ambiente, as superfícies habilitadas e os recursos documentados. Se a sessão for reiniciada ou retomada sem a documentação necessária, carregá-la novamente antes de continuar.

Não transportar de outra sessão nomes de métodos, comandos de automação, IDs de janela, seletores, coordenadas de clique, atalhos ou permissões como se ainda fossem válidos. O estado visual, a versão do aplicativo e os recursos disponíveis precisam ser confirmados no momento. Só usar APIs e ações descritas pela ferramenta atual.

Confirmar a existência do aplicativo e do recurso necessário antes de prometer uma medição ou teste nativo. Se CAD ou Excel não estiver acessível, distinguir as validações alternativas possíveis do teste que ficou indisponível. Registro por script, XML, coordenadas ou renderizador não comprova operação na interface do aplicativo.

Uma limitação de ferramenta não interrompe os itens independentes. Registrar o item afetado e a alternativa efetivamente utilizada em `Pendências`, conforme [03 — Dúvidas e continuidade](03_duvidas_e_continuidade.md). Não inventar resultado nativo para completar a entrega.

## 2. Controlar a sessão e identificar os documentos

### Um único operador de interface

Manter **um único agente operando a interface de toda a sessão compartilhada**, inclusive quando houver aplicativos diferentes. Cliques, digitação, seleção de arquivos, mudanças de foco e comandos não podem ocorrer em concorrência. Um agente que calcula ou extrai dados em segundo plano não manipula a interface enquanto o operador estiver atuando.

Se houver troca de operador, o anterior deve cessar as ações e transmitir o estado comprovado: aplicativo, documento, janela, comando ou diálogo ativo e próximo passo. O sucessor lê o estado atual antes de operar. Um print antigo não garante o foco atual. Ver [09 — Agentes e retomada](09_agentes_e_retomada.md).

### Distinguir o que já estava aberto

Antes de abrir arquivos ou modificar janelas, inventariar os documentos acessíveis nos aplicativos que serão usados. Registrar quais já estavam abertos e, quando observável, caminho, janela/aba, condição de modificação e contexto. O registro existe para proteger o trabalho do usuário e orientar o encerramento; não precisa coletar conteúdo alheio ao escopo.

Classificar cada documento:

| Condição observada | Tratamento |
|---|---|
| Já aberto antes da tarefa | Documento preexistente; preservar e não fechar no encerramento da tarefa |
| Aberto/criado pela tarefa e identificado com segurança | Documento da tarefa; salvar o resultado aplicável e fechar após uso |
| Origem ou propriedade da janela não comprovada | Tratar como preexistente até esclarecer pela própria evidência disponível |

Uma aba com nome igual não prova que é o mesmo arquivo. Confirmar caminho completo por mecanismo disponível, como propriedade, título expandido ou diálogo do aplicativo, sem mudar o documento por engano. Evitar abrir duplicata de arquivo já aberto. Para marcações, preferir uma cópia identificada e abrir essa cópia, preservando a janela original.

### Verificar o alvo antes de cada grupo de ações

Confirmar aplicativo, janela, documento e estado atual. Conferir arquivo completo, projeto, disciplina, prancha, revisão, página/vista, Model/layout e região. Em planilha, confirmar workbook, aba e célula/intervalo; em CAD, objeto e camada; em PDF, página e detalhe. Não depender apenas da aba selecionada na operação anterior.

Após ação que muda foco ou abre diálogo, ler novamente o estado relevante. Confirmar a conclusão de comandos antes de digitar outro. Se o estado não corresponder ao esperado, interromper aquela sequência de cliques e reidentificar o alvo; continuar outras atividades independentes se necessário.

## 3. Operar CAD e comprovar medições

### Preparação da cópia

Preservar o DWG e demais fontes originais. Criar cópia com nome identificável e relação explícita com arquivo/revisão de origem antes de acrescentar contornos, camadas, polilinhas, marcações ou objetos. Conferir o caminho após `Salvar como`, pois o aplicativo pode manter o original aberto ou mudar o documento ativo conforme sua implementação.

Na cópia, verificar referências externas, camadas e vista necessárias. Confirmar unidade por distâncias conhecidas, plano/Z, faces, fechamento, arcos, vazios e objeto a medir. Os critérios de geometria estão em [04 — Áreas](04_calculo_de_areas.md) e [05 — Perímetros e alturas](05_perimetros_e_alturas.md); a interface não decide o critério arquitetônico.

Não alterar escala, mover vértices ou escolher entidade para obter um número esperado. Se houver ajuste técnico na cópia, registrar motivo, fonte, antes/depois e efeito sobre as medições dependentes.

### Medição nativa é uma ação efetivamente executada

Usar o comando e a opção confirmados no aplicativo e na versão disponíveis. No AutoCAD, por exemplo, `AREA` → `Object` pode ser apropriado para um objeto auditado quando essa opção estiver disponível. Em outro aplicativo, usar e nomear o equivalente real, sem simular uma sequência do AutoCAD.

Para afirmar medição nativa, registrar em conjunto:

1. Arquivo/cópia, revisão de origem e vista/espaço efetivamente utilizados.
2. Objeto selecionado e identificador disponível, como camada, handle ou ID.
3. Contorno ou trecho visível, incluindo os detalhes que fundamentam limites e deduções.
4. Comando/opção realmente executados e resultado legível da execução.
5. Unidade, fator de conversão quando houver e correspondência entre resultado e memória.

Registrar propriedades de fechamento, comprimento ou área quando ajudarem a comprovar a entidade. Distinguir propriedade lida, variável de último resultado, cálculo por coordenadas e novo comando executado. Uma leitura armazenada pode se referir a medição anterior; verificar a correspondência antes de usá-la.

Uma captura apenas do número, sem identificação do arquivo/objeto ou vínculo ao contorno, é evidência insuficiente para reproduzir a medição. Combinar imagem geral, detalhe e resultado quando uma única imagem não permitir a leitura. Salvar log textual nativo quando disponível e legível; não reconstruir um log como se tivesse sido produzido pelo aplicativo.

Se o comando falhar, o objeto não for selecionável ou a interface não permitir confirmar a execução, registrar esse resultado real. Um cálculo alternativo pode continuar válido com rótulo próprio; não recebe a origem de medição nativa.

## 4. Salvar e fechar a cada arquivo

Organizar o trabalho por arquivo ou conjunto inseparável de referências: abrir, verificar, executar os usos necessários, capturar evidências, salvar, confirmar o salvamento e fechar os documentos abertos pela tarefa. Não acumular desenhos e planilhas abertos depois que seu uso terminou.

O uso de um arquivo pode envolver várias medições do mesmo lote antes do fechamento. Isso não autoriza manter todos os arquivos do projeto abertos até o fim. Se precisar retornar depois, reabrir a versão salva e identificada.

### Sequência de encerramento do documento da tarefa

1. Confirmar que resultados, contornos, fórmulas, imagens e registros necessários já foram preservados no destino correto.
2. Salvar alterações autorizadas na cópia ou arquivo de trabalho adequado. Evitar `Salvar` sobre a fonte quando o destino deveria ser uma cópia.
3. Verificar nome, caminho e conclusão do salvamento por evidência disponível. Quando necessário, confirmar existência do arquivo e reabrir a versão final para a validação prevista em [08 — Conferência, comparação e entrega](08_conferencia_comparacao_e_entrega.md).
4. Fechar o documento/aba aberto pela tarefa assim que seu uso terminar.
5. Conferir que a janela/aba deixou de estar aberta e registrar a conclusão.

Se aparecer diálogo de alterações não salvas, reidentificar o documento e as alterações antes de agir. Não escolher automaticamente `Descartar`, `Não salvar` ou opção equivalente. Salvar o conteúdo relevante da tarefa em destino identificado; preservar alterações ou documentos do usuário cuja origem não esteja comprovada.

Não fechar documentos preexistentes, não descartar alterações do usuário e não encerrar um aplicativo inteiro para fechar um único arquivo se isso atingir outras janelas. Não usar encerramento forçado de processo como atalho de limpeza.

### Localização dos artefatos

Quando não houver estrutura definida pelo usuário, a execução usa a raiz `levantamento-orcamento/execucoes/<data>/`. Destinos relevantes para a interface:

| Conteúdo | Subpasta da execução |
|---|---|
| Evidências de tela, contorno e comandos | `04_evidencias` |
| Planilhas resultantes | `05_planilhas` |
| Resultado das verificações | `06_conferencia` |
| Backups anteriores a substituições autorizadas | `07_backups` |
| Geometrias, logs, registro de documentos e dados técnicos | `08_dados_tecnicos` |

Adaptar os caminhos ao destino autorizado e relacionar cada artefato à fonte. Não depender de capturas ou cópias mantidas apenas em diretório temporário. A cópia CAD deve ter localização final identificada no registro técnico e linkado pela memória pertinente.

## 5. Tratar falhas e comprovar o encerramento

Prever limpeza também se ocorrer erro de ferramenta, medição, salvamento ou validação. Em automação, usar mecanismo equivalente a `try/finally` quando disponível; na operação manual, manter o mesmo controle de ciclo de vida. A limpeza não substitui a proteção contra perda de conteúdo.

Após falha:

1. Identificar o estado atual e quais documentos da tarefa permanecem abertos.
2. Preservar os resultados e evidências já obtidos; se houver conteúdo recuperável ainda sem destino, salvar uma cópia de recuperação identificada quando o aplicativo permitir com segurança.
3. Fechar somente os documentos da tarefa cujo conteúdo relevante foi preservado ou cujo encerramento não descarta trabalho do usuário.
4. Registrar o que foi salvo, fechado, ficou sem confirmação ou permaneceu aberto, com motivo e caminho de recuperação quando existente.
5. Continuar atividades independentes e refletir a limitação no item técnico afetado.

Se a ferramenta perder acesso ao aplicativo, tentar recuperar o estado pelos recursos documentados disponíveis. Não repetir cegamente comandos de salvamento/fechamento e não presumir que uma chamada sem confirmação teve sucesso.

Se não for possível salvar ou confirmar a propriedade do conteúdo, preservar a janela em vez de forçar descarte. O registro deve indicar explicitamente a exceção e seu alcance. Isso não permite afirmar `todos os arquivos fechados`.

No encerramento da execução, reconciliar o inventário inicial com o registro de arquivos abertos pela tarefa. Confirmar o fechamento destes, preservando os preexistentes. Encerrar o aplicativo somente quando tiver sido aberto para a tarefa e for possível comprovar que isso não atingirá documentos preexistentes ou trabalho do usuário.

Relatar apenas o observado: `salvo e fechado`, `salvo, fechamento não confirmado`, `aberto, preservado por alteração não identificada` ou `aplicativo indisponível`, conforme o caso. A entrega e a conferência do arquivo final seguem a referência 08; este documento controla a operação e seu encerramento.

## 6. Registro técnico mínimo

Manter registro estruturado, por exemplo CSV, JSON ou tabela da planilha, em `08_dados_tecnicos` ou no local equivalente da execução. Trata-se de evidência operacional dos arquivos, não de memória informal de projeto nem lista Markdown de tarefas.

| Campo | Conteúdo |
|---|---|
| Execução/documento | ID único da execução e ID do documento |
| Fonte e cópia | Caminhos, revisão e identificador de conteúdo quando disponível |
| Aplicativo | Nome e versão observável, ferramenta usada |
| Origem da janela | Preexistente, aberta/criada pela tarefa ou não comprovada |
| Estado inicial | Documento ativo, vista/aba e alteração não salva observável |
| Uso efetivo | Leitura, medição, edição, recálculo ou verificação realizados |
| Evidência | Arquivos e IDs que comprovam contorno, comando e resultado |
| Salvamento | Caminho final, confirmação e momento do salvamento |
| Encerramento | Fechado, não confirmado ou preservado aberto, com motivo |
| Limitação técnica | Item afetado e ID na aba Pendências quando aplicável |

**Exemplo fictício:** um desenho já aberto antes da tarefa permanece aberto. A cópia criada para conferência recebe contornos, é salva em caminho identificado e fechada após as medições. O registro distingue as duas janelas e relaciona a evidência à cópia; não declara que o original foi medido nem que o usuário fechou seu documento.
