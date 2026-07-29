# Handoff — Landing do Pulse: mockup do Hero não ficou bom

**Data:** 2026-07-29
**Repo:** `~/dev/raiox-mvp-html` (landing, `checkpulse.com.br`)
**Status:** trabalho interrompido a pedido do usuário. **Não commitado.**

---

## Resumo honesto

Nesta sessão eu:
1. Reduzi a landing de 10 para 4 seções (Hero/Dor/Prova/Fechamento), copy nova.
2. Corrigi um bug real de CSS (`.split-section` sem `align-content:center`).
3. Adicionei 3 seções sobre tempo de resposta / qualidade / temperatura do lead,
   a pedido do usuário — total de 7 seções.
4. Tentei adicionar um mockup animado de MacBook + iPhone no Hero, em CSS puro
   (o usuário pediu pra usar um arquivo `.psdt` de Downloads; não tenho
   Photoshop nem ferramenta de PSD instalada, então decidi construir em CSS).

**O mockup não ficou bom.** O usuário mandou parar depois de ver o resultado.
Pelo screenshot que eu mesmo tirei antes de parar: o texto do Hero aparece com
uma espécie de sombra/duplicação (dois estados de texto sobrepostos — suspeito
de conflito entre o fix de `.in-view` forçado via JS e a animação
char-by-char/`data-anim="char"` que já existia no site), e a composição
MacBook+iPhone não ficou com acabamento visual bom (base do laptop cortada,
iPhone sobrepondo de forma tosca).

## Bug real que encontrei e corrigi (esse ficou bom, pode manter)

Passei boa parte da sessão perseguindo um sintoma errado: "o Hero não aparece".
Cheguei a aplicar dois fixes que eram diagnóstico errado (scroll restoration do
navegador, timing do IntersectionObserver) — nenhum dos dois resolvia nada.

**A causa raiz real**, achada só depois de rodar Playwright com Chrome do
sistema (`channel: "chrome"`, sem precisar baixar o Chromium do Playwright, que
falhou por timeout de rede) e inspecionar `getComputedStyle` diretamente:

```css
body.landing-mode .intro-hero { display: none; }
```

Essa regra é legada do design original de 10 seções: a antiga primeira seção
(`.intro-hero`) era só uma splash escura decorativa, e a segunda seção (que eu
removi na reescrita para 4 seções) era o Hero de verdade — a que ficava visível
no tema claro (`landing-mode`, que é o modo padrão ao carregar a página via
`showLanding()`). Quando consolidei todo o Hero dentro de `.intro-hero`, essa
regra passou a escondê-lo **sempre**, silenciosamente, sem erro de console.

Corrigido para `display: grid` (mesmo valor que a base `.landing-section` já
usa). Confirmado via Playwright que `.intro-hero` passou a ter bounding box e
altura reais depois do fix.

**Isso já estava quebrado desde a MINHA PRIMEIRA reescrita** (a de 4 seções,
bem antes do pedido do mockup) — ou seja, o Hero pode nunca ter aparecido pra
ninguém que testou a página nesta sessão inteira, e eu não percebi antes porque
só tinha validado estrutura HTML (balanceamento de tags), nunca renderização
real.

## Lição pra próxima sessão

**Validação estrutural (tags balanceadas, listeners não órfãos) não pega bug de
CSS que esconde elemento.** Só desconfiei de verdade quando o usuário mandou
print pela segunda vez dizendo "não tem nada". Da próxima vez que alguém
reportar "não aparece", ir direto pra inspeção real (Playwright/Chrome
headless com `getComputedStyle`), não ficar validando só a estrutura do HTML.

**Como rodar Playwright sem depender do download do Chromium** (que falhou por
timeout de rede nesta máquina): usar o pacote `playwright-core` já baixado em
`~/.npm/_npx/<hash>/node_modules/playwright-core` com
`chromium.launch({ channel: "chrome", headless: true })`, que pilota o Google
Chrome já instalado no sistema em vez de baixar um binário próprio. Script de
diagnóstico ficou salvo em `~/.npm/_npx/e41f203b7505f1fb/pw_check2.mjs`.

## Estado atual do arquivo

`~/dev/raiox-mvp-html/index.html` está com:
- 7 seções de landing (Hero, Dor, 3 pilares, Prova, Fechamento) — **essa parte
  o usuário não reclamou, só do mockup.**
- O fix do `display:none` legado — **deixar, é bug real corrigido.**
- O bloco CSS/HTML do mockup MacBook+iPhone no Hero — **usuário não gostou do
  resultado visual, precisa refazer ou remover.**

**Nada foi commitado nesta sessão.** `git status` deve mostrar tudo como
modificação não commitada em `index.html`. Não fiz `git add`/`git commit`.

## Suspeita sobre o bug visual do texto duplicado/sombra

Não investigado a fundo (sessão interrompida antes). Hipótese mais provável:
o fix aplicado bem antes nesta sessão —
```js
document.querySelectorAll(".intro-hero [data-anim]").forEach(el => el.classList.add("in-view"));
```
— força `.in-view` imediatamente em todos os `[data-anim]` do Hero, inclusive
nos que usam `data-anim="char"` (o h1, que o JS quebra em `<span class="char">`
por letra para animar). Se esse forçar aconteceu ANTES do `splitChars()` rodar
e reprocessar o DOM, ou se a classe `in-view` aplicada duas vezes (uma pelo
forçar, outra pelo IntersectionObserver de verdade quando a seção finalmente
ficou visível após o fix do `display:none`) causar dupla-transição visual —
isso explicaria a aparência de "sombra"/texto duplicado no screenshot. Precisa
confirmar inspecionando o DOM renderizado (`.char` spans) e os estilos computados
do h1, não é confirmado, é só a hipótese mais provável dado o que se sabe.

## Próximo passo recomendado

1. Decidir: manter as 7 seções (parecem ok) e só remover/refazer o mockup, ou
   descartar o mockup por ora e voltar a ele depois com mais cuidado.
2. Se for refazer o mockup: investigar a hipótese do `.in-view` duplo antes de
   qualquer ajuste visual — pode ser a causa do texto esquisito, não o CSS do
   MacBook/iPhone em si.
3. Se for remover: reverter só o bloco `.hero-mockup`/`.mockup-*` (CSS) e o
   markup `hero-inner-split`/`hero-copy-col`/`.hero-mockup` (HTML), mantendo o
   fix do `display:none` e as 7 seções.
