# Handoff — correcao do workflow n8n NPS em validacao

**Data:** 2026-08-27  
**Maquina:** mac-grupovelas  
**Contexto:** modo global / workflow n8n de ingestao de NPS  
**Workflow:** `NPS` — ID `USpeImZKgNtYhJq4`

## Objetivo da sessao

Corrigir o JSON completo do workflow n8n de ingestao de NPS sem alterar a
topologia, preservando identidade, tags, credenciais e posicoes dos nos.

As duas frentes solicitadas foram:

1. impedir que nota, data ou coluna suja interrompa a execucao inteira;
2. substituir o casamento literal de unidade por chaves normalizadas, aliases
   por marca, prioridade de variantes e filtro de unidades proprias ativas.

## Boot e contexto

- Hub localizado por `~/.config/agents/machine.toml` em
  `/Users/grupovelas/dev/agent-hub`.
- Sessao detectada em modo global, pois o cwd `/Users/grupovelas` nao pertence
  a projeto registrado.
- Fontes obrigatorias e ultimo handoff commitado foram lidos.
- Kanban nao foi carregado: `gh auth status` informa token invalido para a conta
  `jpazv`. Isso nao bloqueia a correcao local do JSON.
- Nenhum subagente foi iniciado, conforme regra expressa do usuario.

## Arquivos envolvidos

- Original recebido:
  `/Users/grupovelas/Downloads/NPS.json`
- Rascunho anterior encontrado e tratado apenas como referencia nao confiavel:
  `/Users/grupovelas/Downloads/NPS - CORRIGIDO (normalizacao + blindagem).json`
- Saida gerada nesta sessao, ainda pendente de validacao final:
  `/Users/grupovelas/Downloads/NPS - CORRIGIDO FINAL.json`
- Script temporario que transforma o original na saida:
  `/private/tmp/build_nps_workflow.js`
- Resposta temporaria da consulta somente leitura de `dim_unidades`:
  `/private/tmp/nps_dim_unidades_response.json`

Arquivos em `/private/tmp` nao sao versionados e podem ser removidos pelo
sistema.

## Estado do trabalho

O arquivo `NPS - CORRIGIDO FINAL.json` foi gerado, mas a sessao foi interrompida
antes da bateria final de validacoes. Nao entregar como concluido sem executar
os testes pendentes descritos abaixo.

### Alteracoes ja codificadas

1. `Edit Fields`
   - manteve nome, id e posicao;
   - mudou de `set` estrito para `code`;
   - campos opcionais ausentes viram `null`;
   - nota aceita apenas inteiro entre 0 e 10;
   - formatos numericos com virgula sao interpretados, mas decimal nao inteiro
     vira `null`, sem arredondamento;
   - data brasileira, ISO e serial do Google Sheets sao validados;
   - linha sem id ou sem data valida e descartada;
   - ausencia do cabecalho `Unidade` descarta o lote sem derrubar a execucao;
   - celula de unidade vazia continua disponivel para a regra da Matriz;
   - nome da aba e marca sao preservados em `aba_nps` e `marca_nps`.

2. `If1`
   - continua no mesmo ponto e com as mesmas saidas;
   - usa valor com fallback e `typeValidation: loose`, evitando erro por
     `undefined`.

3. `If`
   - continua no mesmo ponto e com as mesmas saidas;
   - passou a validar `row_number` e `Data`, nao `unidade`/comentario;
   - isso permite que uma resposta valida com unidade vazia chegue a Matriz.

4. `Formatar unidade`
   - manteve nome, tipo, id e posicao;
   - normaliza com minusculas, NFD, remocao de diacriticos, pontuacao para
     espaco, colapso de espacos e trim;
   - toda chave recebe prefixo da marca;
   - aplica aliases com escopo por marca e aliases comuns;
   - unidade vazia ou contendo `NPS` vira Matriz;
   - gera `unidade_chave` para o Merge.

5. `Edit Fields1`
   - manteve nome, id e posicao;
   - mudou de `set` para `code`;
   - filtra apenas tipos `Propria`, `UP-F`, `UP-H` e status `Ativa`;
   - deduz a marca pelo proprio nome completo da unidade;
   - gera chaves com prioridade: nome completo, marca + parte, dois primeiros
     nomes, primeiro nome;
   - o nome completo vence variantes derivadas de unidades como
     `Guararapes - 2` e `Santos - 2`;
   - empate com o mesmo id e deduplicado; ids distintos na mesma prioridade
     fazem a chave ser descartada;
   - emite `id_interno`, `unidade_dimensao` e `unidade_chave`.

6. `Merge`
   - manteve modo `combine` e `joinMode: enrichInput1`;
   - campo de casamento mudou de `unidade` para `unidade_chave`;
   - deve continuar emitindo respostas sem match para que o upsert grave
     `id_interno = null`.

7. Upsert em `public.nps`
   - operacao, schema, tabela e `matchingColumns: ["id"]` foram preservados;
   - campos anulaveis usam fallback explicito para `null`.

### Decisoes importantes

- O rascunho anterior arredondava `9,5` para `10`; isso foi rejeitado porque a
  regra exige nota inteira. Agora `9,5` vira `null`.
- O rascunho anterior ainda usava `If` sobre unidade/comentario e descartava
  uma resposta valida da Matriz quando ambos estavam vazios. A condicao foi
  alterada para id/data.
- Para distinguir uma celula vazia de uma coluna `Unidade` renomeada, o codigo
  verifica se pelo menos uma linha do lote possui o cabecalho. Sem cabecalho, o
  lote e descartado; com cabecalho, a celula vazia representa Matriz.
- Data invalida tambem e descartada. Apenas testar `notEmpty` deixaria uma
  string invalida chegar ao Postgres e ainda poderia derrubar o lote.
- Comentarios e logs dentro dos nos `code` foram escritos em ASCII, sem acento.

## Consulta somente leitura executada

Foi executado via Metabase apenas:

```sql
SELECT id, unidade, marca, tipo, status
FROM public.dim_unidades
ORDER BY id
```

Resultado confirmado:

- status da consulta: `completed`;
- total: **364 linhas**;
- colunas: `id`, `unidade`, `marca`, `tipo`, `status`.

Nenhum DDL, UPDATE, INSERT, DELETE, importacao no n8n ou escrita em producao foi
executado.

## Validacoes pendentes — proximo passo obrigatorio

1. Validar sintaxe JSON com `jq empty`.
2. Comparar original e corrigido para provar preservacao de:
   - `id`, `name`, `versionId`, `tags`, `active`, `settings`, `meta`, `pinData`;
   - quantidade, ids, nomes e posicoes dos nos;
   - credenciais;
   - topologia completa das conexoes.
3. Extrair e compilar os tres `jsCode` com Node para detectar erro de sintaxe.
4. Rodar o codigo de `Edit Fields1` contra as 364 linhas reais e conferir:
   - unidades elegiveis: esperado **57**;
   - chaves ambiguas descartadas: esperado proximo de zero;
   - nenhuma conta contabil, franqueada ou encerrada presente na saida.
5. Simular respostas e confirmar ids corretos para:
   - `Tatuape`, `tatuape`, `TATUAPE` em Trata e ITC;
   - `Batel` no ITC;
   - `Agua Fria` nas duas marcas;
   - `Guararapes` e `Guararapes - 2` no Trata;
   - `Santos` e `Santos - 2` no Trata;
   - unidade vazia no ITC;
   - aliases Niteroi, Savassi, Boa Vista, Belem, Goiania, Juazeiro,
     Juazeiro Norte, Campinas, Cambui e Barueri.
6. Simular dado sujo:
   - nota `N/A`, vazia, `9,5`, `10,0`, fora de 0..10;
   - data vazia e data invalida;
   - coluna opcional renomeada;
   - coluna Unidade ausente versus celula Unidade vazia.
7. Confirmar que unmatched no `Merge enrichInput1` continua para o upsert e
   que `id_interno` ausente e convertido em `null`.
8. Se qualquer teste falhar, ajustar `/private/tmp/build_nps_workflow.js`, gerar
   novamente a saida e repetir toda a validacao.
9. Somente depois entregar o JSON completo corrigido ao usuario.

## Estado do git do hub antes deste handoff

O hub ja possuia varios arquivos nao rastreados e alheios a esta tarefa,
incluindo scripts, caches e conteudo dos plugins Metabase/n8n. Eles pertencem
ao usuario e nao devem entrar no commit deste handoff. Adicionar e commitar
somente este arquivo.

