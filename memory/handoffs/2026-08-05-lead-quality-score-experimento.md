# Handoff — Experimento: Score de Qualidade de Atendimento vs Conversão

**Data:** 2026-08-05
**Máquina:** macbook-jpazv
**Projeto:** `~/dev/lead-quality-score` (novo, criado nesta sessão)
**Contexto:** análise de dados sobre o Metabase do Grupo Velas — **não é o Pulse**

---

## ⚠️ Antes de continuar em outra máquina

**O código existe SÓ no macbook-jpazv e não está em git.** `~/dev/lead-quality-score`
não é repositório e não foi publicado em lugar nenhum. Para continuar em outra
máquina é preciso primeiro decidir onde versionar (repo próprio no
Grupo-Velas? pasta no hub?) e subir. São ~1.200 linhas em 6 arquivos Python,
leves — o que pesa é `cache/` (26 MB de Parquet), que **não deve** ser
versionado: é regenerável com `extract.py` em ~4 min.

**Token de sessão do Metabase** fica em `~/dev/lead-quality-score/.metabase_session`
(chmod 600, gitignored). **Não commitar** — sessão do Metabase expira e não deve
ir para o GitHub. Renovar quando expirar.

---

## Objetivo

Descobrir o que explica a conversão de lead. Estado inicial declarado pelo
chefe: temperatura correlaciona 0,4 com conversão (~16% de explicação); somando
tempo de resposta ≤30min chegaria a ~50%. A peça que faltava era medir
**qualidade de atendimento** melhor que a métrica atual.

**Restrição dura:** nada é escrito no BD Grupo Velas. Sem tabela, sem view, sem
MV. Leitura apenas via API do Metabase. Fase de teste — se provar valor, aí se
discute materializar. Entrega em Excel.

Proposta original era workflow n8n; foi decidido fazer em Python local porque o
experimento exige loop rápido de iteração (ajustar peso → rodar → ver
correlação). n8n fica para quando a fórmula estiver provada e virar job
recorrente.

---

## Arquitetura

Duas fases separadas, e a separação é o ponto:

| Arquivo | Papel |
|---|---|
| `mb.py` | cliente Metabase somente-leitura, com guarda que bloqueia qualquer coisa que não comece com SELECT/WITH |
| `extract.py` | extração → `cache/*.parquet`, blocos semanais (~4 min, roda uma vez) |
| `score.py` | fórmula do score — **todos os pesos e cortes no topo do arquivo** |
| `analyze.py` | decis, matrizes unidade×semana, correlações, Excel |
| `regressao.py` | regressão múltipla e R² incremental |
| `comparativo.py` | temperatura vs qualidade, decomposição de comunalidade |
| `vocab_atual.json` | vocabulário por etapa da trilha, extraído do próprio `lead_score_output` |

`analyze.py` roda em ~40s sobre o cache. É o loop de iteração.

**Ambiente:** venv em `.venv` (Python 3.9 do sistema). Deps: pandas numpy pyarrow
scipy xlsxwriter requests openpyxl statsmodels.

---

## Descobertas sobre o schema (custaram tempo, não redescobrir)

- **`%CVS` = metric 2589** = `sum(agend)/sum(leads_sec)` sobre
  `mv_hibrida_unidade_propria` (via modelo card 2457). Só existe agregado por
  **dia × unidade** — não tem chave de lead.
- **Lead quente = `lead_score >= 0.60`** (card 12962 "Leads Quentes (60-100 pts)").
- **`lsv_conversas` está VAZIA** (0 linhas). O transcript pré-montado não existe;
  tem que remontar de `conversations` + `messages`.
- **`sender_id` NÃO identifica o atendente**: 99,7% das mensagens de saída vêm da
  conta de integração "WhatsApp" (id 181) + "Não direcionar" (id 1). Para separar
  bot de humano usa-se o corte `primeiro_humano_em` da MV — reproduz `msg_humano`
  exato em 78% dos leads, erro ≤1 em 88%.
- **`tb_leads_z_api` é tabela base** populada por ETL externo; a lógica de
  classificação bot/humano não está em SQL legível.
- **CSV do Metabase vem sem charset** → requests assume ISO-8859-1 e o português
  acentuado vira mojibake. `mb.py` força `resp.encoding = "utf-8"`. Sem isso, 67%
  das mensagens corrompem e o casamento de palavras quebra.
- **`modelo_evidencias` em `lead_score_output` é 100% NULL** nas 47.376 linhas.
- **`lead_score_output` só cobre a partir de 18/05/2026.**

---

## Desenho final

- Janela: 6 semanas completas (22/06 a 02/08). Semana em curso descartada.
- Estrato: leads com `min_ate_secretaria_expediente <= 30` → 22.722 de 28.737.
  Segura a velocidade constante para isolar qualidade.
- Matriz A: unidade × semana → qualidade. Matriz B: unidade × semana → %CVS.
- 229 células, 39 unidades. Chave `unidade` bate 100% entre as duas fontes.

**Fórmula:** `(0.30·cobertura + 0.35·profundidade + 0.00·responsividade +
0.35·condução) × gate_abandono`

---

## Resultados

### O que funcionou

- **`% de atendimento bom` supera `score médio`** — within-unidade contra
  conversão lead-level: **+0,231 (p=0,0006)** vs +0,142. Corte 0,800, derivado do
  cotovelo da curva de decis (degrau, salto de 15,3pp no decil 10), não escolhido
  a dedo.
- Zeros eliminados: 0,0% contra 25,2% da métrica antiga.
- **0,409 reproduzido:** % leads quentes × %CVS por unidade×semana dá Pearson
  **ponderado por volume +0,411 a +0,416** (excluindo semana parcial, célula
  mínima ~10-20 leads_sec).

### O que NÃO funcionou (e é o mais importante)

- **A qualidade agrega 0,48% de R² único** sobre a temperatura (within-unidade,
  conversão lead-level). Temperatura sozinha: 12,85%. Juntas: 13,33% — não somam,
  3,82pp são compartilhados.
- **No nível do lead, a qualidade agrega 0,00%** depois que volume de conversa
  entra no modelo. Coeficiente padronizado −0,0015 (p=0,40).
- **A métrica antiga bate a nova em correlação bruta no nível do lead**:
  Spearman +0,280 vs +0,203. Empatam só no nível unidade×semana.

### Os quatro achados que mudam o entendimento do problema

1. **Volume de conversa domina tudo.** 1 msg do atendente → 0,47% de conversão;
   11+ → **31,01%**. 66x. `msgs_atendente` sozinho dá +0,52 within — mais forte
   que qualquer score. Como lead interessado puxa conversa, parte disso é o lead,
   não o atendente. Criado `qualidade_residual` (score menos efeito de
   log-volume): **não correlaciona** — o poder do score vem do volume.

2. **O %CVS é alvo contaminado.** Numerador conta 2.735 agendamentos onde só
   1.659 são rastreáveis aos leads: **+65% de conversão que não passou pela
   secretaria**. Os dois alvos correlacionam entre si só 0,50. Contra %CVS o
   score não correlaciona; contra conversão lead-level, sim.

3. **Responsividade estava invertida** (Spearman −0,143). `min_resposta_media_humana`
   é o intervalo *entre* respostas: conversa longa e engajada tem pausas naturais
   e média alta; troca curta que morre tem média baixa. "Ritmo rápido" marca
   conversa morta. Peso zerado, mantida como diagnóstico.

4. **Mídia sem transcrição cega 57% da base**, e é a faixa que mais converte.
   Faixa 70-90% de visibilidade converte 20,8%; faixa sem mídia nenhuma converte
   3,4% (são conversas de 1-2 mensagens roteirizadas). **Uso de mídia é marcador
   de atendimento humano engajado.** Decisão tomada: medir `visibilidade_textual`
   e estratificar, **NÃO imputar** — creditar etapa não observada trocaria falso
   negativo por falso positivo, e num experimento que testa se qualidade prevê
   conversão o falso positivo contamina o achado (mídia é mais comum onde já
   converte → correlação subiria por construção).

### Alerta metodológico registrado

- O 0,409 é **frágil**: nos mesmos dados, Pearson simples vai de −0,157 (sem
  filtro) a +0,398 (≥50 leads). Troca de sinal. O número estável é o **Spearman:
  +0,32 a +0,36** em todas as variantes. Defender 0,33, não 0,41.
- Colapsando por semana (n=11, juntando unidades) a correlação vai a **+0,89**.
  Isso é inflação por agregação, não resultado melhor. Se alguém citar correlação
  muito alta, checar em que grão foi calculada.
- **Não reproduzimos o "quase 50%".** Tempo de resposta adiciona 0,04% sobre a
  temperatura no nível do lead e 2,10% único no nível de célula. Nenhum modelo
  passou de 36,97%. Provável que os 50% originais fossem bivariados ou em dado
  agregado. **Vale reconciliar — muda a linha de base do projeto.**
- Correlações por unidade individual (6 semanas cada) são **ruído**: com n=6
  precisa |r|>0,81 para significância. "Qualidade positiva em 20 de 37 unidades"
  é indistinguível de cara-ou-coroa.

---

## Entregas

`~/dev/lead-quality-score/output/`

| Arquivo | Conteúdo |
|---|---|
| `qualidade_atendimento.xlsx` | 12 abas: scores_lead (22.722 linhas), matrizes, correlações, curva de decis, visibilidade, confundimento, dicionário |
| `regressao_multipla.xlsx` | R² incremental, 4 abas |
| `comparativo_temp_qualidade.xlsx` | comunalidade temperatura×qualidade, por unidade |

Verificações feitas: `agend`/`leads_sec` batem exato com a fonte (2.967/28.737);
soma de leads bate com N das células; 20 conversas lidas nos extremos (score
1,000 é atendimento de manual, 0,020 é "não é nossa especialidade" e fim).

---

## Próximos passos sugeridos

1. **Reconciliar o "50%"** com o chefe — de onde veio, em que grão. Muda a
   baseline.
2. **Cobrar transcrição de mídia do fornecedor.** 57% da base cega, justamente
   onde converte. O número desta análise é o argumento comercial.
3. **Estender a janela** até 18/05 (limite do `lead_score_output`) para ter ~11
   semanas — análise por unidade precisa de ~20 semanas, hoje impossível.
4. Só depois refinar a fórmula. Refinar peso em cima de 43% de visibilidade é
   otimizar no escuro. A dimensão `cobertura` é a mais fraca (+0,08): a correção
   condicional que impede punir conversa curta corrige demais e apaga o sinal de
   que *chegar longe* é o que converte.
