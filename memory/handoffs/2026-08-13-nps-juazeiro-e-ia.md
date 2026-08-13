# Handoff: NPS — Juazeiro + Análise de IA

**Data:** 2026-08-13
**Solicitante:** Ernandes Lima
**Issues:** #269 (Juazeiro, em andamento), #270 (IA nos comentários)

---

## Overview do workflow NPS

**Workflow:** `NPS - João Paulo` (cópia inativa do original do Ernandes)
**Editor:** `https://connect.grupovelas.com.br/workflow/aUmhVvVMK7RLpJWN`
**Frequência:** a cada 20 minutos (Schedule Trigger)
**Credenciais:** Google Sheets OAuth2 (Ernandes) + Postgres BD Velas

### Fluxo (13 nós)

```
Schedule Trigger (20min)
  ├─> Get row(s) ── DataTable n8n "ids_nps"
  │     Lista de planilhas: cada row tem {sheets_id, table}
  │     "table" = nome da aba na planilha (ex: "ITC", "Trata")
  │
  ├─> Select rows from a table ── dim_unidades (Postgres)
  │     Pega todas as unidades com {id, unidade}
  │     → Edit Fields1 (renomeia id → id_interno)
  │     → vai pro Merge (input 2)
  │
  └─> Loop Over Items (itera cada planilha da DataTable)
        │
        └─> Get row(s) in sheet ── Google Sheets
              Lê planilha {sheets_id} aba {table}
              │
              └─> If1 (Data não vazia?)
                    │
                    └─> Edit Fields (mapeia colunas: Unidade, Nota, Data, 
                          Comentário, Status, atendimento_recepcao,
                          fisioterapeuta_ouviu, fisio_tecnicas, 
                          estrutura_clinica, Comentário Pesquisa)
                          │
                          └─> volta pro Loop Over Items
                                │
                                └─> If (unidade notEmpty OR Comentário notEmpty)
                                      │
                                      └─> Remove Duplicates (por todos os campos exceto row_number)
                                            │
                                            └─> Formatar unidade (Code node — JavaScript)
                                                  Mapeamento de nomes:
                                                  - Prefixo: row_number contém "ITC" → "ITC Vertebral"
                                                             row_number contém "Trata" → "Instituto Trata"
                                                  - Substituições especiais:
                                                    Batel → Curitiba
                                                    Barueri → Alphaville
                                                    Niterói → Niterói - RJ (só ITC)
                                                    Savassi → BH - Savassi (só ITC)
                                                    Boa Vista → Porto Alegre - Boa Vista (só ITC)
                                                    Bélem/Belém → Belém - PA (só ITC)
                                                    Goiânia → Goiânia - Setor Marista (só ITC)
                                                    São Luís → São Luis (só ITC)
                                                  - NÃO TEM: Juazeiro do Norte (!!!)
                                                  - Caso padrão: Prefixo + " - " + Unidade
                                                  │
                                                  └─> Merge (enrich com dim_unidades por "unidade")
                                                        │
                                                        └─> UPSERT em public.nps
                                                              Match por "id" (ex: "1563 - Trata")
                                                              Campos: nota, data, comentario, status,
                                                              id_interno, atendimento_recepcao,
                                                              fisioterapeuta_ouviu, fisio_tecnicas,
                                                              estrutura_clinica, comentario_pesquisa
```

### ID do registro NPS

O `id` é composto: `{row_number} - {table}` onde row_number vem da planilha (número da linha na aba) e table é o nome da aba (ITC/Trata). Exemplos: `1563 - Trata`, `2230 - ITC`.

### Tabela destino: `public.nps`

| Coluna | Tipo | Fonte |
|---|---|---|
| id | text (PK, upsert key) | `row_number - table` |
| nota | integer | Coluna "Nota" da planilha |
| data | timestamp | Coluna "Data" da planilha |
| comentario | text | Coluna "Comentário" |
| status | text | Coluna "Status" |
| id_interno | bigint | JOIN com dim_unidades por nome |
| atendimento_recepcao | text | Pergunta sobre recepção |
| fisioterapeuta_ouviu | text | Pergunta sobre escuta |
| fisioterapeuta_tecnicas_tratamento | text | Pergunta sobre técnicas |
| estrutura_clinica | text | Pergunta sobre estrutura |
| comentario_pesquisa | text | Coluna "Comentário Pesquisa" |

---

## Diagnóstico: por que Juazeiro não cadastra

### Causa provável (95% de certeza)

O nó **"Formatar unidade"** (Code node) faz mapeamento de nomes. Ele tem tratamento especial para: Batel→Curitiba, Barueri→Alphaville, Niterói→Niterói-RJ, Savassi→BH-Savassi, Boa Vista, Belém, Goiânia, São Luís.

**Juazeiro do Norte NÃO tem mapeamento especial.** Se o nome na planilha é "Juazeiro do Norte" e a aba é "ITC", o case padrão gera `ITC Vertebral - Juazeiro do Norte`. Isso DEVERIA funcionar porque `dim_unidades` tem exatamente `ITC Vertebral - Juazeiro do Norte` (id=267).

### Causa alternativa

O problema pode estar ANTES do mapeamento:

1. **A DataTable `ids_nps`** pode não ter a planilha de Juazeiro (se cada unidade tem sua própria planilha/aba)
2. **A planilha de Juazeiro pode não existir** ou o sheets_id pode estar errado
3. **A coluna "Unidade" na planilha pode estar vazia** para Juazeiro, fazendo o If (unidade notEmpty OR Comentário notEmpty) falhar se comentário também estiver vazio
4. **O nome na planilha pode ser diferente** (ex: "Juazeiro" sem "do Norte"), gerando `ITC Vertebral - Juazeiro` que não bate com `dim_unidades`

### Para confirmar

Preciso acessar:
- A **DataTable `ids_nps`** no n8n (id: `jzV9ApCq4atCsmWd`) — ver se tem Juazeiro listado
- A **planilha Google Sheets** correspondente — ver como "Unidade" está preenchida

Sem credenciais do n8n/Google não consigo acessar nenhum dos dois.

### O que dá pra fazer via Metabase

- ✅ Confirmar que Juazeiro (id_interno=267) tem ZERO registros na tabela `nps`
- ✅ Confirmar que `dim_unidades` tem `ITC Vertebral - Juazeiro do Norte` (id=267)
- ✅ Entender o schema completo da tabela `nps`
- ✅ Verificar 55 unidades cadastradas, ~4.100 registros total
- ❌ Não consigo ler a DataTable do n8n
- ❌ Não consigo ler a planilha Google Sheets
- ❌ Não consigo executar o workflow

---

## Problema 2: Análise de IA nos comentários (issue #270)

### Ideia

Adicionar um nó entre "Merge" e "UPSERT" que:
1. Pega o campo `comentario` e/ou `comentario_pesquisa`
2. Manda pra uma LLM (Claude API ou OpenAI)
3. Retorna: sentimento, temas, alerta (sim/não)
4. Salva os resultados em colunas novas na tabela `nps`

### Implicações de schema

Precisaria de colunas novas na `public.nps`:
- `sentimento` (text: positivo/neutro/negativo)
- `temas` (text[] ou jsonb)
- `alerta` (boolean)
- `analise_ia` (text — output completo)

### Dependência

Resolver Juazeiro primeiro (#269). A análise de IA (#270) pode ser feita depois, independente.

---

## O que o JP precisa fazer (passos práticos)

### Para resolver Juazeiro (#269)

1. **Acessar a DataTable `ids_nps` no n8n** — verificar se Juazeiro está listado
   - URL: connect.grupovelas.com.br → projeto PQ0A9ifGldK6O7eJ → datatables → jzV9ApCq4atCsmWd
   - Se não estiver: adicionar row com o sheets_id e table corretos
   - Se estiver: o problema é na planilha ou no mapeamento

2. **Abrir a planilha Google Sheets de Juazeiro** — verificar:
   - A coluna "Unidade" tem valor? Qual? ("Juazeiro do Norte"? "Juazeiro"?)
   - A coluna "Data" está preenchida? (se vazia, o nó If1 descarta)

3. **Se o nome na planilha for diferente** (ex: "Juazeiro" sem "do Norte"):
   - Adicionar um case no nó "Formatar unidade":
     ```javascript
     } else if (unidadeModificada === 'Juazeiro' || unidadeModificada === 'Juazeiro do Norte') {
         novoNome = prefixo + ' - Juazeiro do Norte';
     }
     ```

4. **Trocar credenciais** antes de ativar:
   - Google Sheets OAuth2: precisa de client ID + secret do Google Cloud Console (pedir ao Ernandes)
   - Postgres: já tem `Postgres - BD Velas` (id: zSuxDy2EHKaKRRql) — provavelmente já existe na instância

### Para a análise de IA (#270)

Depois de Juazeiro resolvido:
1. Adicionar nó Claude/OpenAI entre Merge e UPSERT
2. ALTER TABLE nps ADD COLUMN sentimento text, temas jsonb, alerta boolean, analise_ia text
3. Mapear os campos novos no nó UPSERT

---

## Sessão de hoje — outras entregas

### Dashboard 384 — [TESTE] Análise Trimestral (mv_venda_propria)

- 4 cards SQL nativo (13545-13548) replicando dash 286
- Validação: 155/156 comparações exatas (0,00%), 1 com +0,4%
- Filtros Data (mês/ano) e Marca (dropdown) funcionais
- Issue #268, status: Em validação

### Artifacts publicados

- **Porta Pra Dentro** — framework storytelling lead→agendamento (artifact 4c4d4d34)
- **Lead Score Velas** — documento visual com anatomia, evidências, propostas (artifact e46002ea)
- **Lead Score Velas.docx** — ~/Downloads/ (versão doc para Google Docs)
