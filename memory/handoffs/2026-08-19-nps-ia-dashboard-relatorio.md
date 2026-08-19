# Handoff — NPS IA: Dashboard + Relatório Automático

**Data:** 2026-08-19 (atualizado)
**Sessão:** Dashboard NPS com dados de IA + geração de relatórios por unidade
**Máquina:** mac-grupovelas

---

## Contexto

Workflow de IA (Gemini Flash via OpenRouter) classificou ~1829 comentários NPS com sentimento, áreas (13 categorias v3.0.0), temperatura, dor e elogio. Coluna `ia_analise` (jsonb) na tabela `public.nps`. Backfill parou na rodada 12 (~1200 feitos, ~810 pendentes → verificar se user rodou de novo). Query usa `ia_analise IS NULL` então continua de onde parou.

## O que foi feito

### 1. Dashboard NPS - Análise IA (Teste)
- **Dashboard 387** na collection **Testes** (id 576)
- 11 cards criados, todos com `dashboard_id: 387` (não poluem collection)
- Cards: 13597 (NPS Score scalar), 13600 (Comentários Analisados), 13601 (% Alertas), 13598 (Sentimento bar), 13599 (Áreas bar), 13602 (Temperatura bar), 13603 (Alertas table), 13604 (Dores Recorrentes table com agrupamento CASE WHEN), 13605 (Sentimento por Marca bar), 13606 (Áreas por Marca bar), 13607 (Evolução Mensal line)
- Card 13604 (Dores) agrupa texto livre em 10 clusters via SQL CASE WHEN (Preço/Custo=212, Espaço Físico=64, Equipamentos=55, etc.)
- **PROBLEMA**: user quer REFAZER o dashboard usando as metrics de Dados Gerais como base (ver seção abaixo)

### 2. Relatório visual (Artifact)
- Artifact gerado: https://claude.ai/code/artifact/073e4e86-b91f-4228-a367-f525ea92b6b3
- ITC SBC e Trata Jundiaí — formato visual, NÃO é o formato final

### 3. Relatório textual (PENDENTE)
- User quer relatório no formato dos documentos .docx (só texto, sem visual)
- 6 documentos modelo em `~/Downloads/` (convertidos para .txt no scratchpad)
- Formato: Título → NPS TRATAMENTO (Visão Geral + Sentimento) → NPS AVALIAÇÃO (idem)
- Dados já extraídos para ITC SBC e Trata Jundiaí (ver sessão anterior)

### 4. Workflow n8n "NPS - Relatório por Unidade" (EM ANDAMENTO)
- **Arquivo**: `~/Downloads/NPS - Relatorio por Unidade.json`
- **Arquitetura**: 3 fluxos webhook separados:
  1. **Front público** (`/nps-relatorio-unidade`): auth JWT → chama interno → lista unidades OU detalhe
  2. **Front interno** (`/nps-relatorio-unidade-interno`): SQL busca unidades elegíveis (≥40 comentários), renderiza lista ou página de detalhe com botão "Gerar Relatório"
  3. **Gerador** (`/nps-relatorio-gerar`): auth JWT → busca comentários da unidade → monta prompt → OpenRouter (Gemini 3.7 Flash) → renderiza HTML bonito com glassmorphism/dark theme

#### Bug encontrado — "column undefined does not exist"
- **Nó**: "Buscar Comentarios Unidade"
- **Causa**: A expressão `{{ $('NPS Relatorio - Gerar Interno').first().json.query.id_interno }}` resolve como `undefined` quando o parâmetro não vem na URL
- **Fix**: trocar por `{{ Number($('NPS Relatorio - Gerar Interno').first().json.query.id_interno) || 0 }}` (mesmo padrão do nó "Buscar Unidades Elegiveis" que funciona)

#### Pedido do user
- **Quer abrir direto no relatório completo** ao clicar na unidade, sem etapa intermediária de "página de detalhe + botão Gerar"
- Ou seja: lista → clica → já abre o relatório gerado pela IA

## Modelo NPS em Dados Gerais (Metabase)

O user quer que o dashboard use as mesmas métricas/modelo que já existem em Dados Gerais:

- **Collection**: Dados Gerais (id 13) → NPS (id 166)
- **Modelo (dataset 2098)**: "Modelo de NPS" — query builder sobre `public.nps`, tem campo calculado "Cálculo" (promotor/neutro/detrator)
- **Metrics existentes**:
  - 2100: NPS - Respostas (COUNT sobre modelo)
  - 2101: NPS - Promotor (COUNT WHERE Cálculo contains "promotor")
  - 2102: NPS - Detrator (COUNT WHERE Cálculo contains "detra")
  - 2103: NPS - Comentários (COUNT WHERE comentario not-empty)
  - 2104: NPS - NPS (fórmula: promotor/respostas - detrator/respostas)
- **Implicação**: ao refazer o dashboard, usar `source-table: "card__2098"` e referenciar as metrics 2100-2104 ao invés de queries SQL brutas

## Próximos passos

1. **Fix imediato**: corrigir `undefined` no nó "Buscar Comentarios Unidade" do workflow n8n
2. **Refazer dashboard 387**: usar metrics de Dados Gerais (2098-2104) como base, adicionar cards de IA em cima
3. **Simplificar fluxo**: lista → clica → relatório direto (sem página intermediária)
4. **Gerar relatório textual**: formato .docx para ITC SBC e Trata Jundiaí

## Pendências adicionais

1. Backfill NPS: verificar se ~810 pendentes foram processados
2. Workflow pós-backfill: adicionar filtro 7 dias (opcional, impacto negligível sem)
3. NPS Juazeiro: fix "Formatar unidade", UPDATE órfãos, DELETE teste
4. Metabase sync: user precisa sincronizar schema no Admin para ver `ia_analise` na UI

## Decisões tomadas

- Dores agrupadas via SQL CASE WHEN (10 clusters) — user preferiu "deixar assim por enquanto"
- Dashboard na collection Testes (576)
- Relatório deve ser textual puro — "apenas palavras seguindo rigorosamente com os modelos"
- Workflow usa OpenRouter com Gemini 3.7 Flash (chave embutida no JSON)
