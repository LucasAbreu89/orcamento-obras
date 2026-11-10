# Levantamento de quantitativos: guia de uso

Esta pasta é uma skill para agentes (Codex e compatíveis) que transforma uma pasta de projetos e uma planilha de serviços em quantitativos com memória de cálculo. Serve para reforma e construção nova, em qualquer disciplina, desde que os projetos estejam acessíveis.

## Preparação única do computador

As bibliotecas ficam num ambiente virtual dentro da skill (o Python do Homebrew e de várias distribuições não aceita `pip install` direto no sistema):

```bash
python3 -m venv procedimentos-orcamento/.venv
```

```bash
procedimentos-orcamento/.venv/bin/python -m pip install -r procedimentos-orcamento/scripts/requirements.txt
```

Com o ambiente criado, o agente roda os scripts com `procedimentos-orcamento/.venv/bin/python`.

Também recomendados:
- **ODA File Converter** (gratuito, Open Design Alliance): converte DWG em DXF sem abrir o CAD. Sem ele, o agente usa um CAD instalado pela interface ou pede DXF/PDF.
- **LibreOffice**: recálculo independente da planilha entregue e conversão de XLS/ODS.

Para conferir o que está disponível: `python3 procedimentos-orcamento/scripts/ambiente.py`. Para testar o kit com arquivos sintéticos (os testes que dependem de uma biblioteca ausente são pulados):

```bash
procedimentos-orcamento/.venv/bin/python -m unittest discover -s procedimentos-orcamento/scripts/tests
```

IFC: o kit não traz leitor de IFC. Com modelo IFC, o agente usa uma ferramenta IFC instalada (por exemplo, IfcOpenShell) ou pede DWG, PDF ou os quantitativos exportados do modelo.

## Como pedir

```text
Use $procedimentos-orcamento.
Projetos: /caminho/da/obra/projetos
Planilha de serviços: /caminho/da/obra/servicos.xlsx
```

Para um pedido menor, diga o alcance: "só catalogar", "só os itens 3.1 a 3.8", "só comparar com a coluna do empreiteiro".

Inicie a chamada no modelo de nível topo da tabela de [references/09](references/09_agentes_retomada_e_revisoes.md); os demais o agente escolhe por ela.

## O que acontece

1. O agente checa as ferramentas, inventaria os arquivos, faz backup e uma "fotografia" da planilha.
2. Lê todos os projetos (todas as pranchas, layouts e camadas) e monta um catálogo.
3. Mapeia todas as abas da planilha, classifica os itens e liga cada um à especificação do projeto.
4. **Para e mostra o escopo proposto**: abas e itens que vai levantar, disciplinas cobertas, itens que são custo indireto, critérios de maior impacto e documentos faltantes. Você confirma ou corrige numa resposta. (Se o pedido já disser tudo isso, ele segue direto e registra as escolhas como premissas.)
5. Mede por elemento (ambientes, paredes, vãos, forros, pontos) e apropria cada item.
6. Gera a planilha de entrega e os prints marcados a partir de um arquivo de dados único.
7. Valida tudo por script (originais intactos, vínculos, estados, prints, valores recalculados) e entrega.

## O que você recebe

- A planilha recebida, sem nenhuma célula alterada, com as colunas `QTD LEVANTADA`, `ESTADO`, `MEMÓRIA` e `OBS LEVANTAMENTO`.
- Uma aba de memória por item: critério, parcelas com fórmulas, print do projeto com as parcelas marcadas e o texto "o que entrou / o que ficou fora / o que falta".
- **Pendências**: perguntas prontas para enviar ao projetista ou ao cliente, ordenadas por impacto.
- **Premissas**: valores adotados quando o projeto não dizia, com a justificativa e como confirmar.
- **Sugestões**: serviços que o projeto pede e a lista não tem (fora da principal).
- **Comparação**, quando você pedir: quantidade levantada × referência, com a diferença explicada.
- **Critérios**, **Fontes** e **Resumo** (com as limitações do que não pôde ser verificado).

Estados de cada item: **CONFIRMADO** (tudo veio do projeto), **PREMISSA** (depende de um valor adotado e listado), **SUBTOTAL** (parte medida, falta parte), **PENDENTE** (falta informação), **NÃO APLICÁVEL** (fora do levantamento, com motivo). Nada desconhecido aparece como zero.

## Como personalizar

- **Critérios de medição:** o padrão está em [references/11_criterios_padrao.md](references/11_criterios_padrao.md). Para mudar o padrão da empresa, edite esse arquivo; para uma obra só, diga no pedido ou no checkpoint (ex.: "não descontar vãos até 2 m²").
- **Nível de premissas:** `conservador` (só o que está no projeto), `padrão` ou `amplo` (adota valores usuais sempre que possível).
- **Limite para investigar diferenças** numa comparação (padrão: 5%).

## Onde ficam os arquivos

Cada execução cria `levantamento-orcamento/execucoes/AAAAMMDD_HHMMSS/` dentro da obra, com as pastas `fontes`, `dados`, `evidencias`, `planilha` e `conferencia`. Os projetos e a planilha originais nunca são alterados nem movidos.

## Instalação da skill

Neste workspace, a skill está registrada por dois links que apontam para esta pasta: `.agents/skills/procedimentos-orcamento`, lido pelo Codex, e `.claude/skills/procedimentos-orcamento`, lido pelo Claude Code. No Codex, ela é chamada por `$procedimentos-orcamento` ou pela lista de skills; no Claude Code, por `/procedimentos-orcamento`. Para usar em outro projeto, indique o caminho do `SKILL.md` ou disponibilize a pasta como skill naquele ambiente.
