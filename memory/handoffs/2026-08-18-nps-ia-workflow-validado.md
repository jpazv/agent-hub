# Handoff: NPS IA Workflow — Validação Completa

**Data:** 2026-08-18
**Issue:** #270 (Análise de IA nos comentários NPS)

---

## Workflow analisado

**Nome:** `NPS - Extração IA (proposta, chave embutida)`
**ID n8n:** `gqb8Qk98V6xEoetC`
**JSON exportado:** `~/Downloads/NPS - Extração IA (proposta, chave embutida).json`

### Fluxo (12 nós)

```
Manual Trigger ──┐
                 ├─> Config ─> Buscar comentários (SELECT) ─> Montar lotes (40/lote)
Agendamento     ─┘    │           ─> Loop por lote ─> Montar payload ─> OpenRouter
(diário 4h)           │           ─> Normalizar saída ─> Gravar no banco?
                      │                                    ├─ true  → UPDATE ia_analise
                      │                                    └─ false → Prévia (não grava)
                      │
                      └─ gravar_no_banco = false (trava)
                         somente_pendentes = false (⚠️ AJUSTAR)
                         limite = 40
                         modelo = google/gemini-3.7-flash
```

### Config atual

| Param | Valor | Status |
|---|---|---|
| `gravar_no_banco` | `false` | OK — trava de segurança |
| `somente_pendentes` | `false` | ⚠️ MUDAR pra `true` antes de ativar |
| `limite` | `40` | OK |
| `modelo_classificacao` | `google/gemini-3.7-flash` | OK |

### Conclusões da análise

1. **NÃO papora créditos** — roda 1x/dia às 4h, não a cada 5min
2. **NÃO apaga dados** — faz UPDATE só de `id` + `ia_analise`, não toca as 11 colunas do ingest
3. **Ingest workflow é separado** — upsert de 11 colunas explícitas, `ia_analise` não está na lista
4. **`somente_pendentes` precisa ser `true`** — senão reprocessa todos os 1.800+ comentários a cada dia
5. **Custo incremental:** ~US$ 0,09/mês (~5 novos comentários/dia)

### Taxonomia (prompt v3.0.0)

- 5 sentimentos, 13 áreas (multi-label), 4 temperaturas, 6 intuitos
- `temperature: 0` para reprodutibilidade
- JSON Schema com `strict: true` no response_format

### Próximos passos

1. Mudar `somente_pendentes` → `true`
2. Rodar backfill manual (1.806 comentários, ~US$ 0.52 em batch)
3. Ligar `gravar_no_banco` → `true`
4. Ativar o workflow

### ⚠️ Chave API exposta no JSON

O arquivo exportado contém a chave OpenRouter em plaintext no header Authorization do nó HTTP. Não commitar esse JSON em repo público.

---

## Contexto paralelo

- Issue #260 (mb_sync.py) — concluída
- Issue #282 (UI adjustments dashboard 316) — concluída
- Mapa Metabase (`mapa_metabase.html`) — landing redesign concluído, próximo passo: página de logs de auditoria
