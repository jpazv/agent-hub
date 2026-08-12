---
data: 2026-08-11
maquina: mac-grupovelas
projeto: Explorador Visual Metabase
status: em andamento
---

# Explorador Metabase - Handoff

## Onde parou
Reescrevendo `scratchpad/explorador-metabase.html` (artifact 545fdc1d). Pendencias:

1. **Mapa BR bugado** - SVG real ja extraido em `scratchpad/brazil-clean.svg` (27 estados, viewBox 0 0 354 368, fonte: luisdalmolin/mapa-brasil-svg)
2. **Busca burra** - falta: accent-folding (normalizar acentos), busca por ID numerico, busca por tabela
3. **Quick search** - search fab (bolha no canto) ja no CSS, falta painel de resultados em tempo real com JSON
4. **Pan limits** - limitar pan ao bounding box das bolhas + margem pequena

## Arquivos chave (scratchpad)
- `explorador-metabase.html` - versao atual (bugada)
- `brazil-clean.svg` - SVG limpo pronto pra usar
- `data_const.txt` - JSON com 257 dashboards agrupados
- `watchos_data_v2.json` - dados enriquecidos

## Regras
- Metabase API: SOMENTE SELECT/WITH, zero ALTER/CREATE/DELETE
- Plano aprovado: `.claude/plans/delightful-sauteeing-zebra.md`
- Issue #260 no GitHub
