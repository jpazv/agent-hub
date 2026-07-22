# Handoff — 2026-07-22 — Pulse (MVP no ar: fixes visuais, insight de qualidade, modo demo, deploy Vercel)

## De onde veio

Continuação de `memory/handoffs/2026-07-22-pulse-rebuild-fase3.md` (Fase 3 do
plano — frontend — já estava concluída). Esta sessão foi toda de **verificação
visual e polimento pós-Fase-3**, não uma nova fase do plano formal. Repo:
`https://github.com/jpazv/pulse` (privado), tudo já commitado e pushed —
`git pull` antes de continuar em qualquer máquina.

## O que foi feito (tudo commitado, 4 commits novos além da Fase 3)

1. **Verificação visual real com Playwright** (não tínhamos `chromium-cli`
   disponível — instalado playwright standalone no scratchpad e escrito um
   driver próprio). Achado real: login/signup redirecionavam pra `/rede`
   (rota que não existe, 404) — corrigido pra `/`. Commit
   `4ea5e56`.
2. **Bordas quase invisíveis no design system** — `--border` em
   `oklch(0.922)` num fundo `oklch(1)` (contraste baixíssimo), e o componente
   `Card` usava `ring-foreground/10` (ainda mais fraco, nem a variável
   `--border`). Corrigido: `--border`/`--input`/`--sidebar-border` pra
   `oklch(0.8)`, `Card` trocado pra `border border-border` sólida. Mesmo
   commit `4ea5e56`.
3. **`scripts/seed-demo-data.mjs`** — gera ~43 conversas de exemplo pra
   `demo@pulse.local` (tenant "Clínica Demo", unit "Matriz", senha
   `demo12345`). Importante: dispara o **endpoint real** `/api/cron/score-leads`
   pra calcular temperatura/qualidade — não uma reimplementação aproximada
   (isso foi corrigido depois de eu ter cometido esse erro na primeira
   versão do script). Mesmo commit `4ea5e56`.
4. **Insight de qualidade do atendimento, revelado com sutileza** (decisão de
   produto do usuário: não vender como feature de cara, deixar o cliente
   "descobrir") — `components/dashboard/atendimento-etapas.tsx`: checklist
   expansível (fechado por padrão) das 5 etapas da trilha genérica
   (abordagem/sondagem/apresentação/oferta de horário/preço), cada uma com a
   citação exata da mensagem que a detectou (já existia em
   `qualidade_evidencias.etapas`, só não estava exposto). Toast de "primeira
   descoberta" (localStorage, 1x só) na primeira conversa de qualidade
   "alta". Commit `6ba1201`.
5. **Modo demo (`NEXT_PUBLIC_DEMO_MODE=true`)** — `scripts/export-demo-data.mjs`
   loga como demo@pulse.local, chama todos os endpoints de leitura reais, e
   salva em `lib/client/demo-data.json`. `lib/client/api.ts` serve desse JSON
   (zero round-trip de rede) quando a flag está ligada — só leituras;
   mutations continuam reais. Validado via Playwright: 0 chamadas de rede
   pros dados, render em ~1s (dominado pelo login, não pelos dados). Trade-off
   aceito: dados congelados no momento do export, reexecutar o script pra
   atualizar. Commit `9f56ef7`.
6. **Deploy no Vercel** — projeto `pulse-app` (nome do diretório
   `Pulse1.0.1` tem maiúsculas/pontos, inválido pro Vercel, por isso o nome
   diferente). **Sem integração automática com GitHub** — a conta Vercel não
   tem login GitHub conectado, então deploy é manual via `vercel --prod`, não
   automático a cada push. Env vars configuradas: Supabase (staging) +
   `NEXT_PUBLIC_DEMO_MODE=true`. **Faltam de propósito** (deploy rápido, não é
   a Fase 4 completa): `WHATSAPP_APP_SECRET`, `META_APP_ID`/`META_APP_SECRET`/
   `META_CONFIG_ID`, `CRON_SECRET`, `GROQ_API_KEY` — sem elas, webhook/
   onboarding real/crons não funcionam em produção, só a navegação do
   dashboard em modo demo (que era o objetivo desta sessão).

## Estado atual no ar

**https://pulse-app-steel-tau.vercel.app** — login `demo@pulse.local` /
`demo12345`. Validado via Playwright contra a URL de produção: 0 erros de
console, todas as telas renderizando com dado real (gerado pelo algoritmo de
scoring de produção, não fake).

## Pendências conhecidas (nenhuma nova além das já registradas nas Fases 2/3)

- Ainda sem Advanced Access da Meta pro Embedded Signup (Fase 2).
- Scheduling de score-leads/detect-agendamentos/ask-compareceu/pg_cron do
  check-alerts (Fase 2/3).
- **Novo**: conectar login GitHub na conta Vercel se quiser deploy automático
  em push (hoje é manual).
- **Novo**: env vars de produção real (Meta, cron, Groq) não configuradas no
  Vercel — só o necessário pro modo demo. Configurar antes de qualquer uso
  real do deploy (isso é trabalho da Fase 4, não fazer apressado).

## Próximo passo

Fase 4 (corte de produção) continua sendo o próximo item formal do plano —
ver `docs/plan-reconstrucao.md` no repo. Nada bloqueia continuar direto do
macbook: `git pull` no repo do Pulse, `.env.local` precisa ser recriado
localmente (não é versionado — valores nas credenciais do Supabase
`pulse-staging`, mesmos de sempre).
