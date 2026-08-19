# Handoff — NPS IA: Dashboard + Relatório Automático

**Data:** 2026-08-19
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

### 2. Relatório visual (Artifact)
- Artifact gerado: https://claude.ai/code/artifact/073e4e86-b91f-4228-a367-f525ea92b6b3
- ITC SBC (NPS 70, 214 respostas) e Trata Jundiaí (NPS 86, 178 respostas)
- Formato visual com métricas, barras, comentários destacados — NÃO é o formato final

### 3. Relatório textual (PENDENTE — tarefa interrompida)
- User quer relatório no formato dos documentos .docx que enviou (só texto, sem visual)
- 6 documentos de referência lidos e convertidos em `/private/tmp/claude-501/-Users-grupovelas/efff2d1f-46e1-43a1-923b-7bd03c6a8a15/scratchpad/*.txt`
- Formato identificado:
  - Título: "ANÁLISE DA NPS [UNIDADE] [PERÍODO]"
  - Separado em **NPS TRATAMENTO** e **NPS AVALIAÇÃO** (campo `status` na tabela)
  - Cada seção: 1. Visão Geral (total, com/sem comentário, distribuição promotores/neutros/detratores com contagens e %) → 2. Análise de Sentimento (positivos com resumo + exemplos, sugestões com exemplos, negativos com ID/Nota/texto/dor, neutros)
- **TODOS os dados já foram puxados** para as duas unidades (ITC SBC e Trata Jundiaí), separados por status:
  - ITC SBC Tratamento: 121 total, 58 com comentário, 98 promotores, 14 neutros, 9 detratores | Sentimento: 23 pos, 23 sug, 7 neu, 4 neg
  - ITC SBC Avaliação: 93 total, 48 com comentário, 67 promotores, 20 neutros, 6 detratores | Sentimento: 17 sug, 14 neu, 11 pos, 5 neg
  - Trata Jundiaí Tratamento: 113 total, 69 com comentário, 105 promotores, 7 neutros, 1 detrator | Sentimento: 45 pos, 20 sug, 3 neu, 1 neg
  - Trata Jundiaí Avaliação: 65 total, 30 com comentário, 54 promotores, 6 neutros, 5 detratores | Sentimento: 11 neu, 9 sug, 8 pos, 2 neg
- Comentários negativos e sugestões com dor já extraídos (ver contexto da sessão)
- Comentários positivos (top 5 por tamanho) já extraídos

## Próximo passo imediato

**Gerar o relatório textual** seguindo rigorosamente o modelo dos .docx. Apenas texto corrido, sem visual. Dois relatórios: ITC SBC e Trata Jundiaí. Cada um com seções NPS Tratamento e NPS Avaliação. Dados já estão todos disponíveis — é só montar o texto.

## Pendências adicionais

1. **Backfill NPS**: verificar se os ~810 pendentes foram processados (user ia rodar de novo)
2. **Workflow pós-backfill**: trocar query do nó "Buscar comentários" para adicionar `AND data >= CURRENT_DATE - INTERVAL '7 days'` (user pode deixar sem, impacto é negligível)
3. **NPS Juazeiro**: aplicar fix "Formatar unidade" no workflow de produção do Ernandes, UPDATE 42 órfãos, DELETE registros de teste
4. **Metabase sync**: user precisa sincronizar schema no Admin para ver `ia_analise` na UI
5. **Automação futura**: transformar geração de relatório em processo automático (workflow n8n ou script) — o "pulo do gato" segundo o user

## Arquivos relevantes

- Documentos modelo: `~/Downloads/ANÁLISE DA NPS *.docx` e `~/Downloads/analise nps *.docx` (6 arquivos)
- Workflow backfill: `~/Downloads/NPS - Extração IA (backfill).json`
- Scratchpad com conversões .txt: `/private/tmp/claude-501/-Users-grupovelas/efff2d1f-46e1-43a1-923b-7bd03c6a8a15/scratchpad/`

## Decisões tomadas

- Dores agrupadas via SQL CASE WHEN (10 clusters) ao invés de corrigir no prompt do Gemini — user preferiu "deixar assim por enquanto"
- Dashboard criado na collection Testes (576), não em produção
- Relatório deve ser textual puro, sem formatação visual — "apenas palavras seguindo rigorosamente com os modelos"
