# Handoff: Alertas Tráfego Pago — Ajustes Ernandes

**Data:** 2026-08-13
**Projeto:** Dashboard 316, aba Alertas (tab 929)
**Solicitante:** Ernandes Lima
**Issue:** Grupo-Velas/produtividade-bi-dev#249

---

## Alterações realizadas

### Card 13520 — Alerta CPL Unidades
- Removido verde e laranja — só mostra variação **≥ 15%**

### Card 13518 — Alerta CPL Criativos
- Só mostra variação **≥ 15%**
- Adicionada coluna **Campanha** (nome exato)
- Adicionada coluna **Status** (Ativo/Pausado)

### Card 13526 — CPL acima de R$35 Criativos (30d)
- Threshold CPL: **R$25 → R$35/dia**
- Nome atualizado para refletir R$35
- Adicionada coluna **Campanha**
- Adicionada coluna **Status**

### Card 13528 — Alerta CPV Engajamento
- Removido verde e laranja — só mostra variação **≥ 15%**
- Adicionada coluna **Campanha**
- Adicionada coluna **Status**

### Text card (dashcard 19575)
- Atualizado com novas regras, legenda sem verde/laranja, explicação de Status

## Regras vigentes

- **Threshold variação**: ≥ 15% (só vermelho)
- **Legenda**: 🔴🔴 >+30% · 🔴 +15% a +30%
- **Status**: Ativo = gastou nas últimas 24h · Pausado = sem gasto 24h+
- **CPL alto**: R$35/dia (era R$25)
- **Campanha**: nome exato em todos os cards de criativos

## Pendência

- **Issue #249**: sem permissão de write no repo `produtividade-bi-dev` (user `jpazv` só tem `pull`). Precisa de role **Triage** ou **Write** pra atualizar issues.
