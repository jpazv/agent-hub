# Handoff — Agendamentos Share / issue #326 — meta oficial e análise entre semanas

Data: 2026-08-26
Máquina: mac-grupovelas
Hub: `/Users/grupovelas/dev/agent-hub`
Modo: global; não há projeto isolado associado a esta sessão.

## Objetivo

Construir, em ambiente de teste, o dashboard `[TESTE] Agendamentos Share` no Metabase para apoiar a proposta da issue #326 do repositório `Grupo-Velas/produtividade-bi-dev`:

https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326

A proposta é comparar agendamentos realizados com uma meta flat e uma meta diária ponderada pelo share histórico do dia da semana, usando 52 semanas ISO completas.

## Decisões de negócio

- A granularidade operacional é diária.
- A sazonalidade histórica é calculada com 52 semanas.
- O share é calculado por DOW (`EXTRACT(ISODOW FROM data)`): segunda=1 até domingo=7.
- O escopo operacional atual é segunda a sexta; dias não úteis e feriados são excluídos.
- A semana corrente e semanas futuras não entram no acompanhamento, pois ainda não estão fechadas.
- O usuário precisa segmentar por marca, unidade, boutique e sócio.
- O gráfico principal não deve alternar para semana/mês. A janela deve ser controlada por quantidade de semanas completas exibidas.
- O filtro atual é `Semanas completas exibidas`, com padrão 4 e tag nativa `numero_semanas`.

## Regra estatística do share

1. Agregar `agend` por semana ISO e DOW nas 52 semanas anteriores à semana corrente.
2. Excluir `dia_util <> 1` e datas existentes em `mb_feriados`.
3. Calcular o share de cada DOW dentro de cada semana.
4. Tirar a média dos shares semanais por DOW.
5. Renormalizar os pesos para que a soma dos DOW seja 100%.
6. Ao aplicar o peso a uma semana que tenha feriado, renormalizar os pesos entre os dias válidos daquela semana.

O `gap` deve ser sempre:

```text
gap = realizado - meta_ponderada
```

Gap positivo significa acima da meta; gap negativo significa abaixo da meta.

## Descoberta importante: fonte oficial da meta flat

O card oficial `Meta Agendamentos` do dashboard Performance (dashboard 10, card 11443) usa:

- `mb_metas_proprias.agendamentos`;
- escopo por `mv_data_geral.id_interno` e mês de competência;
- unidades com `log_unidades.status = 'Ativa'`;
- `log_unidades.tipo = 'Própria'`;
- `log_unidades.canal <> 'Matriz'`;
- dimensões oficiais de `dim_unidades` para unidade, marca e sócio.

O Share usava anteriormente `mv_hibrida_unidade_propria.meta_agd_diaria`, que não era a mesma regra do Performance. Isso foi corrigido no card 13792.

No card diário alinhado ao Performance:

```text
meta_flat_diaria = meta_mensal_oficial / dias_uteis_validos_do_mes
```

A meta ponderada usa o mesmo total mensal oficial, distribuído pelos pesos históricos de DOW.

Para manter os filtros do dashboard em ambas as fontes, o card 13792 possui tags separadas para a meta oficial:

- `meta_data` → campo 2788;
- `meta_unidade` → campo 412;
- `meta_marca` → campo 408;
- `meta_boutique` → campo 2298;
- `meta_socio` → campo 409.

Os parâmetros globais são mapeados tanto para as tags da view de agendamentos quanto para as tags da meta oficial.

## Dashboard atual no Metabase

- URL: https://metabase.grupovelas.com.br/dashboard/389
- Nome: `[TESTE] Agendamentos Share`
- Coleção: 569
- Aba 958: `Visão executiva`
- Aba 959: `Validação e auditoria`

Parâmetros atuais:

- `p-data` — Data, padrão `thismonth`;
- `p-marca` — Marca;
- `p-unidade` — Unidade;
- `p-boutique` — Boutique;
- `p-socio` — Sócio;
- `p-semanas` — Semanas completas exibidas, tipo `number/=`, padrão 4.

Não incluir token de autenticação neste handoff. O token vigente está no arquivo de boot local do hub e já foi atualizado anteriormente.

## Cards atualmente vinculados

### Aba 958 — Visão executiva

- Dashcard 20415, virtual: cartão `Como ler esta aba`, modo nativo `text`, linha 0, largura 24.
- Dashcard 20400 → card 13792, `Realizado vs metas — semanas completas por dia`, combo diário, linha 5, largura 24.
- Dashcard 20401 → card 13787, `Acompanhamento semanal — meta ponderada e gap`, tabela, linha 13, largura 24.
- Dashcard 20399 → card 13779, `Share histórico por dia da semana`, barra, linha 21, largura 24.
- Dashcard 20417 → card 13789, `Evolução semanal — realizado versus meta ponderada`, combo, linha 27, coluna 0, largura 12.
- Dashcard 20419 → card 13791, `Matriz de gap — semana versus dia da semana`, pivot, linha 33, coluna 0, largura 12.

### Aba 959 — Validação e auditoria

- Dashcard 20402 → card 13782, `Auditoria diária`, tabela, linha 0, largura 24.
- Dashcard 20404 → card 13780, `Controle da baseline — 52 semanas`, tabela, linha 9, largura 24.

O card 13790, `Gap percentual por dia da semana`, existe na coleção, mas não está atualmente vinculado a um dashcard.

Não há IDs duplicados entre os dashcards ativos.

## Card diário principal — 13792

Características:

- `display`: combo;
- eixo X: `rotulo_dia`, no formato `DD/MM · Dia da semana`;
- séries: `realizado`, `meta_flat`, `meta_ponderada`;
- todas as séries no eixo Y esquerdo;
- `graph.y_axis.auto_split = false`;
- valores sobre as barras desligados para evitar poluição;
- filtro `numero_semanas` limita a janela às últimas semanas completas;
- semana corrente e semanas futuras ficam fora.

Teste realizado:

- padrão 4 semanas → 20 linhas (4 semanas × 5 dias úteis);
- parâmetro 2 semanas → 10 linhas;
- query executada sem erro.

## Correção do gap semanal

O card semanal original mostrava um gap incorreto porque:

1. chamava `SUM(meta_agd_diaria)` de `meta_ponderada`;
2. calculava `SUM(agend - meta_agd_diaria)`, sujeito a descarte de linhas nulas diferente dos dois `SUM` separados.

Exemplo original da semana de 03/08:

- realizado: 571;
- meta ponderada coerente: aproximadamente 578,75;
- gap correto: aproximadamente -7,75;
- gap antigo exibido: aproximadamente +55,5.

O card semanal 13787 já mostra apenas semanas completas e retorna:

- 03/08: realizado 571, meta 578,75, gap -7,75;
- 10/08: realizado 483, meta 578,75, gap -95,75;
- 17/08: realizado 498, meta 578,75, gap -80,75.

## Nova visão analítica entre semanas

Foram criados os seguintes cards:

- 13789 — evolução semanal realizado versus meta ponderada;
- 13790 — gap percentual por DOW;
- 13791 — matriz de gap semana versus DOW.

Pendências conhecidas:

1. Os cards 13789 e 13791 foram anexados automaticamente à aba 958 durante a tentativa de criar uma nova aba. A aba `Análise entre semanas` não foi criada; o uso de `dashboard_tab_id: -1` foi ignorado pelo endpoint nesta tentativa.
2. O card 13791 está quebrado com:

```text
ERROR: column "dia_semana" does not exist
```

Motivo: a query tenta selecionar `dia_semana` da CTE `diario`, mas `diario` só carrega `dow`; o texto do dia precisa ser reconstruído com `CASE dow ... END` na seleção final, ou incluído explicitamente na CTE.
3. Os cards analíticos 13789/13790/13791 foram derivados antes da troca para a fonte oficial da meta. Devem ser recriados a partir da query do card 13792 para garantir que a meta flat e a meta ponderada sejam idênticas às do gráfico principal.
4. Depois de recriar os cards, substituir os dashcards 20417/20419 e mover os cards para uma aba real `Análise entre semanas`, preservando a aba executiva e a aba de validação.

## Próximo passo recomendado

1. Corrigir a SQL do card de gap por DOW.
2. Recriar os três cards analíticos a partir do card 13792, preservando `meta_data`, `meta_unidade`, `meta_marca`, `meta_boutique`, `meta_socio` e `numero_semanas`.
3. Criar corretamente uma terceira aba no dashboard via PUT completo com `tabs` e `dashcards`, usando o procedimento compatível com esta instalação para IDs temporários de aba.
4. Vincular `p-semanas` aos três cards analíticos.
5. Testar no Metabase:
   - 1, 2 e 4 semanas;
   - marca, unidade, boutique e sócio;
   - ausência da semana corrente;
   - soma semanal igual a `realizado - meta_ponderada`;
   - matriz sem erro de coluna.
6. Auditar novamente que cada card ativo tem exatamente um dashcard e que não houve card analítico solto na coleção sem vínculo.

## Arquivos e artefatos relacionados

Documentação da proposta:

- `/Users/grupovelas/agendamentos-share-proposta-tecnica.md`
- `/Users/grupovelas/agendamentos-share-proposta.html`
- `/Users/grupovelas/Downloads/agendamentos-share-proposta-tecnica.md`
- `/Users/grupovelas/Downloads/agendamentos-share-proposta.html`
- `/Users/grupovelas/Downloads/issue-326-comentario-proposta.md`

Scripts locais relacionados à construção/análise do dashboard:

- `/Users/grupovelas/rebuild-share-dashboard.sh`
- `/Users/grupovelas/fix-share-template-tags.sh`
- `/Users/grupovelas/fix-agendamentos-share-filters.sh`
- `/Users/grupovelas/recreate-main-share.sh`

O comentário técnico da issue #326 foi publicado anteriormente no GitHub:

https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326#issuecomment-5428350140

## Regras operacionais para continuar

- Não ler handoffs anteriores; este arquivo é o registro desta sessão.
- Para cards existentes, evitar `PUT /api/card/:id`; recriar via `POST /api/card` e substituir no dashboard.
- Ao alterar o dashboard, enviar o payload completo com `tabs` e `dashcards`.
- Usar apenas SQL de leitura no banco.
- Não expor nem commitar tokens.
- Após qualquer criação de card com `dashboard_id`, auditar e remover dashcards duplicados ou anexos automáticos fora da aba pretendida.
