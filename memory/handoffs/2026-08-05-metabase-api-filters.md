# Metabase API - Filtros de Dashboards de Sócios

**Data:** 2026-08-05  
**Status:** Em andamento

## Contexto

Atualizando filtros dos dashboards de Performance de sócios (P0-P3) para ficarem iguais ao dashboard 10 (RPD master), exceto filtro Sócio.

## Token de Sessão

```
X-Metabase-Session: a8fc6a42-fa5f-4107-946f-b62ccff2dbf0
```

**Base URL:** `https://metabase.grupovelas.com.br`

## Filtros Configurados (9 total)

| ID | Nome | Slug | Tipo | Source |
|---|---|---|---|---|
| ab748570 | Canal | canal | string/= | Modelo Segmentação |
| 9646d786 | Marca | marca | string/= | Modelo Segmentação |
| 3457d8b | Unidade | unidade | string/= | Modelo Segmentação |
| ff97c004 | Data | data | date/all-options | default: thismonth |
| 10c7e05 | Localização | localização | string/= | Modelo Segmentação (uf) |
| 91b7369 | Região | região | string/= | Modelo Segmentação |
| 8b102015 | Ano | ano | date/all-options | default: thisyear |
| c6e74a17 | Estorno | estorno | string/= | static-list (sim/não) |
| 84ea6960 | Agrupamento de tempo | agrupamento_de_tempo | temporal-unit | default: day |

## Progresso

### Feito

1. ✅ Filtros globais aplicados em 19 dashboards de sócios
2. ✅ Cada dashboard usa seu próprio Modelo de Segmentação

### Pendente

1. ❌ Mapear filtros nos cards (parameter_mappings)
   - PUT em `/api/dashboard/{id}/cards` requer: id, size_x, size_y, row, col, card_id, dashboard_tab_id, parameter_mappings

## Dashboards e Modelos

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

## Modelos Base (source-table dos cards)

Os cards usam estes modelos como fonte:
- card__2457 (30 cards) - Modelo principal com todos os campos
- card__51 (14 cards) - Vendas/serviços
- card__2141 (6 cards) - Agendamentos
- card__1816 (6 cards) - Clientes
- card__2228 (4 cards) - Leads
- card__2131 (4 cards) - Metas
- card__2158 (2 cards) - Sessões
- card__2231 (1 card) - Estoque
- card__2091 (1 card) - Profissionais

## Campos disponíveis por modelo

**Model 2457:** data, unidade, marca, socio, canal, regiao, uf, estorno, ...
**Model 51:** data, unidade, marca, socio, canal, regiao, uf, estorno, ...
**Model 2141:** data, unidade, marca, socio, canal, regiao, uf, ...
**Model 2131:** data, unidade, marca, socio, canal (SEM regiao, uf, estorno)

## Próximo Passo

Atualizar `parameter_mappings` de cada dashcard:

```bash
# Buscar dashcards
curl -s "https://metabase.grupovelas.com.br/api/dashboard/343" \
  -H "X-Metabase-Session: a8fc6a42-fa5f-4107-946f-b62ccff2dbf0" | jq '.dashcards[] | {id, size_x, size_y, row, col, card_id: .card.id, dashboard_tab_id}'

# PUT com todos os campos obrigatórios
curl -X PUT "https://metabase.grupovelas.com.br/api/dashboard/343/cards" \
  -H "X-Metabase-Session: a8fc6a42-fa5f-4107-946f-b62ccff2dbf0" \
  -H "Content-Type: application/json" \
  -d '{"cards": [{
    "id": DASHCARD_ID,
    "size_x": X,
    "size_y": Y,
    "row": ROW,
    "col": COL,
    "card_id": CARD_ID,
    "dashboard_tab_id": TAB_ID,
    "parameter_mappings": [
      {"parameter_id": "ab748570", "card_id": CARD_ID, "target": ["dimension", ["field", "canal", {"base-type": "type/Text"}], {"stage-number": 0}]},
      ...
    ]
  }]}'
```

## Referências

- Dashboard master: `/dashboard/10`
- Collection sócios: `/collection/180`
- Doc API: `https://metabase.grupovelas.com.br/api/docs`
