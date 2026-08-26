# Handoff — Dashboard Share reconstruído

**Data:** 2026-08-26  
**Máquina:** mac-grupovelas  
**Dashboard:** [Metabase 389 — Agendamentos Share](https://metabase.grupovelas.com.br/dashboard/389)  
**Issue:** [#326](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326)

## Resultado da reconstrução

O dashboard 389 foi reconstruído seguindo o padrão do dashboard de Performance (ID 10):

- Data como filtro de período;
- Agrupamento de tempo como filtro `temporal-unit`;
- Marca, Unidade, Boutique e Sócio como segmentações;
- abas separadas por objetivo;
- texto explicativo no topo da visão executiva;
- gráfico principal largo;
- cards de apoio e auditoria na aba de validação.

Abas mantidas:

- `958` — Visão executiva
- `959` — Validação e auditoria

## Cards definitivos atuais

- `13772` — Share histórico por dia da semana — definitivo
- `13773` — Realizado vs meta — dia/semana/mês
- `13774` — Acompanhamento semanal — definitivo
- `13775` — Auditoria diária — definitivo
- `13776` — Controle da baseline — 52 semanas — definitivo v2
- `13777` — Controle da baseline — 52 semanas — definitivo v2 (último substituto)

O card ativo mais recente de baseline é o `13777`; confirmar no GET do dashboard antes de qualquer alteração. O texto explicativo é o dashcard virtual `20384`. O dashboard deve permanecer com seis dashcards ativos, sem duplicatas.

## Lógica implementada

- fonte única dos cards novos: `mv_hibrida_unidade_propria`, evitando conflito de field filters entre tabelas;
- baseline histórica: 52 semanas ISO completas, sem a semana corrente;
- normalização: volume do dia dividido pelo volume da semana;
- meta diária: peso histórico do dia normalizado pelos dias elegíveis do mês;
- meta semanal: soma das metas diárias;
- feriados: excluídos via `mb_feriados`;
- dias elegíveis: `dia_util = 1`, atualmente resultando em cinco dias observados;
- realizado: `SUM(agend)`;
- filtros aplicados à mesma tabela e aos mesmos níveis de histórico, realizado e meta;
- cálculo interno decimal, arredondamento somente na apresentação.

## Correção importante de filtros

O erro anterior era:

```text
missing FROM-clause entry for table "mv_hibrida_unidade_propria"
```

Ele ocorria porque field filters do Metabase expandiam o nome original da tabela, enquanto as queries usavam aliases. A reconstrução usa a mesma visão híbrida em todas as CTEs e não usa aliases nas tabelas filtradas.

O `Agrupamento de tempo` não pode ser declarado como template tag `temporal-unit` dentro de SQL nativa. O Metabase rejeita esse tipo de tag em cards SQL. A solução aplicada foi:

- parâmetro do dashboard: `temporal-unit`;
- mapeamento do dashboard: target `variable` para `agrupamento_de_tempo`;
- template tag do card: `text` com default `day`;
- SQL: `date_trunc({{agrupamento_de_tempo}}, data)`.

## Testes realizados

- cinco cards definitivos sem filtros retornaram dados;
- gráfico principal em `day`: 21 linhas;
- gráfico principal com `week`: 5 linhas;
- gráfico principal com Sócio `P0` e `week`: 5 linhas, sem erro;
- baseline: 52 semanas, share histórico total de 100%;
- filtro Marca testado anteriormente nos cards de apoio;
- abas e vínculos preservados no dashboard 389;
- cards antigos foram removidos dos dashcards ativos.

## Observação de negócio

O perfil retorna cinco dias porque `dia_util` exclui sábado e domingo. Confirmar com Operações se sábado deve participar. Se sábado for operacional, revisar o calendário antes de oficializar a meta.

## Token

O token fornecido pelo usuário está atualizado em:

`/Users/grupovelas/dev/agent-hub/memory/metabase-boot.md`

Não expor o valor do token em respostas ou novos arquivos.

## Próxima sessão

1. Abrir o dashboard 389 e validar visualmente o combo chart.
2. Testar no próprio Metabase Data, Agrupamento de tempo, Marca, Unidade, Boutique e Sócio.
3. Confirmar se a UI do parâmetro temporal envia `day`, `week` e `month` para o template tag textual.
4. Se o filtro Data precisar afetar também os cards de apoio, mapear `p-data` aos cards que usam `{{data}}`.
5. Não recriar cards novamente sem antes verificar o GET do dashboard e os dashcard IDs atuais.
6. Não usar `PUT /api/card/:id`; alterações de query devem recriar o card já com `dashboard_id:389` e substituir o dashcard dentro do dashboard.
7. Confirmar sábado e, então, atualizar a documentação técnica e a issue #326 com o resultado final.

## Scripts de apoio

- `/Users/grupovelas/rebuild-share-dashboard.sh` — reconstrução inicial;
- `/Users/grupovelas/fix-share-template-tags.sh` — correção de tipos de tags;
- `/Users/grupovelas/recreate-main-share.sh` — tentativa antiga; revisar antes de usar;
- `/Users/grupovelas/agendamentos-share-proposta-tecnica.md` — proposta completa;
- `/Users/grupovelas/agendamentos-share-proposta.html` — apresentação executiva.
