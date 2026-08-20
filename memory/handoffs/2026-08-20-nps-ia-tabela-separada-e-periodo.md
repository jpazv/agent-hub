# Handoff — NPS IA: tabela separada nps_ia, seletor de período, login por popup

**Data:** 2026-08-20
**Sessão:** global (n8n workflows + artefato), máquina do JP
**Relacionado:** `2026-08-19-nps-relatorio-html-e-dashboard-387.md`

---

## Contexto

Sessão com o JP e input do Ernandes via WhatsApp. Três frentes: arquitetura de dados (migração nps_ia), UX do relatório (período + auth), e artefato de custos.

## O que foi feito

### 1. Migração para tabela `nps_ia` (proposta do Ernandes)

**Decisão arquitetural:** separar dados de IA da tabela `nps` principal.

- Nova tabela `nps_ia` com `hash` (PK, CHAR(32)), `nps_id` (FK), `analise` (JSONB), `criado_em`
- Hash gerado no fluxo de **ingestão** do NPS (responsabilidade do Ernandes), não calculado na hora da query
- JOIN direto: `nps_ia.hash = nps.hash` — sem `md5()` em runtime
- DDL em `~/Downloads/nps_ia_ddl.sql` com pré-requisito documentado (Ernandes cria `nps.hash` primeiro)
- Migração inclusa: copia `nps.ia_analise` existente para `nps_ia.analise`

**Arquivos alterados:**

| Arquivo | Nodes alterados | Mudança |
|---|---|---|
| `NPS - Extração IA.json` | Buscar comentários, Normalizar saída, Gravar ia_analise | `WHERE ia_analise IS NULL` → `LEFT JOIN nps_ia ... WHERE ia.hash IS NULL`; UPDATE nps → UPSERT nps_ia |
| `NPS - Relatório por Unidade.json` | Buscar Unidades Elegíveis, Buscar Comentários Unidade | `n.ia_analise` → `LEFT JOIN nps_ia ia ON ia.hash = n.hash` + alias `ia.analise AS ia_analise` |

**Ordem de deploy:**
1. Ernandes cria coluna `nps.hash` e popula com `md5(btrim(comentario))`
2. Roda `nps_ia_ddl.sql` (cria tabela + migra dados existentes)
3. Importa os dois JSONs no n8n
4. Testa extração (deve encontrar 0 novos se migração rodou)

### 2. Seletor de período no relatório

**Node "Render Front NPS" — `detailPage()`:**
- Botão único "Gerar Relatório" substituído por 4 cards de período: 30 dias, 90 dias, 180 dias, Todo o período
- Seleção visual (borda + fundo azul no card ativo)
- Parâmetro `&dias=` enviado ao endpoint de geração

**Node "Buscar Comentarios Unidade" — SQL:**
- Filtro de data adicionado: `AND (0 = dias OR n.data >= NOW() - (dias || ' days')::interval)`

**Node "Montar Prompt Relatorio" — título:**
- Título dinâmico: "ANÁLISE DA NPS UNIDADE — Últimos 30 dias" (ou 90/180/Todo o período)

**URL para Metabase** (inalterada): `https://connect.grupovelas.com.br/webhook/nps-relatorio-unidade?id_interno={{id_interno}}`

### 3. Login por popup (fix de UX)

**Problema:** token expirado → redirect pra `velas-login?next=<url>` → após login, usuário ficava preso no hub sem voltar pro relatório.

**Solução:** substituí o redirect por **popup** de login em 3 pontos:
- 2 nodes "Respond - Auth Erro" (rotas nps-relatorio-unidade e nps-relatorio-gerar)
- INJECTOR no Code node "Render Front NPS"

**Fluxo novo:**
1. Token expirado → mostra card "Sessão expirada" com botão "Fazer Login"
2. Clique abre popup 480×640 com `velas-login`
3. Página original fica aberta, poll localStorage a cada 600ms
4. Token detectado → "Login detectado! Recarregando…" → `location.reload()`
5. Usuário nunca sai da URL do relatório

### 4. Artefato de custos de token

- Refeito como lauda única, tema escuro fixo, sem tabela por clínica
- 3 números-chave no topo: $0.07/mês total, $0.00005/comentário, $0.003/relatório
- Comparativo visual antes/depois: $57.60 → $0.07 (redução 99.9%)
- Download via `downloads.save()` (API de artifacts) em vez de `window.print()`
- URL: https://claude.ai/code/artifact/db5af575-8109-419d-bc58-7df10c0e44c4

## Pendências

- [ ] **Ernandes**: criar coluna `nps.hash`, popular, e rodar `nps_ia_ddl.sql`
- [ ] **JP**: importar os dois JSONs atualizados no n8n após Ernandes confirmar
- [ ] **Seletor de período**: JP pediu para mostrar contagem de comentários ao selecionar período + botão de confirmar (não implementado ainda — interrompido pelo input do Ernandes)
- [ ] **Cron extração**: JP disse "eu mesmo coloco" — verificar se já colocou 2x/dia
- [ ] **Relatórios texto**: ITC SBC e Trata Jundiaí (de sessão anterior, ainda pendente)

## Arquivos tocados

- `~/Downloads/NPS - Extração IA.json`
- `~/Downloads/NPS - Relatório por Unidade.json`
- `~/Downloads/nps_ia_ddl.sql`
- Artefato token-costs (republicado 3x na sessão)

## Decisões tomadas

1. **Hash na ingestão, não na query** — proposta Ernandes, aceita. Workflows usam `n.hash` direto
2. **JSONB mantido** — `nps_ia.analise` continua JSONB (não desnormalizado em colunas)
3. **Login popup vs redirect** — popup mantém usuário na URL original
4. **Artefato single-page dark** — JP pediu lauda única sem muitos números, tema escuro, download direto
