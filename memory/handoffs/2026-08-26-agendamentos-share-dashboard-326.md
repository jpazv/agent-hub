# Handoff — Agendamentos Share / Issue #326

**Data:** 2026-08-26  
**Máquina:** mac-grupovelas  
**Modo:** global  
**Issue:** [#326 — Share de meta de agendamento por semana e estratégia de geração automática](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326)  
**Dashboard de teste:** [Metabase dashboard 389 — Agendamentos Share](https://metabase.grupovelas.com.br/dashboard/389)

## Contexto da issue

A issue pede uma regra para transformar a meta mensal de agendamentos em metas semanais e automatizar o processo. Ela deixa três decisões abertas:

1. rateio linear, por dias úteis ou histórico;
2. semana ISO cheia de segunda a domingo ou faixas fixas do mês;
3. cálculo em MV, view ou ETL.

O usuário decidiu que a sazonalidade deve usar **52 semanas** e que a granularidade oficial é **o dia**. A semana será somente a soma das metas diárias para acompanhamento.

Comentário técnico publicado na issue: https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326#issuecomment-5428350140

## Decisão de lógica

Regra aprovada para a proposta:

```text
share_semana_dia = volume_dia / volume_semana

share_final_dia = média robusta dos shares de 52 semanas
                  renormalizada para somar 100%

meta_dia = meta_mensal × peso_dia
           ─────────────────────────────
           soma dos pesos dos dias elegíveis no mês

meta_semana = soma das metas diárias da semana
```

Escolhas adicionais documentadas:

- usar 52 semanas ISO completas, excluindo a semana corrente incompleta;
- tratar feriados e dias não úteis antes do cálculo;
- aplicar os filtros ao histórico, realizado e meta;
- filtros previstos: unidade, boutique, marca e sócio;
- comparar média simples, média aparada, mediana e ponderação por recência;
- recomendação estatística inicial: média aparada ponderada por recência, meia-vida de 13 semanas;
- usar fallback para nível superior quando um filtro tiver amostra insuficiente;
- manter casas decimais no cálculo e usar maior resto caso metas inteiras sejam necessárias;
- não alterar schema nem fazer escrita no banco.

## Dados confirmados no Metabase

- `mv_agendamento_propria`: `data`, `id`, `unidade`, `boutique`, `marca`, `socio`, `dia_util`.
- `mv_hibrida_unidade_propria`: `data`, `unidade`, `boutique`, `marca`, `socio`, `agend`, `meta_agd_diaria`, `meta_agd_cheia`, `dia_util`.
- `mb_metas_proprias`: `data_competencia`, `agendamentos`.
- `mb_feriados`: `data`.
- `dim_unidades`: dimensões de unidade, marca, boutique, status e tipo.
- `log_unidades`: status, tipo, boutique e canal.

Observação: `vw_boutique_unidade` está catalogada, mas a consulta sem schema falhou; não deve ser usada sem confirmar o schema correto.

## Dashboard 389 — estado atual

O dashboard `[TESTE] Agendamentos Share` está na collection `569` e possui duas abas reais:

- `958` — **Visão executiva**
- `959` — **Validação e auditoria**

Dashcards atuais:

| Dashcard | Card | Aba | Conteúdo |
|---:|---:|---:|---|
| 20384 | virtual | 958 | Texto explicativo em Markdown nativo do Metabase |
| 20388 | 13761 | 958 | Share histórico por dia da semana |
| 20392/20393 | 13766 | 958 | Gráfico principal realizado vs metas |
| 20390 | 13763 | 958 | Acompanhamento semanal |
| 20383 | 13756 | 959 | Auditoria diária |
| 20391 | 13764 | 959 | Controle da baseline — 52 semanas |

Os IDs antigos substituídos não estão vinculados a nenhum dashboard. Houve cards intermediários criados durante as correções, mas a última auditoria de dashcards mostrou somente os seis itens acima dentro do dashboard 389.

### Cards de apoio validados

O card de controle da baseline retornou:

- 52 semanas válidas;
- primeira semana: 2025-08-25;
- última semana: 2026-08-17;
- 5 dias observados;
- share total médio: 100%.

O perfil histórico retornou cinco dias porque `dia_util` atualmente trata sábado e domingo como não operacionais. Confirmar com Operações se sábado deve participar.

## Problemas encontrados

O gráfico principal apresentou:

```text
ERROR: missing FROM-clause entry for table "mv_hibrida_unidade_propria"
```

Causa: field filters do Metabase expandem para o nome completo da tabela, enquanto os SQLs usavam aliases (`a`, `h`, `x`) em CTEs. Algumas substituições automáticas também alteraram por engano a referência ao CTE final `a`.

Correção parcial já aplicada nos cards de apoio: SQL sem aliases nas tabelas filtradas. O filtro Marca foi testado com sucesso nos cards de perfil, semanal, baseline e auditoria.

O gráfico principal ainda precisa da correção final. Foi preparado, mas **não executado**, o script:

`/Users/grupovelas/recreate-main-share.sh`

Esse script cria um novo card já vinculado ao dashboard 389, troca o filtro Data por `Agrupamento de tempo`, fixa a competência no mês corrente, adiciona Sócio e substitui o dashcard antigo. Ele deve ser revisado antes de executar porque é uma escrita externa e ainda não foi validado.

## Padrão do dashboard de Performance revisado

O dashboard de Performance é o dashboard `10`, “🚀 Relatório de Performance”. Ele usa uma hierarquia de decisão mais madura:

- abas por contexto: RPD, Acelerômetros, Consolidado, Vendas Detalhado, Evolução de Clínicas, Histórico e Distribuição;
- filtros globais: Canal, Marca, Sócio, Unidade, Data, Localização, Região, Ano, Estorno e Agrupamento de tempo;
- cards grandes para tendências e gráficos de barras/combo;
- scalars compactos para KPIs de leitura imediata;
- cards de texto para separar blocos narrativos;
- mapeamentos de filtro por campo ou template tag, conforme a fonte do card;
- uso de “Agrupamento de tempo” como `temporal-unit`, ligado ao campo `data`.

O usuário quer que o dashboard Share siga esse padrão: entendimento imediato, narrativa visual, filtros de segmentação consistentes e manipulação de granularidade para decisões importantes.

## Próximo passo recomendado

1. Revisar o SQL de `/Users/grupovelas/recreate-main-share.sh`.
2. Recriar o gráfico principal sem aliases e com filtros textuais explícitos (`marca = {{marca}}`, etc.).
3. Adicionar o parâmetro global `Agrupamento de tempo`, default `day`, e o filtro global `Sócio`.
4. Decidir se os cards de apoio também devem receber `Agrupamento de tempo` ou permanecerem em visões fixas de validação.
5. Executar o gráfico com filtros de Marca, Unidade, Boutique e Sócio; testar `day`, `week` e `month`.
6. Confirmar visualmente se o combo chart exibe: realizado em barras, meta flat como referência tracejada e meta ponderada como linha destacada.
7. Confirmar com Operações o tratamento de sábado e feriados municipais.
8. Só depois de validar, considerar comentar na issue que a proposta foi implementada em dashboard de teste.

## Arquivos criados ou atualizados nesta sessão

- `/Users/grupovelas/agendamentos-share-proposta-tecnica.md`
- `/Users/grupovelas/agendamentos-share-proposta.html`
- `/Users/grupovelas/Downloads/agendamentos-share-proposta-tecnica.md`
- `/Users/grupovelas/Downloads/agendamentos-share-proposta.html`
- `/Users/grupovelas/Downloads/issue-326-comentario-proposta.md`
- `/Users/grupovelas/create-agendamentos-share.sh`
- `/Users/grupovelas/repair-agendamentos-share.sh`
- `/Users/grupovelas/add-baseline-validation.sh`
- `/Users/grupovelas/fix-agendamentos-share-filters.sh`
- `/Users/grupovelas/recreate-main-share.sh` — preparado, pendente revisão/execução

## Restrições e cuidados

- Não ler handoffs anteriores, conforme pedido do usuário.
- Não usar subagentes.
- Consultas ao banco somente `SELECT/WITH`.
- Para cards já vinculados a dashboard, não usar `PUT /api/card/:id`; recriar o card via `POST /api/card` com `dashboard_id` e substituir o dashcard no `PUT /api/dashboard/:id`.
- Antes de qualquer PUT de dashboard, obter e preservar o payload completo com `tabs` e `dashcards`.
- Após qualquer criação, conferir que cada card aparece exatamente uma vez no dashboard 389.
