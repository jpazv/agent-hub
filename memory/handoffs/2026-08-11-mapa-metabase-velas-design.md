# Handoff — Mapa do Metabase: Rebuild Velas Connect Design

**Data:** 2026-08-11
**Maquina:** mac-grupovelas
**Projeto:** Metabase Hub (~/Downloads/Metabase-hub/)

## O que foi feito

### 1. Full crawl do Metabase (sessao anterior)
- 256 dashboards crawlados via API (`/api/dashboard` + `/api/dashboard/{id}`)
- Resolucao de modelos: cards que referenciam `card__X` tiveram suas tabelas reais resolvidas
- Catalogo de 330 tabelas reais validado contra `/api/table`
- JSON fonte de verdade salvo em `~/Downloads/Metabase-hub/mapa_metabase.json` (4.8MB)
- Tambem copiado para `$HUB/memory/mapa_metabase.json`

### 2. Pagina HTML interativa — Design Velas Connect
Arquivo: `~/Downloads/Metabase-hub/mapa-metabase.html` (695 KB, dados embarcados)

Design system aplicado:
- Background: #060d1a com dot grid overlay e blur blobs animados (azul/amarelo)
- Sidebar fixa 90px com link de volta ao velas-hub e badge "MAPA"
- Eyebrow "VELASCONNECT" + titulo "Mapa do Metabase"
- Tipografia: Inter (body) + JetBrains Mono (mono/badges)
- Cards com border-radius 18px, box-shadow profundo
- Inputs com border-radius 14px, foco azul com glow
- Tags coloridas por tipo: mv_ (verde), tb_/fat_ (amarelo), dim_ (roxo)

Duas views:
- **Dashboards**: agrupados por categoria semantica (Performance Geral, Trafego Pago, Lead Score, etc.) com colapsamento por grupo
- **Tabelas -> Dashboards**: grid de tabelas, clique expande drill-down mostrando quais dashboards e cards usam aquela tabela

UX fixes aplicados:
- Dashboards no drill-down de tabelas abrem **colapsados** por padrao (classe `collapsed` no `td-dash`)
- Botao "Minimizar" e search bar interna no expanded table detail
- Encoding UTF-8 corrigido (meta charset como primeira linha)

### 3. Workflow n8n
Arquivo: `~/Downloads/Metabase-hub/Metabase Hub - Frontend.json` (817 KB)

16 nodes, 2 rotas:
- **Rota 1** (`/webhook/metabase-hub`): serve HTML shell (27 KB) que faz fetch dos dados via API
- **Rota 2** (`/webhook/metabase-hub-data`): serve o JSON completo

Auth chain (identica nas 2 rotas):
1. Webhook → Extrair Token (header Bearer / query vc_token / cookie vc_token)
2. Sub Verificar JWT (POST para connect.grupovelas.com.br/webhook/sub-verificar-jwt)
3. Validar Acesso (roles: superadmin, bi, admin)
4. If Auth OK → Serve HTML ou JSON / Reject com pagina 401

Token Injector v3 embutido no shell HTML:
- Persiste JWT em cookie + localStorage + sessionStorage
- Intercepta fetch para adicionar Bearer token
- Redireciona para velas-login em 401/403

Credential placeholder: `"id": "CONFIGURE_ME"` — precisa configurar httpHeaderAuth no n8n.

### 4. Configuracao no Hub
- `$HUB/AGENT-HUB.md` tem secao "Metabase Hub — sob demanda" (NAO carrega no boot)
- `$HUB/memory/metabase-boot.md` tem token e referencia rapida do Metabase
- Sync incremental: comparar `updated_at` do `/api/dashboard` com o JSON salvo

## Artefato
URL: https://claude.ai/code/artifact/c37b547a-fc55-4a3e-8c5e-d60dd43e7892
(atualizado com design Velas Connect — nota: Google Fonts bloqueado pelo CSP do artifact, usa fallback system fonts)

## Proximos passos
- Importar o workflow JSON no n8n e configurar a credential httpHeaderAuth
- Testar auth end-to-end via connect.grupovelas.com.br
- Subir o `mapa_metabase.json` como dado estatico ou configurar endpoint que le do arquivo
- Implementar sync incremental (detectar dashboards alterados/criados/excluidos)

## Arquivos relevantes
```
~/Downloads/Metabase-hub/
  mapa-metabase.html          # pagina visual completa (695 KB, dados embarcados)
  mapa_metabase.json           # fonte de verdade JSON (4.8 MB)
  Metabase Hub - Frontend.json # workflow n8n (817 KB)

$HUB/memory/
  metabase-boot.md             # referencia rapida Metabase
  mapa_metabase.json           # copia do JSON
```
