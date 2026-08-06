# Handoff — Documento Técnico: Método de Score de Qualidade de Atendimento

**Data:** 2026-08-06
**Máquina:** macbook-jpazv
**Código:** `projects/lead-quality-score/` dentro do hub
**Handoff anterior (resultados e contexto):** `2026-08-05-lead-quality-score-experimento.md`

Este documento especifica **como a qualidade de atendimento é calculada** — preciso
o bastante para reimplementar do zero. Os resultados do experimento estão no
handoff anterior; aqui é só o método.

---

## 1. O que este score mede, e o que ele NÃO mede

**Mede:** o comportamento do **atendente** numa conversa de WhatsApp.

**Não mede:** a propensão do **lead** a converter. Isso é a temperatura
(`lead_score`), métrica separada e que deve continuar separada.

A separação não é cosmética. Se qualidade entrar como parcela somada na
temperatura, cria-se confundimento circular: o lead fica "quente" porque o
atendente foi bom, não porque quer comprar. E perde-se o cruzamento, que é onde
está o valor acionável:

| | Atendimento bom | Atendimento ruim |
|---|---|---|
| **Lead quente** | fluxo normal | **prioridade máxima de intervenção** |
| **Lead frio** | descartar | treinar o atendente |

O quadrante superior-direito só existe se os dois números forem independentes.

---

## 2. Unidade de análise e estrato

**Uma linha por lead** (`cw_id_tb_leads`), agregada depois para unidade × semana.

**Estrato:** apenas leads com `min_ate_secretaria_expediente <= 30`.

Motivo: o tempo até a primeira resposta já é uma variável conhecida e forte.
Segurando-a constante, o que sobrar de correlação é atribuível à qualidade da
conversa, não à velocidade. Usa-se a versão *expediente* (que desconta horário
fora de funcionamento) porque a secretária não pode responder às 2h — a versão
de relógio corrido mediria o lead, não o atendente.

Efeito: 22.722 de 28.737 leads (79%) em 6 semanas.

**Consequência que precisa estar clara:** dentro do estrato a velocidade da
primeira resposta é quase constante. Qualquer dimensão baseada nela perde
variância e vira ruído. Ver §5.3.

---

## 3. Fontes

| Fonte | Papel |
|---|---|
| `analytics.mv_chatwoot_conversa_metricas` | espinha lead-level: chave, unidade, data, tempos, contagens, desfechos |
| `public.conversations` + `public.messages` | transcript (remontado — `lsv_conversas` está vazia) |
| `public.lead_score_output` | temperatura e vocabulário da trilha |
| `mv_hibrida_unidade_propria` | `agend` e `leads_sec` → %CVS |

Ligação: `mv.contact_id` → `conversations.contact_id` → `messages.conversation_id`.
Validado: 29.750 leads, todos com `contact_id` único, 99,7% com mensagem.

---

## 4. Classificação do papel de cada mensagem

**`sender_id` não serve.** 99,7% das mensagens de saída vêm de duas contas de
integração ("WhatsApp" id 181 e "Não direcionar" id 1), não do atendente real.

Regra usada:

```
message_type = 0                              → lead
message_type = 1 e created_at >= primeiro_humano_em  → atendente
message_type = 1 e created_at <  primeiro_humano_em  → bot
message_type = 2, ou private = true                  → descartado
```

`primeiro_humano_em` vem da MV. **Precisão medida:** reproduz `msg_humano`
exato em 78% dos leads e com erro ≤1 em 88%. Viés médio +0,60 mensagem. É
aproximação declarada, não exatidão.

Normalização do texto: minúsculas, sem acento (NFKD → ASCII), espaços
colapsados. Aplicada aos dois lados — texto e vocabulário — para `avaliação`
casar com `avaliacao`.

---

## 5. As quatro dimensões

Vocabulário: 78 termos em 6 etapas, extraídos de
`lead_score_output.trilha_evidencias`. Reusar o dicionário existente é
deliberado — assim a comparação com a métrica atual isola o **método** e não o
vocabulário.

Ordem canônica, inferida empiricamente de `ordem_detectada`:

```
abordagem → sondagem → captura → apresentacao → preco → agendamento
```

`preco` e `agendamento` se alternam na prática; a checagem de ordem tolera a
troca entre esses dois.

Todas as detecções são feitas **apenas nas mensagens do atendente**.

### 5.1 Cobertura condicional — peso 0,30

O conserto central sobre a métrica atual. O denominador **não** é o total de 6
etapas: é a **etapa mais avançada que a conversa alcançou**. Só se penaliza
etapa pulada se a conversa passou dela.

Motivo: lead que sumiu na segunda mensagem gera 2/6 = 0,33 na métrica antiga,
mesmo que o atendente tenha feito tudo certo até onde deu. Isso pune o atendente
por comportamento do lead.

```
peso_etapa = {abordagem 0.5, sondagem 1.5, captura 1.0,
              apresentacao 1.5, preco 1.2, agendamento 2.0}

ult      = índice da etapa mais avançada presente
obtido   = Σ peso_etapa[e] para e presente
possivel = Σ peso_etapa[e] para e com índice <= ult

cobertura = clip( (obtido / possivel) × (1.05 se ordem_ok senão 0.95), 0, 1 )
```

Etapa final pesa mais que saudação: agendamento (2,0) vale 4× abordagem (0,5).

### 5.2 Profundidade — peso 0,35

Transforma o binário em contínuo. Não basta tocar na etapa; conta quantas vezes
foi trabalhada e com quantos termos distintos, com saturação para não premiar
repetição.

```
sat(x, k) = clip(x / k, 0, 1)

por etapa presente e:
    prof[e] = 0.5 · sat(ocorrencias[e], 3) + 0.5 · sat(termos_distintos[e], 3)

profundidade = média de prof[e] sobre as etapas presentes  (0 se nenhuma)
```

### 5.3 Responsividade — **peso 0,00**

**Calculada e exportada, mas fora da composição.** Documentada aqui porque a
decisão de zerá-la é o achado, não um descuido.

```
responsividade = 1 − log1p(clip(min_resposta_media_humana, 0, 480)) / log1p(480)
```

Diagnóstico por decil mostrou comportamento **invertido**: Spearman −0,143
contra conversão; decil 1 converte 18,6% e decil 10 converte 5,3%.

Causa: `min_resposta_media_humana` é o intervalo médio **entre** respostas.
Conversa longa e engajada se estende por horas com pausas naturais do lead →
média alta. Troca curta que morre rápido → média baixa. "Ritmo rápido" marca
conversa morta, não bom atendimento.

A velocidade que de fato importa — a da primeira resposta — já é o filtro do
estrato (§2). Não há terceira coisa para essa dimensão medir.

**Se o estrato de ≤30min for removido, esta dimensão precisa ser reavaliada, não
reativada como estava.**

### 5.4 Condução — peso 0,35

A dimensão mais bem comportada (Spearman +0,314, monotônica em todos os decis:
0,5% → 35,8%).

```
conducao = 0.40 · sat(perguntas_atendente, 4)
         + 0.35 · sat(alternancias, 6)
         + 0.25 · [existe mensagem do atendente com termo de agendamento E "?"]
```

- `perguntas_atendente`: mensagens do atendente contendo `?`
- `alternancias`: trocas de locutor na sequência da conversa
- terceiro termo: CTA explícito de agendamento

---

## 6. Gate de abandono

Multiplicativo, não somado — uma falha grave deve destruir a nota, não ser
diluída por média.

```
abandonou = (última mensagem da conversa é do lead)
gate      = 0.55 se abandonou senão 1.00
```

Lead falou por último e ninguém respondeu. Separa atendimento de
não-atendimento. Incide em 11,3% dos casos.

---

## 7. Composição

```
qualidade = clip( (0.30·cobertura + 0.35·profundidade
                 + 0.00·responsividade + 0.35·conducao) × gate, 0, 1 )
```

Os pesos são **chute informado**, não calibrados contra desfecho. Ficam num
dict único no topo de `score.py` — mudar é uma linha.

**Calibrá-los por regressão contra o desfecho real é o próximo passo óbvio** e
transformaria o score de opinião em modelo. Não foi feito.

---

## 8. Dado faltante: mídia sem transcrição

Áudio/imagem chegam com `content` nulo — o fornecedor não entrega transcrição.
Atinge 57% da base (menos de 50% das mensagens do atendente legíveis).

**Regra: não imputar. Medir e estratificar.**

```
visibilidade_textual = (mensagens do atendente com texto) / (mensagens do atendente)
CORTE_VISIBILIDADE = 0.70
```

`visibilidade_textual` é **indicador de confiança do score**, nunca um ajuste
nele.

Por que não imputar: creditar etapa não observada troca falso negativo por falso
positivo, e os dois erros não custam o mesmo. Falso negativo custa poder
estatístico — há 22.722 leads, dá para perder alguns. Falso positivo custa a
**validade do achado**: mídia é mais comum nas conversas engajadas, que já
convertem mais; imputar inflaria o score exatamente onde a conversão já é alta e
a correlação subiria por construção. O experimento terminaria confirmando a si
mesmo.

Dado que sustenta a regra — a relação **não é monotônica**:

| Visibilidade | Leads | Mídias | Msgs atend. | Conversão |
|---|---|---|---|---|
| 0–25% | 6.727 | 4,3 | 4,9 | 1,17% |
| 25–50% | 6.164 | 4,2 | 7,1 | 5,81% |
| 50–70% | 2.948 | 4,4 | 11,4 | 19,30% |
| 70–90% | 2.564 | 2,7 | 13,5 | **20,83%** |
| 90–100% | 4.319 | 0,1 | 3,9 | 3,40% |

**Uso de mídia é marcador de atendimento humano engajado.** A faixa sem mídia
nenhuma tem 63,7% de conversas com 1–2 mensagens roteirizadas e converte 3,4%.
Um score puramente textual penaliza exatamente as conversas boas — mas creditar
mídia seria a imputação circular. Daí: medir e estratificar.

---

## 9. Agregação para unidade × semana

Semana por `date_trunc('week', lead_data)`. Semana em curso **sempre descartada**
— parcial entra com denominador menor e distorce.

Duas métricas agregadas:

```
score_medio = média de qualidade na célula
pct_bom     = fração de leads com qualidade >= 0.800
```

**`pct_bom` é a métrica principal.** Evidência: within-unidade contra conversão
lead-level dá **+0,231 (p=0,0006)** contra +0,142 do score médio.

O corte **0,800 não foi escolhido a dedo** — saiu do cotovelo da curva de decis
(forma de degrau, maior salto 15,3pp no decil 10, 5,7× a média dos demais
saltos). Escolher limiar na mão é onde esse tipo de análise se engana sozinha:
com liberdade no corte, acha-se correlação em qualquer lugar.

**Procedimento obrigatório ao mudar a fórmula:** recalcular a curva de decis e
rederivar o corte. Não herdar 0,800.

Células com menos de 20 leads ficam fora das correlações.

---

## 10. Confundidor conhecido: volume de conversa

Não é detalhe, é o fato dominante.

| Msgs do atendente | Leads | Conversão |
|---|---|---|
| 1 | 3.637 | 0,47% |
| 6–10 | 5.802 | 2,26% |
| 11+ | 4.714 | **31,01%** |

66×. `msgs_atendente` sozinho correlaciona +0,52 (within) com conversão — mais
forte que qualquer score. Como lead interessado puxa conversa, parte disso é o
**lead**, não o atendente.

Controle implementado:

```
qualidade_residual = qualidade − ajuste_linear(qualidade ~ log1p(msgs_atendente))
```

É a parte que **não** é tamanho de conversa. Resultado: `qualidade_residual` não
correlaciona com conversão — ou seja, o poder preditivo do score vem
majoritariamente do volume. **Reportar sempre junto**, nunca só o score bruto.

---

## 11. Protocolo de validação

Toda mudança de fórmula precisa passar por isto antes de virar número oficial:

1. **Curva de decis** — conversão por decil de score. Se não for monotônica, a
   fórmula tem dimensões se cancelando (foi o que revelou a responsividade
   invertida).
2. **Decis por dimensão isolada** — identifica qual dimensão carrega e qual
   atrapalha.
3. **Baseline obrigatório** — mesma correlação com `qualidade_atendimento`
   antiga. Sem isso não há como afirmar que a nova é melhor.
4. **Confundimento** — correlação do score com `msgs_atendente` e `msg_inbound`.
5. **Estratificação por visibilidade** — se funciona onde dá para ler e falha
   onde não dá, o problema é o dado, não o score.
6. **Duas leituras de correlação** — *pooled* (entre unidades) e *within-unidade*
   (efeito fixo). A segunda é a que responde "melhorar move o ponteiro?".
7. **Leitura humana** — ~20 conversas nos extremos. Score que não sobrevive a
   leitura não vale correlação.
8. **Conferência de totais** — `agend`/`leads_sec` do script contra a metric 2589.

---

## 12. Alvo: qual desfecho usar

**Usar conversão lead-level (`marcou_agendamento`), não o %CVS oficial.**

O %CVS (metric 2589 = `sum(agend)/sum(leads_sec)`) conta **+65% mais
agendamentos** do que os rastreáveis a esses leads: 2.735 contra 1.659. Inclui
conversão que nunca passou pela secretaria. Os dois alvos correlacionam entre si
apenas 0,50 (within).

Consequência medida: contra o %CVS o score não correlaciona (+0,060, n.s.);
contra a conversão lead-level, correlaciona (+0,231). Isso não é o score
falhando — é o alvo medindo outra coisa. Há teto estrutural: parte da variância
do %CVS é inexplicável por qualidade de conversa, por construção.

O %CVS continua sendo a métrica de negócio. Só não serve como alvo de validação
deste score.

---

## 13. Limitações declaradas

- **Pesos não calibrados** contra desfecho. São chute informado.
- **Cobertura corrige demais.** Ao não punir conversa curta, dá 0,86 para quem
  chegou na etapa 2 e cobriu as duas — perde o sinal de que *chegar longe* é o
  que converte. É a dimensão mais fraca (Spearman +0,08) e a primeira a
  reformular.
- **Papel da mensagem é aproximado** (78% exato).
- **Vocabulário de 78 termos**, herdado. Não cobre paráfrase.
- **57% da base cega** por mídia.
- **A métrica antiga bate a nova** em correlação bruta no nível do lead
  (Spearman +0,280 vs +0,203). Empatam só no nível unidade × semana.
- **A qualidade agrega 0,48% de R² único** sobre a temperatura. Ausência de
  sinal não é ausência de efeito — mas também não é evidência de efeito.

---

## 14. Versionamento da fórmula

Todo parâmetro vive no topo de `score.py`, em um lugar só: `PESOS`,
`PESO_ETAPA`, `ORDEM_CANONICA`, `SAT_*`, `TETO_RITMO_MIN`,
`PENALIDADE_ABANDONO`, `CORTE_RESPOSTA_MIN`, `CORTE_VISIBILIDADE`.

Ao mudar qualquer um: registrar o antes/depois das oito verificações do §11 e o
corte de `pct_bom` rederivado. Score sem esse rastro não deve virar número
oficial — a fórmula tem graus de liberdade suficientes para produzir a
correlação que se quiser.
