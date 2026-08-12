---
data: 2026-08-11
maquina: mac-grupovelas
projeto: Hub / Metabase API
status: procedimento validado e testado em produção
---

# Como criar abas e dashcards no Metabase via API

## Conceito fundamental

Para adicionar uma aba e/ou dashcards a um dashboard existente, **sempre usar PUT no dashboard inteiro** enviando `tabs` + `dashcards` juntos. Enviar `dashcards` sem `tabs` (ou vice-versa) causa perda de dados.

## Token e base

```bash
T="<metabase-session-token>"
B="https://metabase.grupovelas.com.br"
```

## Passo 1 — Ler o estado atual do dashboard

```bash
curl -s "$B/api/dashboard/{DASH_ID}" -H "X-Metabase-Session: $T"
```

Guardar: `tabs`, `dashcards`, `parameters`.

## Passo 2 — Criar os cards (questions) antes

Cada card é criado individualmente via `POST /api/card`:

```bash
curl -s -X POST "$B/api/card" \
  -H "X-Metabase-Session: $T" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nome do Card",
    "dataset_query": {
      "database": 2,
      "type": "native",
      "native": {
        "query": "SELECT ...",
        "template-tags": {}
      }
    },
    "display": "table",
    "visualization_settings": {},
    "collection_id": 569
  }'
```

- `collection_id: 569` = coleção pessoal do JP (tem permissão de escrita)
- `collection_id: null` ou `collection_id: root` = **vai dar 403**
- `display`: "table", "line", "bar", "scatter", "number", etc.
- Guardar o `id` retornado — será usado no dashcard

### Template-tags para filtros

Se o card precisa receber filtros do dashboard, declarar `template-tags`:

```json
{
  "template-tags": {
    "data": {
      "id": "data", "name": "data", "display-name": "Data",
      "type": "dimension",
      "dimension": ["field", FIELD_ID, null],
      "widget-type": "date/all-options"
    },
    "unidade": {
      "id": "unidade", "name": "unidade", "display-name": "Unidade",
      "type": "dimension",
      "dimension": ["field", FIELD_ID, null],
      "widget-type": "string/="
    }
  }
}
```

**CUIDADO:** o `FIELD_ID` deve ser da tabela usada no SQL do card. IDs errados causam `missing FROM-clause entry` no Metabase.

Para descobrir field IDs:

```bash
curl -s "$B/api/table/{TABLE_ID}/fields" -H "X-Metabase-Session: $T"
```

Tables conhecidas:
- `mv_mkt_outcomes_diario` = table 487
- `mv_mkt_criativos_ad_dia` = buscar ID
- `mv_chatwoot_conversa_metricas` = table 383

## Passo 3 — Montar o PUT do dashboard

O payload do PUT **deve conter tudo**: tabs existentes + novas, dashcards existentes + novos.

### Estrutura do payload

```json
{
  "tabs": [
    {"id": 734, "name": "Tráfego"},
    {"id": 740, "name": "Financeiro"},
    {"id": -1, "name": "Nova Aba"}
  ],
  "dashcards": [
    // TODOS os dashcards existentes (copiar do GET)
    {
      "id": 12345,
      "card_id": 11265,
      "row": 0, "col": 0,
      "size_x": 18, "size_y": 8,
      "dashboard_tab_id": 734,
      "parameter_mappings": [...],
      "visualization_settings": {...},
      "series": [...]
    },
    // Novos dashcards na nova aba
    {
      "id": -1,
      "card_id": 13468,
      "row": 0, "col": 0,
      "size_x": 9, "size_y": 8,
      "dashboard_tab_id": -1,
      "parameter_mappings": [],
      "visualization_settings": {},
      "series": []
    },
    {
      "id": -2,
      "card_id": 13469,
      "row": 0, "col": 9,
      "size_x": 9, "size_y": 8,
      "dashboard_tab_id": -1,
      "parameter_mappings": [],
      "visualization_settings": {},
      "series": []
    }
  ]
}
```

### Regras dos IDs

- **Aba nova:** `id: -1` no tab, `dashboard_tab_id: -1` nos dashcards
- **Dashcard novo:** `id: -1`, `-2`, `-3`, etc. (IDs negativos únicos)
- **Dashcards existentes:** manter o `id` original do GET
- **Tabs existentes:** manter o `id` original do GET

### Enviar o PUT

```bash
curl -s -X PUT "$B/api/dashboard/{DASH_ID}" \
  -H "X-Metabase-Session: $T" \
  -H "Content-Type: application/json" \
  -d '{"tabs": [...], "dashcards": [...]}'
```

## Passo 4 — Adicionar texto explicativo (card de texto)

Cards de texto não têm `card_id` — são virtuais:

```json
{
  "id": -10,
  "card_id": null,
  "row": 0, "col": 0,
  "size_x": 18, "size_y": 4,
  "dashboard_tab_id": -1,
  "parameter_mappings": [],
  "visualization_settings": {
    "virtual_card": {
      "name": null,
      "display": "text",
      "visualization_settings": {},
      "dataset_query": {},
      "archived": false
    },
    "text": "# Título\n\nTexto em **markdown** aqui."
  },
  "series": []
}
```

## Passo 5 — Mapear filtros do dashboard aos novos cards

Se o dashboard tem parâmetros (filtros) e os novos cards devem responder a eles, adicionar `parameter_mappings` no dashcard:

```json
{
  "parameter_mappings": [
    {
      "parameter_id": "ff97c004",
      "card_id": 13468,
      "target": ["dimension", ["template-tag", "data"], {"stage-number": 0}]
    },
    {
      "parameter_id": "3457d8b",
      "card_id": 13468,
      "target": ["dimension", ["template-tag", "unidade"], {"stage-number": 0}]
    }
  ]
}
```

Para cards com query structured (não native), o target usa field name:

```json
{
  "target": ["dimension", ["field", "unidade", {"base-type": "type/Text"}], {"stage-number": 0}]
}
```

## Erros comuns e soluções

| Erro | Causa | Solução |
|---|---|---|
| 403 "Você não tem permissões de curadoria" | `collection_id` errado no POST /api/card | Usar `collection_id: 569` |
| FK constraint `dashboard_tab_id not present` | Usando PUT antigo `/api/dashboard/:id/cards` | Usar `PUT /api/dashboard/:id` com tabs + dashcards |
| `missing FROM-clause entry for table X` | Field ID no template-tag é de outra tabela | Conferir field IDs com `GET /api/table/{id}/fields` |
| Dashcards sumiram após PUT | Enviou `dashcards` sem `tabs` | **Sempre** enviar ambos juntos |
| Cards duplicados na aba | Múltiplos PUTs sem limpar | Filtrar duplicatas pelo card_id, manter só o mais recente |

## Grid do Metabase

- Largura total: 18 colunas
- Card lado a lado: `size_x: 9` cada, `col: 0` e `col: 9`
- 3 lado a lado: `size_x: 6` cada, `col: 0`, `col: 6`, `col: 12`
- Card full width: `size_x: 18, col: 0`

## Formatação condicional nas tabelas

```json
{
  "visualization_settings": {
    "table.column_formatting": [
      {
        "columns": ["vs 7d %"],
        "type": "single",
        "operator": "<",
        "value": -30,
        "color": "#C23B22",
        "highlight_row": false
      }
    ],
    "column_settings": {
      "[\"name\",\"CPL\"]": {"prefix": "R$ "},
      "[\"name\",\"vs 7d %\"]": {"suffix": "%"},
      "[\"name\",\"CTR\"]": {"suffix": "%"}
    }
  }
}
```

## Script Python reutilizável

O padrão completo em Python está em:
`scratchpad/create_cards.py` (sessão 832031ae)

Fluxo: criar cards → ler dashboard → montar payload com tabs + dashcards → PUT.
