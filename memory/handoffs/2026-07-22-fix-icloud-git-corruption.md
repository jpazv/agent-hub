# Handoff — 2026-07-22 — Fix definitivo: repos fora do escopo do iCloud

## De onde veio

Sessão no `macbook-jpazv`. Contexto imediato:
`memory/handoffs/2026-07-22-pulse-mvp-instant-demo-e-deploy.md` (MVP do
Pulse no ar). Durante essa sessão, o `.git` do Pulse corrompeu **de novo**
(mesmo bug já registrado antes, ver "mudança estrutural" em
`memory/current-state.md`), e logo em seguida o **mesmo bug atingiu o
próprio `agent-hub`**. Ver detalhe completo do diagnóstico e da recuperação
em `memory/current-state.md`, seção "⚠️ Bug recorrente conhecido". Este
handoff é sobre o **fix definitivo** que foi aplicado depois disso.

## Causa raiz (resumo)

`~/Desktop` e `~/Documents` sincronizam via iCloud "Desktop e Documentos"
entre `mac-grupovelas` e `macbook-jpazv`, **arquivo por arquivo**. Um `.git`
tem escrita concorrente constante (index, HEAD, refs, objects mudam a cada
comando). O iCloud não trata isso como uma unidade atômica — quando as duas
máquinas escrevem quase ao mesmo tempo, ele cria cópias de conflito
(`index 2`, `objects 2`, `refs` sumindo, arquivos duplicados) e corrompe o
repo. Ter um remoto real no GitHub não resolve sozinho, porque o diretório
continua fisicamente dentro do escopo sincronizado — o iCloud não sabe que
o git já cuida da sincronização e continua tentando sincronizar o `.git/`
por conta própria.

## O que foi feito (aplicado só no `macbook-jpazv` até agora)

1. `~/Desktop/Pulse1.0.1` → **`~/dev/pulse`** (`mv`, sem perda — repo já
   estava limpo de um re-clone recente).
2. `~/Documents/agent-hub` → **`~/dev/agent-hub`** (`mv`).
3. `~/.claude/CLAUDE.md` (local, não sincronizado) atualizado: as "fontes de
   verdade obrigatórias" agora apontam pra `/Users/jp/dev/agent-hub/...` em
   vez de `/Users/jp/Documents/agent-hub/...`.
4. `registry/projects.yaml`: `path` do projeto `pulse` atualizado pra
   `~/dev/pulse` (com nota explicando que o caminho absoluto difere por
   máquina).
5. `memory/current-state.md` atualizado com o fix aplicado.
6. A pasta antiga corrompida do Pulse
   (`~/Desktop/Pulse1.0.1.icloud-corrupted-backup-20260722`) foi **mantida**
   como backup, não apagada — pode ser removida depois de confirmar que
   `~/dev/pulse` está saudável por alguns dias.

`~/dev/` não está no escopo do iCloud Desktop/Documentos, então esses dois
repos agora sincronizam **exclusivamente via `git push`/`pull`** contra o
GitHub — nunca mais pelo iCloud.

## ⚠️ Pendente no `mac-grupovelas`

O mesmo fix **ainda não foi aplicado na outra máquina**. Antes de continuar
trabalhando lá, fazer o equivalente:

```bash
mkdir -p ~/dev
mv ~/Desktop/Pulse1.0.1 ~/dev/pulse   # ajustar se o caminho lá for outro
mv ~/Documents/agent-hub ~/dev/agent-hub
```

E editar `~/.claude/CLAUDE.md` **daquela máquina** trocando
`/Users/grupovelas/Documents/agent-hub/...` por
`/Users/grupovelas/dev/agent-hub/...` nas "fontes de verdade obrigatórias".

Enquanto isso não for feito, o `mac-grupovelas` continua exposto ao mesmo
bug — e pior, os dois repos (`~/dev/...` no macbook vs `~/Documents/...` no
outro Mac) deixam de ser a mesma pasta fisicamente, então o iCloud vai
parar de tentar sincronizá-los entre si (o que é o objetivo), mas isso só
funciona de verdade depois que a outra máquina também sair do
`~/Documents`.

## Próximo passo

Nada bloqueado no `macbook-jpazv` — pode seguir direto pra Fase 4 do Pulse
(`~/dev/pulse`, ver `docs/plan-reconstrucao.md` dentro do repo). Só lembrar
de aplicar o mesmo fix no `mac-grupovelas` na próxima sessão lá.
