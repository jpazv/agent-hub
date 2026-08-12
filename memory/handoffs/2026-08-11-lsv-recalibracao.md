# Handoff — LSV Recalibração de Faixas e Migração de Fonte

**Data:** 2026-08-11  
**Dashboard:** 🌡️ Lead Score Velas — ID 369  
**Tabs:** Temperatura (882), Qualidade (883)

## Faixas de temperatura (NOVA REGRA)

- Frio: 0-29° (lead_score < 0.30)
- Morno: 30-49° (0.30 ≤ score < 0.50)
- Pré-quente: 50-72° (0.50 ≤ score < 0.73)
- Quente: 73-100° (score ≥ 0.73)

## Cards na aba Temperatura (882)

### Usando mv_mkt_outcomes_diario (agregados, não dependem de faixa)
| Card ID | Nome | Display |
|---|---|---|
| 13511 | Total de Leads | smartscalar |
| 12961 | Leads Scoreados | smartscalar |
| 12965 | Temperatura Media | smartscalar (°) |
| 12968 | Intencao de Agendar | smartscalar (°) |
| 12971 | 4 Indicadores de Temperatura | bar (°) |

### Usando mv_chatwoot + lead_score_output (lead-level, respeitam 73+)
| Card ID | Nome | Display |
|---|---|---|
| 12962 | Leads Quentes (73-100°) | smartscalar |
| 12967 | %CVS dos Quentes | smartscalar (%) |
| 12972 | Calibração — Faixa de Score vs %CVS | combo (bar+line) |
| 12973 | Evolução — Temperatura e % Quentes | line (filtro granularidade) |
| 12969 | Comparativo 30d vs 30d anteriores | table |
| 13512 | Análise por Origem — Temp e Conversão | table |

### Aba Qualidade (883) — card corrigido
| 12974 | Leads Quentes sem Agendamento | table (threshold 0.73) |

## Filtros do dashboard
| Param ID | Nome | Tipo |
|---|---|---|
| 96331952... | Data | date/all-options → mapeia pra `dia` (MV) ou `lead_data` (chatwoot) |
| ca382a70... | Unidade | string/= |
| 0bfc0ff2... | Marca | string/= |
| tipo-campanha-001 | Tipo Campanha | string/= |
| granularidade-001 | Periodo | dropdown (day/week/month), default week, só card 12973 |

## Field IDs usados nos template-tags
- mv_mkt_outcomes_diario (table 487): dia=8388, unidade=8397, marca=8385, tipo_campanha=8395
- mv_chatwoot_conversa_metricas: lead_data=6531, unidade=6252, marca=6279, tipo_campanha=6268

## Regras salvas no metabase-boot.md
- Nunca sugerir/executar alterações de schema
- Eficiência de tokens: agrupar chamadas, suprimir output, evitar GET desnecessário

## Pendente
- Cards da aba Qualidade (883) ainda usam fonte antiga com threshold 0.60 (exceto 12974 já corrigido)
- Verificar se MV temp_quente usa threshold diferente de 0.73 (provavelmente 0.60)
