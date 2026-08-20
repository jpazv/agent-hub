# Plugin GitHub — Kanban e criação de cards

Como **ler** o kanban e como **criar cards padronizados** no GitHub Projects do time de BI.

- **Repo:** `Grupo-Velas/produtividade-bi-dev`
- **Project (número):** `1` — "Produtividade BI e Dev"
- **Project ID (GraphQL):** `PVT_kwDOEJ3d0M4BVg6Y`

---

## Parte 1 — LER o kanban (boot de toda sessão)

```bash
gh project item-list 1 --owner Grupo-Velas --format json --limit 400
```

Identificar tasks do JP (o board não usa assignee de forma confiável):
- título casando `[JP]` ou `JP:`
- OU corpo contendo `jpazv`

Ordem de exibição: **Em andamento → Em validação → Solicitada → Triagem/Backlog**.
Nunca listar `Concluída`. `Bloqueada` só se pedirem.

Issues direto pelo repo:
```bash
gh issue list --repo Grupo-Velas/produtividade-bi-dev --state open --limit 100 \
  --json number,title,assignees,labels,updatedAt
gh issue view <N> --repo Grupo-Velas/produtividade-bi-dev --json title,body,comments
```

### Token
Exige escopo `project` no `gh`. Conferir com `gh auth status`; se faltar:
```bash
gh auth refresh -h github.com -s project -c
```
O device flow **não funciona** pelo bash do agente — o JP roda num terminal próprio.

---

## Parte 2 — CRIAR card padronizado (`/criar-card`)

### Campos a coletar

**Obrigatórios** (perguntar se faltar):

| Campo | Pergunta |
|---|---|
| Responsável | "Para quem é o card?" |
| Projeto | "Qual projeto? (Metas, Unity, SCAL, Instagram, Fechamento, Regulatório, Core, Locus AI, Geral)" |
| Atividade | "Qual a atividade em uma frase curta?" |
| Setor solicitante | "Qual setor solicitou?" |
| Tipo | "Demanda / Bug / Melhoria / Automação / Relatório / Infra" |
| Prioridade | "Baixa / Media / Alta / Critica" |

**Opcionais** (perguntar sempre; em branco → `—`): Prazo desejado · Objetivo · Contexto · Critério de sucesso.

### Título — formato obrigatório

```
[NomeProjeto] Descrição curta da atividade
```

Exemplos: `[Instagram] Criar schema novo do banco de dados` · `[Fechamento] Criar estrutura de tabelas de fechamento histórico`

> O prefixo antigo `[JP]`, `[Ernandes]`, `[Gustavo]`, `[Kadu]` foi **substituído pelo nome do projeto**. O responsável vai só em `assignees`.

### Body

```markdown
## Objetivo
{objetivo ou —}

## Contexto
{contexto ou —}

## Critério de sucesso
{critério ou —}

---

**Prazo desejado:** {prazo ou "A definir"}
**Setor solicitante:** {setor}
**Responsável sugerido:** {nome legível}
```

### Responsáveis → username

| Nome | Username |
|---|---|
| Ernandes / eu / mim | `NandesLima` |
| Gustavo | `Gustavo62` |
| João Paulo / JP | `jpazv` |
| Kadu / Karlos Eduardo | `eduardosr99` |

### IDs dos campos do board

**Status** `PVTSSF_lADOEJ3d0M4BVg6YzhQ8NQA`

| Valor | ID |
|---|---|
| Solicitada | `f75ad846` |
| Triagem/Backlog | `47fc9ee4` ← **padrão ao criar** |
| Em andamento | `df73e18b` |
| Em validação | `83bf4887` |
| Concluída | `a0be2e68` |
| Bloqueada | `cac16de1` |

**Setor solicitante** `PVTSSF_lADOEJ3d0M4BVg6YzhQ8WNw`

| Valor | ID | | Valor | ID |
|---|---|---|---|---|
| BI | `e9e14faa` ← padrão | | Diretoria | `49dbbedd` |
| Financeiro | `007a6567` | | Franquias | `9ba97ea2` |
| Comercial | `69950013` | | Expansão | `03c6ccb8` |
| Marketing | `f7544bb3` | | Operações | `702ab94e` |
| RH | `13f782db` | | TI | `a4e954dd` |
| Outros | `e06455f9` | | | |

**Prioridade** `PVTSSF_lADOEJ3d0M4BVg6YzhQ8WfA`

| Baixa | Media | Alta | Critica |
|---|---|---|---|
| `a66aee31` | `025cac08` ← padrão | `41348086` | `e60d2fc5` |

**Tipo** `PVTSSF_lADOEJ3d0M4BVg6YzhQ8Wh8`

| Demanda | Bug | Melhoria | Automação | Relatório | Infra |
|---|---|---|---|---|---|
| `f1cc9795` ← padrão | `3cee77dc` | `cfb73994` | `bb9dea05` | `94de961c` | `dbe04c92` |

---

## Script — bash / `gh` (macOS e Linux)

Usa a autenticação do próprio `gh`. **Não embutir token no script.**

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="Grupo-Velas/produtividade-bi-dev"
PROJECT_ID="PVT_kwDOEJ3d0M4BVg6Y"

TITULO="[Projeto] Descrição curta"
ASSIGNEE="jpazv"
STATUS_ID="47fc9ee4"      # Triagem/Backlog
SETOR_ID="e9e14faa"       # BI
PRIORIDADE_ID="025cac08"  # Media
TIPO_ID="f1cc9795"        # Demanda

BODY=$(cat <<'MD'
## Objetivo
—

## Contexto
—

## Critério de sucesso
—

---

**Prazo desejado:** A definir
**Setor solicitante:** BI
**Responsável sugerido:** João Paulo
MD
)

URL=$(gh issue create --repo "$REPO" --title "$TITULO" --body "$BODY" --assignee "$ASSIGNEE")
NUM="${URL##*/}"
NODE_ID=$(gh api "repos/$REPO/issues/$NUM" --jq .node_id)

ITEM_ID=$(gh api graphql -f query="
mutation { addProjectV2ItemById(input: {projectId: \"$PROJECT_ID\", contentId: \"$NODE_ID\"}) { item { id } } }
" --jq '.data.addProjectV2ItemById.item.id')

for pair in \
  "PVTSSF_lADOEJ3d0M4BVg6YzhQ8NQA:$STATUS_ID" \
  "PVTSSF_lADOEJ3d0M4BVg6YzhQ8WNw:$SETOR_ID" \
  "PVTSSF_lADOEJ3d0M4BVg6YzhQ8WfA:$PRIORIDADE_ID" \
  "PVTSSF_lADOEJ3d0M4BVg6YzhQ8Wh8:$TIPO_ID"; do
  FIELD_ID="${pair%%:*}"; OPT_ID="${pair##*:}"
  gh api graphql -f query="
  mutation { updateProjectV2ItemFieldValue(input: {
    projectId: \"$PROJECT_ID\", itemId: \"$ITEM_ID\",
    fieldId: \"$FIELD_ID\", value: {singleSelectOptionId: \"$OPT_ID\"}
  }) { projectV2Item { id } } }" >/dev/null
done

echo "#$NUM criado — $URL"
```

## Script — PowerShell (máquina Windows)

Mesma lógica. **Carregar o token de `secrets.env`, nunca hardcoded:**

```powershell
Get-Content "$env:USERPROFILE\.config\agents\secrets\secrets.env" | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process') }
}
$token = $env:GITHUB_TOKEN
$projectId = "PVT_kwDOEJ3d0M4BVg6Y"

$payload = @{ title = "[Projeto] Atividade"; body = $body; assignees = @("jpazv") } | ConvertTo-Json -Depth 3
$issue = Invoke-RestMethod -Uri "https://api.github.com/repos/Grupo-Velas/produtividade-bi-dev/issues" `
  -Method POST -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json; charset=utf-8" } `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))

$q = '{"query":"mutation { addProjectV2ItemById(input: {projectId: \"' + $projectId + '\" contentId: \"' + $issue.node_id + '\"}) { item { id } } }"}'
$itemId = (Invoke-RestMethod -Uri "https://api.github.com/graphql" -Method POST `
  -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } -Body $q).data.addProjectV2ItemById.item.id

foreach ($pair in @(
    @("PVTSSF_lADOEJ3d0M4BVg6YzhQ8NQA", "47fc9ee4"),
    @("PVTSSF_lADOEJ3d0M4BVg6YzhQ8WNw", "e9e14faa"),
    @("PVTSSF_lADOEJ3d0M4BVg6YzhQ8WfA", "025cac08"),
    @("PVTSSF_lADOEJ3d0M4BVg6YzhQ8Wh8", "f1cc9795")
)) {
    $q = '{"query":"mutation { updateProjectV2ItemFieldValue(input: {projectId: \"' + $projectId + '\" itemId: \"' + $itemId + '\" fieldId: \"' + $pair[0] + '\" value: {singleSelectOptionId: \"' + $pair[1] + '\"}}) { projectV2Item { id } } }"}'
    Invoke-RestMethod -Uri "https://api.github.com/graphql" -Method POST `
        -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } -Body $q | Out-Null
}
Write-Host "#$($issue.number) — $($issue.html_url)"
```

> ⚠️ **Nunca commitar PAT (`ghp_…`) no hub.** O GitHub revoga automaticamente token detectado em push. Guardar em `~/.config/agents/secrets/secrets.env` (fora do git).

---

## Imagens em cards e comentários

A **API do GitHub não faz upload de imagem** — é limitação da plataforma. Imagens só entram pela interface web.

**Manual (o que funciona sempre):** abrir o card → *Edit* → arrastar a imagem na caixa de texto (ou Ctrl+V). O GitHub gera `![image](https://github.com/user-attachments/...)`.

**Se já existe URL do `user-attachments`** (ex.: o usuário colou no chat), dá para embutir direto via API:
```markdown
![descrição](https://github.com/user-attachments/assets/<id>)
```
Essas URLs exigem autenticação para baixar — use `-H "Authorization: token $(gh auth token)"` no curl.

**Alternativa via MinIO** (bucket público `imagens`):
```bash
ssh velas_adm "cat > /tmp/$NOME" < "$ARQUIVO"
ssh velas_adm "docker exec minio mc cp /tmp/$NOME local/imagens/$NOME && rm /tmp/$NOME"
# https://storage.grupovelas.com.br/imagens/$NOME
```
Credenciais `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` em `secrets.env`. Depende do DNS no Cloudflare.

---

## Comportamento padrão ao criar

- Status: **Triagem/Backlog** · Prioridade: **Media** · Tipo: **Demanda** · Setor: **BI** (se interno)
- Confirmar com: `#NNN criado — <link>`
