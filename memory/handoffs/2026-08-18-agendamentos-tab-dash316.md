# Handoff — Aba Agendamentos no Tráfego Pago (dash 316)

Data: 2026-08-18
Sessão: Claude Code Desktop (mac-grupovelas)
Projeto: Metabase dashboards — Grupo Velas

## Contexto

Construindo a aba "Agendamentos" (tab 943) no dashboard Tráfego Pago (dash 316, produção) no Metabase.
Também existe dash de teste (385, tab não relevante agora — foco é produção).

**Session token Metabase**: `35cc2098-9ca6-4a1e-8388-22ec60a12116`
**Base URL**: `https://metabase.grupovelas.com.br`

## Cards na tab 943 (Agendamentos) — estado atual

| dashcard | card_id | nome | display | posição |
|----------|---------|------|---------|---------|
| 19935 | None (markdown) | — | — | row=42 |
| 19936 | 13579 | Agendamentos — Leads | scalar | row=16 col=0 w=12 |
| 19937 | 13580 | Agendamentos — Agend. | scalar | row=16 col=12 w=12 |
| 19938 | 13578 | Agendamentos — Diário | combo | row=20 w=24 |
| 19939 | 13581 | Agendamentos — Projeção | table | row=28 w=24 |
| 19940 | 13577 | Agendamentos — Semanal | table | row=8 w=24 |
| 19941 | 13576 | Agendamentos — Alerta KPI | table | row=0 w=24 |
| (novos) | 13585 | Invest x Agend. | combo | row=34 col=0 w=12 |
| (novos) | 13586 | CPAg | table | row=34 col=12 w=12 |

Card 13584 (Financeiro Diário — tabela Dia/Invest/CPL/CPA) foi removido da tab, substituído pelos gráficos 13585+13586.

## Parâmetros do dashboard 316

- Unidades: `59d9c347`
- Data: `99fbb78f`
- Marca: `2ebac36a`

## Field IDs (tabela mv_mkt_outcomes_diario, table 487)

dia=8388, marca=8385, unidade=8397, socio=8391, boutique=8396, campanha=8395

## Pendências URGENTES (continuar na próxima sessão)

### 1. CPL > R$35 vermelho na Projeção (card 13581)
- Formatação condicional já foi aplicada via API (`operator: ">"`, `value: 35`, `color: "#C23B22"`)
- **NÃO está aparecendo no dashboard** apesar de estar salva
- CPL é `type/Decimal` na query — deveria funcionar
- Havia duplicatas na formatação (já limpas no script `fix_cpl_e_mover.py` mas não rodado)
- **Rodar**: `python3 /private/tmp/claude-501/.../scratchpad/fix_cpl_e_mover.py`

### 2. Metas nos scalars (13579/13580) com valores errados
- Usuário reportou: "meta ta beeeem diferente dos outros"
- SQL usa `SUM(meta_leads)` e `SUM(meta_agendamentos)` para o mês filtrado
- **Precisa cruzar** com aba Tráfego (cards 11268 proj leads, 11276 proj agend) e validar
- Formato atual: `Real / Saldo / Meta` — sinal corrigido (+ se passou, - se falta)

### 3. Semanal report-style 8 semanas (card 13577)
- SQL reescrito em `semanal_report_8sem.sql` — report com 4 sub-linhas (Valor, vs faixa anterior, Marca, Veredito)
- 8 colunas de semanas (s1-s8) com datas reais via viz_settings column_title
- Baseado em `date_trunc('week', ...)` — últimas 8 semanas ISO (seg-dom)
- **Aplicado via `apply_all_changes.py` mas precisa validar** se rodou corretamente

### 4. Novo scalar: Agend. Esperado vs Proj. Esperado
- Esperado = `quente*0.2582 + pré_quente*0.1113 + morno*0.0351 + frio*0.0097` (acumulado até hoje)
- Proj. Esperado = projeção desse esperado por dias úteis para o mês todo
- SQL pronto em `apply_all_changes.py` mas o POST falhou (card não foi criado)
- **Problema**: criar card via POST gera item solto na collection
- Solução: criar o card E imediatamente adicionar ao dashboard via PUT no dash inteiro

### 5. Cards soltos em collections
- Collection 569: ~10 cards de teste [Agend] — precisam ser deletados ou arquivados
- Cards 13584 e 13586 estão na collection 1 (raiz) — mover para collection 12
- Script `fix_cpl_e_mover.py` move 13584 e 13586 → collection 12 (não rodado ainda)

### 6. Validação cruzada de números
- Usuário pediu: "checar numero por numero com outros dash já validados e testar os filtros, batendo unidade por unidade e kpi por kpi"
- Comparar com aba Tráfego (tab 939): cards 11268 (Proj Leads), 11276 (Proj Agend), 11279 (%CVS)
- Testar filtro de unidade em cada card da tab 943

## Regras CRÍTICAS

1. **NUNCA criar cards soltos** — só UPDATE (PUT) em cards existentes. Se precisar de card novo, criar E adicionar ao dash no mesmo script
2. **NUNCA ALTER/CREATE/DELETE/UPDATE no banco** — apenas SELECT
3. **Sempre dar o comando pro usuário rodar** — não rodar diretamente

## Arquivos de trabalho

Todos em: `/private/tmp/claude-501/-Users-grupovelas-Documents/8bfc8333-7b03-40ea-ab30-894feba21cfa/scratchpad/`

- `semanal_report_8sem.sql` — SQL do semanal report 8 semanas
- `semanal_pivot.sql` — versão anterior (3 linhas simplificada, descartada)
- `apply_all_changes.py` — script principal (aplica semanal, scalars, projeção CPL, novo card)
- `fix_cpl_e_mover.py` — fix CPL vermelho + mover cards soltos (NÃO RODADO)
- `grafico_invest_agend.sql` — SQL do gráfico invest x agend (card 13585)
- `grafico_cpa.sql` — SQL do gráfico CPAg (card 13586)
- `projecao.sql`, `kpi.sql`, `diario.sql` — SQLs de referência

## Próximos passos (ordem sugerida)

1. Rodar `fix_cpl_e_mover.py` e verificar se CPL vermelho aparece
2. Investigar por que metas nos scalars estão diferentes — comparar queries
3. Criar card Esperado vs Proj. Esperado e adicionar ao dash
4. Validação cruzada unidade por unidade
5. Limpar cards de teste na collection 569
