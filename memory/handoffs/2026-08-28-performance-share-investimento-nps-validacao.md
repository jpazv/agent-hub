# Handoff — Performance, cards BI, Share de Investimento e validação NPS

**Data:** 2026-08-28
**Sessão:** global, máquina `mac-grupovelas`
**Responsável operacional:** JP (`jpazv`)
**Issues principais:** [#351](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/351), [#353](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/353), [#354](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/354), [#355](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/355), [#356](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/356)

---

## Estado executivo

1. O agrupamento de tempo dos gráficos de Investimento e Agendamentos foi publicado no dashboard 10 e está em validação na issue #356.
2. A regra de negócio da semana é **domingo a sábado**, mas as queries publicadas ainda usam a âncora nativa do PostgreSQL, que começa na segunda. A correção SQL está documentada, mas **não foi aplicada**.
3. A série da meta de Agendamentos ficou sem o emoji de laboratório e foi restaurada após o `PUT` de nome removê-la do gráfico.
4. A skill local `criar-card` foi criada, instalada e validada sem persistir o token exposto pelo usuário.
5. Foram criadas as issues #353 a #356 no Project do BI.
6. O estudo de Share de Investimento ainda não virou dashboard: existe a issue #353 e uma pesquisa técnica inicial; o usuário prefere granularidade semanal.
7. A lacuna de NPS desde 18/08 foi preenchida, sem buracos de ID e com ingestão nova em 28/08. Entretanto, a regressão dos **100 órfãos históricos** permanece; portanto, a issue #351 ainda não deve ser encerrada.

---

## 1. Dashboard de Performance — agrupamento de tempo

### Demanda

No dashboard **10 — 🚀 Relatório de Performance**, o usuário pediu:

- `Investimento x Dia` respondendo ao filtro `Agrupamento de tempo`;
- o gráfico de Agendamentos da seção RAG respondendo ao mesmo filtro;
- a meta flat de Agendamentos deixando de ficar fixa em `115` quando o agrupamento fosse semanal ou mensal;
- criação de novos dashcards/questions para validar sem alterar os originais.

### Parâmetro

- Nome: `Agrupamento de tempo`
- ID: `84ea6960`
- Tipo no dashboard: `temporal-unit`
- Default: `day`

Para SQL nativo, foi usada uma template tag textual `agrupamento_de_tempo`, default `day`, mapeada por:

```json
["variable", ["template-tag", "agrupamento_de_tempo"]]
```

Motivo: o Metabase não aceita template tag nativa do tipo `temporal-unit`; o dashboard continua temporal e envia `day`, `week` ou `month` para a variável textual.

### Estado atual confirmado pela API

Dashboard 10, collection `12`, aba RPD (`tab_id = 5`), **116 dashcards**.

| Visual atual | Card | Dashcard | Linha | Estado |
|---|---:|---:|---:|---|
| `Investimento x Período` | `15251` | `22597` | 31 | ativo, collection 12, dashboard 10 |
| `Agendamentos x Período` | `15254` | `22601` | 55 | ativo, collection 12, dashboard 10 |
| `Meta Agendamentos por Período` | `15253` | série do `22601` | — | arquivado, collection 1, ainda referenciado como série |

Observação: o nome retornado para o card `15251` possui um espaço inicial (`" Investimento x Período"`), mas não possui mais emoji.

### Fórmulas implementadas

Investimento:

```sql
date_trunc({{agrupamento_de_tempo}}, dia)::date AS data,
ROUND(SUM(invest_total_sem), 2) AS investimento,
ROUND(SUM(meta_investimento), 2) AS meta
```

Meta de Agendamentos:

```text
meta diária = meta mensal / quantidade de dias úteis da competência
meta do período = soma das metas diárias incluídas no agrupamento
```

O agrupamento é aplicado tanto às barras quanto à série auxiliar da meta.

### Filtros preservados

- Investimento: Data, Marca, Unidade, Sócio, Região e Agrupamento de tempo.
- Agendamentos principal: Canal, Marca, Sócio, Unidade, Data e Agrupamento de tempo.
- Série da meta: Data, Marca, Unidade, Sócio, Canal e Agrupamento de tempo.

O dashcard `22601` ficou com 12 mappings; 6 são da série `15253`.

### Testes executados

Meta de Agendamentos no último período do teste:

| Agrupamento | Meta |
|---|---:|
| dia | 115,00 |
| semana | 575,00 |
| mês | 2.300,00 |

Investimento no recorte de teste:

| Agrupamento | Investimento | Meta |
|---|---:|---:|
| semana técnica de 24/08/2026 | R$ 72.063,85 | R$ 95.688,50 |
| agosto/2026 até 28/08 | R$ 500.304,84 | R$ 535.855,60 |

Os valores são snapshots e podem mudar com a atualização da MV.

### Regra semanal — pendência crítica

O usuário corrigiu a regra: a semana de negócio começa no **domingo**, não na segunda-feira.

O SQL publicado ainda usa:

```sql
date_trunc('week', data)
```

No PostgreSQL isso ancora na segunda-feira. A expressão proposta e documentada na issue é:

```sql
(date_trunc('week', data + INTERVAL '1 day') - INTERVAL '1 day')::date
```

Aplicar a mesma correção em Investimento e Meta de Agendamentos para manter as séries alinhadas de domingo a sábado. **Nenhuma query foi alterada após a correção verbal do usuário.**

### Armadilha na remoção do emoji

O card `15253` estava arquivado na collection 1 e era apenas série do dashcard `22601`. Um `PUT` apenas com o novo nome removeu a série do gráfico — exatamente a classe de risco já registrada nas práticas do Metabase.

Correção aplicada imediatamente:

- o snapshot anterior do dashboard foi usado para restaurar a série;
- o nome embutido foi atualizado para `Meta Agendamentos por Período`;
- dashboard permaneceu com 116 dashcards;
- série `15253` voltou ao `22601`;
- 12 mappings e os 6 mappings da meta foram preservados;
- nenhuma ocorrência de `🧪` permaneceu no dashboard 10.

Risco restante: a série continua arquivada/collection 1. Validar o gráfico com usuário não administrador. Se houver falha de permissão, recriar a série em uma collection acessível e trocar com cuidado, sem question solta ou dashcard órfão.

### Documentação na issue

Foi publicado e depois **editado o mesmo comentário** — nenhum comentário duplicado:

- [issuecomment-5453935899](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/356#issuecomment-5453935899)

O comentário contém causa raiz, fórmulas, IDs, filtros, resultados de teste, segurança e checklist. Foi corrigido para domingo e marca explicitamente que o SQL ainda precisa do ajuste.

### Backups e temporários

- `/private/tmp/investimento_agrupado.sql`
- `/private/tmp/meta_agendamentos_agrupada.sql`
- `/private/tmp/create_metabase_grouping_test_cards.sh`
- `/private/tmp/rename_agendamentos_periodo_safe.sh`
- `/private/tmp/issue-356-documentacao-agrupamento.md`
- vários snapshots `dashboard-10-*` e `metabase-dashboard-10-*` em `/private/tmp`

Temporários não são versionados e podem desaparecer.

---

## 2. Skill `criar-card`

O usuário forneceu um Markdown de `/criar-card`. A skill `abrir-card` foi procurada, mas não existe nesta máquina/sessão. O material enviado era de **criação**, não de abertura.

A skill `skill-creator` foi usada para estruturar e validar:

- `/Users/grupovelas/.codex/skills/criar-card/SKILL.md`
- `/Users/grupovelas/.codex/skills/criar-card/references/project-board.md`
- `/Users/grupovelas/.codex/skills/criar-card/references/images.md`

Validação: `quick_validate.py` retornou `Skill is valid!`.

### Segurança

O Markdown fornecido continha um token GitHub literal. O token **não foi persistido** na skill; foi substituído por autenticação via `gh`/ambiente. O usuário foi orientado a revogar/rotacionar o token exposto.

### Limitação de assignee

A conta ativa do `gh` é `jpazv`. O GitHub permitiu criar as issues, mas recusou atribuir `jpazv` como assignee (`ReplaceActorsForAssignable` e REST 404). As issues foram criadas pela conta `jpazv` e registram João Paulo no body, mas algumas ficaram sem assignee formal.

---

## 3. Issues criadas nesta sessão

| Issue | Título resumido | Status | Setor | Prioridade | Tipo |
|---|---|---|---|---|---|
| [#353](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/353) | Share de investimento — dashboard em Estudos | Triagem/Backlog | Marketing | Media | Relatório |
| [#354](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/354) | Realizado vs Metas por dia em semanas completas | Triagem/Backlog | BI | Media | Melhoria |
| [#355](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/355) | Mensagem D1 com meta do dia da semana | Triagem/Backlog | BI | Media | Melhoria |
| [#356](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/356) | Validar agrupamento de tempo no Performance | Em validação | BI | Media | Melhoria |

Por instrução explícita do usuário, os títulos usam o prefixo `[JP]`, mesmo que a convenção original da skill prefira o projeto entre colchetes.

---

## 4. Estudo de Share de Investimento

### Escopo acordado

- Criar futuramente um dashboard novo na collection **Estudos (677)**, dentro de Testes (576).
- Usar o dashboard **389 — Share de Agendamentos** como padrão de organização e narrativa, não como fórmula copiada.
- Começar por um estudo técnico completo antes de transformar a ideia em regra operacional.
- Explicar claramente a metodologia ao lado de cada tabela e gráfico.
- O usuário prefere **granularidade semanal** para o share sazonal de investimento.
- Nenhum dashboard de Share de Investimento foi criado ainda.

### Três conceitos que não devem ser misturados

1. **Share realizado:** participação de unidade/marca/canal no investimento total.
2. **Share de resultado:** participação nos leads, agendamentos, vendas, receita ou margem.
3. **Share recomendado:** distribuição sugerida considerando eficiência, capacidade, retorno marginal e restrições.

O histórico de gasto descreve decisões passadas; sozinho, não prova qual distribuição é ótima.

### Pesquisa técnica inicial

Foi usada a skill `firecrawl-search`. Arquivos locais:

- `/Users/grupovelas/.firecrawl/search-meridian-weekly.json`
- `/Users/grupovelas/.firecrawl/search-fpp3-weekly.json`
- `/Users/grupovelas/.firecrawl/search-robyn-official.json`
- `/Users/grupovelas/.firecrawl/search-google-mmm-weekly.json`

Fontes primárias/autorativas úteis:

- Meta Robyn — `An Analyst's Guide to MMM`: recomenda coleta semanal como best practice, mínimo de dois anos de dados semanais, controle de sazonalidade/feriados, variação e volume suficientes, adstock e saturação.
- Hyndman et al., *Forecasting: Principles and Practice*: dados semanais têm período anual não inteiro (`52,18` semanas); sugere STL quando a sazonalidade muda e regressão harmônica/Fourier para ciclos longos; efeitos móveis e feriados precisam de variáveis específicas.
- Google Meridian: separar contribuição incremental, ROI, ROI marginal e curvas de resposta; ROI médio alto não implica bom retorno para o próximo real investido. Modelagem por geografia é preferível quando há variação suficiente.

### Direção técnica — ainda não aprovada

O estudo semanal deve começar descritivo e só depois avançar para recomendação causal:

1. validar calendário de domingo a sábado e semanas 53/parciais;
2. comparar share de investimento por semana com share de resultados na mesma granularidade;
3. controlar feriados, campanhas, mudanças de orçamento, capacidade e abertura/fechamento de unidades;
4. analisar estabilidade em janelas longas e recentes;
5. separar eficiência média de retorno marginal;
6. considerar adstock: investimento de uma semana pode produzir resultado nas semanas seguintes;
7. não chamar um rateio de “recomendado” sem teste de resposta/causalidade ou regra de negócio explícita.

### Dados/fontes internas desejáveis

- regra atual de orçamento fixo e pool rateado;
- planos e metas de Marketing;
- histórico semanal de investimento, impressões/cliques, leads, agendamentos, vendas, receita e margem;
- campanhas, feriados, promoções, inaugurações e mudanças de operação;
- capacidade das unidades e restrições mínimas/máximas de verba;
- definição do KPI que deve ser otimizado.

### Próximo passo do estudo

Produzir a síntese técnica aplicada ao schema do Grupo Velas e desenhar a primeira aba exploratória do novo dashboard, sem criar ainda regra de alocação definitiva.

---

## 5. Issue #351 — validação da ingestão de NPS

### Handoff-base lido

- `memory/handoffs/2026-08-27-nps-ingestao-restabelecida-e-regressao.md`
- relacionados: `2026-08-27-nps-workflow-correcao-em-validacao.md` e `2026-08-26-nps-ia-voltar-hub-e-boutique.md`

O workflow de ingestão reconstruído é `USpeImZKgNtYhJq4`. O handoff registrava 3.803 linhas antes, última resposta em 19/08 11:15, e uma regressão posterior que elevou órfãos históricos para 100.

### Consulta atual — 28/08

Query local: `/private/tmp/nps_gap_validation.sql`, executada via Metabase, banco 2, somente `SELECT`.

Resumo:

| Métrica | Atual |
|---|---:|
| total | **3.884** |
| última resposta | **28/08/2026 11:01** |
| linhas desde 18/08 | **104** |
| linhas após a parada | **78** |
| órfãos totais | **100** |
| órfãos desde 18/08 | **0** |
| notas nulas | **25** |
| `hash` nulo | **2.053** |
| IDs duplicados | **0** |

Watermarks e continuidade:

| Aba | Antes | Atual | Linhas acima do watermark antigo | IDs faltantes no intervalo |
|---|---:|---:|---:|---:|
| ITC | 2.279 | **2.303** | 24 | **0** |
| Trata | 1.585 | **1.630** | 45 | **0** |

Primeiro/último dado após os watermarks:

- ITC: 20/08 15:00 → 27/08 19:18.
- Trata: 19/08 14:56 → 28/08 11:01.

Cobertura diária:

| Dia | Total | ITC | Trata |
|---|---:|---:|---:|
| 18/08 | 21 | 15 | 6 |
| 19/08 | 16 | 9 | 7 |
| 20/08 | 15 | 8 | 7 |
| 21/08 | 7 | 3 | 4 |
| 22/08 | 3 | 1 | 2 |
| 23/08 | 1 | 0 | 1 |
| 24/08 | 7 | 2 | 5 |
| 25/08 | 8 | 1 | 7 |
| 26/08 | 14 | 8 | 6 |
| 27/08 | 9 | 3 | 6 |
| 28/08 | 3 | 0 | 3 |

Todos os dias de 18 a 28 possuem dados e nenhum registro desse recorte está órfão.

### Extração de IA

Validação sobre `public.nps_ia`:

| Métrica | Atual |
|---|---:|
| comentários distintos elegíveis | **1.753** |
| analisados | **1.753** |
| pendentes | **0** |
| total em `nps_ia` | **1.753** |
| análises `ausente=true` | **0** |
| gravadas desde 27/08 | **31** |
| última análise | **28/08 14:00:42 UTC** |

Conclusão: o backlog de IA também foi absorvido e não há “pílulas envenenadas” detectadas.

### Conclusão da validação

**A lacuna desde 18/08 foi preenchida.** Evidências:

- datas contínuas no recorte 18–28/08;
- nenhum ID faltante após os watermarks antigos;
- dado novo em 28/08, indicando que a ingestão continuou após a execução manual de ontem;
- zero órfãos no recorte novo;
- IA com 100% de cobertura e zero pendentes.

**A issue #351 ainda não está concluída**, porque os 100 órfãos históricos continuam no banco. A correção de prioridade no nó `Chaves de unidade` não foi aplicada, não rodou no workflow correto ou não produziu o efeito esperado.

Também não foi possível inspecionar diretamente o histórico de executions do n8n: o alias SSH `velas_adm` não resolve nesta máquina e não foi encontrado API key local. A cadência exata de 20 minutos não foi provada; a existência de resposta nova em 28/08 e análise de IA às 14:00 UTC prova atividade recente dos fluxos.

### Próximo passo obrigatório da #351

1. Abrir o workflow efetivamente ativo e confirmar a lógica de prioridade no nó `Chaves de unidade`.
2. Rodar a ingestão uma vez.
3. Reexecutar a query de validação.
4. Exigir redução dos 100 órfãos ao baseline esperado e manter `órfãos desde 18/08 = 0`.
5. Só então comentar a issue e decidir se pode ser concluída.

Nenhum comentário/status da issue #351 foi alterado nesta sessão.

---

## 6. Decisões e cuidados consolidados

1. Não alterar dashboard question via `PUT` para query/visualização; recriar já com `dashboard_id` e collection do dashboard.
2. Mesmo um `PUT` de nome em série arquivada pode remover a série do dashcard; sempre guardar snapshot e auditar imediatamente.
3. Em SQL nativo, filtro temporal do dashboard usa template tag textual para alimentar `date_trunc`.
4. A semana de negócio do Grupo Velas é domingo–sábado.
5. Não fechar a #351 só porque a data máxima avançou; validar continuidade, órfãos e IA.
6. Não confundir share histórico de gasto com recomendação ótima de investimento.
7. Nenhum subagente foi usado, conforme regra do hub.

---

## 7. Próxima retomada sugerida

1. Corrigir o início semanal para domingo nos cards `15251` e `15253`, por recriação segura, e revalidar #356.
2. Resolver a situação de permissão/arquivamento da série `15253` e testar com usuário não administrador.
3. Retomar a #351 no nó `Chaves de unidade`, rodar e provar a queda dos 100 órfãos.
4. Publicar na #351 um comentário de validação somente depois da correção dos órfãos.
5. Retomar o estudo semanal de Share de Investimento e desenhar a metodologia aplicada ao banco antes de criar o dashboard em Estudos.
