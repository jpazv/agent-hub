# Boas Praticas Globais de Engenharia

**Regra:** ler em todo boot. Nao pesquisar autores automaticamente; este
arquivo ja e a sintese operacional.

## Principio central

Entregue software simples de mudar, dificil de quebrar, seguro por padrao e
facil de operar. Antes de alterar codigo, entenda comportamento atual,
contratos, dados envolvidos, risco da mudanca e verificacao necessaria.

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

1. Pedido mais recente foi atendido?
2. Mudanca respeita padroes locais?
3. Teste/verificacao e proporcional ao risco?
4. Typecheck/lint/build relevantes passaram ou a falha foi explicada?
5. Seguranca, dados, tenants e segredos foram considerados?
6. Deploy/rollback/observabilidade foram considerados quando aplicavel?
7. Memoria/documentacao foi atualizada quando a decisao precisa sobreviver?

## Referencias condensadas

Beck, Fowler, Martin, McConnell, Ousterhout, Evans, Vernon, Kleppmann,
Feathers, Weinberg, Forsgren, Humble, Kim, Farley, OWASP, NIST e Google SRE.
Use essas linhas como base conceitual, nao como obrigacao de leitura no boot.
