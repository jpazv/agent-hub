# Handoff — Boas praticas: complexidade ciclomatica de McCabe

**Data:** 2026-07-28  
**Maquina:** mac-grupovelas  
**Tipo:** conhecimento / boas praticas de engenharia  
**Escopo:** qualidade de codigo, testes, refatoracao

---

## Tema

Complexidade ciclomatica de McCabe e uma metrica criada por Thomas J.
McCabe em 1976 para medir a complexidade estrutural de um trecho de codigo.
Ela estima quantos caminhos independentes existem dentro de uma funcao,
metodo ou programa.

Quanto mais decisoes existem no codigo, mais caminhos possiveis de execucao
existem. Mais caminhos significam mais dificuldade para entender, testar e
manter.

---

## Regra pratica de calculo

Forma simples:

```text
complexidade = numero de decisoes + 1
```

Costumam contar como decisoes:

- `if`
- `else if`
- `for`
- `while`
- `case` em `switch`
- `catch`
- operadores logicos que criam ramificacao, como `&&` e `||`, dependendo da
  ferramenta

Exemplo:

```js
function aprovar(pessoa) {
  if (pessoa.idade >= 18) {
    if (pessoa.documentoValido) {
      return true;
    }
  }

  return false;
}
```

Ha 2 decisoes:

- `if pessoa.idade >= 18`
- `if pessoa.documentoValido`

Complexidade:

```text
2 + 1 = 3
```

---

## Interpretacao sugerida

```text
1-5    simples, facil de entender
6-10   moderada, ainda aceitavel
11-20  complexa, pede atencao
21+    muito complexa, forte candidata a refatoracao
```

Esses limites nao sao lei. Uma funcao com complexidade 12 pode ser aceitavel
se for muito clara. Uma funcao com complexidade 5 pode ser ruim se misturar
responsabilidades.

---

## Por que importa

A complexidade ciclomatica ajuda a responder:

- Quantos testes minimos preciso para cobrir os caminhos principais?
- Essa funcao esta acumulando regras demais?
- O codigo ficou dificil de revisar?
- Existe risco maior de bug ao alterar?

Use a metrica como alerta, nao como verdade absoluta. O objetivo nao e
"baixar numero"; e tornar o codigo mais facil de entender, testar e
modificar.

---

## Sinais de problema

Exemplo de funcao com ramificacoes demais:

```js
function calcularPreco(cliente, produto, cupom) {
  if (cliente.vip) {
    if (produto.categoria === "premium") {
      if (cupom) {
        return produto.preco * 0.7;
      }
      return produto.preco * 0.8;
    }

    if (cliente.tempoDeCasa > 12) {
      return produto.preco * 0.85;
    }

    return produto.preco * 0.9;
  }

  if (cupom && cupom.valido) {
    return produto.preco * 0.95;
  }

  return produto.preco;
}
```

O problema nao e so o numero de `if`s. O problema e que a funcao mistura
varias regras de negocio e obriga quem le a simular mentalmente muitos
cenarios.

---

## Boas praticas

### 1. Preferir retornos antecipados

Evita aninhamento profundo:

```js
function podeComprar(usuario) {
  if (!usuario.ativo) return false;
  if (!usuario.emailVerificado) return false;
  if (usuario.bloqueado) return false;

  return true;
}
```

### 2. Extrair condicoes com nomes claros

```js
function clienteTemDescontoVip(cliente) {
  return cliente.vip && cliente.tempoDeCasa > 12;
}
```

Nomear a regra reduz carga mental melhor do que apenas mover codigo para
outra funcao sem criterio.

### 3. Separar regras em funcoes menores

```js
function calcularPreco(cliente, produto, cupom) {
  if (cupom?.valido) return precoComCupom(produto, cupom);
  if (cliente.vip) return precoVip(cliente, produto);

  return produto.preco;
}
```

### 4. Tratar a metrica como indicador de risco

Complexidade alta deve acionar revisao, testes focados e possivel
refatoracao. Ela nao deve virar uma meta cega. Codigo simples de medir pode
continuar ruim se tiver nomes fracos, responsabilidades misturadas ou efeitos
colaterais escondidos.

---

## Recomendacao para agentes

Ao revisar ou modificar codigo:

1. Identificar funcoes com muitas ramificacoes ou aninhamento profundo.
2. Avaliar se a complexidade representa regra de negocio real ou mistura de
   responsabilidades.
3. Reduzir primeiro aninhamento e duplicacao de condicoes.
4. Extrair funcoes quando o nome da funcao explicar uma regra do dominio.
5. Adicionar testes para os caminhos principais antes ou junto da refatoracao.

Resumo pratico:

```text
complexidade ciclomatica mede caminhos independentes;
complexidade alta aumenta custo de entendimento, teste e mudanca;
refatorar deve melhorar clareza, nao apenas reduzir um numero.
```
