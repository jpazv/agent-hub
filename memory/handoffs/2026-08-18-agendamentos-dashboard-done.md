# Handoff — Aba Agendamentos Dashboard Tráfego Pago
**Data:** 2026-08-18
**Sessão:** Claude Code (MacBook JP)
**Status:** ✅ Concluído — em validação

## O que foi feito

Criação completa da aba **Agendamentos** no dashboard principal **Tráfego Pago** (dash 316) e no dashboard de teste (dash 385).

### Cards criados (dash 316, collection 12, tab 938)

1. **Agendamentos — Alerta KPI** — Tabela sem filtros. Mostra unidades com %FAT, %Agend ou %Lead < 100%. Trimestre usa lógica MTD/TRI do card 13549 (mv_venda_propria + mv_analise_faturamento_trimestral). Vermelho em < 100% e Trimestre < 0.

2. **Agendamentos — Semanal** — Visão igual ao report_mkt do VelasConnect. 3 métricas (Leads, Agendamentos, %CVS) × 4 sub-linhas (Valor, vs. faixa anterior, Marca, Veredito). Colunas: Dia 01-07, 08-14, 15-21, 22-28, 29-fim. Threshold: 5pp volumes, 0.5pp taxas. Verde/vermelho em +/-.

3. **Agendamentos — Diário** — Gráfico combo: Agendamentos (barra), Leads (linha eixo direito), Agend. Esperado (linha). Coeficientes: quente×0.2582 + pré_quente×0.1113 + morno×0.0351 + frio×0.0097.

4. **Agendamentos — Leads do Dia** — Scalar "X / Y" (realizado / meta do dia).

5. **Agendamentos — Agend. do Dia** — Scalar "X / Y" (realizado / esperado do dia).

6. **Agendamentos — Projeção** — 5 linhas: Meta, Realizado, Meta-Realizado, Projeção, Meta-Projeção. Colunas: Investimento (R$), CPL (R$), Leads, Agend. Projeção: leads por dia corrido, agend por dia útil (regra Performance). Sinais explícitos: -79 = falta (vermelho), +50 = sobra (verde).

7. **Texto markdown** explicando como ler cada card.

### Cards de teste (dash 385, collection 569, tab 937)
Mesma estrutura, cards: 13553 (KPI), 13554 (Semanal), 13555 (Diário), 13556 (Leads Dia), 13569 (Agend Dia), 13557 (Projeção).

### Filtros
- Dash 316: apenas "Unidades" (param 59d9c347) mapeado a todos cards exceto KPI
- Dash 385: data, marca, unidade, sócio, boutique, campanha (KPI sem filtros)
- Unidade padrão no 385: "ITC Vertebral - Bairro de Fátima"

### Regras críticas
- **APENAS SELECT** no banco analítico — nunca ALTER/CREATE/DELETE/UPDATE
- CPL Meta = SUM(meta_investimento) / SUM(meta_leads)
- Projeção: leads/dc_ate × dc_total, agend/du_ate × du_total
- Verdict dual threshold: 5 para volumes, 0.5pp para taxas

## Issue
- GitHub: [#282](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/282) — status "Em validação", tag [JP]

## Arquivos de trabalho
Todos em `/private/tmp/claude-501/-Users-grupovelas-Documents/8bfc8333-7b03-40ea-ab30-894feba21cfa/scratchpad/`:
- `kpi.sql`, `semanal_pivot.sql`, `diario.sql`, `saldo_leads.sql`, `saldo_agend.sql`, `projecao.sql`
- `apply_3mudancas.py`, `apply_saldo.py`, `apply_projecao_fix.py`, `criar_dashcards_316.py`
- `backup_dash316.json`, `backup_13553.json`, `backup_13554.json`, `backup_13556.json`
- `src_*.json` — snapshots dos cards fonte

## Pendências de validação
- Conferir valores KPI vs dashboard Performance
- Conferir projeção vs dash Performance (card 13359)
- Conferir Trimestre vs dash Análise Trimestral (card 13549)
- Validar semanal vs report_mkt do VelasConnect
- Conferir scalars do dia

## Próximo
Seguir para issue do NPS com IA.
