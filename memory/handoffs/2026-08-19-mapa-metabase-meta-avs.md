# Handoff — Mapa Metabase + %Meta Avs

**Data:** 2026-08-19  
**Sessão:** Claude Opus  
**Status:** EM PROGRESSO

---

## Contexto geral

Duas frentes nesta sessão: (1) adicionar card %Meta Avs ao dashboard 10 e (2) evoluir o mapa_metabase.html.

## %Meta Avs — card 13596

### Situação
- Card 13596 criado com SQL correto (projeção av_presente / meta avs)
- **Adicionado ao dashboard 10, aba RPD (tab_id=5)** via PUT com sucesso (HTTP 200)
- Posicionado em row=100 (fundo da aba) — usuário precisa arrastar para posição correta e substituir o card antigo (11446)

### SQL do card 13596
```sql
WITH filtrado AS (SELECT * FROM public.mv_hibrida_unidade_propria WHERE 1=1 [[AND {{data}}]] [[AND {{canal}}]] [[AND {{marca}}]] [[AND {{socio}}]] [[AND {{unidade}}]]),
escopo AS (SELECT DISTINCT date_trunc('month', data) AS mes, id_interno FROM filtrado),
mes_cheio AS (SELECT * FROM public.mv_hibrida_unidade_propria WHERE date_trunc('month', data) IN (SELECT DISTINCT mes FROM escopo) [[AND {{canal}}]] [[AND {{marca}}]] [[AND {{socio}}]] [[AND {{unidade}}]]),
projecao AS (SELECT (CAST(SUM(CASE WHEN mes_cheio.data < CURRENT_DATE THEN mes_cheio.av_presente ELSE 0.0 END) AS DOUBLE PRECISION) / NULLIF(CAST(COUNT(DISTINCT CASE WHEN mes_cheio.dia_util_ate_hoje = 1 THEN CAST(mes_cheio.data AS date) END) AS DOUBLE PRECISION), 0.0)) * COUNT(DISTINCT CASE WHEN mes_cheio.dia_util = 1 THEN CAST(mes_cheio.data AS date) END) AS valor FROM mes_cheio),
meta AS (SELECT SUM(mb_metas_proprias.avs) AS valor FROM mb_metas_proprias JOIN escopo ON mb_metas_proprias.data_competencia = escopo.mes AND mb_metas_proprias.id_interno = escopo.id_interno LEFT JOIN log_unidades ON log_unidades.id = mb_metas_proprias.log_id WHERE log_unidades.status = 'Ativa' AND log_unidades.tipo = 'Própria' AND log_unidades.canal <> 'Matriz')
SELECT CAST(projecao.valor AS DOUBLE PRECISION) / NULLIF(CAST(meta.valor AS DOUBLE PRECISION), 0.0) AS "%Meta Avs" FROM projecao, meta;
```

### Template-tags
- data=e85e62da, canal=c7d2d14c, marca=2c69baf3, socio=4288aca4, unidade=4f15f237

### Parameter mappings no dashcard
- ff97c004 → data, ab748570 → canal, 9646d786 → marca, 8dc354c1 → socio, 3457d8b → unidade

### Validação
- Sem filtros: projeção=1692, meta=1830 → **92.5% ✅**
- Com filtro sócio válido (ex: "P0 - Alessandra"): funciona
- Card antigo 11446 ("%Meta Faturamento - Modificado") dava nulo porque template-tags não estavam mapeados aos parâmetros do dashboard

### Pendência
- Usuário precisa abrir dashboard 10 → aba RPD → rolar até embaixo → arrastar card 13596 para posição correta → remover card antigo 11446 da posição

## Mapa Metabase (mapa_metabase.html)

### O que está pronto
- Landing com dashboards recentes + autor das alterações
- Tasks GitHub (issues com keywords BI)
- Catálogo de tabelas
- Distribuição por collection
- Script mb_sync.py (~1240 linhas) gera HTML + slim JSON + boot MD
- Script mb_health.py (~280 linhas): `--days 7`, `--all`, `--dash`, `--compare`, `--dry-run`

### Health check (mb_health.py) — resultados
- Full scan: 260 dashboards, 7887 OK, 21 empty, **33 broken**
- Broken: 15 timeouts (dashboards antigos), 10 column missing, 7 inactive tables, 1 metadata error
- **Dashboards de produção (10, 316, 369, sócios): 100% healthy**
- Consistency: 18 sócio clones vs dash 10 → **0 divergências**, 233 valores conferidos

### Pendências do mapa
1. **Integrar health.json no HTML** — painel mostrando cards quebrados e resultados do compare
2. **Audio upload** — seção para upload de áudio de reunião e extração de tarefas Metabase (discutido, não iniciado)
3. **Hosting no VelasConnect em /bi-hub** (futuro, usuário pediu pra não focar ainda)

## Arquivos relevantes
- `/Users/grupovelas/dev/agent-hub/memory/scripts/mb_sync.py`
- `/Users/grupovelas/dev/agent-hub/memory/scripts/mb_health.py`
- `/Users/grupovelas/dev/agent-hub/memory/health.json`
- `/Users/grupovelas/dev/agent-hub/memory/mapa_metabase.html`
- `/Users/grupovelas/dev/agent-hub/memory/mapa_metabase_slim.json`
- `/Users/grupovelas/dev/agent-hub/memory/metabase-boot.md`

## Próximo passo
Integrar health.json na landing do mapa_metabase.html — mostrar painel de saúde dos dashboards e resultados de consistência.
