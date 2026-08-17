# Handoff — Dashboard Agendamentos (stand-by)

**Data:** 2026-08-17  
**Sessão:** Claude Opus  
**Status:** STAND-BY — aguardando definição do modelo de classificação VelasConnect

---

## Contexto

Dashboard 385 `[TESTE] Agendamentos - Tráfego Pago` na collection 569 (pessoal JP).
Tab "Agendamentos" (tab_id=937) com 5 cards prontos e funcionais:

| Card  | Nome               | Tipo        | Status |
|-------|--------------------|-------------|--------|
| 13553 | Macro por Unidade  | Tabela      | ✅ Funcional, precisa virar "alerta" |
| 13554 | Semanal            | Combo chart | ✅ OK |
| 13555 | Diário             | Bar chart   | ✅ OK |
| 13556 | Delta do Dia       | Scalar      | ✅ OK |
| 13557 | Projeção           | Tabela      | ✅ OK (conditional formatting vermelho/verde) |

## Parâmetros do dashboard

6 filtros mapeados em todos os 5 cards: `p-data` (default=thismonth, required), `p-marca`, `p-unidade`, `p-socio`, `p-boutique`, `p-campanha`.

## Fórmulas validadas

- **CPL Meta** = `SUM(meta_investimento) / SUM(meta_leads)` (NÃO usar MAX(meta_cpl))
- **Agend. Esperados** = `temp_quente * 0.2582 + temp_pre_quente * 0.1113 + temp_morno * 0.0351 + temp_frio * 0.0097`
  - Coeficientes = %CVS por faixa de temperatura do dashboard 369 (Lead Score Velas), card 12972
- **Projeção** = Realizado + o que a sobra de budget compra ao CPL atual
  - Quando estourou budget: Projeção = Realizado (mostra 🚨)
  - Falta p/ Meta: conditional formatting vermelho quando > 0
- **Template tags**: type=dimension, widget-type=string/contains (marca/unidade/boutique/campanha), string/= (socio), date/all-options (data)
- **Field IDs** (mv_mkt_outcomes_diario, table 487): dia=8388, marca=8385, unidade=8397, socio=8391, boutique=8396, campanha=8395

## O que falta (pendência principal)

A ideia da aba é ser um **painel de alerta**: a tabela Macro (card 13553) deve mostrar **apenas unidades que não estão performando bem**.

### Critério de classificação → VelasConnect

O modelo de classificação (Estável / Atenção / Gerar) vem do VelasConnect:
- **API**: `https://velasconnect.grupovelas.com.br/api/report-mkt`
  - `?list=1` → lista de unidades
  - `?unit_id=X&pa_de=...&pa_ate=...&pc_de=...&pc_ate=...` → relatório da unidade
- **Auth**: Bearer JWT (login via `/gv-academy/api/auth/login?vc_token=...`)
- O token expira em ~8h. Pedir novo ao JP quando retomar.

### O que descobri na API

A resposta do endpoint de unidade retorna: `un.analisado` e `un.anterior` (leads/agend/avaliacoes/tratamentos), `mc.analisado/anterior` (mesmos campos para a marca). Campos `financeiro`, `serie`, `serie_marca` vieram null — pode ser que precisem de parâmetros extras ou que o modelo de classificação seja calculado no frontend.

### Próximo passo

1. Obter token fresco e investigar como o frontend do VelasConnect calcula o modelo (Estável/Atenção/Gerar) — pode estar no código JS do report_mkt
2. Ou perguntar ao JP qual é a regra exata de classificação
3. Com a regra definida, alterar o SQL do card 13553 para filtrar apenas unidades com status "Atenção" ou "Gerar"

## Erros corrigidos nesta sessão (referência)

- Tab FK constraint (tabs orphanadas no cache Metabase)
- p-unidade com default errado `['Boutique - Alphaville']`
- `{{unidade}}` faltando no WHERE do Macro
- p-campanha sem mapping nos dashcards
- CPL Meta usando MAX em vez de SUM/SUM
- Agend. Esperados com coeficientes arbitrários → corrigido com CVS reais

## Arquivos tocados

- Apenas via Metabase API (cards 13553-13557, dashboard 385)
- Nenhum arquivo local de código alterado

## Outras pendências (não relacionadas)

- NPS IA Workflow Merge (issue #270) — pausado
