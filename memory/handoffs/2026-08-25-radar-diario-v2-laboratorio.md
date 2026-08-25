# Handoff — Aba 📡RADAR: seção Diário v2 no Laboratório (dash 316)

**Data:** 2026-08-25
**Sessão:** Claude Code (mac-grupovelas)
**Projeto:** Metabase dashboards — Grupo Velas
**Issue:** [#282](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/282) — `[Tráfego Pago] Aba RADAR` (OPEN, Em andamento)
**Dashboard:** 316 📈 Tráfego Pago · aba de staging `🧪 Laboratório` (955)

---

## 1. Estado ao fim da sessão

Aba **955 (Laboratório)** — 9 dashcards, 5 cards, todos `(rascunho)`:

| dashcard | card | row | o que é |
|---|---|---|---|
| 20318 | **13734** | 9  | Leads · Real / Saldo / Meta |
| 20319 | **13735** | 9  | Agend. · Real / Saldo / Meta |
| 20331 | **13736** | 12 | Investimento: real x cobrado x meta |
| 20329 | **13737** | 18 | Leads x Meta |
| 20330 | **13738** | 24 | Agendamentos x Meta |
| 20347 | — | 30 | heading órfão da fase 3 (tabela foi descartada pelo JP) |

**Os 5 cards respondem a 2 filtros:** `Unidades` (`59d9c347`) e
`Agrupamento de tempo` (`cc765c0a`, temporal-unit, default `day`).

Contagem por aba ao fim: Tráfego 20 · Financeiro 7 · Criativos 3 · Alertas 5 ·
📡RADAR 18 · Laboratório 9 · 14 parâmetros. **Nenhum dashcard do backup sumiu.**

A aba **943 (📡RADAR) de produção NÃO foi tocada** nesta sessão.

---

## 2. A descoberta técnica principal

**Parâmetro `temporal-unit` FUNCIONA em card native (SQL).** Não precisa ser
question GUI.

Isso não tinha precedente na casa: os **18 cards** amarrados a um `temporal-unit`
no dash 316 e no dash 10 são todos `tipo=query` (MBQL). Testei antes de construir,
com um card descartável (`13730`, já arquivado):

- template-tag `{{gran}}` do tipo `text`
- mapping do dashcard: `{"parameter_id":"cc765c0a","target":["variable",["template-tag","gran"]]}`
- no SQL: `date_trunc({{gran}}, dia)` — o Postgres aceita a unidade como string
- o PUT aceita o mapping e a query roda (`quarter` → 2 períodos, `month` → 4)

Metabase **v0.55.3**.

### Limites descobertos

- **`semester` não existe** no `date_trunc` do Postgres. Dá pra derivar
  (`date_trunc('year',d) + (quarter>2)*interval '6 months'` — testado, funciona),
  mas o **widget temporal-unit do Metabase também não oferece essa opção**. Só
  com um filtro customizado `string/=` de lista estática.
- Ficou fora por decisão do JP: **só dia, semana e mês**, porque a
  `mv_mkt_outcomes_diario` só tem lead a partir de **20/05/2026** (a MV vai de
  01/05 a 01/10, mas as linhas anteriores a 20/05 têm meta e zero lead).
  Trimestre daria 2 barras, uma incompleta. O SQL degrada sem erro se alguém
  escolher trimestre/ano, mas a leitura não se sustenta.

---

## 3. Decisões de modelagem (o "porquê", que é o que não se recupera do SQL)

### 3.1 🔴 `invest_total_sem`, NUNCA `invest_total_com`

Errei isso na primeira versão e só peguei cruzando com a Projeção `13581`:
realizado da rede deu **R$ 457.640** contra os **R$ 448.100** dela.

Não é cosmético: com a coluna errada a rede aparece *exatamente no plano*
(`-R$ 498`); com a certa está **2,2% abaixo** (`-R$ 10.037`).

**A causa raiz é documentação errada, não descuido:** o **§4 do DOC do Radar**
(comentário do Ernandes de 21/08 na #282) diz que `CPL`/`CPAg` vêm de
`invest_total_com`. Conferi os cards: `13576` (Radar), `13585` e `13586`
**todos usam `invest_total_sem`**. Os cards estão certos, o DOC mente — e o DOC
é a primeira coisa que se lê antes de construir.

> **A §4 da issue #282 precisa ser corrigida.** Não fiz porque não é meu texto.

A regra está escrita na linha 104 do SQL do semanal `13669`:
`-- Investimento usa invest_total_sem (nacional abatido da contribuicao das franquias), NUNCA invest_total_com.`

### 3.2 Saldo contra a meta do MESMO intervalo

Os scalars antigos (`13579`/`13580`) comparavam o realizado acumulado contra a
**meta cheia do mês**. No dia 24 de 31 isso é estruturalmente negativo e não
carrega sinal. Caso real: Tatuapé aparecia `742 / -125 / 867` (vermelho) quando
estava **+71 adiantado** no ritmo; agendamento aparecia `-38` estando `-16`.
Os dois pareciam o mesmo problema e não eram.

Regra final: **realizado e meta cortam no mesmo intervalo** — do início do
período até hoje inclusive. Assim o saldo é sinal de ritmo em qualquer
granularidade, e em `day` o comportamento é idêntico ao que o JP validou.

### 3.3 A régua de ritmo é um `SUM`, não uma contagem de dias úteis

`meta_agendamentos` já vem **0,00 em sábado e domingo** e `meta_leads` vem flat
todo dia. Então `SUM(meta_*) WHERE dia < CURRENT_DATE` já produz a convenção do
RPD (agendamento por dias úteis, lead por dias corridos) **sem contar dia útil,
sem `generate_series`, sem projetar**. Conferido: 71,84 no Tatuapé = 16 dias
úteis × 4,49.

### 3.4 Meta NULL em vez de 0 no fim de semana

Emitir `0` fazia a linha tracejada de agendamentos **despencar toda semana**.
Emitimos `NULL` + `line.missing: "interpolate"` → a linha atravessa reta, sem
ponto e sem rótulo. Padrão copiado da série `Meta Agendamentos Diária` do
card **88** (dash 10).

### 3.5 Corte em junho + marcação `(parcial)`

- `(parcial)` — período em curso; a meta dele também é parcial, para a barra ser
  comparável à linha em vez de parecer queda falsa.
- **A série dos 3 gráficos começa no primeiro mês COMPLETO da base: junho/2026.**
  Maio tem meta cheia desde 01/05 e primeiro dado real em **20/05** (leads, agend
  e investimento, os três) — 8.268 leads contra meta de 18.885, ou seja aparecia
  como fracasso de 44% sendo 12 dias de dado. Decisão do JP em 25/08.
- 🔴 O corte usa `min(dia)` **GLOBAL, sem o filtro de unidade**. Se fosse por
  unidade, uma com dado recente (ITC Guararapes, lead só desde 18/08) empurraria
  o corte para frente e ficaria sem série nenhuma. Conferido: Guararapes mantém
  3 períodos no mês.
- Sem data fixa no SQL (`date_trunc('month', min(dia)) + INTERVAL '1 month'`) —
  auto-ajusta se a base ganhar histórico.
- Na prática o corte só morde em `month` (4 → 3 períodos). As janelas de `day`
  (30 dias) e `week` (12 semanas) já começavam depois de junho.

### 3.6 Cobrado da `mv_mkt_financeiro`

`gasto_distribuido` é **mensal**, rateado por dia na proporção do real, com
🔴 **fator POR UNIDADE aplicado ANTES de somar as unidades** (CTE `bu`) — mesma
mecânica do semanal `13670`. Agrupar só por período pegaria o fator de uma
unidade arbitrária e o total não fecharia.

Invariante conferido (Σ cobrado = Σ real com todas as unidades):
`month -0,0015%` · `day +0,14%` · `week -0,54%`. O desvio sub-mensal é esperado
e já está documentado na legenda do semanal (o fator é mensal, o mix de unidades
da semana difere do mix do mês).

⚠️ **No dia, a barra do cobrado é a do real vezes uma constante do mês** — mesma
forma, altura diferente. Informa o NÍVEL (quanto a unidade absorve do nacional),
não o movimento diário.

### 3.7 %CVS projetada (card foi descartado pelo JP, mas a fórmula fica registrada)

Convenção dos cards `11425`/`11428` do dash 10:
```
proj leads = realizado ÷ dias CORRIDOS decorridos × dias corridos totais
proj agend = realizado ÷ dias ÚTEIS   decorridos × dias úteis totais
%CVS projetada = proj agend ÷ proj leads
```
"Dia útil" = dia com `meta_agendamentos > 0` (respeita como a meta foi cadastrada,
inclusive feriado) em vez de `isodow < 6`.

**Validado:** aplicado à rede, o método reproduz exatamente a Projeção do card
`13581` — 24.276 leads e 2.288 agendamentos.

⚠️ Trocar o "esperado" do Lead Score pelo alvo implícito **inverte o veredito**:
o card antigo mostrava `7,5% real / 6,5% esperada` (bom); contra o alvo fica
`7,5% / 10,9%` (ruim). O Lead Score responde "esses leads deveriam converter
quanto?"; a meta responde "o negócio precisa de quanto?".

---

## 4. Achado de negócio: 31% dos leads chegam em dia sem meta de agendamento

Rede, agosto/2026, mês corrente até ontem:

| | leads | % do total | agend. | %CVS | investimento |
|---|---|---|---|---|---|
| dia útil | 12.985 | 69,1% | 1.683 | **12,96%** | R$ 300.466 |
| fim de semana | 5.809 | **30,9%** | 60 | **1,03%** | **R$ 147.634** |

**R$ 147 mil de mídia rodando em dias que convertem a 1%.**

No Tatuapé é pior: **35,9 leads/dia no fim de semana contra 28,4 no dia útil** —
chega *mais* lead no sábado — e 287 leads de fim de semana geraram 2 agendamentos.

Isso **reescreve o diagnóstico da unidade**: o %CVS cheio de 7,5% parece problema
de conversão, mas no dia útil o Tatuapé converte a **11,87%**, *acima* do alvo de
10,87%. O que derruba a média é o terço dos leads que cai em dia sem meta.

Só aparece na granularidade diária — o semanal agrega seg–dom num balde só e
apaga o efeito.

---

## 5. ⚠️ Incidente: card foi parar na Lixeira durante a sessão

O card Ritmo (`13712`) sumiu da aba durante um script de reconstrução —
`archived: true`, `collection_id: 1`.

**Não consegui determinar a causa.** Duas explicações cabem:
1. O comportamento não-determinístico já documentado em `memory/best-practices.md`
   (commit `9409981`, 24/08): *"PUT numa dashboard question a DESANEXA e manda pra
   Lixeira, mesmo que o payload não mencione dashboard_id nem collection_id... no
   mesmo lote, alguns cards sobrevivem e outros não."* O script fez 7
   `PUT /api/card` de arquivamento e o `13712` **não estava entre eles**.
2. Edição concorrente pela UI. Há indício: a nota da aba encolheu de 26 para 8
   linhas e os scalars viraram um 2×2 irregular, nada disso feito por script.

**A falha real foi de verificação:** o diff de integridade comparava contra o
backup original, então nunca enxergaria um card *de laboratório* sumindo.

### Protocolo corrigido (usar daqui pra frente)

```
1. capturar o conjunto de card_id da aba ANTES
2. POST dos cards novos
3. GET → identificar e remover órfãos (POST com dashboard_id auto-pendura na 1ª aba)
4. PUT do dashboard (tabs + dashcards + parameters juntos)
5. VERIFICAR que nada sumiu — abortar se sumiu
6. só então arquivar os antigos, UM DE CADA VEZ
7. reverificar a aba depois de CADA arquivamento
```
Rodou limpo nas 4 levas seguintes: `sumiram: nenhum` em todas.

---

## 6. Arquivos

**Nenhum arquivo de código do repo foi alterado.** Tudo via API do Metabase.

SQLs versionados em
`/private/tmp/claude-501/-Users-grupovelas-Documents/56f8d656-.../scratchpad/sql/`
(⚠️ scratchpad é efêmero — se for promover, recuperar o SQL dos próprios cards):

| arquivo | card |
|---|---|
| `x1_leads.sql` / `x2_agend.sql` | 13734 / 13735 (scalars com granularidade) |
| `w1_leads.sql` / `w2_agend.sql` / `w3_invest.sql` | 13737 / 13738 / 13736 (gráficos, corte em junho) |
| `h_cvs_proj.sql` | %CVS projetada (card descartado, fórmula validada) |
| `t_diaria.sql` | tabela diária (descartada pelo JP) |

Backup: `BACKUP_dash316_20260825.json` (dashboard inteiro, antes de tudo).

**Cards arquivados nesta sessão** (todos rascunhos, na Lixeira):
13706 13707 13708 13709 13710 13711 13712 13713 13714 13715 13716 13717 13718
13719 13720 13721 13722 13725 13726 13727 13730 13731 13732 13733

---

## 7. Pendências

### Desta sessão
- [ ] **JP valida a aba 955 na tela** (era o combinado: "amanhã validarei")
- [ ] Heading órfão da fase 3 (dashcard `20347`, row 30) — remover
- [ ] Decidir se promove para a 943 e o que substitui: os gráficos novos entram no
      lugar de `13578` (Diário, que tem a linha do Lead Score) e `13585`
- [ ] **Corrigir a §4 da issue #282** — `invest_total_com` → `invest_total_sem`
- [ ] Atualizar §7 e §14 da #282: descrevem 15 dashcards e o card `13577`, que foi
      arquivado em 24/08 e substituído por `13669`–`13672`

### ⚠️ Conflito a alinhar antes de promover
O Ernandes pediu em 18/08 na #282, explicitamente: *"Não exibir o dado do último
dia; mostrar Realizado / Faltante / Meta referentes ao mês completo"*. A decisão do
JP nesta sessão **inverte isso** (granularidade do dia / período corrente).
Alinhar com ele, senão vira ida e volta.

### Dívida anterior que continua aberta
- [ ] **A reconstrução do semanal de 24/08 nunca teve handoff.** `13577` foi
      arquivado e substituído por `13669`–`13672`. Está descrito só na legenda
      dentro do dashboard (dashcard `19935`), nem na issue nem no hub.
- [ ] Os 7 pontos abertos do §15 do DOC seguem abertos, entre eles: backfill do
      ITC Guararapes (lead só a partir de 18/08), `Santos - 2` (429) com R$ 68 mil
      sem meta cadastrada, `meta_cpl` inflada 10–30x no Instituto Trata.
- [ ] 5 filtros mortos na aba 943 — **decidido nesta sessão: ficam inertes**. Só
      `Unidades` deve funcionar. Parâmetro no MB 0.55 é global às abas, então não
      dá pra escondê-los por aba de qualquer forma. Já documentado na legenda.

---

## 8. Próximo passo concreto

1. JP valida a aba 955 na tela (dia/semana/mês × filtro de unidade)
2. Se aprovar: promover para a 943 **substituindo o SQL/visualização no mesmo id
   dos cards de produção** (convenção do §11 do DOC), tirando o sufixo `(rascunho)`
3. Reescrever a seção `## Diário` da legenda (dashcard `19935`) — hoje ela ainda
   descreve os 4 números antigos, o `Esperado vs Projetado` e a linha do Lead Score
4. Comentar na #282 com o resultado + as correções de §4/§7/§14

## Acesso

- Base: `https://metabase.grupovelas.com.br` · header `X-Metabase-Session`
- Aba: `https://metabase.grupovelas.com.br/dashboard/316-trafego-pago?tab=955`
- Regra que vale sempre: **somente SELECT** no banco analítico
