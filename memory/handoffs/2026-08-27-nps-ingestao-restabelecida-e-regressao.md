# Handoff — NPS: ingestão restabelecida, regressão aberta, e organização de Estudos

**Data:** 2026-08-27
**Sessão:** global, máquina mac-grupovelas (Claude Code)
**Issues:** [#351](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/351) (NPS) · [#326](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326) (Share) · [#352](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/352) (LSV)
**Relacionado:** `2026-08-26-nps-ia-voltar-hub-e-boutique.md`, `2026-08-27-nps-workflow-correcao-em-validacao.md`

---

## ⚠️ ESTADO ATUAL — LEIA ANTES DE CONTINUAR

A ingestão do NPS **voltou a funcionar**, mas há **uma regressão aberta em produção**
que ainda não foi corrigida. Ver seção "Regressão".

**Próximo passo imediato:** aplicar a correção de prioridade no nó
`Chaves de unidade` do workflow de ingestão e rodar uma vez. Isso restaura
sozinho os 99 vínculos perdidos — o upsert relê a planilha inteira.

---

## 1. O problema original

`public.nps` congelada em **3.803 linhas**, última resposta **19/08 11:15** (aba ITC)
e 09:00 (Trata). Oito dias de zero, abrupto, simultâneo nas duas abas e em todas as
unidades. Um sócio reclamou.

### Pistas falsas eliminadas

- **Resto do ETL saudável** — `dim_unidades` gravada em 26/08, dezenas de tabelas no dia.
- **Extração de IA saudável e ociosa** — 0 pendentes, 1.722 análises para 1.722 textos
  distintos. Ela só lê da tabela; não pode ser causa.
- **DDL de 21/08** (criou `nps.hash`) — rodou dois dias *depois* da parada.
- **A fonte não secou** — planilha "Controle NPS" (`1xBjqXChUpr7QtzNoD1GS6gddOMQLp5m-CRxRavXiCh0`,
  dona `lucas@grupovelas.com.br`) modificada em 27/08 às 21:01.

### O que fechou o diagnóstico

`pg_stat_user_tables`: **nenhuma escrita em `public.nps` desde 21/08 17:12**, e esse
carimbo é do `UPDATE` em massa do próprio DDL. Como o workflow relê a planilha
**inteira** a cada 20 min e faz upsert de tudo, mesmo sem resposta nova os
contadores subiriam. Logo, o nó de upsert não estava sendo alcançado.

### Causa real

O workflow `USpeImZKgNtYhJq4` (tag `Atualização BD`) **não existia mais**. Foi
recriado do zero nesta sessão.

## 2. Cascata de erros na reconstrução

| erro | causa |
|---|---|
| `Could not find the data table: jzV9ApCq4atCsmWd` | Data table é **escopado por projeto** no n8n; vivia no projeto `PQ0A9ifGldK6O7eJ`, que foi junto |
| `EAUTH` / `invalid_client` | Google recusando o **aplicativo** OAuth (Client ID/Secret), não o usuário. `invalid_grant` seria token de usuário |
| `Sheet with name {{ $json.table }} not found` | Campo em modo **Fixed** em vez de **Expression** — expressão virou texto literal |
| `Sheet with name Trata not found` | A aba existe; o valor vinha com caractere invisível do CSV importado |
| `404 NOT_FOUND` | Mesmo problema no `sheets_id`, agora no campo Document |

**Solução:** `{{ String($json.sheets_id).trim() }}` e `{{ String($json.table).trim() }}`,
mantendo os seletores em **By ID** e **By Name**.

**Gotcha do n8n:** o **From list** do campo Sheet retorna vazio enquanto o Document
for expressão — o carregador roda no editor, sem `$json`. Fixar o id temporariamente
destrava o dropdown; depois é obrigatório devolver para Expression.

### Fatos confirmados da planilha

- Abas: **`ITC`**, **`Trata`**, `disparados`, `Comentários ITC`, `Comentários Trata`
- Compartilhada com o **domínio `grupovelas.com.br` como writer** — qualquer conta
  @grupovelas lê, e dá para compartilhar com uma Service Account sem depender do
  lucas nem do Ernandes
- Coluna `Data` está em **ISO** (`2023-06-07 00:00:00`), não DD/MM — some o risco
  de trocar dia com mês
- Tem célula de `Nota` **genuinamente vazia** (4 numa amostra de 386 linhas)
- Data table `ids_nps`: duas linhas, mesmo `sheets_id`, `table` = `Trata` e `ITC`

## 3. Correções aplicadas no workflow de ingestão

**Blindagem de tipos.** `Edit Fields` era Set com `Nota` tipada `number` e
`typeValidation: strict`, rodando **dentro do loop** — uma célula não-numérica
derrubava a execução inteira, levando as duas abas junto. Virou Code node com
leitura normalizada de cabeçalho, nota inválida → `NULL`, linha sem data descartada.

**Fim do casamento por nome exato.** O `Merge` comparava `unidade` por igualdade
literal (foi assim que Juazeiro acumulou 42 órfãos silenciosos, #269 — e o rewrite
de 17/08 daquela issue **nunca chegou nesta produção**, só no fork `qca1fFQOlAubJb6w`).
Agora as duas pontas normalizadas, com variantes (nome completo, marca+parte, dois
primeiros nomes, primeiro nome) e **prioridade**, mais mapa de apelidos por marca.

**Bug de loop.** A primeira versão devolvia `[]` em três guardas. No n8n, nó que
emite zero itens não dispara o próximo: o `splitInBatches` nunca é rechamado, a
saída "done" não fica pronta e **o run termina sem gravar nada, sem erro**.
Trocado por sentinela.

**Validação:** 251 grafias plausíveis contra as 364 linhas reais de `dim_unidades`
→ **245 corretas**; as 4 divergências são a desambiguação desejada das unidades `- 2`.

## 4. Resultado

| métrica | antes | depois |
|---|---|---|
| total de linhas | 3.803 | **3.879** |
| última resposta | 19/08 11:15 | **27/08 15:59** |
| linhas desde 18/08 | 26 | **99** |
| marca d'água ITC | 2279 | **2302** |
| marca d'água Trata | 1585 | **1626** |

## 5. ⚠️ Regressão — NÃO CORRIGIDA

**Órfãos foram de 2 para 100.** Não são linhas novas: são **99 linhas históricas**
de 12 unidades **encerradas ou franqueadas** (São Luis, Franca, Itaim Bibi,
Paulista, Boa Vista, Belém, Araçatuba, Pinheiros) que tinham `id_interno` e foram
**zeradas pelo upsert**.

**Causa:** restringi o universo do mapa de chaves a
`tipo IN ('Própria','UP-F','UP-H') AND status = 'Ativa'` para eliminar ambiguidade,
depois de conferir que essas unidades não recebiam NPS novo. Não considerei que
**o upsert reescreve as linhas antigas** — tirar a unidade do mapa apagou um vínculo
que já existia.

**Impacto nos dashboards: nenhum.** Essas unidades já estavam fora do universo do
dashboard 59 (36 boutiques / próprias ativas). Das 99, 58 são de 2023–2024 e só 19
de 2026.

**Correção desenhada, ainda não aplicada:** trocar o filtro rígido por **prioridade
combinada** — própria+ativa ganha sempre; encerrada e franqueada entram só onde não
colidem com uma ativa. Fórmula: `prioridade = nivelVariante * 10 + (elegivel ? 0 : 5)`.
Como o upsert relê tudo, o próximo run reescreve sozinho o `id_interno` correto:
**não precisa de `UPDATE` manual nem de backup**.

### As 25 notas nulas não são dano

`nota IS NULL` foi de 0 para 25. A planilha tem célula de Nota genuinamente vazia,
então `NULL` é fiel à origem — o valor anterior era fabricado pela conversão do Set
antigo. 0,6% da base; é correção, não perda.

## 6. Extração de IA — pílula envenenada corrigida

No `Normalizar saída`, quando o modelo não devolvia entrada para um id, o nó
**gravava uma análise falsa** (`ausente: true`, `Não classificável`, confiança 0)
com o hash daquele comentário. A partir daí `ia.hash IS NULL` vira falso e o
comentário **nunca mais é reprocessado**. Se a resposta inteira falhasse o
`JSON.parse`, os **100 comentários do lote** eram condenados de uma vez, em silêncio.

Corrigido: linha sem resposta sai com `comentario_hash: null`, o `Gravar no banco?`
desvia para o ramo que não grava, e ela volta na rodada seguinte. O nó continua
devolvendo **todos** os itens — array vazio travaria o `splitInBatches`.

Testado: modelo responde tudo (3 gravados), modelo trunca (1 gravado, 2 pendentes),
resposta não é JSON (os 3 pendentes).

## 7. Metabase — organização

Criada pelo usuário a coleção **`Estudos` (677)**, dentro de `Testes` (576).
Movidos para lá, com integridade conferida:

| dashboard | de | para | integridade |
|---|---|---|---|
| **389** `[TESTE] Agendamentos Share` | 569 | **677** | 14 dashcards · 3 abas |
| **433** `Validação LSV` | 576 | **677** | 28 dashcards · 4 abas |

Só o `collection_id` mudou. URLs inalteradas.

## 8. Arquivos gerados (em `~/Downloads`, NÃO versionados)

| arquivo | o que é |
|---|---|
| `NPS - NOVO (importar limpo).json` | ingestão, para importar como workflow novo (data table e credencial em branco) |
| `NPS - CORRIGIDO FINAL (patch loop).json` | ingestão, versão do GPT + patch do loop, com ids do projeto antigo |
| `NPS - Extracao IA (sem envenenar pendentes).json` | extração de IA com o fix da pílula envenenada |
| `nps_validacao.sql` | 8 queries de validação da ingestão |
| `nps_pos_import.sql` | 9 queries de verificação pós-import, com baselines |
| `prompt_gpt_nps.md` | prompt usado para o GPT reescrever o workflow |
| `ids_nps.csv` | conteúdo do data table |

## 9. Pendências

- [ ] **Aplicar a correção de prioridade** no `Chaves de unidade` e rodar uma vez
- [ ] Importar o `NPS - Extracao IA (sem envenenar pendentes).json`
- [ ] Confirmar que a credencial Postgres (`zSuxDy2EHKaKRRql`) resolve no projeto novo
- [ ] OAuth do Sheets: se o consent screen ficar em **Testing**, o Google mata o
      refresh token em 7 dias e o pipeline morre de novo. Pôr como **Internal** ou
      migrar para **Service Account**
- [ ] `nps.hash` fica NULL nas linhas novas. Não quebra (o `coalesce` cobre), mas se
      alguém **editar** um comentário antigo na planilha a análise velha fica colada.
      Hoje: 0 casos. Limpeza definitiva é dropar `nps.hash` junto com o
      `DROP nps.ia_analise` já pendente
- [ ] Desativar o fork `qca1fFQOlAubJb6w`, se ainda existir — dois workflows ativos
      escrevendo na mesma tabela
- [ ] Normalização de `dim_unidades.boutique` (Ernandes) — herdada do handoff de 26/08

## 10. Query de verificação

```sql
SELECT count(*)                                              AS total,
       to_char(max(data),'YYYY-MM-DD HH24:MI')               AS ultima,
       count(*) FILTER (WHERE id_interno IS NULL)            AS orfaos,
       count(*) FILTER (WHERE nota IS NULL)                  AS nota_nula,
       max(split_part(id,' - ',1)::int) FILTER (WHERE id LIKE '% - ITC')   AS wm_itc,
       max(split_part(id,' - ',1)::int) FILTER (WHERE id LIKE '% - Trata') AS wm_trata
FROM public.nps WHERE split_part(id,' - ',1) ~ '^[0-9]+$';
```

Baselines: antes do import 3.803 / 19-08 11:15 / 2 órfãos / 0 nota nula / 2279 / 1585.

## 11. Decisões tomadas

1. **Universo por `tipo`+`status`**, não pela lista fixa de 36 boutiques do dashboard —
   se mantém sozinho quando abre unidade nova. **Mas precisa da prioridade**, senão
   apaga histórico (ver Regressão).
2. **Prioridade entre variantes de chave** — nome completo sempre vence variante
   derivada, senão `Guararapes - 2` anula `Guararapes`.
3. **Chave ambígua é descartada**, não chutada — órfão aparece na auditoria,
   `id_interno` errado não aparece em lugar nenhum.
4. **Nunca devolver array vazio dentro de loop no n8n** — trava o `splitInBatches`
   e mata o run inteiro sem erro. Vale para os dois workflows.
5. **Não gravar análise fabricada** quando o modelo não responde — deixar pendente.
