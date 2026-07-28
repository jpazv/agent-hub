# Handoff — Pulse: Embedded Signup bloqueado, proposta ao parceiro, filtros

**Data:** 2026-07-27
**Máquina:** mac-grupovelas
**Repo:** `~/dev/pulse` (Vercel `pulse-app`)

---

## Nome correto do usuário

**João Paulo Azevedo** — não "João Pedro". O e-mail
`jpazevedomoreiraa@grupovelas.com.br` induz ao erro; não inferir daí.
Conta Google do Drive: `jp@grupovelas.com.br`.
Assinatura formal: "João Paulo Azevedo — Pulse".

## Domínios do Pulse (esclarecido)

`pulse-eco-app.vercel.app` **é alias do projeto Vercel `pulse-app`**, servido
de `~/dev/pulse`. Outros aliases do mesmo deploy: `app.checkpulse.com.br`,
`pulse-app-steel-tau.vercel.app`, `checkpulse-app.vercel.app`,
`pulse-app-eco.vercel.app`.

Atenção: `vercel --prod` atualiza só alguns aliases. Foi preciso rodar
`vercel alias set <deploy> pulse-eco-app.vercel.app` manualmente nas duas
vezes. Conferir sempre com `vercel alias ls` depois de subir.

## O que foi feito

1. **Env vars da Meta** setadas em produção no `pulse-app`: `META_APP_ID`,
   `META_APP_SECRET`, `META_CONFIG_ID`, `NEXT_PUBLIC_META_APP_ID`,
   `NEXT_PUBLIC_META_CONFIG_ID`, `NEXT_PUBLIC_WHATSAPP_EMBEDDED_SIGNUP_ENABLED=true`.
   - App ID `1572749784433574`, Config ID `4507266826228314` — recuperados do
     bundle JS em produção do tempo-resposta-app (são públicos).
   - `META_APP_SECRET` **não é recuperável** do Vercel (`env pull` devolve
     vazio) nem existe em `.env` local. Veio do painel da Meta.

2. **Conversas — filtros** (`app/(dashboard)/conversas/page.tsx` +
   `app/api/dashboard/conversas/route.ts`): faixa de TPR (atalhos + faixa
   livre), número de WhatsApp, classe de temperatura. `sem_resposta` é filtro
   separado porque `tpr_minutos IS NULL` não cai em intervalo numérico.
   Filtros também funcionam em modo demo (aplicados em JS sobre o demo-data).

3. **Detalhe da conversa virou somente-consulta**: removido o formulário de
   envio, adicionada busca no histórico com realce. O endpoint
   `POST /api/dashboard/enviar-mensagem` **continua existindo** e o helper
   `enviarMensagem` em `lib/client/api.ts` virou código morto — decidir se
   remove.

4. **Emoji → ícones lucide**: novo `components/dashboard/temperatura.tsx`
   (Flame/CloudSun/Snowflake), aplicado em Conversas, Espera e detalhe.

## Bloqueio principal: Acesso Avançado da Meta

Embedded Signup falha com `#2655111` — "app do parceiro não tem permissões
avançadas". Diagnóstico final:

- Usuário **já é Tech Provider**, mas isso **não concede Acesso Avançado**.
  Quem concede é o **App Review**, que ainda não foi submetido.
- Acesso Padrão ("Pronto para teste") só opera com ativos de teste do próprio
  app e usuários com cargo no app.
- **O número de teste da Meta NÃO contorna o bloqueio** — o gate está no fluxo
  do Embedded Signup, não no número. (Eu havia sugerido isso e estava errado.)
- Falta: Verificação de Negócio + 2 screencasts + submissão.
- Os screencasts **podem ser substituídos por scripts cURL / WhatsApp Manager**,
  o que dispensa construir tela de envio e de criação de template no produto.

## Decisão de produto: coexistence

O Pulse deve conectar números em **coexistence**
(`featureType: whatsapp_business_app_onboarding`, `sessionInfoVersion: 3`),
não Cloud API pura.

Motivo: em Cloud API pura o número sai do celular e a recepção perde a
ferramenta de trabalho — e como o dashboard agora é somente leitura, ninguém
responderia o lead. Em coexistence a secretária atende normalmente e a Meta
manda `message_echoes` (o parser em `lib/webhook/parse.ts` já trata).

Limitações aceitas: grupos não sincronizam, 20 mps, sem catálogo/etiquetas/
listas, exige WhatsApp Business App 2.24.17+.

**A validar no primeiro teste real:** se mensagens enviadas pelo WhatsApp Web
(dispositivo vinculado) geram echo. Se não gerarem, o TPR sai errado para
quem atende pelo computador.

## Proposta ao parceiro (Tech Provider já aprovado)

Objetivo: operar o Pulse sob o app Meta do parceiro até o App Review próprio
sair.

**Achado que mudou o desenho:** o parceiro alegou "só pode ter um webhook".
Verdade para o callback padrão, mas a Meta suporta **webhook override**:

- Por número: `POST /<PHONE_NUMBER_ID>` com
  `webhook_configuration.override_callback_uri` + `verify_token`
- Por WABA: `POST /<WABA_ID>/subscribed_apps` com os mesmos campos
- Precedência: número → WABA → callback padrão do app
- Template e conta não são sobrescrevíveis (irrelevante, só usamos `messages`)

Isso elimina a necessidade de o parceiro construir roteador, **e** tira o dado
da infraestrutura dele (argumento LGPD forte a favor dele).

Faturamento: cada clínica anexa o próprio método de pagamento à própria WABA —
o parceiro não estende linha de crédito e não é cobrado pela Meta.

**Artefatos gerados:**
- Proposta (HTML, artefato privado):
  https://claude.ai/code/artifact/6af267ca-32a4-4352-9a4d-f706ceea49bd
- Especificação técnica (Google Docs):
  https://docs.google.com/document/d/134Flx3SYsDEyx_7AgOne3U3D7-8_TsPNAQTzyGAy_e8/edit
- E-mail: `docs/email-parceiro-acesso-app.md` no repo pulse
- `docs/proposta-parceiro-acesso-app.md` está **DESATUALIZADO** (ainda descreve
  o roteador, sem seções de faturamento/dados). O HTML é a versão boa.

## Pendências

1. **Responsividade mobile** — não iniciada. Sidebar é `w-56` fixa sem
   breakpoint; em iPhone come metade da tela. Usuário pediu quebras baseadas
   nos modelos Apple.
2. **Caminho manual de conexão** — não existe forma de popular
   `whatsapp_connections` sem o Embedded Signup. Decidir entre script CLI, tela
   no dashboard, ou os dois. Destravaria demo ponta a ponta com o número de
   teste.
3. **Scripts cURL para o App Review** — propostos, não escritos.
4. Preencher lacunas da proposta: nome do parceiro, teto em meses, prazo de
   submissão, contrapartida.
5. Compartilhar o artefato e o Google Doc antes de mandar os links (ambos
   privados hoje).
6. Gmail MCP sem escopo de escrita — não foi possível criar rascunho.
