# Eficiencia de Tokens — Claude Code

**Regra:** ler em todo boot. Fonte: firecrawl.dev/blog/claude-code-token-efficiency.
Objetivo: reduzir tokens gastos por sessao sem perder qualidade de trabalho.

## Diagnostico antes de otimizar

- `/context` mostra o breakdown de tokens ao vivo por componente da sessao.
- `/usage` mostra quais componentes mais consomem.
- `/memory` mostra quais arquivos carregaram no boot.
- Baseline normal de boot (system prompt + CLAUDE.md + memoria + schemas MCP)
  fica entre 20k-30k tokens antes de digitar qualquer coisa — use isso como
  referencia, nao como alarme.

## Web e dados brutos

- Nunca jogar HTML cru no contexto. Pagina crua chega a ~38k tokens; o
  conteudo real costuma ser ~2,8k. Usar Firecrawl (ou scrape equivalente) para
  extrair como markdown limpo antes de processar.
- Filtrar saida de ferramentas antes de injetar no contexto: logs de build e
  teste devem mostrar so o que falhou, nao o passo a passo de sucesso.

## CLAUDE.md e regras

- Manter CLAUDE.md enxuto (ideal: abaixo de ~200 linhas). Remover qualquer
  coisa que o Claude consiga inferir lendo o codigo.
- Comentarios HTML (`<!-- -->`) dentro de CLAUDE.md custam zero tokens —
  usar para anotacoes que so humanos precisam ler.
- Regras que so se aplicam a um subconjunto de arquivos devem usar frontmatter
  `paths:` para carregar sob demanda, em vez de sempre-carregado.
- Preferir skills (carregam so nome+descricao no boot, ~30-100 tokens; o
  conteudo completo so entra quando a skill e de fato acionada) a colar tudo
  no CLAUDE.md.

## Exclusao de arquivos

- `.claudeignore` e sinal consultivo (Claude ainda pode ler se decidir que
  precisa).
- Para bloqueio de verdade, usar `permissions.deny` em
  `.claude/settings.json`.
- Excluir por padrao: `node_modules/`, `dist/`, `*.lock`, `__pycache__/`,
  `*.min.js` e afins.

## MCP e modelos

- Cada servidor MCP conectado adiciona ~10k-20k tokens de schema por sessao.
  Desconectar servidores nao usados no inicio da sessao; reconectar no meio
  limpa o prompt cache.
- Rotear tarefa para o modelo certo: Sonnet como padrao; Opus so para decisao
  arquitetural profunda ou bug complexo; Haiku para subagentes, inspecao de
  log e boilerplate.

## Prompts e modo de sessao

- Prompt precisos > prompts abertos: verbo especifico, escopo, constraints
  negativas ("nao redesenhar arquitetura", "nao adicionar dependencia") e
  orcamento de resposta ("no maximo 5 bullets").
- Separar modos: planejar (mapear dependencias antes de implementar),
  implementar (a partir de uma secao especifica do plano), debugar (formato
  estruturado de incidente, nao narrativa).

## Recuperacao de contexto

- Compactar (`/compact`) proativamente por volta de 250k-300k tokens, antes do
  auto-compact forcado.
- Ao encerrar ou perder contexto, preferir handoff registrado (ver regra de
  handoff no CLAUDE.md global) a depender so do historico de chat.

## Quando NAO usar o agente

- Para fix localizado e sem ambiguidade, editar a mao pode ser mais rapido
  que o overhead de orquestrar o agente. Reconhecer esse caso em vez de
  insistir em automatizar.
</content>
