# Handoff — 2026-07-22 — Pulse (reconstrução do tempo-resposta-app)

## De onde veio

Sessão no `mac-grupovelas`. Depois de uma auditoria completa do SaaS atual
(`~/Documents/tempo-resposta-app`), foi aprovado um plano de reconstrução
full-stack (frontend + backend), reaproveitando o banco Supabase atual.
**Plano completo e aprovado em:**
`/Users/grupovelas/.claude/plans/wondrous-hopping-gizmo.md` — ler esse arquivo
primeiro, ele tem todo o contexto de arquitetura, schema, RLS, ordem de fases.
Esse handoff é só o estado de execução da Fase 0, não repete o plano.

⚠️ **Importante**: o projeto antigo (`~/Documents/tempo-resposta-app`)
**continua em produção** e não deve ser desligado até a Fase 4 do plano.

## ⚠️ Verificar antes de continuar no macbook-jpazv

Este projeto novo está em `~/Desktop/Pulse1.0.1` — **fora de `~/Documents`**,
que é a pasta confirmada como sincronizada via iCloud entre as duas máquinas
(ver memória `agent-hub-icloud-sync`). Não há confirmação de que `~/Desktop`
sincroniza da mesma forma. Antes de continuar:

1. Confirmar no macbook se `~/Desktop/Pulse1.0.1` já aparece (iCloud "Desktop e
   Documentos" pode estar ligado, sincronizando ambos juntos).
2. Se **não** aparecer: o repo git local (`git init` já feito, 1 commit) está
   só no `mac-grupovelas`. Vai precisar ou (a) criar um remoto no GitHub e dar
   push de lá, ou (b) mover o diretório pra dentro de `~/Documents` (aí sim
   sincroniza automaticamente).

## O que foi feito nesta sessão (Fase 0 do plano)

1. **Auditoria completa do código atual** (segurança, escalabilidade,
   estrutura, funcionalidades) — resultado incorporado no plano aprovado.
2. **Plano de reconstrução escrito e aprovado** pelo usuário (plan mode) —
   ver arquivo citado acima. Cobre: stack (Next.js+TS+Tailwind+shadcn+TanStack
   Query+Recharts+Vitest+Zod), schema atual do banco, modelo de
   multi-usuário por tenant (`tenant_members`), RLS policies concretas,
   estrutura de pastas, ordem de execução em 5 fases, riscos, verificação.
3. **Projeto Supabase de staging criado**:
   - Nome: `pulse-staging`
   - Reference ID: `fiswngbbjpezivneiete`
   - Org: `tnumeveypqsklzezdksf` (Grupo Velas jpazvOrg)
   - Região: São Paulo (`sa-east-1`)
   - Senha do banco: **não está aqui** (segredo nunca entra no hub) — salva em
     `~/Desktop/Pulse1.0.1/.staging-supabase-credentials` (só no
     `mac-grupovelas`, arquivo com `chmod 600`, ignorado pelo git). Se
     continuar no macbook e esse arquivo não estiver acessível, resetar a
     senha do banco no dashboard do Supabase é mais simples que tentar
     recuperar.
   - Ainda **não linkado** localmente (`supabase link` não foi executado) e
     **nenhuma migration foi aplicada** nela ainda.
4. **Scaffold do Next.js criado e commitado** em `~/Desktop/Pulse1.0.1`:
   - `create-next-app` com TypeScript, Tailwind, ESLint, App Router, alias
     `@/*`.
   - `package.json` renomeado de `pulse-scaffold-tmp` pra `pulse`.
   - `git init` local feito, 1 commit (`scaffold inicial: Next.js (App
     Router, TS, Tailwind)`). **Sem remoto configurado ainda.**
   - **`npm install` ainda não foi rodado** — não há `node_modules/`.
5. **Task list criada** nesta sessão do Claude Code (5 fases do plano) — não
   persiste entre sessões/máquinas, recriar se necessário (ver plano pra
   descrição de cada fase).

## Pendente / próximo passo imediato (dentro da Fase 0)

Ordem sugerida pra continuar exatamente de onde parou:

```bash
cd ~/Desktop/Pulse1.0.1   # (ou onde o diretório estiver acessível no macbook)
npm install
npx shadcn@latest init    # design system — ainda não configurado
npm install @supabase/supabase-js @supabase/ssr @tanstack/react-query recharts zod
npm install -D vitest @testing-library/react

# Linkar o projeto de staging (senha em .staging-supabase-credentials):
supabase login   # se ainda não estiver autenticado nessa máquina
supabase link --project-ref fiswngbbjpezivneiete

# Copiar as migrations do projeto atual como ponto de partida:
mkdir -p supabase/migrations
cp ~/Documents/tempo-resposta-app/supabase/migrations/*.sql supabase/migrations/
supabase db push   # aplica as migrations existentes no staging
```

Depois disso, seguir a **Fase 1 do plano** (migrations novas: `tenant_members`,
RLS policies reais, mover secrets pra Vault, dropar índice obsoleto,
validar isolamento multi-tenant com 2 tenants sintéticos em staging).

## Nota lateral (fora do escopo técnico, não bloqueia)

Em paralelo a esta sessão, uma conversa separada (fork de agente) discutiu
direção visual e chegou a **PostHog** como âncora de design (dashboard denso,
hero chart, dark-mode-friendly) — isso já está registrado no plano aprovado,
seção "Direção visual". Não precisa reabrir essa decisão, só usar como
referência na Fase 3 (frontend).
