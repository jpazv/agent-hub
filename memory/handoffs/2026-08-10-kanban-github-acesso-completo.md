---
data: 2026-08-10
maquina: mac-grupovelas
projeto: Hub / Kanban
status: acesso configurado e testado; full CRUD
---

# Kanban GitHub — acesso completo e instruções de boot

## 1. Board

- **Org:** Grupo-Velas
- **Project V2 number:** 1
- **Project node ID:** `PVT_kwDOEJ3d0M4BVg6Y`
- **Título:** Produtividade BI e Dev - Grupo Velas
- **URL:** https://github.com/orgs/Grupo-Velas/projects/1
- **Repo das issues:** `Grupo-Velas/produtividade-bi-dev`

## 2. Requisito de token

O `gh` precisa do escopo `project`. Conferir com:

```bash
gh auth status
```

Se faltar:

```bash
gh auth refresh -h github.com -s project -c
```

**O device flow NÃO funciona pelo bash do agente** — o JP precisa rodar no
terminal próprio. O código de 8 dígitos é impresso pelo `gh` no terminal,
não vem por app.

## 3. Identificação das tasks do JP

O board não usa assignee de forma confiável. Filtrar por:

- título casando `[JP]` ou `JP:`
- **OU** corpo contendo `jpazv`

## 4. Leitura — listar tasks

```bash
gh project item-list 1 --owner Grupo-Velas --format json --limit 400
```

Cada item tem: `id`, `title`, `status`, `assignees`, `labels`, `content.body`,
`content.number`, `repository`.

### Status disponíveis (mostrar nesta ordem)

| Status | Option ID | Mostrar por padrão |
|---|---|---|
| Em andamento | `df73e18b` | sim |
| Em validação | `83bf4887` | sim |
| Solicitada | `f75ad846` | sim |
| Triagem/Backlog | `47fc9ee4` | sim |
| Bloqueada | `cac16de1` | só se JP pedir |
| Concluída | `a0be2e68` | **nunca** |

### Prazo vencido

Comparar `### Prazo desejado` no corpo da issue com a data de hoje.
Sinalizar se vencido.

## 5. Escrita — editar status de uma task

```bash
gh project item-edit \
  --project-id PVT_kwDOEJ3d0M4BVg6Y \
  --id ITEM_NODE_ID \
  --field-id PVTSSF_lADOEJ3d0M4BVg6YzhQ8NQA \
  --single-select-option-id OPTION_ID
```

Exemplo mover para "Em andamento":

```bash
gh project item-edit \
  --project-id PVT_kwDOEJ3d0M4BVg6Y \
  --id PVTI_lADOEJ3d0M4BVg6Yzg... \
  --field-id PVTSSF_lADOEJ3d0M4BVg6YzhQ8NQA \
  --single-select-option-id df73e18b
```

## 6. Escrita — criar issue (task nova)

```bash
gh issue create \
  --repo Grupo-Velas/produtividade-bi-dev \
  --title "[JP] Título da task" \
  --body "$(cat <<'EOF'
### Setor solicitante

BI

### Tipo

Demanda

### Prioridade

Média

### Prazo desejado

YYYY-MM-DD

### Objetivo

Descrever o que precisa ser feito.

### Contexto

Descrever o porquê.

### Criterio de sucesso

Como validar que está pronto.

### Responsavel sugerido

jpazv
EOF
)"
```

Depois de criar, adicionar ao project:

```bash
gh project item-add 1 --owner Grupo-Velas --url ISSUE_URL
```

## 7. Escrita — comentar em uma issue

```bash
gh issue comment ISSUE_NUMBER \
  --repo Grupo-Velas/produtividade-bi-dev \
  --body "Comentário aqui"
```

## 8. Escrita — editar título ou corpo de uma issue

```bash
gh issue edit ISSUE_NUMBER \
  --repo Grupo-Velas/produtividade-bi-dev \
  --title "Novo título" \
  --body "Novo corpo"
```

Para editar só o título, omitir `--body` (e vice-versa).

## 9. Leitura — ver detalhes de uma issue

```bash
gh issue view ISSUE_NUMBER \
  --repo Grupo-Velas/produtividade-bi-dev \
  --json title,body,state,comments,labels,assignees
```

## 10. Fields do project (para edições avançadas)

| Field | Type | ID |
|---|---|---|
| Status | SingleSelect | `PVTSSF_lADOEJ3d0M4BVg6YzhQ8NQA` |
| Priority | SingleSelect | `PVTSSF_lADOEJ3d0M4BVg6YzhQ8OOg` |
| Size | SingleSelect | `PVTSSF_lADOEJ3d0M4BVg6YzhQ8OOk` |
| Setor solicitante | SingleSelect | `PVTSSF_lADOEJ3d0M4BVg6YzhQ8WNw` |
| Prioridade | SingleSelect | `PVTSSF_lADOEJ3d0M4BVg6YzhQ8WfA` |
| Tipo | SingleSelect | `PVTSSF_lADOEJ3d0M4BVg6YzhQ8Wh8` |
| Start date | Field | `PVTF_lADOEJ3d0M4BVg6YzhQ8OOs` |
| Target date | Field | `PVTF_lADOEJ3d0M4BVg6YzhQ8OOw` |

Para listar opções de um SingleSelect:

```bash
gh api graphql -f query='
query {
  organization(login: "Grupo-Velas") {
    projectV2(number: 1) {
      field(name: "FIELD_NAME") {
        ... on ProjectV2SingleSelectField {
          options { id name }
        }
      }
    }
  }
}'
```

## 11. Repos da org

pulse, unity-back, unity-front, raiox-mvp-html, locus_etl, locus_evento,
locus_front, locus_back, bcpc-pipeline, core-front, core-back,
produtividade-bi-dev

## 12. Regra de boot (referência ao AGENT-HUB.md)

Toda sessão DEVE:

1. Verificar `gh auth status` (escopo `project`)
2. Listar tasks do JP (filtro §3)
3. Reportar agrupadas por status (ordem §4)
4. Sinalizar prazos vencidos

Não esperar o JP pedir. Isso está na regra 8 do AGENT-HUB.md.
