# Boas Praticas Globais de Engenharia

**Regra:** ler em todo boot. Nao pesquisar autores automaticamente; este
arquivo ja e a sintese operacional.

## Principio central

Entregue software simples de mudar, dificil de quebrar, seguro por padrao e
facil de operar. Antes de alterar codigo, entenda comportamento atual,
contratos, dados envolvidos, risco da mudanca e verificacao necessaria.

## Escopo e checkpoints

- Nao alterar ambiente, variavel de producao, alias de dominio, credencial,
  schema ou fazer deploy sem pedido explicito na mensagem atual. Investigar e
  propor nao e o mesmo que aplicar.
- Antes de qualquer mudanca global, perguntar se o usuario quer salvar handoff.
  Checkpoint funciona como save de videogame: existe para poder voltar, e o
  momento de criar e ANTES da mudanca arriscada, nao depois.
- Conta como mudanca global: variavel de producao, deploy, alias, migration,
  rotacao de segredo, alteracao em `CLAUDE.md` ou nos arquivos do hub, e
  refatoracao que atravessa varios modulos.
- Criar checkpoint tambem ao concluir marco entregavel, mesmo sem mudanca
  arriscada a seguir — handoff barato agora evita reconstrucao caro depois.
- Nao afirmar caminho de painel, endpoint ou permissao de terceiro sem
  confirmar na documentacao oficial.
- Separar o que foi verificado do que foi inferido, e dizer qual e qual. Marcar
  inferencia como inferencia, inclusive quando ela parecer obvia.

## Codigo

- Prefira clareza a esperteza: nomes revelam intencao e dominio.
- Funcoes devem ter uma responsabilidade e um nivel de abstracao coerente.
- Reduza aninhamento com retornos antecipados quando isso deixar o fluxo mais
  direto.
- Extraia funcoes quando o nome explicar uma regra real do negocio.
- Remova duplicacao de conhecimento, nao apenas linhas parecidas.
- Comentarios explicam decisoes e tradeoffs; codigo deve explicar o fluxo.
- Preserve estilo e padroes locais antes de criar abstracao nova.
- Evite estado global, efeitos colaterais escondidos e flags booleanas que
  mudam a semantica inteira de uma funcao.

## Complexidade

- Use McCabe como alerta: complexidade ciclomatica = decisoes + 1.
- `1-5` simples; `6-10` ok com atencao; `11-20` revisar; `21+` refatorar ou
  justificar.
- Complexidade essencial do dominio pode ser aceitavel; complexidade
  acidental deve ser removida.
- Refatore em passos pequenos e verificaveis. Em legado, primeiro crie
  caracterizacao do comportamento.

## Arquitetura

- Arquitetura boa preserva opcoes e reduz acoplamento, nao adiciona camadas
  por estetica.
- Regras de negocio devem depender menos de detalhes externos como framework,
  banco, UI, fila, email ou provedor cloud.
- Prefira monolito modular antes de microservicos prematuros.
- Separe dominio/casos de uso de infraestrutura e interface quando o projeto
  tiver complexidade suficiente.
- Modele com linguagem do negocio; nao misture contextos diferentes no mesmo
  modelo.
- Interfaces devem esconder decisoes dificeis e expor uma superficie pequena.

## Dados e integracoes

- Operacoes externas precisam considerar timeout, retry, idempotencia e falha
  parcial.
- Use chaves de idempotencia em webhooks, pagamentos, convites,
  provisionamento e jobs.
- Nao faca retry cego em operacao nao idempotente.
- Versione contratos publicos e planeje migrations em etapas: expandir,
  migrar, contrair.
- Constraints criticas pertencem tambem ao banco, nao so ao app.
- Logs devem ter contexto para investigar sem expor segredos ou dados
  sensiveis.

## Testes

- Teste comportamento, nao implementacao.
- Unitarios para regra pura; integracao para banco/contratos; e2e para fluxos
  criticos.
- Ao corrigir bug, adicionar teste que falharia antes.
- Ao mexer em auth, autorizacao, pagamento, tenant, dados ou deploy, aumentar
  rigor de verificacao.
- Testes devem ser deterministas, pequenos e independentes de ordem global.
- Sem teste automatizado, rode uma verificacao manual objetiva e registre o
  risco restante.

## Seguranca

- Autenticacao e autorizacao devem ser server-side, centralizadas e negar por
  padrao.
- Verifique autorizacao em toda acao sensivel e em todo acesso a objeto
  pertencente a usuario/tenant.
- Segredos nunca entram no codigo, git, logs ou resposta ao usuario.
- Validar input no limite do sistema; escapar output conforme contexto.
- Usar bibliotecas maduras para criptografia, hashing, sessoes e tokens.
- Webhooks precisam verificar assinatura e tolerar replay com idempotencia.
- Aplicar minimo privilegio em tokens, roles, buckets, service accounts e RLS.
- Revisar riscos comuns: IDOR, XSS, SQL/command injection, SSRF, CSRF,
  upload inseguro, secrets hardcoded e dependencias vulneraveis.

## CI/CD e operacao

- Main/trunk deve ficar entregavel; branches pequenos e de vida curta.
- Pipeline deve falhar cedo: install travado, lint/format, typecheck, testes,
  build, scan de secrets e dependencias.
- Deploy deve ser pequeno, reversivel e observavel.
- Preview/staging devem ter smoke test antes de promocao.
- Configuracao e segredo sao coisas diferentes; ambiente deve ser
  reproduzivel.
- Medir DORA como termometro: frequencia de deploy, lead time, taxa de falha e
  tempo de recuperacao.
- Observabilidade minima: erro, latencia, volume, saturacao e metricas de
  negocio do fluxo critico.

## Revisao

Prioridade em review: bugs/regressoes, seguranca/privacidade, quebra de
contrato/schema, falta de teste em area de risco, complexidade desnecessaria,
legibilidade. Nao bloquear por gosto; bloquear por risco concreto.

## Checklist final do agente

1. Pedido mais recente foi atendido, e nada alem dele?
2. Mudanca respeita padroes locais?
3. Teste/verificacao e proporcional ao risco?
4. Typecheck/lint/build relevantes passaram ou a falha foi explicada?
5. Seguranca, dados, tenants e segredos foram considerados?
6. Deploy/rollback/observabilidade foram considerados quando aplicavel?
7. Memoria/documentacao foi atualizada quando a decisao precisa sobreviver?
8. Havia mudanca global no caminho? Checkpoint foi oferecido antes dela?

## Metabase — cards de dashboard (dashboard questions)

Aprendido na marra em 2026-08-24: tres incidentes na mesma sessao, com cards
sumindo do dashboard e indo parar na Lixeira. Ler antes de mexer via API.

### Como criar (unico caminho seguro)

- Criar ja vinculado, num **unico POST**:
  `POST /api/card` com `{"dashboard_id": <dash>, "collection_id": <col do dash>}`.
  Nao criar solto e vincular depois.
- **NAO** usar `PUT /api/card/:id` para setar `dashboard_id` depois — a versao
  anterior deste documento mandava fazer isso e e o que causa o problema abaixo.

### A armadilha: PUT numa dashboard question a DESANEXA

Um card com `dashboard_id` vive dentro do dashboard. Um `PUT /api/card/:id`
nele pode remover o dashcard e arquivar o card na Lixeira (`collection_id: 1`),
**mesmo que o payload nao mencione dashboard_id nem collection_id**.
Observado com:

- `PUT {"collection_id": X}`            -> desanexou (confirmado)
- `PUT {"dataset_query": ..., "visualization_settings": ...}` -> desanexou 4 de 7 cards
- `PUT /api/dashboard/59` com a lista completa de dashcards -> derrubou 5 dashcards

Nao consegui isolar a condicao exata: no mesmo lote, alguns cards sobrevivem e
outros nao. Trate como **nao deterministico** e assuma o pior.

**Regra**: para alterar query, visualizacao ou collection de um card de
dashboard, **recrie o card** (POST com `dashboard_id`) e troque o `card_id` do
dashcard. Nunca PUT.

### Efeito colateral: auto-anexo cria dashcard orfao

Criar (ou desarquivar) um card com `dashboard_id` **pendura ele sozinho na
primeira aba** do dashboard, sem mapeamento de filtro. Se voce tambem adicionar
o dashcard na aba certa, o card fica duplicado.

**Sempre** depois de criar/desarquivar:
1. `GET /api/dashboard/:id` e conferir a contagem de dashcards contra o esperado
2. remover os dashcards do card novo que estejam fora da aba pretendida
3. confirmar que cada `card_id` aparece **exatamente uma vez**

O dry-run que preve N dashcards e o PUT que devolve N+k denuncia k orfaos.

### Checklist antes de qualquer PUT de dashboard

- `PUT /api/dashboard/:id` exige `tabs` + `dashcards` juntos — omitir um apaga o outro
- guardar o GET anterior em arquivo de backup antes de escrever
- depois do PUT, diffar contra o backup: dashcards sumidos, alterados e intrusos
- conferir que nenhuma aba pre-existente mudou quando a mudanca era so numa aba

### Permissoes

- Card em `collection_id: 1` esta na **Lixeira** — invisivel para usuario comum
  e candidato a expurgo. Se um card renderiza para admin e nao para os demais,
  checar a collection dele antes de suspeitar de permissao de grupo.
- Card criado dentro do dashboard herda o acesso do dashboard. E o jeito de
  liberar para todos sem precisar de admin.
- `/api/permissions/group` exige superuser. O usuario jp@grupovelas.com.br
  **nao e** superuser — nao da para ler nem alterar o grafo de permissoes.

### Filtros

- Filtro e do **dashboard inteiro**, nunca da aba. Nao existe default por aba.
  Para um default que valha so numa aba, criar um parametro novo e mapea-lo
  apenas nos cards daquela aba.
- Conferir `values_source_type` e `default` antes de reaproveitar um filtro:
  um `static-list` com defaults pode esconder linhas silenciosamente.
  Caso real: o filtro "Boutique" do dash 59 tem 35 valores fixos de default e
  deixa de fora 2 boutiques que tem alerta — uma delas Critica.
- O mesmo `parameter_id` pode ter semantica diferente entre dashboards
  (`5c3fc048` = Boutique no dash 59, = Unidade no dash 387). Sempre conferir o
  `target` real antes de reaproveitar mapeamento.
- Template-tags `dimension` com `widget-type: "string/contains"` so aceitam
  `type: "string/contains"` na API de query, nao `string/=`.

### Outros

- Cloudflare bloqueia `python-urllib` nesta instancia (erro 1010 / HTTP 403).
  Usar `curl` para todas as chamadas.
- Estilo de referencia a colunas: cards MBQL sobre um modelo referenciam por
  **nome** (`["field","nota",...]`), nao por id — entao trocar a fonte de um
  modelo e seguro desde que os nomes internos das colunas sejam preservados.

## Referencias condensadas

Beck, Fowler, Martin, McConnell, Ousterhout, Evans, Vernon, Kleppmann,
Feathers, Weinberg, Forsgren, Humble, Kim, Farley, OWASP, NIST e Google SRE.
Use essas linhas como base conceitual, nao como obrigacao de leitura no boot.

## Documentação de issues do GitHub

**Padrão vigente desde 2026-09-02.** A issue do GitHub é o registro de
microgerenciamento: toda entrega, decisão, hipótese descartada e limite de dado vai
documentada nela — não só no chat, não só no handoff.

Estrutura, regras de conteúdo e a relação com o handoff estão em
[`memory/padrao-documentacao-issues.md`](padrao-documentacao-issues.md).

Resumo: o handoff do hub é memória **entre sessões de IA**; a issue é memória **do time**.
Os dois precisam existir.
