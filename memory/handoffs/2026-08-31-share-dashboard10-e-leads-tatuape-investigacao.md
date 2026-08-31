# Handoff — Share, Dashboard 10 e leads de Tatuapé

**Data:** 2026-08-31  
**Máquina:** `mac-grupovelas`  
**Sessão:** global / Metabase  
**Responsável:** JP  
**Modo ao encerrar:** somente investigação; não aplicar novas correções sem autorização explícita

## Orientação mais recente do usuário

O chat apresentou instabilidade e o usuário continuará em outra sessão. A instrução final foi:

- não fazer mais alterações;
- apenas investigar e documentar;
- registrar todo o estado em handoff.

## 1. Share de Investimento

### Dashboard criado anteriormente

- Dashboard: `435 — Share de Investimento`
- URL: `https://metabase.grupovelas.com.br/dashboard/435`
- Collection: `677 — Estudos`
- Fonte: `public.mv_mkt_outcomes_diario`
- Estrutura atual: 3 abas, 9 questions e 12 textos

Cards atuais:

| Card | Nome |
|---:|---|
| 15269 | Resumo do último fechamento |
| 15270 | Share recebido x share entregue — maiores desvios |
| 15271 | Onde o resultado devolve mais ou menos share |
| 15272 | Quem recebeu mais ou menos verba que o padrão de 13 semanas |
| 15273 | Evolução semanal — share recebido x share entregue |
| 15274 | Matriz semanal — diferença entre share entregue e recebido |
| 15275 | Consistência em 13 semanas |
| 15277 | Auditoria semanal por unidade |
| 15278 | Controle da base — 13 semanas |

### Mudança posterior de escopo

O dashboard `435` deve ser tratado como **rascunho ainda não aprovado**. Depois da criação, o usuário redefiniu a ordem do estudo:

1. Primeiro validar somente o share de investimento.
2. Trabalhar em granularidade semanal.
3. Entender historicamente quais posições da semana/mês recebem mais investimento.
4. Validar o funcionamento entre semanas e entre unidades.
5. Não comparar com Leads, Agendamentos ou Faturamento ainda.
6. Somente após aprovação começar comparações com outros resultados.

Definição básica aprovada para a fase inicial:

```text
share de investimento da unidade na semana
= investimento da unidade na semana
÷ investimento total do escopo na mesma semana
```

Ponto crítico já validado: o filtro de Unidade deve selecionar quem aparece, sem alterar o denominador do escopo. No teste com `ITC Vertebral - Alphaville`, o share permaneceu `1,99%` com e sem o filtro de Unidade.

### Estudo já realizado, mas não usar ainda como tela principal

Nas 13 semanas disponíveis:

- correlação share de investimento × Leads: `0,738`;
- investimento × Agendamentos: `0,563`;
- investimento × Faturamento: `0,414`;
- investimento × Faturamento da semana seguinte: `0,403`.

O usuário decidiu adiar essas comparações. A próxima sessão deve redesenhar o dashboard para começar apenas pela distribuição semanal do investimento.

## 2. Auditoria de finais de semana no dashboard 10

Dashboard: `10 — Performance`.

### Resultado da auditoria

- `15251 — Investimento x Período` já incluía sábado e domingo.
- `124 — Leads x Dia` já incluía sábado e domingo.
- O card antigo de Agendamentos `15259` excluía finais de semana e feriados do realizado por `dia_util = 1`.

Evidências:

- A barra de Investimento rotulada `27/07` continha apenas 01/08, sábado, `R$ 18.841,72`, e 02/08, domingo, `R$ 20.819,94`, total `R$ 39.661,66`.
- Leads na semana 02–08/08: `4.445` de segunda a sexta e `1.601` no fim de semana, total `6.046`.
- Os rótulos eram diferentes porque Investimento usava `date_trunc('week', dia)` e começava visualmente na segunda; Leads usava o agrupamento nativo do Metabase e começava no domingo.

## 3. Card de Agendamentos recriado

A demanda explícita foi incluir sábado e domingo também em Agendamentos.

- Card atual: `15279`
- Dashcard: `22656`
- Dashboard: `10`
- Collection: `12`
- Aba: `5`
- Layout: linha `55`, coluna `0`, `24 × 8`
- Mappings: `9`
- Card anterior arquivado: `15259`

O card novo inclui sábado e domingo em:

- Realizado;
- Cancelamentos;
- totais de Dia, Semana e Mês.

Metas flat e ponderada continuam apenas em dias úteis. Não foi aprovada redistribuição de meta para sete dias.

Validação da query:

| Agrupamento | Pontos | Realizado | Cancelamentos |
|---|---:|---:|---:|
| Dia | 23 | 1.477 | 415 |
| Semana | 4 | 1.477 | 415 |
| Mês | 1 | 1.477 | 415 |

Foram encontrados 43 agendamentos e 22 cancelamentos em sete datas de fim de semana.

O dashboard permaneceu com `116` dashcards e os demais cards foram comparados por ID sem divergência.

## 4. Bug ativo: card de Agendamentos mostra “Sem resultado” no dashboard

**O problema continua ativo. Não foi corrigido após a orientação de somente investigar.**

Comportamento:

- ao abrir o card `15279` isoladamente, ele retorna dados;
- dentro do dashboard `10`, aparece `Sem resultado`;
- o endpoint do contexto do dashboard retornou `23` linhas normalmente.

Causa técnica identificada:

O `visualization_settings` do dashcard `22656` ainda contém `columnValuesMapping` apontando para o card antigo:

```text
sourceId: card:15259
```

As métricas do dashcard usam aliases como `COLUMN_7`, `COLUMN_8`, `COLUMN_9` e `COLUMN_10`, todos derivados desse mapeamento antigo. O card novo é `15279`, então o Metabase recebe as linhas, mas não associa as colunas às séries na visualização do dashboard.

Correção provável, ainda não aplicada:

- recriar/atualizar apenas a configuração visual do dashcard para mapear as colunas do `card:15279`;
- preservar card, SQL, filtros, posição e todos os demais dashcards;
- validar no endpoint do dashboard e visualmente.

Como o usuário determinou somente investigação, a próxima sessão deve pedir autorização antes de alterar o dashboard.

## 5. Leads ausentes — Alexandre Almeida / Tatuapé

Card da demanda:

- `#358 — [JP] Investigar ausência de leads — Tatuapé`
- URL: `https://github.com/Grupo-Velas/produtividade-bi-dev/issues/358`

Escopo encontrado:

- Sócio: `P0 - Alexandre Almeida`
- Unidade: `224 — ITC Vertebral - Tatuapé`

### Resultado confirmado

As duas MVs concordam:

- `mv_hibrida_unidade_propria`: último dia com lead em `25/08/2026`;
- `mv_mkt_outcomes_diario`: último dia com lead em `25/08/2026`;
- últimos sete dias: `5` leads;
- sete dias anteriores: `147` leads.

Linha do tempo:

| Data | leads_sec / hibrida | leads_scal | leads / outcomes | Investimento | Agendamentos |
|---|---:|---:|---:|---:|---:|
| 23/08 | 29 | 25 | 29 | 803,93 | 0 |
| 24/08 | 24 | 24 | 24 | 835,06 | 3 |
| 25/08 | 5 | 10 | 5 | 468,28 | 9 |
| 26/08 | nulo | 4 | 0 | 337,05 | 4 |
| 27/08 | nulo | nulo | 0 | 427,44 | 3 |
| 28/08 | nulo | nulo | 0 | 467,82 | 1 |
| 29/08 | nulo | nulo | 0 | 674,16 | 0 |
| 30/08 | nulo | nulo | 0 | 803,28 | 0 |
| 31/08 | nulo | nulo | 0 | 64,05 | 0 |

Conclusões já sustentadas pelos dados:

1. Não é filtro do dashboard: a ausência existe nas duas MVs.
2. Não é atraso global das MVs: outros sócios têm leads até 31/08.
3. Não é paralisação total da unidade: investimento e agendamentos continuaram chegando depois de 25/08.
4. A falha é específica do fluxo de leads da unidade 224.
5. O `leads_scal` ainda recebeu 4 registros em 26/08, um dia depois de `leads_sec` parar; a interrupção completa ocorre a partir de 27/08.
6. A causa está a montante das MVs ou no vínculo/mapeamento da fonte de leads específica de Tatuapé.

### Próximo passo de investigação

Rastrear a definição de `mv_hibrida_unidade_propria` para identificar as tabelas/joins que alimentam `leads_sec` e `leads_scal`; em seguida consultar diretamente a fonte da unidade 224 e verificar:

- se os registros deixaram de ser ingeridos;
- se o identificador da unidade/campanha mudou;
- se o nome/código passou a não casar no join;
- se existe lacuna de workflow ou credencial específica.

Uma tentativa de criar o helper `/private/tmp/get_hibrida_viewdef.py` foi interrompida pelo usuário antes da conclusão. Verificar se o arquivo existe antes de reutilizar; nenhuma consulta de definição foi concluída.

## 6. Issues criadas com a skill `criar-card`

O usuário informou que não pode usar assignee. Por orientação explícita dele, a responsabilidade foi representada pelo prefixo `[JP]`; `assignees` ficou vazio.

### #357

- Título: `[JP] Ajustar finais de semana no gráfico de agendamentos`
- URL: `https://github.com/Grupo-Velas/produtividade-bi-dev/issues/357`
- Status: Triagem/Backlog
- Setor: BI
- Prioridade: Media
- Tipo: Bug

### #358

- Título: `[JP] Investigar ausência de leads — Tatuapé`
- URL: `https://github.com/Grupo-Velas/produtividade-bi-dev/issues/358`
- Status: Triagem/Backlog
- Setor: BI
- Prioridade: Media
- Tipo: Bug

## 7. Arquivos e backups locais

- `/private/tmp/dashboard-10-before-agendamentos-weekends-2026-08-31.json`
- `/private/tmp/dashboard-10-after-agendamentos-weekends-2026-08-31.json`
- `/private/tmp/dashboard-10-live-debug.json`
- `/private/tmp/card-15279-final.json`
- `/private/tmp/card-15279-query-final.json`
- `/private/tmp/card-15279-dashboard-empty.json`
- `/private/tmp/include_weekends_agendamentos_dashboard10.py`
- `/private/tmp/audit_weekends_dashboard10.py`
- `/private/tmp/investigate_alexandre_leads.py`
- `/private/tmp/investigate-alexandre-leads-result.json`
- `/private/tmp/create_jp_performance_cards.sh`

## 8. Ordem recomendada para a próxima sessão

1. Ler este handoff e confirmar que o modo ainda é somente investigação.
2. Se autorizado, corrigir o `columnValuesMapping` do dashcard `22656` e validar o card `15279` dentro do dashboard 10.
3. Continuar o rastreamento upstream dos leads de Tatuapé a partir da definição de `mv_hibrida_unidade_propria`.
4. Documentar a causa na issue `#358`.
5. Só depois retomar o dashboard `435`, redesenhando-o para share semanal puro de investimento, sem comparação com resultados.
