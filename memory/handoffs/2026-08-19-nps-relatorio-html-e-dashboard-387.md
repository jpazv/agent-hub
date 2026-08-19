# Handoff — NPS: relatório HTML Velas + incremento dashboard 387

**Data:** 2026-08-19
**Sessão:** global (Metabase + n8n), máquina do JP
**Relacionado:** handoffs anteriores `2026-08-18-nps-ia-workflow-validado.md`, `2026-08-19-nps-ia-dashboard-relatorio.md`

---

## Contexto geral

Dois frentes ativas, ligadas ao NPS com análise de IA:
1. **Workflow n8n** "NPS - Relatório por Unidade" — front por unidade + geração de relatório formal.
2. **Dashboard Metabase 387** "NPS - Análise IA (Teste)" (coleção 576, pasta Testes) — sendo enxugado em 2 abas operacionais.

O usuário quer, na ordem: (a) mexer nos dados/dashboard primeiro, (b) **depois refazer o workflow n8n do zero** ("vamos refazer o workflow por completo").

---

## PARTE 1 — Workflow n8n (arquivo: `/Users/grupovelas/Downloads/NPS - Relatorio por Unidade.json`)

Estado atual do JSON (26 nodes, íntegro). Fluxos:
- **Front:** `NPS Relatorio - Front` (GET /webhook/nps-relatorio-unidade) → auth (5 nodes) → HTTP interno → `Buscar Unidades Elegiveis` (filtra por `id_interno`) → `Render Front NPS` (página de DETALHE da unidade) → resposta.
- **Gerar:** `NPS Relatorio - Gerar` (GET /webhook/nps-relatorio-gerar?id_interno=X) → auth → HTTP interno → `Buscar Comentarios Unidade` → `Montar Prompt Relatorio` (Gemini JSON) → `OpenRouter — Relatorio` → `Render Relatorio HTML` → `NPS Relatorio - Gerar Resposta` (text/html).

### Decisões/correções aplicadas nesta sessão
- **Google Docs REMOVIDO por completo** (nodes Criar Doc/Inserir/Montar URL/Formatar Resposta). Salvamento agora é **PDF via print do browser** (decisão do usuário).
- **Front virou página de UMA unidade** (recebe `?id_interno=X`, mostra só ela + botão "Gerar Relatório"). Fallback: lista se sem id.
- **Self-heal de auth** nos nodes `Respond - Auth Erro` (unidade + gerar): varre localStorage/sessionStorage por JWT (`eyJ...`), grava cookie `vc_token; Path=/`, recarrega com flag `_vcr=1` (evita loop). Só vai pro velas-login se não achar token. Motivo: navegação direta (Metabase) não manda header; token do usuário fica em localStorage, não em cookie que o servidor lê.
- **iframe breakout** (mesmos nodes + Render): se `window.top!==window.self`, `window.top.location.href=url` — quebra pra fora do iframe. Motivo RAIZ do "cai no hub": **Metabase está embedado (iframe) no connect hub**; ao clicar, a URL abre no iframe (contexto de 3ª parte), cookie/localStorage particionados → auth falha → login → hub. Breakout resolve.
- **Relatório = HTML bonito no design system Velas** (skill `frontend-velas`): fundo preto, blobs animados, glassmorphism, Inter, azul #0056a4, logo Velas, botão "Baixar PDF" (window.print + CSS @media print que preserva o dark). Gemini retorna **JSON estruturado** (narrativa por categoria); os **números vêm das stats calculadas no SQL** (não inventados). Testado com dados fake via Node — renderiza certo (resumo executivo, tiles NPS, barra de distribuição, grid de sentimento, blocos Positivos/Sugestões/Negativos com cards ID+Nota, por pesquisa Tratamento/Avaliação).
- Botão "Gerar" no front abre **nova aba** (window.open no gesto do clique), loading Velas, fetch → escreve o HTML pronto.

### Credenciais no workflow (o usuário configura no n8n após import)
- OpenRouter no node `OpenRouter — Relatorio` (key sk-or-v1-REDACTED)
- Header - Velas (id oUutVo70r2AR3lsh) nos HTTP Request internos + Sub-Verificar-JWT
- Postgres - BD Velas (id zSuxDy2EHKaKRRql) nos nodes Postgres

### IMPORTANTE sobre o workflow
- O usuário pediu para **REFAZER o workflow do zero** depois do dashboard. O JSON atual pode servir de base, mas a intenção é reconstruir.
- Interno webhooks NÃO têm auth (proteção é server-to-server via Header-Velas).
- Ao reimportar, garantir que só UMA versão fica ATIVA (import cria duplicado; webhook path duplicado ativo quebra).

---

## PARTE 2 — Dashboard 387 (Metabase)

### Conhecimento capturado (salvo em memory `reference_nps_data_model.md`)
- Tabela `public.nps` (db 2, table 181): 3803 respostas, 1830 com `ia_analise` (≈ todas comentadas). Colunas: id (text "X - Marca"), nota, data, comentario, status ('Tratamento' 2117 / 'Avaliação' 1683), id_interno (→ dim_unidades.id), campos pesquisa, ia_analise jsonb.
- **Marca** via `SPLIT_PART(id,' - ',2)` → valores reais: **'ITC' (2263)** e **'Trata' (1540)**.
- **NPS oficial (métrica 2104)** = (promotor−detrator)/respostas, sobre campo `Cálculo` do modelo 2098: `if nota>=9 Promotor, nota>=7 Neutro, else Detrator`. Base COMPLETA (3803).
- **DIVERGÊNCIA:** NPS do dash IA (card 13597) e SQL do n8n filtram `ia_analise IS NOT NULL` (1830) → NPS não bate com produção. Ao mostrar NPS na aba IA, usar base completa OU rotular "dos analisados".
- `ia_analise` v3: sentimento (Positivo 742/Sugestão 612/Neutro 256/Negativo 214), temperatura (1 Baixa 1111/2 Média 607/3 Alta 94/4 Crítica 18), intuito (Elogio/Sugestão/Reclamação/Risco de cancelamento 8/...), areas (13 categorias), elogio/dor, confianca.
- Dashboards: **59 "NPS"** produção (col 12, MBQL + métricas 2100-2104, abas Tratamento/Avaliação/Pesquisa/Evolução); **299 "NPS - Gestão"** espelho; **387** teste IA (col 576, SQL nativo).

### Decisão do usuário sobre o incremento
- **Mexer SÓ no 387** (pasta Testes), não tocar produção.
- **2 abas enxutas**, regra dos 5 segundos, visões operacionais **divididas por marca (ITC × Trata)**.
- **Remover o resto** — ficar só com as 2 abas; os outros ~9 cards saem do dashboard (continuam existindo no Metabase).

### Layout planejado das 2 abas
- **Aba 1 "Alertas por Marca":** card `Alertas por Marca (Alta+Crítica)` [bar] + `Lista de Alertas` [table].
- **Aba 2 "Unidades & Relatórios":** card `NPS por Marca` [bar] + `Unidades Elegíveis` [table 13608, click→front n8n].

### FEITO nesta sessão
- Criados 3 cards NOVOS como **dashboard-internal** (`dashboard_id: 387`, NÃO collection_id — criar com collection_id=null dá 403 root; JP não tem perm root):
  - **13629** — Alertas por Marca (Alta + Crítica) [bar, stacked, Crítica vermelho/Alta âmbar]
  - **13630** — Lista de Alertas (Temp. Alta e Crítica) [table]
  - **13631** — NPS por Marca [bar]
- SQLs validadas via /api/dataset (dry-run OK). Resultados: Alertas ITC 56+10, Trata 35+8; NPS Trata 77, ITC 71; 25 unidades elegíveis.
- SQLs salvas em `/tmp/sql/*.sql`; ids em `/tmp/mb/ids.json`.

---

## PENDÊNCIAS (próximos passos concretos)

### Dashboard 387 (continuar daqui)
1. **Atualizar card 13608** (Unidades Elegíveis) para incluir coluna `du.id AS "id_interno"` (SQL pronta em `/tmp/sql/unidades.sql`) — necessária pro click→URL do relatório. Depois setar `click_behavior` (linkType url, template `https://connect.grupovelas.com.br/webhook/nps-relatorio-unidade?id_interno={{id_interno}}`) na coluna "Unidade" e esconder a coluna id_interno via `table.columns`.
2. **PUT /api/dashboard/387** montando as 2 abas + dashcards (usar tab ids negativos -1/-2 para novos; dashcards negativos). PUT dashboard EXIGE `tabs` + `dashcards` juntos — omitir um apaga o outro. Preservar layout. Cards: aba1 = [13629, 13630], aba2 = [13631, 13608]. Remover os demais (13597,13598,13599,13600,13601,13602,13603,13604,13605,13606,13607) do dashboard.
3. Verificar visual final (abrir 387, conferir 5-seg por marca).

### Workflow n8n
4. **Refazer o workflow do zero** (pedido do usuário) — usar o JSON atual como referência. Alinhar a SQL do gerar com o padrão do 13608 (marca via SPLIT_PART, join du.id=n.id_interno).
5. Testar ponta a ponta: clique no 387 → front da unidade (breakout+self-heal) → Gerar → relatório HTML Velas em nova aba → Baixar PDF.

---

## Acesso Metabase
- Base: https://metabase.grupovelas.com.br ; db 2
- Token em `/tmp/mbt.txt` (renovar via /api/session se 401). **Cloudflare bloqueia python-urllib (erro 1010) — usar curl** para todas as chamadas.
- Login: jp@grupovelas.com.br / Lara1212@@
- Regra: SÓ SELECT. Cards de dashboard: criar com `dashboard_id` (não collection_id null → 403 root).

## Arquivos tocados
- EDITADO: `/Users/grupovelas/Downloads/NPS - Relatorio por Unidade.json` (workflow n8n)
- CRIADO: memory `reference_nps_data_model.md` + índice `MEMORY.md` atualizado
- CRIADO no Metabase: cards 13629, 13630, 13631 (internos ao dash 387)
- SQLs/payloads temporários em `/tmp/sql/`, `/tmp/mb/`
