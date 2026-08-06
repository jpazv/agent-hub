# Score de Qualidade de Atendimento — experimento de correlação

Experimento para testar se uma métrica de qualidade de atendimento melhor que a
atual adiciona poder explicativo à conversão de leads.

**Nada é escrito no BD Grupo Velas.** Leitura apenas, via API do Metabase, com
guarda de segurança em `mb._assert_readonly` (bloqueia qualquer coisa que não
comece com `SELECT`/`WITH`). Todo processamento e persistência são locais.

## Como rodar

```bash
python3 -m venv .venv && .venv/bin/pip install pandas numpy pyarrow scipy xlsxwriter requests openpyxl
echo "<token>" > .metabase_session      # sessão do Metabase (expira)
.venv/bin/python extract.py             # ~4 min, popula ./cache — roda uma vez
.venv/bin/python analyze.py             # ~40 s, gera ./output/qualidade_atendimento.xlsx
```

`extract.py` é a fase lenta (puxa 390 mil mensagens em blocos semanais para
Parquet). `analyze.py` roda só em cima do cache — é o loop de iteração da
fórmula. Pesos e cortes ficam todos no topo de `score.py`.

## Desenho

- **Janela:** 6 semanas completas (a semana em curso é descartada — semana
  parcial entra na matriz com denominador menor e distorce a correlação)
- **Estrato:** apenas leads respondidos em ≤30 min de expediente (22.722 de
  28.737). Segurando a velocidade constante, o que sobrar de correlação é
  atribuível à qualidade, não ao tempo de resposta
- **Matriz A:** unidade × semana → qualidade agregada
- **Matriz B:** unidade × semana → %CVS (metric 2589 = `sum(agend)/sum(leads_sec)`)
- **Correlação:** *pooled* (entre unidades) e *within-unidade* (efeito fixo, só
  variação semana a semana dentro da mesma unidade)

## Achados

### 1. `pct_bom` supera `score_medio` — a pergunta original, respondida

Contra a conversão lead-level, within-unidade:

| Métrica | Spearman | p |
|---|---|---|
| **% de atendimento bom** | **+0,231** | 0,0006 |
| Score médio | +0,142 | 0,036 |

A curva de decis tem forma de degrau (maior salto 15,3pp no decil 10, 5,7× a
média dos demais saltos), então o corte do "% bom" saiu do cotovelo — 0,800 —
e não de escolha a dedo. Isso importa: com liberdade para mexer no limiar,
acha-se correlação em qualquer lugar.

### 2. O %CVS oficial é alvo contaminado

| | |
|---|---|
| Agendamentos no %CVS (negócio) | 2.735 |
| Rastreáveis a estes leads (Chatwoot) | 1.659 |
| **Excedente não rastreável** | **+64,9%** |

O numerador do %CVS conta 65% mais agendamentos do que estes leads produziram —
inclui conversão que nunca passou pela secretaria. Os dois alvos correlacionam
entre si a apenas 0,50 (within).

Consequência: **contra o %CVS o score não correlaciona** (within +0,035, n.s.);
**contra a conversão lead-level da mesma célula, correlaciona.** Isso não é o
score falhando — é o alvo medindo outra coisa. Há um teto estrutural: parte da
variância do %CVS é inexplicável por qualidade de conversa, por construção.

### 3. Responsividade estava medindo o oposto (peso zerado)

Spearman **−0,143** contra conversão; decil 1 converte 18,6% e decil 10 converte
5,3%. `min_resposta_media_humana` é o intervalo médio *entre* respostas: conversa
longa e engajada se estende por horas com pausas naturais do lead, então a média
sobe. Troca curta que morre rápido tem média baixa. "Ritmo rápido" marca conversa
morta. Peso 0 na composição, mantida como diagnóstico.

### 4. Volume de conversa é o confundidor dominante

| Msgs do atendente | Leads | Conversão |
|---|---|---|
| 1 | 3.637 | 0,47% |
| 6–10 | 5.802 | 2,26% |
| 11+ | 4.714 | **31,01%** |

66× de diferença. `msgs_atendente` sozinho correlaciona +0,52 (within) com a
conversão lead-level — mais forte que qualquer score. Como lead interessado puxa
conversa, parte disso é o lead, não o atendente. Por isso existe
`qualidade_residual` (score menos o efeito de `log(msgs_atendente)`): é a parte
que **não** é tamanho de conversa. Ela não correlaciona — ou seja, o poder
preditivo do score vem majoritariamente do volume.

### 5. Mídia sem transcrição cega 57% da base

O fornecedor não entrega transcrição de áudio/imagem: essas mensagens chegam com
`content` nulo. 57% dos leads têm menos de 50% das mensagens do atendente
legíveis.

**Nada foi imputado.** Creditar etapas não observadas trocaria falso negativo por
falso positivo, e num experimento que testa justamente se qualidade prevê
conversão, o falso positivo contamina o achado: como mídia é mais comum nas
conversas engajadas (que já convertem), a imputação inflaria o score onde a
conversão já é alta e a correlação subiria por construção.

Em vez disso mede-se `visibilidade_textual` e estratifica-se:

| Visibilidade | Leads | Mídias | Msgs atend. | Conversão |
|---|---|---|---|---|
| 0–25% | 6.727 | 4,3 | 4,9 | 1,17% |
| 25–50% | 6.164 | 4,2 | 7,1 | 5,81% |
| 50–70% | 2.948 | 4,4 | 11,4 | 19,30% |
| 70–90% | 2.564 | 2,7 | 13,5 | **20,83%** |
| 90–100% | 4.319 | 0,1 | 3,9 | 3,40% |

Note a não-monotonicidade: **uso de mídia é marcador de atendimento humano
engajado.** A faixa sem mídia nenhuma (90–100%) tem 63,7% de conversas com
apenas 1–2 mensagens do atendente — texto curto e roteirizado, que converte 3,4%.
Penalizar mídia, que é o que um score puramente textual faz, é exatamente ao
contrário. Creditá-la seria a imputação circular. Por isso: medir e estratificar.

No estrato legível (≥70%), o score correlaciona +0,59 (Spearman pooled,
p=0,00004) com a conversão. O teste *within* nesse estrato tem só 42 células e
não tem poder para concluir.

## Limitações conhecidas

- **Papel da mensagem é aproximado.** `sender_id` não serve: 99,7% das saídas vêm
  da conta de integração "WhatsApp" (id 181). Usa-se o corte `primeiro_humano_em`,
  que reproduz `msg_humano` exato em 78% dos leads e com erro ≤1 em 88%.
- **Cobertura condicional corrige demais.** Ao não punir conversa curta, ela dá
  0,86 para quem chegou na etapa 2 e cobriu as duas. Perde o sinal de que
  *chegar longe* é o que converte. É a dimensão mais errática (Spearman +0,08).
- **Vocabulário de 78 termos**, herdado de `lead_score_output.trilha_evidencias`
  — foi reusado de propósito, para que a comparação com a métrica atual isole o
  método e não o dicionário.
- **`lsv_conversas` está vazia** (0 linhas); o transcript foi remontado de
  `conversations` + `messages`.
- Ausência de sinal ≠ ausência de efeito: o score pode estar mal construído.

## Arquivos

| | |
|---|---|
| `mb.py` | cliente Metabase somente-leitura |
| `extract.py` | extração → `cache/*.parquet` |
| `score.py` | fórmula (pesos e cortes no topo) |
| `analyze.py` | decis, matrizes, correlações, Excel |
| `vocab_atual.json` | vocabulário por etapa da trilha |
| `output/qualidade_atendimento.xlsx` | entrega, 12 abas |
