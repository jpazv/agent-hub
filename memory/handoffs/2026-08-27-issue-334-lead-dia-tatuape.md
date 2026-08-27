# Handoff — Issue 334: gráfico Lead x Dia não aparece no Tatuapé

**Data:** 2026-08-27
**Sessão:** Claude Opus 5
**Status:** FIX APLICADO — aguardando aceite do Alexandre
**Issue:** Grupo-Velas/produtividade-bi-dev#334

---

## Contexto

Ernandes abriu a 334 reportando o Alexandre: "meu meta não aparece o gráfico de lead dia do Tatuapé". A issue pedia separar ausência de dado de falha de exibição — no fim **eram os dois**, em camadas diferentes.

## Parte 1 — o bug do card (RESOLVIDO)

### Causa

- Dashboard **341** — `🚀 Relatório de Performance - Alexandre Almeida`
- Card **11809** — `Leads x Dia` (dashcard 16292, aba RPD, tab_id 787)

Alexandre Almeida (`P0 - Alexandre Almeida`) tem **uma única unidade: ITC Vertebral - Tatuapé** (id_interno 224).

Todos os cards de Lead do dashboard filtram por sócio — `["contains",["field","socio"],"Alexandre"]` — menos o `Leads x Dia`, que ficou com lista de unidades chumbada de outro sócio (resíduo de clonagem):

```
["in", ["field","unidade"],
  "Instituto Trata - Bairro de Fátima",
  "Instituto Trata - Meireles",
  "ITC Vertebral - Bairro de Fátima",
  "ITC Vertebral - Mairiporã",
  "ITC Vertebral - Meireles"]     <- Tatuapé fora
```

Com filtro de Unidade em Tatuapé → 0 linhas (gráfico some). Sem filtro → mostrava lead de **outros sócios**. Os dois errados.

### Fix aplicado

`PUT /api/card/11809` → HTTP 200. Filtro novo:

```json
["and",
  ["=",["expression","Filtro datas válidas",{"base-type":"type/Boolean"}],true],
  ["contains",["field","socio",{"base-type":"type/Text"}],"Alexandre",{"case-sensitive":false}]]
```

Segue o sócio em vez de unidades fixas — não quebra de novo se ele ganhar outra unidade. Os `parameter_mappings` do dashcard já estavam corretos (marca / unidade / data), não foram tocados.

### Validação

| Cenário | Linhas | Soma |
|---|---|---|
| Antes, `Unidade = ITC Vertebral - Tatuapé` | 0 | — |
| Depois, sem filtro | 362 | 7.721 |
| Depois, `Unidade = ITC Vertebral - Tatuapé` | 362 | 7.721 |

Bate exatamente com o card 8493 (`Leads x Dia` do dash 266 — ITC Tatuapé), que já funcionava.

### Blast radius

Card 11809 usado **só no dashboard 341**. Nada mais afetado.

## Parte 2 — captação Z-API parada (NÃO É BI, fora do escopo)

Depois do fix os dias 26 e 27/08 continuaram zerados. Rastreado até a origem:

| Camada | Tatuapé em 26/08 |
|---|---|
| Card 11809 | 0 |
| `mv_leads_ps_propria` | 1 linha esqueleto, `telefone` nulo |
| `tb_leads_z_api` (base) | **nenhuma linha** |

MV fiel à base. Último lead real de Tatuapé: **25/08 12:24**.

### Três unidades secaram, não só o Tatuapé

| Unidade | id_interno | Média/dia (18–24/08) | Último dia com lead |
|---|---|---|---|
| Instituto Trata - Niterói | 39 | 12,3 | 21/08 |
| ITC Vertebral - Barra da Tijuca | 111 | 22,3 | 24/08 |
| ITC Vertebral - Tatuapé | 224 | 21,0 | 25/08 |

### Ingestão global saudável

```
data         leads  unidades  último lead_create
2026-08-24     963      40     2026-08-27 03:20
2026-08-25     872      39     2026-08-26 13:47
2026-08-26     724      38     2026-08-27 10:10
2026-08-27     115      34     2026-08-27 10:28   (parcial)
```

Contagem de unidades caiu **41 → 38** — exatamente as três, uma de cada vez.

### Descartado na investigação

- Não é Metabase nem a MV
- Não é o join de `log_unidades` — as três estão `Ativa` / `Própria`, sem distrato (logs 8394, 8390, 8388, criados 03/08/2026)
- Não é recorte de sócio, marca ou UF — Alexandre/SP, Carolina/RJ, Jhonatha/RJ, marcas diferentes

Padrão aponta para **instância Z-API caindo por unidade**, uma de cada vez.

## Conhecimento de modelo (útil para próximas)

- `mv_leads_ps_propria` = `mv_data_geral` **FULL JOIN** `tb_leads_z_api` em (data, id_interno, log_id), + `dim_unidades`, + `log_unidades`
- `WHERE lu.status='Ativa' AND lu.tipo='Própria' AND lu.canal<>'Matriz' AND COALESCE(lza.eh_outbound,false)=false`
- O FULL JOIN com `mv_data_geral` gera **linha esqueleto por dia mesmo sem lead** — por isso `count(*)`=1 e `count(telefone)`=0. Sempre contar por `telefone is not null`, nunca `count(*)`
- Metric **2229** = `Qtd. Leads (PS) - Próprias` = count where telefone not empty, sobre `card__2228`
- Card **2228** = model `Modelo de Leads Z-Api` = `select * from mv_leads_ps_propria`
- `lead_create` **não** é sinal confiável de recência por unidade (nulo em muitas linhas — ex. Bairro de Fátima com max 04/08 mas 27 leads depois). Usar `max(data) filter (where telefone is not null)`
- `mv_leads_ps_propria` não aparece em `information_schema.columns` (é matview) — usar `pg_attribute` / `pg_matviews`

## O que foi registrado na issue

Dois comentários:
1. [#issuecomment-5439171194](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/334#issuecomment-5439171194) — causa + fix + validação
2. [#issuecomment-5439363386](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/334#issuecomment-5439363386) — observação da captação Z-API, enquadrada como contexto, explicitamente fora do escopo

Decisão do JP: **não abrir issue separada** para a Z-API — só deixar a observação registrada caso o Alexandre questione os últimos dias.

## Pendências

- [ ] Confirmação do Alexandre de que o gráfico voltou (último item do checklist da 334)
- [ ] Captação Z-API de Niterói / Barra da Tijuca / Tatuapé — sem dono definido, não virou demanda formal
- Backup do JSON original do card 11809 ficou só no scratchpad da sessão (efêmero). Para reverter: trocar o filtro de volta para o `["in",["field","unidade"], ...5 unidades]`

## Próximo passo

Cobrar o aceite do Alexandre e fechar a 334. Se ele reclamar dos dias vazios, a resposta já está no comentário 2.
