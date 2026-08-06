"""Temperatura x Qualidade: quanto cada uma explica, e quanto SOMAM.

Tres leituras, porque respondem perguntas diferentes:

  ENTRE unidades  — colapsa cada unidade na media das semanas (n=39). Responde
                    "unidade com lead mais quente / melhor atendimento converte
                    mais?". E o ranking de unidades.
  DENTRO (pooled) — cada unidade centralizada na propria media. Responde
                    "quando a unidade melhora, o CVS melhora?".
  POR UNIDADE     — serie temporal de cada unidade isolada.

Decomposicao de comunalidade: com preditores correlacionados, R²(A) + R²(B) NAO
e R²(A,B). A parte compartilhada e contada duas vezes. Aqui ela e separada.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

import analyze
import score

warnings.filterwarnings("ignore")

TEMP = "temperatura"
QUAL = "pct_bom"


def _r2(d: pd.DataFrame, cols: list[str], alvo: str) -> float:
    d = d[cols + [alvo]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(d) < len(cols) + 3:
        return np.nan
    X = sm.add_constant(d[cols].astype(float), has_constant="add")
    return float(sm.OLS(d[alvo].astype(float), X).fit().rsquared)


def comunalidade(d: pd.DataFrame, alvo: str, a: str = TEMP, b: str = QUAL) -> dict:
    """Separa: so A, so B, compartilhado, total."""
    r2a, r2b = _r2(d, [a], alvo), _r2(d, [b], alvo)
    r2ab = _r2(d, [a, b], alvo)
    return {
        "n": int(d[[a, b, alvo]].dropna().shape[0]),
        f"R2_{a}": r2a,
        f"R2_{b}": r2b,
        "soma_ingenua": r2a + r2b,
        "R2_juntas": r2ab,
        f"unico_{a}": r2ab - r2b,
        f"unico_{b}": r2ab - r2a,
        "compartilhado": r2a + r2b - r2ab,
    }


def _fmt(dic: dict) -> pd.DataFrame:
    out = []
    for k, v in dic.items():
        out.append({"componente": k, "valor": v if k == "n" else round(v, 4),
                    "pct": "" if k == "n" else f"{100*v:.2f}%"})
    return pd.DataFrame(out)


def main() -> int:
    r = score.rodar()
    dec = analyze.curva_decis(r)
    corte, _ = analyze.escolher_corte(dec)
    A = analyze.matriz_score(r, corte)
    B = analyze.matriz_cvs()
    p = A.merge(B[["unidade", "semana", "agend", "leads_sec", "cvs"]], on=["unidade", "semana"])
    p = p[p["leads"] >= analyze.MIN_LEADS_CELULA].copy()
    print(f"painel: {len(p)} celulas | {p.unidade.nunique()} unidades | {p.semana.nunique()} semanas\n")

    for alvo, rotulo in [("cvs", "%CVS oficial"), ("conversao_lead", "conversao lead-level")]:
        print("=" * 74)
        print(f"ALVO: {rotulo}")
        print("=" * 74)

        # --- ENTRE unidades
        entre = p.groupby("unidade").apply(lambda g: pd.Series({
            TEMP: np.average(g[TEMP].fillna(g[TEMP].mean()), weights=g["leads"]),
            QUAL: np.average(g[QUAL], weights=g["leads"]),
            "cvs": g["agend"].sum() / max(g["leads_sec"].sum(), 1),
            "conversao_lead": np.average(g["conversao_lead"], weights=g["leads"]),
        })).reset_index()
        print(f"\n-- ENTRE unidades (n={len(entre)}) --")
        for m in (TEMP, QUAL):
            d = entre[[m, alvo]].dropna()
            pr = stats.pearsonr(d[m], d[alvo])
            sr = stats.spearmanr(d[m], d[alvo])
            print(f"   {m:14s} Pearson {pr[0]:+.4f} (p={pr[1]:.3g})  Spearman {sr[0]:+.4f}")
        print(_fmt(comunalidade(entre, alvo)).to_string(index=False))

        # --- DENTRO (pooled com efeito fixo)
        dentro = p.copy()
        for c in (TEMP, QUAL, alvo):
            dentro[c] = dentro[c] - dentro.groupby("unidade")[c].transform("mean")
        print(f"\n-- DENTRO das unidades, pooled (n={len(dentro)}) --")
        for m in (TEMP, QUAL):
            d = dentro[[m, alvo]].dropna()
            pr = stats.pearsonr(d[m], d[alvo])
            sr = stats.spearmanr(d[m], d[alvo])
            print(f"   {m:14s} Pearson {pr[0]:+.4f} (p={pr[1]:.3g})  Spearman {sr[0]:+.4f}")
        print(_fmt(comunalidade(dentro, alvo)).to_string(index=False))
        print()

    # --- POR UNIDADE
    print("=" * 74)
    print("POR UNIDADE — serie de 6 semanas cada (n=6 por unidade: pouco poder)")
    print("=" * 74)
    linhas = []
    for u, g in p.groupby("unidade"):
        g = g.dropna(subset=[TEMP, QUAL, "cvs"])
        if len(g) < 4:
            continue
        linhas.append({
            "unidade": u, "semanas": len(g), "leads": int(g["leads"].sum()),
            "cvs_medio": g["agend"].sum() / max(g["leads_sec"].sum(), 1),
            "r_temperatura": stats.pearsonr(g[TEMP], g["cvs"])[0],
            "r_qualidade": stats.pearsonr(g[QUAL], g["cvs"])[0],
        })
    porund = pd.DataFrame(linhas).round(4)
    porund["quem_explica"] = np.where(
        porund["r_temperatura"].abs() > porund["r_qualidade"].abs(), "temperatura", "qualidade")
    print(porund.sort_values("r_qualidade", ascending=False).to_string(index=False))
    print(f"\n  mediana r_temperatura: {porund['r_temperatura'].median():+.4f}")
    print(f"  mediana r_qualidade  : {porund['r_qualidade'].median():+.4f}")
    print(f"  unidades onde qualidade explica mais: "
          f"{(porund['quem_explica']=='qualidade').sum()} de {len(porund)}")
    print(f"  r_temperatura positivo em {(porund['r_temperatura']>0).sum()}/{len(porund)} unidades")
    print(f"  r_qualidade positivo em   {(porund['r_qualidade']>0).sum()}/{len(porund)} unidades")

    xlsx = analyze.OUT / "comparativo_temp_qualidade.xlsx"
    with pd.ExcelWriter(xlsx, engine="xlsxwriter") as xw:
        porund.to_excel(xw, sheet_name="por_unidade", index=False)
        for alvo, aba in [("cvs", "comunalidade_cvs"), ("conversao_lead", "comunalidade_conv")]:
            entre = p.groupby("unidade").apply(lambda g: pd.Series({
                TEMP: np.average(g[TEMP].fillna(g[TEMP].mean()), weights=g["leads"]),
                QUAL: np.average(g[QUAL], weights=g["leads"]),
                "cvs": g["agend"].sum() / max(g["leads_sec"].sum(), 1),
                "conversao_lead": np.average(g["conversao_lead"], weights=g["leads"]),
            })).reset_index()
            dentro = p.copy()
            for c in (TEMP, QUAL, alvo):
                dentro[c] = dentro[c] - dentro.groupby("unidade")[c].transform("mean")
            pd.concat([
                _fmt(comunalidade(entre, alvo)).assign(leitura="entre unidades"),
                _fmt(comunalidade(dentro, alvo)).assign(leitura="dentro das unidades"),
            ]).to_excel(xw, sheet_name=aba, index=False)
    print(f"\nExcel: {xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
