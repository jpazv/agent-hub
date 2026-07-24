# Handoff — Copy rewrite + Deploy + Multi-IA Hub expansion

**Data:** 2026-07-24  
**Máquina:** mac-grupovelas  
**Próxima etapa:** Testar fluxo completo Eco (landing → compra → provisão → app)

---

## O que foi feito

### 1. Reescrita de copy da landing (Pulse Lume + Eco)

**Problema:** Boss reprovou o copy original — muito jargão financeiro (DRE, score, radar) alienava o público-alvo (fisioterapeutas que possuem clínicas, sem background financeiro).

**Solução:** Briefing → Rytr → duas versões reescritas → seleção + implementação.

**Mudanças aplicadas em `index.html`:**

| Seção | ANTES | DEPOIS |
|-------|-------|--------|
| **Hero** | "Transforme dados simples em score, DRE e plano de ação" | "Descubra quanto dinheiro sua clínica está deixando na mesa — em minutos, com um plano claro para agir agora" |
| **Problema** | "Quando a sessão está barata demais, quando o aluguel parece normal..." | "Você acha que está ganhando bem, mas no fim do mês sobra pouco. Por quê? Porque seus preços estão baixos demais, suas salas ficam vazias, o aluguel pesa demais e o atendimento demora..." |
| **Card Lume** | "Score + DRE em linguagem de dono" (features técnicas) | "Recupere o dinheiro que sua clínica perde todo mês" (benefício) + features concretas |
| **Card Eco** | "Alertas de 15, 30 e 60 minutos..." | "Pare de perder pacientes por demora na resposta" (benefício) |
| **Plano Premium** | "DRE, radar de indicadores, plano de ação" | "Diagnóstico completo da sua clínica com visão clara dos vazamentos de dinheiro" |

**Commit:** `d83d22b` em `raiox-mvp-html`  
**Deploy:** ✅ Vercel — live em https://raiox-mvp-html-kslq99ygx... e checkpulse.com.br

---

### 2. Expansão do hub pra suportar Codex + Gemini

**Problema:** Hub só tinha estrutura pra Claude Code. Queremos que Codex e Gemini também puxem contexto igual.

**Solução:** Criar entrada paralela (`~/.codex/CODEX.md`, `~/.gemini/GEMINI.md`) que apontam pro mesmo hub.

**Arquivos criados:**

1. **`~/.codex/CODEX.md`** — entry point pra Codex
   - Mesmo padrão de CLAUDE.md
   - Papéis diferenciados: Codex = executor preciso, não explorador

2. **`~/.gemini/GEMINI.md`** — entry point pra Gemini
   - Mesmo padrão
   - Papéis: análise rápida, busca de padrões

3. **`agent-hub/AGENTS.md`** — documento novo
   - Define papéis de cada agente
   - Fluxo esperado de colaboração
   - Exemplo de fluxo real (Claude → Gemini → Codex → Claude valida)

4. **Updated files:**
   - `agent-hub/README.md` — adicionado referência a AGENTS.md
   - `agent-hub/registry/machines.yaml` — mac-grupovelas agora lista 3 agentes

**Commit:** `e90567f` em `agent-hub`

---

## Estado dos projetos

### `raiox-mvp-html`
- ✅ Copy reescrito, testado, deployado
- ✅ Vercel alias promovido (checkpulse.com.br)
- 🔄 Próximo: testar fluxo real de compra do Eco

### `pulse` (Eco)
- ✅ Onboarding backend (provisioning, convite) pronto
- ⚠️ Pendência: Supabase redirect URL configurada manualmente (Authentication → URL Configuration → add https://pulse-app-steel-tau.vercel.app/convite)
- 🔄 Próximo: testar e2e (landing → compra → email → login → app)

### `agent-hub`
- ✅ Multi-IA estrutura criada e documentada
- ✅ Codex e Gemini podem puxar contexto igual Claude
- ℹ️ Próximo: quando chamar cada um, seguir fluxo em AGENTS.md

---

## Pendências reais (não resolvidas)

1. **Supabase redirect URL** — requer dashboard manual
   - Navegue: https://supabase.com/dashboard/project/fiswngbbjpezivneiete/auth/url-configuration
   - Adicione: `https://pulse-app-steel-tau.vercel.app/convite`

2. **Fluxo e2e não testado**
   - Landing → comprar-eco.html → checkout simulado → provisioning endpoint → email de convite → define senha → app
   - Stripe real ainda não configurado (está simulado)

3. **DNS (checkpulse.com.br)**
   - Alias já aponta, mas requer DNS real
   - Uso: continuamos com Vercel URLs até resolver

---

## Próximos passos (ordem de prioridade)

1. **Configure Supabase redirect** (manual, 1 min)
2. **Teste fluxo Eco e2e** (landing → app completo)
   - Abra landing, clique "Assinar o Eco"
   - Preencha nome + email
   - Email chega com link de convite
   - Clique no link, define senha
   - Cai em `/configuracoes/whatsapp`
3. **Se tudo passar**: documentar procedimento de onboarding em `pulse/docs/`
4. **Próximo negócio**: criar Stripe real (fora de escopo deste handoff)

---

## Notas técnicas

- **iCloud sync**: `~/dev/` está isolado de iCloud (não sincroniza). Ambos os repos (`raiox-mvp-html` e `pulse`) agora estão lá.
- **Git author email**: foi corrigido em sessões anteriores (jpazevedomoreiraa@grupovelas.com.br) — sem bloqueios de deploy agora.
- **Copy e idioma**: usamos padrão de linguagem simples, direto, sem jargão — mantém pra próximas mudanças.
