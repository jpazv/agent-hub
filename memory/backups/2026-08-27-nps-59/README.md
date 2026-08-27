# Backups — alterações no dashboard 59 e nos 42 filhos (2026-08-27)

Ver `memory/handoffs/2026-08-27-nps-distribuido-socios-unidades.md`.

| Arquivo | O que é | Como reverter |
|---|---|---|
| `backup_59_queries.json` | as 33 `dataset_query` dos cards do 59, **antes** do `boutique IN (<36>)` | `PUT /api/card/<id> {"dataset_query": <json>}` por card |
| `backup_59_params_v2.json` | parâmetros do 59 antes da limpeza do filtro Boutique (48 valores) | `PUT /api/dashboard/59 {"parameters": <json>}` |
| `backup_59.json` | parâmetros + mapeamentos do 59 antes de Área/Intuito e da remoção dos 4 de pesquisa | idem, mais os `parameter_mappings` por dashcard |
| `backup_layout.json` | layout dos 12 dashboards de sócio de marca única antes de apagar a metade ausente | só posição; os dashcards apagados **não** voltam por aqui — teria que recopiar o 59 |
| `bout_45.json` | os 36 valores de boutique de `tipo='Própria' AND status='Ativa'` aplicados | referência |
