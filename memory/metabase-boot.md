# Metabase — contexto de boot

Carregar em toda sessão que envolva Metabase, dashboards ou BI.

## Acesso

- **Base URL:** `https://metabase.grupovelas.com.br`
- **API docs:** `https://metabase.grupovelas.com.br/api/docs`
- **Header:** `X-Metabase-Session: <token>`
- **Regra:** somente SELECT — proibido ALTER/CREATE/DELETE/UPDATE no banco
- **NUNCA** sugerir nem executar alterações de schema (ALTER, CREATE TABLE, ADD COLUMN, etc.)
- **Eficiência de tokens:** agrupar todas as alterações de cards/dashboards num único script Python. Suprimir output de resposta da API (só status code). Evitar GET antes de PUT quando já se sabe o payload. Nunca imprimir JSON inteiro de resposta no terminal.

### Como obter token

```bash
curl -s https://metabase.grupovelas.com.br/api/session \
  -H 'Content-Type: application/json' \
  -d '{"username":"jpazevedomoreiraa@grupovelas.com.br","password":"PEDIR_AO_JP"}' | jq -r .id
```

O token dura dias. Verificar validade:

```bash
curl -s -o /dev/null -w '%{http_code}' \
  https://metabase.grupovelas.com.br/api/user/current \
  -H "X-Metabase-Session: TOKEN"
```

200 = válido, 401 = expirado.

## Dashboards-chave

| Dashboard | ID | Descrição |
|---|---|---|
| RPD master (Dados Gerais) | 10 | Dashboard de referência, collection 13 |
| LSV (Lead Score Visualizer) | 369 | 22 cards, 2 tabelas físicas |
| Chapecó | 270 | Performance de sócio, 79 dashcards, 5 abas |
| Tempo de Resposta - Tatuapé | 377 | Clonado do Brooklin |

## Dashboards de sócios (19 total)

| Dash ID | Sócio | Model ID |
|---|---|---|
| 343 | Alessandra Saraiva | 12509 |
| 341 | Alexandre Almeida | 8723 |
| 344 | Daniel Luis | 12510 |
| 345 | Juliana Ramiro | 12511 |
| 346 | Márcio Pimentel | 12512 |
| 347 | Maria Ferreira | 12513 |
| 271 | Fernando/Tariane | 8856 |
| 348 | Híkaro Costa | 12514 |
| 274 | Mariana Martins | 9005 |
| 349 | Pietro Daniel | 12515 |
| 350 | Vanderson Duarte | 12516 |
| 351 | Cleyton França | 12517 |
| 352 | Luciano Nóbrega | 12518 |
| 353 | Mário Andrade | 12519 |
| 84 | Mônica Peixoto | 2724 |
| 103 | Carolina Carvalho | 3389 |
| 273 | Jhonatha Oliveira | 9004 |
| 277 | Pedro Aquino | 9193 |
| 279 | Pedro Jettar | 9262 |

## Filtros padrão (9 filtros do dash 10, replicados nos de sócios)

| ID | Nome | Slug | Tipo |
|---|---|---|---|
| ab748570 | Canal | canal | string/= |
| 9646d786 | Marca | marca | string/= |
| 3457d8b | Unidade | unidade | string/= |
| ff97c004 | Data | data | date/all-options |
| 10c7e05 | Localização | localização | string/= |
| 91b7369 | Região | região | string/= |
| 8b102015 | Ano | ano | date/all-options |
| c6e74a17 | Estorno | estorno | string/= |
| 84ea6960 | Agrupamento de tempo | agrupamento_de_tempo | temporal-unit |

## Modelos base dos cards

| Model (card__) | Cards | Conteúdo |
|---|---|---|
| 2457 | 30 | Principal, todos os campos |
| 51 | 14 | Vendas/serviços |
| 2141 | 6 | Agendamentos |
| 1816 | 6 | Clientes |
| 2228 | 4 | Leads |
| 2131 | 4 | Metas |
| 2158 | 2 | Sessões |
| 2231 | 1 | Estoque |
| 2091 | 1 | Profissionais |

## LSV — tabelas físicas

**`mv_chatwoot_conversa_metricas`** — cw_id_tb_leads, lead_data, unidade, marca,
tipo_campanha, marcou_agendamento, contact_nome, contact_telefone

**`lead_score_output`** — cw_id_tb_leads, lead_score, scored_at,
qualidade_atendimento, intencao_de_agendar, espelhamento_lexico,
densidade_da_conversa, probabilidade_de_vida, trilha_evidencias

**`mv_hibrida_unidade_propria`** (separada) — data, unidade, marca, agend, leads_sec

## Pendências ativas

- Gráfico de faixas de temperatura vs agendamentos no LSV (query em scratchpad/lsv_regua.sql)
- Modelo 1815 sem permissão — trava 2 cards do dash 270
- Varrer 18 dashboards de sócios por filtros clonados errados
- Atualizar estudo de eficiência para régua de 4 faixas por marca
- Mapear parameter_mappings nos cards dos dashboards de sócios

## Comandos úteis

```bash
# Listar cards de um dashboard
curl -s "https://metabase.grupovelas.com.br/api/dashboard/ID" \
  -H "X-Metabase-Session: TOKEN" | jq '.dashcards[] | {id, card_id: .card.id, name: .card.name}'

# Ver query de um card
curl -s "https://metabase.grupovelas.com.br/api/card/ID" \
  -H "X-Metabase-Session: TOKEN" | jq '.dataset_query'

# Executar query de um card
curl -s -X POST "https://metabase.grupovelas.com.br/api/card/ID/query" \
  -H "X-Metabase-Session: TOKEN" | jq '.data.rows[:5]'
```
