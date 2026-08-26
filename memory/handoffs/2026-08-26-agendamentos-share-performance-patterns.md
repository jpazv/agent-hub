# Handoff — Agendamentos Share: padrão de Performance e próximos ajustes

**Data:** 2026-08-26  
**Máquina:** mac-grupovelas  
**Modo:** global  
**Issue:** [#326 — Share de meta de agendamento por semana e estratégia de geração automática](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326)  
**Dashboard em teste:** [Metabase dashboard 389 — Agendamentos Share](https://metabase.grupovelas.com.br/dashboard/389)

## Estado da autenticação

O token mais recente fornecido pelo usuário foi validado e atualizado em:

`/Users/grupovelas/dev/agent-hub/memory/metabase-boot.md`

Não expor o token em respostas, commits adicionais ou arquivos fora do boot local.

## O que foi estudado no dashboard de Performance

Dashboard analisado: ID `10`, **🚀 Relatório de Performance**.

### Padrão de segmentação

Filtros globais observados:

- Canal;
- Marca;
- Sócio;
- Unidade;
- Data;
- Localização;
- Região;
- Ano;
- Estorno;
- Agrupamento de tempo.

O filtro **Agrupamento de tempo** é do tipo `temporal-unit`, default `day`, e é mapeado para o campo `data` dos cards. O filtro Data é separado e controla o período. Esse padrão é melhor que substituir Data por Agrupamento de tempo: o usuário precisa de ambos para escolher **o recorte** e **a granularidade**.

### Padrão de storytelling

- abas organizadas por contexto decisório: RPD, Acelerômetros, Consolidado, Vendas Detalhado, Evolução de Clínicas, Histórico e Distribuição;
- texto curto separando blocos narrativos;
- scalars pequenos no topo para leitura imediata;
- gráfico principal largo para tendência/realizado;
- cards secundários para decomposição e auditoria;
- tabelas/pivots para exploração detalhada;
- filtros mapeados card a card, por campo ou template tag, conforme a origem da consulta.

### Implicação para o Share

O dashboard Share deve manter **Data** para competência/período e adicionar **Agrupamento de tempo** para alterar a visualização entre dia, semana e mês. Sócio deve ser filtro global junto de Unidade, Boutique e Marca. O gráfico principal deve ficar largo, abaixo dos KPIs e do texto de orientação.

## Estado atual do dashboard 389

Dashboard: `[TESTE] Agendamentos Share`, collection `569`.

Abas:

- `958` — Visão executiva
- `959` — Validação e auditoria

Cards ativos dentro do dashboard:

- texto explicativo virtual: dashcard `20384`, aba `958`;
- perfil histórico corrigido: card `13761`, dashcard `20388`, aba `958`;
- gráfico principal atual: card `13766`, dashcard `20393`, aba `958`;
- acompanhamento semanal: card `13763`, dashcard `20390`, aba `958`;
- auditoria diária: card `13756`, dashcard `20383`, aba `959`;
- controle da baseline: card `13764`, dashcard `20391`, aba `959`.

Os cards substituídos em tentativas anteriores não estão vinculados ao dashboard. Não criar novos dashcards soltos na collection.

## Validações já realizadas

- perfil histórico: 5 linhas/dias operacionais, sem erro;
- baseline: 52 semanas válidas, primeira semana `2025-08-25`, última `2026-08-17`, 5 dias observados e share total de 100%;
- semanal: 5 linhas, sem erro;
- auditoria: retorno válido;
- filtro Marca funcionou nos cards de apoio após remoção dos aliases;
- dashboard possui exatamente 6 dashcards ativos, todos dentro das duas abas.

O fato de haver cinco dias vem de `dia_util`; sábado ainda precisa ser confirmado com Operações.

## Erro pendente do gráfico principal

Erro reportado pelo usuário:

```text
ERROR: missing FROM-clause entry for table "mv_hibrida_unidade_propria"
```

Causa: field filters do Metabase expandem referências usando o nome original da tabela, enquanto o SQL tinha aliases em CTEs. A tentativa de remover aliases deixou uma referência indevida ao CTE `a` e o gráfico continuou instável.

## Próximo ajuste técnico obrigatório

O script preparado, mas ainda não executado, é:

`/Users/grupovelas/recreate-main-share.sh`

Ele precisa ser revisado antes da execução. A solução correta deve:

1. preservar um filtro **Data** para o período escolhido;
2. adicionar `Agrupamento de tempo` como `temporal-unit`, mapeado ao campo `data`;
3. adicionar `Sócio` como filtro global;
4. usar SQL sem aliases nas tabelas diretamente filtradas, ou usar variáveis textuais com predicados explícitos;
5. manter o CTE final com alias próprio (`a`) sem substituição automática;
6. retornar no formato wide: `data`, `realizado`, `meta_flat`, `meta_ponderada`, `share_percentual`;
7. agregar o resultado por `date_trunc({{agrupamento_de_tempo}}, data)`;
8. testar o gráfico com Data + Marca + Unidade + Boutique + Sócio;
9. testar `day`, `week` e `month`;
10. substituir o dashcard antigo dentro do dashboard 389, preservando abas e layout.

Importante: ao corrigir cards vinculados, recriar com `POST /api/card` já informando `dashboard_id` e depois atualizar o dashboard completo com `tabs` + `dashcards`. Não usar `PUT /api/card/:id`.

## Decisões de negócio preservadas

- granularidade oficial do cálculo: diária;
- semana: soma das metas diárias, não rateio independente;
- baseline: 52 semanas ISO completas;
- feriados/dias não úteis tratados antes da consolidação;
- meta diária ponderada pelo share histórico do dia;
- meta flat mantida apenas como referência visual;
- filtros: Data, Agrupamento de tempo, Sócio, Unidade, Boutique e Marca;
- implementação inicial somente leitura no Metabase, sem alteração de schema.

## Arquivos e entregáveis

- `/Users/grupovelas/agendamentos-share-proposta-tecnica.md`
- `/Users/grupovelas/agendamentos-share-proposta.html`
- `/Users/grupovelas/Downloads/agendamentos-share-proposta-tecnica.md`
- `/Users/grupovelas/Downloads/agendamentos-share-proposta.html`
- `/Users/grupovelas/Downloads/issue-326-comentario-proposta.md`
- `/Users/grupovelas/recreate-main-share.sh` — pendente revisão e execução
- `/Users/grupovelas/dev/agent-hub/memory/metabase-boot.md` — token atualizado

## Critério para encerrar a próxima sessão

O dashboard só deve ser considerado pronto quando o gráfico principal responder sem erro aos filtros Data, Agrupamento de tempo, Marca, Unidade, Boutique e Sócio, com todas as consultas retornando dados e sem dashcards órfãos ou duplicados.
