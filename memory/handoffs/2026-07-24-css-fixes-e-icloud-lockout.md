# Handoff — fixes de CSS na landing + `~/Documents` travado (EPERM) no mac-grupovelas

**Data:** 2026-07-24
**Máquina:** mac-grupovelas
**Continua em:** a definir (máquina vai ser desligada)

## O que foi feito

### 1. Novo incidente: `~/Documents` ficou inacessível (EPERM)
No meio da sessão, `~/Documents/raiox-mvp-html/index.html` passou a dar
`Operation not permitted` em qualquer leitura (Read tool, `grep`, `ls`) —
e pouco depois **todo `~/Documents`** (não só esse arquivo) ficou
inacessível do mesmo jeito, incluindo `ls ~/Documents/`. Isso é diferente
dos 3 incidentes anteriores desta semana (corrupção de `.git`, pasta
duplicada, pasta sumida) — parece uma revogação de permissão do macOS
(Files and Folders / Full Disk Access) pro processo que executa o Bash
tool, não corrupção de arquivo. `~/dev` continuou 100% acessível o tempo
todo. **Não foi diagnosticado/resolvido** — se persistir, checar em
`Configurações do Sistema → Privacidade e Segurança → Arquivos e Pastas`
(ou Acesso Total ao Disco) se o Terminal/app que roda o Claude Code ainda
tem permissão pra `~/Documents`.

**Mitigação aplicada**: como `raiox-mvp-html` já estava versionado no
GitHub (`Grupo-Velas/raiox-mvp-html`, primeiro commit do dia anterior),
cloneio fresco em `~/dev/raiox-mvp-html` e segui o trabalho lá — isso
também resolve de vez a pendência (já registrada no handoff de ontem) de
mover esse repo pra fora do escopo do iCloud, igual já tinha sido feito
com `pulse` e `agent-hub`. **`~/Documents/raiox-mvp-html` (o original)
não foi apagado** — só ficou de lado, inacessível; se a permissão voltar,
tem um diretório duplicado ali que pode ser descartado depois de
confirmar que `~/dev/raiox-mvp-html` tem tudo.

### 2. Fixes de CSS na landing (`raiox-mvp-html`)
Reportados pelo usuário via screenshot + descrição:
- **Subtítulo do hero desalinhado**: "Diagnóstico financeiro completo em
  minutos — e o que ajustar primeiro." aparecia colado à esquerda embaixo
  do título centralizado. Causa: `.landing-copy` não tinha `text-align`
  nem `margin: auto` — a caixa do parágrafo (max-width:680px) ficava
  centralizada pelo grid pai, mas o texto dentro dela, ao quebrar em
  2-3 linhas, alinhava à esquerda dentro dessa caixa estreita. **Corrigido**:
  adicionado `text-align: center` e `margin: 20px auto 0`.
- **Botão "quase encostando no card"**: usuário reportou botões com
  "length alto" (interpretei como muito largos/grudados na borda) em
  algum card. Investiguei e encontrei DOIS candidatos plausíveis:
  (a) os 3 cards de preço (Free/Premium/Personalizado) têm
  `body.landing-mode .pricing-card .btn { width: 100% }` de propósito
  (padrão de tabela de preço, pré-existente, não é bug); (b) o card do
  "Eco" no grid de produtos (que eu adicionei nesta sessão) tem um botão
  que não é `width:100%`, mas talvez esteja com pouco respiro embaixo.
  **Não tive certeza de qual o usuário via** (não veio screenshot desse
  específico) — aplicado um ajuste conservador (`margin-bottom:6px` no
  `.landing-actions` do card Eco) como palpite, mas **isso precisa ser
  confirmado com um screenshot** na próxima sessão; se não for isso, a
  causa mais provável é o padrão intencional dos cards de preço (b acima),
  que talvez precise de mais padding lateral em vez de mudar o `width:100%`.

## ⚠️ Pendência nova: deploy do `raiox-mvp-html` também não promove alias

Depois do fix, `vercel --prod` funcionou (build ok, sem erro), mas
**o alias curto não foi promovido** — mesmo sintoma já visto no
`pulse-app` (ver handoff de ontem): `vercel alias set <deployment>
raiox-mvp-html.vercel.app` respondeu **"Error: The deployment ... is not
ready"**, mesmo com o deploy servindo 200 na URL direta. Tentei de novo
(2x) e disparei um novo `vercel --prod` que **ficou rodando em background
e não terminou até a sessão precisar encerrar** — status desconhecido.

**Isso confirma um padrão**: dois projetos diferentes (`pulse-app` ontem,
`raiox-mvp-html` hoje) tiveram problema pra promover o alias de produção
via CLI na mesma conta Vercel, num intervalo de ~24h. Vale suspeitar de
algo na conta/time (não só no projeto específico) — verificar no
dashboard da Vercel se há algum aviso de billing, limite, ou mudança de
permissão recente na conta `jpazevedomoreiraa-1824s-projects`.

**Estado atual no ar**: `https://raiox-mvp-html.vercel.app` e
`https://pulse-raiox.vercel.app` ainda estão servindo a versão **sem** o
fix do subtítulo (confirmado via curl, `.landing-copy` sem
`text-align`). O fix está commitado e pushado
(`Grupo-Velas/raiox-mvp-html`, commit mais recente em `main`), só falta
o deploy/alias realmente ir ao ar.

## Próximos passos (ordem)

1. Checar se o `vercel --prod` que ficou rodando em background terminou
   (ou disparar de novo) e promover o alias:
   ```
   cd ~/dev/raiox-mvp-html
   vercel --prod --yes
   vercel alias set <url-do-deployment-mais-recente> raiox-mvp-html.vercel.app
   vercel alias set <url-do-deployment-mais-recente> pulse-raiox.vercel.app
   ```
2. Confirmar visualmente (ou via `curl .../ | grep -A3 landing-copy`) que o
   subtítulo já aparece centralizado.
3. Pedir um screenshot específico do botão "encostando no card" pro
   usuário antes de insistir num fix diferente do que já foi aplicado.
4. Investigar a causa raiz do padrão de alias/autorização falhando em 2
   projetos diferentes na mesma conta Vercel em <24h — dashboard primeiro.
5. Se `~/Documents` continuar travado (EPERM) na próxima sessão, checar
   permissões de Files-and-Folders do macOS pro app/terminal usado; se
   resolver, comparar `~/Documents/raiox-mvp-html` (original) com
   `~/dev/raiox-mvp-html` (clone novo) antes de descartar um dos dois.
6. Resolver também a pendência já registrada ontem: deploy travado do
   `pulse-app` com erro "Not authorized" (ver handoff 2026-07-23).
