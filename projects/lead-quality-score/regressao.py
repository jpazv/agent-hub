"""Regressao multipla e R² incremental.

Responde: quanto de explicacao NOVA a qualidade de atendimento adiciona sobre
o que temperatura e tempo de resposta ja explicam?

Como os preditores sao correlacionados entre si, o R² sequencial depende da
ordem de entrada. Por isso reporta-se tambem a contribuicao UNICA de cada
bloco (R² do modelo cheio menos R² sem aquele bloco) — essa nao depende de
ordem e e o numero honesto para "quanto SO ele explica".
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

import analyze
import score

warnings.filterwarnings("ignore")


# Blocos de preditores. log1p onde a escala e de cauda longa.
BLOCOS_LEAD = {
    "temperatura": ["temperatura"],
    "tempo_resposta": ["resp_log", "resp_ate30"],
    "qualidade": ["qualidade"],
    "volume": ["vol_log"],
}

BLOCOS_CELULA = {
    "temperatura": ["temperatura"],
    "tempo_resposta": ["resp_log", "pct_ate30"],
    "qualidade": ["pct_bom"],
    "volume": ["msgs_atendente"],
}


def _preparar_lead(r: pd.DataFrame) -> pd.DataFrame:
    d = pd.DataFrame(index=r.index)
    d["y"] = r["converteu"].astype(float)
    d["temperatura"] = r["temperatura"]
    t = pd.to_numeric(r["min_ate_secretaria_expediente"], errors="coerce")
    d["resp_log"] = np.log1p(t.clip(lower=0))
    d["resp_ate30"] = (t <= 30).astype(float)
    d["qualidade"] = r["qualidade"]
    d["vol_log"] = np.log1p(pd.to_numeric(r["msgs_atendente"], errors="coerce").fillna(0))
    return d.replace([np.inf, -np.inf], np.nan).dropna()


def _r2(d: pd.DataFrame, cols: list[str]) -> float:
    if not cols:
        return 0.0
    X = sm.add_constant(d[cols].astype(float), has_constant="add")
    return float(sm.OLS(d["y"].astype(float), X).fit().rsquared)


def _mcfadden(d: pd.DataFrame, cols: list[str]) -> float:
    X = sm.add_constant(d[cols].astype(float), has_constant="add") if cols else \
        sm.add_constant(pd.DataFrame(index=d.index).assign(_c=1.0)[[]], has_constant="add")
    try:
        return float(sm.Logit(d["y"].astype(float), X).fit(disp=0).prsquared)
    except Exception:  # noqa: BLE001
        return np.nan


def incremental(d: pd.DataFrame, blocos: dict[str, list[str]], ordem: list[str]) -> pd.DataFrame:
    """R² sequencial na ordem dada + contribuicao unica de cada bloco."""
    linhas, acum, r2_ant = [], [], 0.0
    for nome in ordem:
        acum = acum + blocos[nome]
        r2 = _r2(d, acum)
        linhas.append({"passo": f"+ {nome}", "vars": len(acum),
                       "R2": round(r2, 4), "delta_R2": round(r2 - r2_ant, 4),
                       "pct_explicado": round(100 * r2, 2)})
        r2_ant = r2
    todas = [c for n in ordem for c in blocos[n]]
    r2_full = _r2(d, todas)
    for nome in ordem:
        sem = [c for n in ordem if n != nome for c in blocos[n]]
        linhas.append({"passo": f"unico: {nome}", "vars": len(blocos[nome]),
                       "R2": round(r2_full - _r2(d, sem), 4),
                       "delta_R2": np.nan, "pct_explicado": round(100 * (r2_full - _r2(d, sem)), 2)})
    return pd.DataFrame(linhas)


def coeficientes(d: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Coeficientes padronizados: comparaveis entre si na mesma escala."""
    z = d[cols].astype(float)
    z = (z - z.mean()) / z.std(ddof=0)
    m = sm.OLS(d["y"].astype(float), sm.add_constant(z, has_constant="add")).fit()
    out = pd.DataFrame({"var": m.params.index, "beta_padronizado": m.params.values,
                        "p": m.pvalues.values})
    return out[out["var"] != "const"].round(4).reset_index(drop=True)


def main() -> int:
    print("=" * 78)
    print("NIVEL LEAD — base completa (tempo de resposta com variancia real)")
    print("=" * 78)
    r_full = score.rodar(estratificar=False)
    d = _preparar_lead(r_full)
    print(f"n = {len(d):,} leads | conversao {100*d['y'].mean():.2f}%\n")

    ordem = ["temperatura", "tempo_resposta", "qualidade"]
    inc = incremental(d, BLOCOS_LEAD, ordem)
    print("R² incremental (ordem: temperatura -> tempo -> qualidade):")
    print(inc.to_string(index=False))

    print("\nMesmos blocos + volume de conversa:")
    inc_v = incremental(d, BLOCOS_LEAD, ordem + ["volume"])
    print(inc_v.to_string(index=False))

    todas = [c for n in ordem + ["volume"] for c in BLOCOS_LEAD[n]]
    print(f"\nMcFadden pseudo-R² (logistica, modelo cheio): {_mcfadden(d, todas):.4f}")
    print("\nCoeficientes padronizados (modelo cheio):")
    print(coeficientes(d, todas).to_string(index=False))

    print("\n" + "=" * 78)
    print("NIVEL UNIDADE x SEMANA — o desenho do experimento")
    print("=" * 78)
    r = score.rodar(estratificar=True)
    dec = analyze.curva_decis(r)
    corte, _ = analyze.escolher_corte(dec)
    A = analyze.matriz_score(r, corte)
    extra = r.assign(ate30=(pd.to_numeric(r["min_ate_secretaria_expediente"], errors="coerce") <= 30).astype(float),
                     rlog=np.log1p(pd.to_numeric(r["min_ate_secretaria_expediente"], errors="coerce").clip(lower=0)))
    ag = extra.groupby(["unidade", "semana"]).agg(pct_ate30=("ate30", "mean"), resp_log=("rlog", "mean")).reset_index()
    ag["semana"] = pd.to_datetime(ag["semana"]).dt.normalize()
    A = A.merge(ag, on=["unidade", "semana"])
    B = analyze.matriz_cvs()
    p = A.merge(B[["unidade", "semana", "agend", "leads_sec", "cvs"]], on=["unidade", "semana"])
    p = p[p["leads"] >= analyze.MIN_LEADS_CELULA]

    for alvo, rotulo in [("conversao_lead", "conversao lead-level"), ("cvs", "%CVS oficial")]:
        dd = p.rename(columns={alvo: "y"})[["y"] + [c for b in BLOCOS_CELULA.values() for c in b]]
        dd = dd.replace([np.inf, -np.inf], np.nan).dropna()
        print(f"\n--- alvo: {rotulo} (n = {len(dd)} celulas) ---")
        print(incremental(dd, BLOCOS_CELULA, ordem + ["volume"]).to_string(index=False))

    # --- Excel
    xlsx = analyze.OUT / "regressao_multipla.xlsx"
    with pd.ExcelWriter(xlsx, engine="xlsxwriter") as xw:
        inc_v.to_excel(xw, sheet_name="lead_incremental", index=False)
        coeficientes(d, todas).to_excel(xw, sheet_name="lead_coeficientes", index=False)
        for alvo, aba in [("conversao_lead", "celula_conversao"), ("cvs", "celula_cvs")]:
            dd = p.rename(columns={alvo: "y"})[["y"] + [c for b in BLOCOS_CELULA.values() for c in b]]
            dd = dd.replace([np.inf, -np.inf], np.nan).dropna()
            incremental(dd, BLOCOS_CELULA, ordem + ["volume"]).to_excel(xw, sheet_name=aba, index=False)
    print(f"\nExcel: {xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
