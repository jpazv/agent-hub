# Handoff — dashboard técnico Validação LSV

**Data:** 2026-08-27  
**Máquina:** mac-grupovelas  
**Contexto:** Metabase / Lead Score Velas / validação técnica  
**Dashboard criado:** `Validação LSV` — ID **433**  
**Coleção:** `Testes` — ID **576**  
**URL:** https://metabase.grupovelas.com.br/dashboard/433

## Objetivo

Criar um dashboard separado do LSV de produção para demonstrar consistência dos
dados, validade estatística, explicabilidade, riscos metodológicos e o protocolo
de evolução do modelo quando transcrições de áudio/imagem estiverem disponíveis.

Regra visual aplicada: cada tabela/gráfico ocupa 17 colunas e possui uma
marcação técnica pareada de 7 colunas na mesma linha. A marcação explica
pergunta, fonte/grão, cálculo, leitura, critério de aprovação e limitação.

## Estrutura criada

| Aba | ID | Análises | Marcações |
|---|---:|---:|---:|
| 1. Integridade | 1219 | 3 | 3 |
| 2. Validade | 1220 | 4 | 4 |
| 3. Explicabilidade | 1221 | 4 | 4 |
| 4. Mídias vNext | 1222 | 3 | 3 |
| **Total** |  | **14** | **14** |

Dashboard final: **28 dashcards**.

## Filtros

- `vl-data-001` — Data do lead
- `vl-unidade-001` — Unidade
- `vl-marca-001` — Marca
- `vl-campanha-001` — Tipo Campanha

Os 11 cards dinâmicos têm os quatro mapeamentos apontando para os template-tags
`lead_data`, `unidade`, `marca` e `tipo_campanha`. Três cards são globais ou
históricos e informam explicitamente na marcação que não respondem aos filtros.

## Cards criados

### Integridade

- 15236 — `VL | Integridade da base filtrada`
- 15237 — `VL | Cobertura do score por unidade`
- 15238 — `VL | Reconciliação global de fontes e desfecho`

### Validade

- 15239 — `VL | Conversão por decil de temperatura`
- 15240 — `VL | Performance das faixas atuais`
- 15241 — `VL | AUC mensal do Lead Score`
- 15242 — `VL | Momento do score versus agendamento`

### Explicabilidade

- 15243 — `VL | Correlação dos componentes`
- 15244 — `VL | Distribuição e saturação dos componentes`
- 15245 — `VL | Etapas detectadas e conversão`
- 15246 — `VL | Matriz Temperatura x Qualidade`

### Mídias vNext

- 15247 — `VL | Baseline histórico de visibilidade textual`
- 15248 — `VL | Prontidão atual do output para mídias`
- 15249 — `VL | Protocolo de aprovação do modelo multimodal`

Todos foram criados como dashboard questions com `dashboard_id=433`; a coleção
576 não contém nenhum card `VL |` solto.

## Fontes usadas

- `public.lead_score_output` — score, quatro componentes, qualidade, evidências e `scored_at`
- `public.mv_chatwoot_conversa_metricas` — lead, unidade, marca, campanha, mensagens e desfecho atribuível
- `public.mv_hibrida_unidade_propria` — reconciliação do agendamento oficial

Somente SELECT. Nenhum schema/tabela/view foi alterado.

## Achados que orientaram o dashboard

- output: 68.742 linhas; MV de conversas: 68.643; join 1:1: 66.309 (96,6%)
- zero duplicidade, zero score crítico nulo e zero valor fora de 0–1
- AUC retrospectiva 0,8485, estável por mês e marca
- faixa 73+ converte 25,86%, captura 63,52% dos agendamentos e tem lift 3,69x
- 96,2% dos convertidos ligados foram scoreados depois do agendamento registrado; uso prospectivo ainda não provado
- sem evidência explícita da etapa Agendamento, AUC cai para 0,6002
- score é dominado por intenção (`corr=0,955`) e densidade (`corr=0,755`)
- `probabilidade_de_vida` tem correlação bruta de apenas 0,026 com agendamento
- `modelo_evidencias` está 100% nulo na base ligada
- agendamento atribuível representa 72,1% do oficial no período comum
- baseline histórico: 57% da base com menos de 50% das mensagens humanas legíveis

## Inconsistências observadas no dashboard LSV de produção (369)

Não foram alteradas nesta sessão:

1. legenda usa faixas 0–25 / 26–50 / 51–72 / 73–100, mas os cards usam 0–29 / 30–49 / 50–72 / 73–100;
2. nove dos dez cards da aba Qualidade mapeiam o filtro Data para `dia`, mas o SQL declara `lead_data`;
3. `mv_mkt_outcomes_diario.temp_*` continua materializada na régua antiga 0,35 / 0,60 / 0,719, embora cards lead-level usem 0,30 / 0,50 / 0,73.

O dashboard 433 evita depender das faixas `temp_*` agregadas.

## Verificação executada

- 14/14 SQLs executados com sucesso via `/api/dataset` antes da criação
- 14 cards salvos e vinculados exatamente uma vez
- 14 marcações laterais
- cada aba tem paridade perfeita análise/texto: 3/3, 4/4, 4/4, 3/3
- 11 cards filtráveis com quatro parameter mappings; três globais com zero
- consultas dos 14 cards aceitas pelo endpoint salvo (`HTTP 202`)
- zero cards `VL |` soltos na coleção 576
- dashboard 433 aparece normalmente como item da coleção Testes

## Arquivo temporário

Script usado: `/private/tmp/create_validacao_lsv.py` — não versionado e pode ser
descartado pelo sistema. Ele valida SQL, cria cards vinculados ao dashboard,
monta layout e verifica duplicidade/contagem.

## Próximos passos

1. Abrir o dashboard 433 no navegador e fazer revisão visual de altura, quebra de texto e cores.
2. Se aprovado, corrigir separadamente as três inconsistências do LSV 369.
3. Quando as mídias chegarem, disponibilizar no output experimental: versão,
   momento do score, tipo/quantidade de mídia, percentual transcrito, score texto
   e score multimodal.
4. Alimentar a aba Mídias vNext em modo sombra, comparando as duas versões nos
   mesmos leads e sem sobrescrever a linha de base.
5. Um maintainer do repositório deve atribuir formalmente a issue #352 ao
   `jpazv`; o token utilizado não possui permissão para alterar assignees.

## Issue GitHub criada

- issue: **#352** — `[LSV] Criar dashboard técnico Validação LSV`
- URL: https://github.com/Grupo-Velas/produtividade-bi-dev/issues/352
- repositório: `Grupo-Velas/produtividade-bi-dev`
- Project: `Produtividade BI e Dev - Grupo Velas`
- Project item: `PVTI_lADOEJ3d0M4BVg6Yzg4VHko`
- Status: `Triagem/Backlog`
- Setor solicitante: `BI`
- Prioridade: `Critica`
- Tipo: `Relatório`

O card contém a documentação técnica completa do dashboard: objetivo, contexto,
critérios de sucesso, estrutura das quatro abas, IDs das 14 análises, fontes,
filtros, achados estatísticos, inconsistências do LSV 369, validações executadas
e próximos passos para o modelo multimodal.

### Limitação de atribuição

O responsável sugerido no corpo é João Paulo (`jpazv`). A tentativa de atribuir
o usuário foi aceita pela API REST sem erro, porém a leitura final da issue
retornou `assignees: []`. A tentativa anterior pela API GraphQL falhou em
`ReplaceActorsForAssignable` por falta de permissão do usuário/token. Portanto,
o único campo pendente é o assignee formal da issue; deve ser definido por um
maintainer com permissão no repositório.

Nenhum token foi salvo no hub ou nos scripts. Como credenciais foram enviadas
diretamente no chat durante as tentativas, elas devem ser rotacionadas após o
uso.

## Arquivos e commits desta sessão

- handoff: `memory/handoffs/2026-08-27-validacao-lsv-dashboard-tecnico.md`
- script temporário do Metabase: `/private/tmp/create_validacao_lsv.py`
- body temporário da issue: `/private/tmp/issue-validacao-lsv.md`
- scripts temporários do GitHub: `/private/tmp/create_issue_validacao_lsv.sh` e
  `/private/tmp/verify_issue_validacao_lsv.sh`
- commit inicial do handoff: `39c0f01` (`docs: registra dashboard tecnico de validacao LSV`)

Os arquivos em `/private/tmp` não são versionados e podem ser descartados pelo
sistema. As demais alterações/untracked existentes no hub pertencem a trabalhos
anteriores e não foram incluídas nos commits desta tarefa.
