# Handoff — Agendamentos Share: base v3, fallback e visões executivas

**Data:** 2026-08-27  
**Máquina:** mac-grupovelas  
**Sessão:** Codex  
**Modo:** global  
**Issue:** [Grupo-Velas/produtividade-bi-dev#326](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326)  
**Dashboard de laboratório:** [Metabase 389 — `[TESTE] Agendamentos Share`](https://metabase.grupovelas.com.br/dashboard/389), collection 569  
**Status:** implementação aplicada e validada por query; revisão visual no navegador ainda pendente

## Limite de escopo

O usuário autorizou escrita livre somente no dashboard de teste 389. Nenhum
dashboard validado deveria ser alterado. O dashboard 10 (`🚀 Relatório de
Performance`) foi auditado ao final: 116 dashcards e nenhum card do laboratório
15224–15235 vinculado.

## Regra de negócio consolidada

O share nasce na granularidade diária e a semana é apenas a soma das metas dos
dias elegíveis:

```text
share_dia_na_semana = agendamentos_dia / agendamentos_semana
peso_dow = média dos shares semanais por dia da semana
meta_data = meta_mensal_da_competência × peso_dow
            / soma dos pesos de todos os dias elegíveis do mês
meta_semana = soma das metas de cada data da semana
```

Baseline:

- janela das 52 semanas ISO anteriores;
- semana corrente excluída da baseline;
- somente segunda a sexta;
- feriados excluídos;
- entram apenas semanas com os cinco dias úteis completos;
- média simples permanece a regra oficial;
- pesos vigentes no escopo da rede: segunda 28,09%, terça 20,81%, quarta
  18,29%, quinta 17,52%, sexta 15,30%;
- 44 semanas completas com dados na janela atual.

## Três frentes corrigidas na base v3

### 1. Semana atravessando competências

A versão anterior escolhia uma única competência (`ref.mes`) para toda a janela.
A v3 calcula a competência por data e busca a meta mensal correspondente. Assim,
uma semana que cruza a virada do mês soma parcelas das duas metas mensais.

Validação em janela de cinco semanas:

- semana de 27/07: meta ponderada 515,18, usando julho;
- semanas de agosto: meta ponderada 564,14, usando agosto.

### 2. Fallback por amostra

O perfil usa o primeiro nível com pelo menos 13 semanas completas com volume:

```text
escopo filtrado → boutique → marca → rede
```

O nível efetivamente usado e a quantidade de semanas válidas aparecem nos cards
de share e auditoria. Teste objetivo: `ITC Vertebral - Recife` possui somente 12
semanas com volume; a query subiu automaticamente para `marca`, com 44 semanas
válidas.

O fallback afeta somente o perfil de pesos. Meta e realizado continuam no escopo
selecionado.

### 3. Semana atual

A janela exibida agora contém a semana corrente. Ela recebe status `Em andamento`.

- `meta_ate_data`: meta acumulada somente até a data de corte;
- `meta_semana_total`: planejamento de todos os dias elegíveis da semana;
- o gap parcial compara realizado com `meta_ate_data`, não com a semana inteira;
- semanas anteriores recebem status `Fechada`.

Exemplo validado durante a sessão para 24–28/08:

- 5 dias planejados;
- 4 dias decorridos;
- realizado 326;
- meta até a data 477,82;
- meta semanal total 564,14;
- gap até a data −151,82;
- atingimento do ritmo 68,2%.

## Cards v3 que substituíram a base anterior

Todos são dashboard questions exclusivos do dashboard 389, com `dashboard_id:389`
e `collection_id:569`:

| Card | Nome | Aba |
|---:|---|---|
| 15224 | Realizado vs metas — semanas completas por dia | Visão executiva |
| 15225 | Acompanhamento semanal — meta ponderada e gap | Visão executiva |
| 15226 | Share histórico por dia da semana | Visão executiva |
| 15227 | Evolução semanal — realizado versus meta ponderada | Análise entre semanas |
| 15228 | Gap por dia da semana — % versus meta ponderada | Análise entre semanas |
| 15229 | Matriz de gap — semana versus dia da semana | Análise entre semanas |
| 15230 | Controle da baseline — 52 semanas | Validação e auditoria |
| 15231 | Auditoria diária — elegibilidade e cálculo | Validação e auditoria |

Os cards anteriores 13796–13803 ficaram órfãos, mas não foram arquivados, para
permitir reversão. O título do card 15224 ainda diz “semanas completas”, embora a
v3 inclua a semana atual; é um polimento pendente e não se deve usar PUT no card
para renomear — recriar e trocar o dashcard se for corrigir.

## Quatro novas visões executivas

### Card 15232 — Ritmo do mês — realizado, meta e projeção

Curva acumulada com:

- realizado acumulado até a data;
- meta ponderada acumulada no mês inteiro;
- projeção a partir da data de corte, mantendo o índice de performance observado
  contra a meta ponderada.

Validação final: 21 dias úteis. Em 27/08, realizado acumulado 1.878 contra meta
ponderada acumulada 2.170,23. A projeção então vigente terminava em 2.089,81 para
uma meta mensal de 2.415; os valores podem mudar com nova ingestão.

### Card 15233 — Necessário por dia útil restante

Escalar:

```text
max(meta_mensal - realizado_acumulado, 0) / dias úteis restantes
```

Na última execução da sessão retornou 247,0. Em execução anterior retornou 268,5;
a diferença ocorreu porque os dados continuaram sendo ingeridos durante a sessão.

### Card 15234 — Onde nasce o gap — 12 unidades com maior impacto

Pareto operacional das 12 unidades com gap negativo mais relevante. Retorna:

- realizado;
- meta ponderada até a data;
- gap absoluto;
- atingimento percentual;
- contribuição para o gap negativo total.

Último resultado: Pinheiros liderava o impacto com gap −36,69 e 10,6% do gap
negativo; Ribeirão Preto ITC vinha em seguida com −30,11 e 8,7%.

### Card 15235 — Mudança de perfil — últimas 13 vs 52 semanas

Compara o share recente com a baseline oficial. Resultado vigente:

| Dia | 52 semanas | 13 semanas | Diferença |
|---|---:|---:|---:|
| Segunda | 28,09% | 26,77% | −1,32 p.p. |
| Terça | 20,81% | 21,43% | +0,63 p.p. |
| Quarta | 18,29% | 18,23% | −0,06 p.p. |
| Quinta | 17,52% | 17,71% | +0,19 p.p. |
| Sexta | 15,30% | 15,86% | +0,56 p.p. |

Leitura: perfil ainda estável; a maior mudança recente está na segunda-feira.

## Layout final da aba Visão executiva

| Linha | Card | Tamanho |
|---:|---|---|
| 0 | texto “Como ler esta aba” | 24×9 |
| 9 | 15233 — necessário por dia restante | 24×3 |
| 12 | 15232 — ritmo acumulado | 24×8 |
| 20 | 15234 — Pareto | 12×9, esquerda |
| 20 | 15235 — 13 vs 52 semanas | 12×9, direita |
| 29 | 15224 — realizado diário | 24×8 |
| 37 | 15225 — acompanhamento semanal | 24×8 |
| 45 | 15226 — perfil do share | 24×6 |

Estado estrutural final:

- 14 dashcards: 2 textos + 12 cards;
- nenhum `card_id` duplicado;
- todos os 12 cards têm os 11 `parameter_mappings`;
- filtros: Data, Marca, Unidade, Boutique, Sócio e Semanas exibidas;
- cards 15232–15235 executados via `/api/card/:id/query`, sem erro;
- dashboard 10 confirmado sem cards do laboratório.

## Incidente durante a montagem do layout

O Metabase respondeu intermitentemente com `dashcards: null` em alguns GETs. Além
disso, a primeira expressão `jq` usada no layout tinha precedência incorreta e
emitia cada dashcard como documento separado, fazendo o payload final ficar nulo.

Correção:

- capturar um GET completo em arquivo temporário;
- validar localmente `.dashcards|type == "array"`;
- usar update assignment:

```jq
(.dashcards[] | select(...)) |= (...)
```

- validar contagem, duplicidade, posições e mappings antes do PUT;
- restaurar os mappings a partir do backup pré-v3, ajustando `card_id` para cada
  card novo.

O script `/Users/grupovelas/apply-agendamentos-share-insights.sh` criou os quatro
cards corretamente, mas sua parte de layout contém a expressão jq defeituosa.
**Não rerodar esse script como está.** O layout foi concluído depois com payload
validado em `/private/tmp/dashboard-389-insights-put.json`.

## Arquivos locais da sessão

- `/Users/grupovelas/agendamentos-share-v3-base.sql`
- `/Users/grupovelas/agendamentos-share-v3-select-13796.sql` até `...-13803.sql`
- `/Users/grupovelas/agendamentos-share-v3-curva-acumulada.sql`
- `/Users/grupovelas/agendamentos-share-v3-necessario-dia.sql`
- `/Users/grupovelas/agendamentos-share-v3-pareto-unidade.sql`
- `/Users/grupovelas/agendamentos-share-v3-share-13x52.sql`
- `/Users/grupovelas/apply-agendamentos-share-v3.sh`
- `/Users/grupovelas/apply-agendamentos-share-insights.sh` — não rerodar sem
  corrigir a parte de layout

Backups temporários:

- `/private/tmp/dashboard-389-pre-v3-20260827-160847.json`
- `/private/tmp/dashboard-389-pre-insights-20260827-163358.json`
- `/private/tmp/dashboard-389-insights-put.json`
- `/private/tmp/dashboard-389-after-insights.json`

## Próximos passos

1. Abrir o dashboard 389 no navegador e validar visualmente os quatro cards:
   escala, legenda, orientação do Pareto, rótulos e projeção.
2. Testar os filtros de Marca, Unidade, Boutique e Sócio pela interface; os
   mappings foram restaurados e auditados, mas falta teste visual/interativo.
3. Considerar reduzir a altura do texto inicial para trazer o indicador e a curva
   acima da dobra.
4. Recriar o card 15224 com título compatível com a semana atual, sem usar PUT.
5. Após aceite, decidir se os cards órfãos 13796–13803 podem ser arquivados.
6. Não promover nada ao dashboard 10 até validação explícita do usuário.

## Regras operacionais

- Somente SELECT no banco.
- Não usar PUT em dashboard questions; para alterar query/nome, recriar via POST
  com `dashboard_id:389` e substituir o dashcard.
- PUT do dashboard sempre com `tabs` + `dashcards` e backup anterior.
- Após POST com `dashboard_id`, remover/reaproveitar o auto-dashcard para evitar
  duplicidade.
- Confirmar cada `card_id` exatamente uma vez e revisar mappings após cada PUT.
