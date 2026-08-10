---
data: 2026-08-10
maquina: mac-grupovelas
projeto: LeadScore / Dashboard LSV / Metabase
status: régua em uso; reconciliação de fontes concluída
escopo: 39 unidades próprias
---

# Régua de expectativa + reconciliação das fontes oficiais

Sucede `2026-08-06-estudo-oe-tres-eixos.md` e `2026-08-06-mapa-dados-mkt-trafego-pago.md`.
Aqueles dois estão **desatualizados** nos números — a régua mudou duas vezes desde então.

## 1. O que o estudo virou

Deixou de ser "índice de eficiência com correlação alta" e passou a ser uma coisa só:
**régua de expectativa de agendamento, dada a temperatura do lead.**

A correlação com CVS (0,92) foi rebaixada a nota de rodapé porque é **circular** —
eficiência = CVS ÷ esperado, então correlacionar com CVS prova aritmética, não mérito.
Quem apontou isso foi o JP, e estava certo.

### O argumento que sobra, e é o único forte

| Comparando | CVS varia | Carteira varia |
|---|---|---|
| 39 unidades entre si | 2,64% a 13,16% = **4,97×** | 5,53% a 9,28% = 1,68× |
| 12 semanas entre si | 5,47% a 8,13% = 1,49× | 5,38% a 8,26% = **1,54×** |

**Entre unidades a régua ajusta pouco** — a carteira só explica 12% da variação do CVS,
e o CVS bruto prevê o futuro até melhor (0,74 contra 0,69 fora da amostra). Quem quiser
ranquear unidades pode usar CVS bruto.

**Entre períodos a régua é indispensável** — a carteira varia mais que o próprio CVS.
Consequência de bolso: **meta de CVS mês a mês cobra a unidade por algo que o marketing
entregou.**

### Usos legítimos, e só estes três
1. Cobrança individual com número: "recebeu X, eram esperados Y, fez Z"
2. Série temporal da mesma unidade
3. Tirar da mesa a desculpa "meus leads são ruins"

### Não serve para
- Ranquear a rede (CVS bruto dá quase a mesma ordem)
- Ser chamada de "índice de qualidade de atendimento"
- Comparar unidades de marcas diferentes (ver §3)

## 2. A régua atual — 4 faixas, congelada em 07/08/2026

O corte do quente saiu de 0,60 para **0,719** por decisão do JP, depois de eu mostrar que
a faixa antiga misturava leads de 13,6% com leads de 27,6% (terços da faixa quente).

| Faixa | Nota | Régua global | Leads |
|---|---|---|---|
| Quente | > 0,719 | 25,55% | 9.500 |
| Pré-quente | 0,60 – 0,719 | 13,63% | 4.725 |
| Morno | 0,35 – 0,60 | 4,41% | 4.172 |
| Frio | < 0,35 | 1,11% | 33.345 |

**Nunca fazer régua dinâmica no tempo.** Testado: com régua fixa os meses dão
1,015 / 1,034 / 0,975 / 0,961; com régua recalculada por mês dão **1,000 nos quatro** —
por construção. Vale a mesma regra para qualquer recorte: régua por unidade zeraria a
eficiência de todas as unidades. Só entram na régua fatores que **não são culpa da unidade**.

## 3. Régua por marca — decisão executiva do JP

Cada marca cobrada pela própria régua. Os cortes das faixas continuam iguais; só as taxas mudam.

| Faixa | Instituto Trata | ITC Vertebral |
|---|---|---|
| Quente > 0,719 | 24,003% | 26,006% |
| Pré-quente | 11,959% | 14,298% |
| Morno | 4,012% | 4,583% |
| Frio | **1,184%** | **1,078%** |

O frio inverte: Trata converte mais lead frio. Não investigado.

**Efeito medido:** Trata sobe 0,064 de eficiência em média, ITC cai 0,021. Só **2 de 39
unidades cruzam o 1,00** (Trata Morumbi e Trata Meireles, ambas com saldo de −2 e −1).
Nenhuma unidade com problema real muda de diagnóstico.

**Duas consequências obrigatórias no documento:**
- Eficiência deixou de ser comparável entre marcas (Trata 1,10 ≠ ITC 1,10)
- Não existe mais "saldo da rede" — cada marca fecha em zero separadamente

## 4. Backfill: escoramos todo lead com conversa

Era 90,4% de cobertura, virou **96,95%**. Os 3.443 pendentes entraram em 07/08.

**A regra de elegibilidade mudou** de `min_ate_secretaria_expediente < 30` para
`msg_inbound > 0 AND msg_humano > 0`. As três edições no n8n (workflow LeadScore V5.1):
linhas 125 (`batch_resgate`), 138 (`base_mv`) e 241 (contador `passivo_total`).
Arquivo pronto em `~/Downloads/LeadScore_V5.2_conversa.json` (importar, não colar).

**Descobertas do pipeline:**
- `score.py` **nunca envia `resgate_size`** (linha 174 manda só `batch_size`) — quem
  decide é o default do node JS "Normaliza pedido delta", não o do SQL
- O laço do `main()` tem duas saídas cegas ao resgate: linha 1012 (`total_candidatos == 0`
  descarta o resgate **antes** de gravar) e linha 1044 (`< BATCH_SIZE`)
- `SCORE_BATCH_SIZE=1` faz o laço girar (1 < 1 é falso), mas quebra o guarda de cursor.
  O que funcionou: batch padrão 100 e várias execuções, ou resgate 500
- Existe trava de processo em `/tmp/leadscore_score.lock` — execuções em série, não paralelo
- O modelo **já é calibrado em lead lento**: divisão 1,00 e 0,97 nos leads de 30min-2h e 2h+

**Sobraram 1.623 leads sem nota (3%), e 97% deles nunca tiveram resposta humana.** Onde a
cobertura de uma unidade é baixa, isso já é o resultado, não furo de dado. Cobertura por
unidade vai de 64,4% a 100%, mediana 98,9%.

**Viés de cobertura:** r(cobertura, divisão) foi de −0,068 para **−0,288** depois do
backfill. Não passa o corte (0,316), mas o mecanismo é real — quem não responde tem
cobertura baixa e os leads não respondidos ficam fora do O/E dela. **Ler a divisão sempre
junto da cobertura.**

## 5. Fontes oficiais do dashboard 10 — mapa resolvido até a tabela física

| Modelo | Cards | Tabela |
|---|---|---|
| `card__2457` Segmentação Unidades | **19** | **`mv_hibrida_unidade_propria`** |
| `card__51` Vendas | 16 | `mv_venda_propria` |
| `card__1816` Avaliações | 6 | `mv_avaliacoes_propria` |
| `card__67` | 5 | **SEM PERMISSÃO** (fonte de %D2, Ticket Médio, Fat/Av, %No-show, %CVF) |
| `card__2141` Agendamentos | 3 | `mv_agendamento_propria` |
| `card__1815` | 3 | **SEM PERMISSÃO** |
| `card__2228` Leads Z-Api | 1 | `mv_leads_ps_propria` |
| `card__2091` Fisioterapeuta | 1 | `mv_hibrida_fisio_propria` |
| `card__2131` Metas | 1 | `mv_data_geral` |
| `card__2231` Estoque | 1 | `tb_agendamentos_proprias` |

### A definição oficial do %CVS
`card 1822` → métrica **2589** = métrica **2587 ÷ 2588** sobre `card__2457`, ou seja:

```
%CVS = SUM(agend) / SUM(leads_sec)   em mv_hibrida_unidade_propria
```

O denominador é **`leads_sec`** (leads que chegaram à secretaria), não todos os leads.

### A reconciliação — conclusão importante

| Fonte | Grão | Leads | Agendamentos | Avaliações |
|---|---|---|---|---|
| `mv_hibrida_unidade_propria` (oficial) | unidade × dia | 53.678 | **5.145** | 3.519 |
| `mv_leads_ps_propria` (oficial) | lead | 54.484 | **3.674** | 2.578 |
| `tb_leads_z_api` | lead | 57.896 | 4.568 | 3.178 |
| `mv_chatwoot_conversa_metricas` | lead | 53.678 | **3.674** | **2.578** |

**A MV do Chatwoot concorda EXATAMENTE com a MV oficial de leads** — 3.674 e 2.578 nas
duas. Não estávamos usando a fonte errada. O que não fecha é a `mv_hibrida`, que reporta
**1.471 agendamentos a mais** e que nenhuma fonte no grão do lead possui.

Interpretação: a híbrida conta todo agendamento da unidade (paciente antigo, retorno,
marcado sem lead de origem); a régua conta agendamento **atribuível a lead**, que é 71%
do total. Numeradores diferentes por definição, não por erro.

**Decisão:** manter a régua sobre `mv_leads_ps_propria` ou o Chatwoot (dão o mesmo), e
declarar no documento que o numerador é "agendamento atribuível a lead".

### Chaves de join (testadas)
- `mv_leads_ps_propria` → Chatwoot: `id_interno` + `telefone` — **95,5%** de cobertura até o score
- `mv_agendamento_propria.lead_id` vem com prefixo `ld-` (`ld-1186554`); o Chatwoot usa
  numérico puro. Depois de `replace(lead_id,'ld-','')` casa, mas o campo só está
  preenchido em **21%** das linhas — inútil para a régua
- `mv_avaliacoes_propria` **não tem** `lead_id`, só `client_id`/`people_id`
- O que a MV do Chatwoot filtra da `tb_leads_z_api`: 4.209 leads, **89% outbound e 95% sem
  mensagem**, carregando 893 agendamentos. O filtro está certo — é lead prospectado sem conversa

## 6. Artifacts publicados

| Documento | URL |
|---|---|
| A régua de expectativa (relatório principal) | claude.ai/code/artifact/70104ea8-105b-44a6-8cd1-9804f5131718 |
| Dicionário da matriz unidade × mês | claude.ai/code/artifact/b78c0b14-ac1a-414b-9c72-d7ba6d0387f3 |
| Caderno de conferência (query por query) | claude.ai/code/artifact/dfde6349-d637-4a9a-b35c-6dfafc8da78b |
| Laudo de tráfego pago | claude.ai/code/artifact/ec3edacd-ce67-4b96-b1f6-71178e16b3d7 |

**Todos precisam de revisão** depois da reconciliação de fontes do §5 — eles usam
"agendamento" sem qualificar que é o atribuível a lead.

## 7. Armadilha de transporte: NÃO COLAR SQL EM EDITOR

Três tentativas de colar a query da matriz no editor SQL do Metabase falharam com erro de
sintaxe em posições diferentes (1488, 1684, 1950), sempre num agregado. A query roda
perfeitamente pela API. O texto chega mutilado — mesmo problema que corrompeu o node do
n8n (linhas cortadas em largura fixa).

**O que funciona:** gravar o arquivo e usar `pbcopy`:
```bash
pbcopy < ~/Downloads/matriz_regua_por_marca.sql
```

Mitigações que apliquei na query e valem manter: sem `FILTER (WHERE)` (trocado por `CASE`
dentro do agregado), sem `percentile_cont`/`WITHIN GROUP`, sem comentário `--`, sem
caractere não-ASCII, linhas abaixo de 90 caracteres, sem `;` final.

## 8. Nomenclatura corrigida

A coluna `faltaram` calculava `real - esperado`, então mostrava **+4** quando a unidade fez
4 **a mais** — o número certo com o rótulo mentindo. Agora são três colunas:

```sql
round(f.ag_real - f.ag_esperado) AS saldo,                        -- com sinal
greatest(0, round(f.ag_esperado - f.ag_real)) AS faltaram,        -- só falta, positivo
greatest(0, round(f.ag_real - f.ag_esperado)) AS sobraram         -- só sobra, positivo
```

E: **somando as células, sobras e faltas se anulam** (503 e 501, saldo −2). É esperado,
a régua é calibrada na base toda. Para o gap de uma unidade, some os meses dela primeiro.

## 8b. ONDE PARAMOS — decisão de escopo da régua

A reconciliação está **concluída**. As três camadas de agendamento, quantificadas:

| Escopo | Agendamentos | % do oficial | O que cobre |
|---|---|---|---|
| Inbound com conversa | **3.683** | 72% | o que o `lead_score` de fato avalia |
| Inbound + outbound | 4.577 | 89% | todo lead identificável |
| Oficial (`mv_hibrida`) | 5.146 | 100% | inclui agendamento sem lead |

`tb_leads_z_api` **está de acordo** com as demais fontes de lead: o inbound dela dá 3.683,
praticamente igual aos 3.674 do Chatwoot e da `mv_leads_ps_propria`. Ela só acrescenta o
outbound. Os 569 restantes (5.146 − 4.577) são agendamento sem lead algum (ligação, retorno,
walk-in).

**Argumento forte para NÃO incluir outbound na régua:** o outbound converte a **23,76%**
contra 6,80% do inbound. Misturar os dois faz a expectativa de uma unidade depender de
quanto ela prospectou — e prospecção não é execução de atendimento. Pior: o `lead_score`
não avalia lead outbound (95% não têm mensagem), então os 3.762 outbound entrariam como
frio por ausência de sinal e seus 894 agendamentos viriam como "sobra", inflando a
eficiência de quem prospecta.

**Se quiser medir outbound:** régua separada, `agend_outbound / leads_outbound` na taxa dele
mesmo (23,76%), como segundo indicador.

### A DECISÃO QUE FALTA (retomar aqui)
Montar a régua definitiva sobre uma destas duas — dão o mesmo número:
- `mv_leads_ps_propria` — fonte oficial do dashboard, 95,5% de ligação com a nota, exige join
- `tb_leads_z_api WHERE NOT eh_outbound` — mesmo número e já traz as métricas de conversa
  na mesma tabela, dispensa join

### Join que continua sem solução
`mv_avaliacoes_propria` **não tem `lead_id`**. Investigação em curso quando paramos:
`mv_leads_ps_propria.patient_id` (preenchido em só **2.640 de 54.533** linhas) contra
`mv_avaliacoes_propria.people_id` (5.269 de 7.674) e `client_id` (3.830 de 7.674).
Os intervalos de valor de `client_id` e `patient_id` parecem do mesmo espaço
(1.216.303/923.327 vs 1.222.113/923.256) — **não testado se casam**. Sem esse join, o eixo
"comparecer" não sai de fonte oficial no grão do lead.

## 9. Pendências

- [ ] `card__67` e `card__1815` sem permissão — sem eles não fecha %No-show nem %CVF
- [ ] Revisar os 4 artifacts com o qualificador "agendamento atribuível a lead"
- [ ] Goiânia Marista escoreia só **65,5%** dos leads que entram na MV (todas as outras
      acima de 81%) — e é uma das duas mais eficientes. Investigar se é falha de pipeline
- [ ] Corrigir a Saída 1 do `score.py` (linha 1012): mover o `break` para depois do
      `salvar_scores`, senão o resgate é descartado quando não há lead novo
- [ ] Medir **eficiência por hora e por dia da semana** (não temperatura — temperatura é
      obra do marketing e a régua já desconta; eficiência por hora é escala e é acionável)
- [ ] Handoffs de 06/08 estão com números velhos — marcar como supersedidos por este
