# Padrão — documentar as issues do GitHub

**Status:** padrão vigente, definido em 2026-09-02
**Escopo:** todo trabalho de BI/Metabase rastreado no `Grupo-Velas/produtividade-bi-dev`

## A regra

**A issue do GitHub é o registro de microgerenciamento.** Toda entrega, correção,
descoberta e decisão vai documentada na issue correspondente — não só no chat, não só
no handoff do hub.

O handoff do hub é a memória **entre sessões de IA**. A issue é a memória **do time**.
São públicos diferentes e os dois precisam existir.

## Por que

- Quem pega o trabalho depois não tem acesso ao chat nem lê handoff de IA.
- Decisão não registrada é decisão que será reaberta em três meses sem argumento novo.
- Hipótese descartada é resultado: sem ela documentada, alguém repete o caminho.
- O board é o instrumento de gestão; issue sem contexto vira card morto.

## Estrutura do comentário de entrega

Ordem fixa, para ser varrível por quem só quer uma parte:

1. **O que foi construído** — artefato, IDs (dashboard, card, coleção), link.
2. **Decisões tomadas** — o que foi escolhido e **por quê**, incluindo o que foi recusado.
3. **Como foi aplicado** — `PUT` no mesmo id ou recriação, e a convenção que justifica.
4. **Validações** — números de antes/depois, invariantes conferidos, cenários testados.
5. **Hipóteses descartadas** — o que foi testado e caiu, com o dado que derrubou.
6. **Limites do dado** — o que a análise não cobre e por quê.
7. **Pendências** — o que ficou aberto e de quem é.

## Regras de conteúdo

- **Número com fonte.** Todo valor vem com a tabela/MV e a janela de onde saiu.
- **Retratação vai no topo.** Se um comentário anterior errou, a correção abre o
  comentário novo — não fica enterrada no meio.
- **Nomear IDs sempre.** `card 15299`, `dashcard 22669`, `coleção 677`. Nome sem id
  obriga o próximo a garimpar.
- **Bloco de código para SQL** que mudou, com o comentário de raciocínio junto.
- **Tabela para comparação** de antes/depois. Texto corrido esconde diferença.
- **Sem adjetivo sem número.** "Melhorou muito" não é registro; "CPL de 23,23 para
  11,70" é.

## Criação de card

Sempre pela skill `criar-card` (`~/.claude/skills/criar-card/`), que padroniza título,
board, setor, tipo e prioridade.

- Título: `[JP] [Projeto] Atividade` — a tag de responsável vai no **título**, porque
  **assignee não funciona** neste repositório (`ReplaceActorsForAssignable`: a conta
  `jpazv` não tem permissão). Confirmado de novo em 2026-09-02.
- Corpo com Objetivo, Contexto e Critério de sucesso preenchidos. Card com corpo em
  branco (ex.: `#305`) não é rastreável.
- O Status às vezes é reposicionado por automação do repo depois da criação —
  conferir com `verificar.graphql` e não assumir.

## Quando comentar

- **Ao entregar** — o comentário de entrega completo.
- **Ao descobrir algo que muda o escopo** — inclusive quando derruba a premissa do
  próprio card.
- **Ao descartar hipótese** — com o teste que a derrubou.
- **Ao encontrar bug em produção** — card próprio, não comentário solto.

## Relação com o handoff do hub

| | Issue do GitHub | Handoff do hub |
|---|---|---|
| Público | time, gestão | próxima sessão de IA |
| Granularidade | por demanda | por sessão |
| Conteúdo | o que foi feito e decidido | como chegamos lá, armadilhas, arquivos locais |
| Vive | para sempre, no board | em `memory/handoffs/`, commitado |

O handoff **referencia** as issues; a issue não referencia o handoff, exceto por
caminho de arquivo quando útil.
