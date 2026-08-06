"""Matriz de Eficiencia do Atendimento (issue #240) + testes de confiabilidade.

Eficiencia = CVS_real / CVS_esperado, onde CVS_esperado vem do mix de
temperaturas do lead (framework O/E, observed/expected).

Entra: export da query de eficiencia (unidade x semana).
Sai:   matriz pivotada + validacao + teste de persistencia.

Os numeros de validacao do issue (0,77 vs CVS real, 0,08 vs CVS esperado) sao
parcialmente ARITMETICOS: CVS_real e o numerador da eficiencia e CVS_esperado e
o denominador. Correlacionar uma razao com seu proprio numerador da alto por
construcao. Os testes que sustentam a metrica sao os de confiabilidade:
persistencia entre semanas e split-half.
"""
from __future__ import annotations

import pathlib
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

OUT = pathlib.Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
MIN_SEMANAS = 6  # unidade precisa disso para entrar nos testes de confiabilidade


def carregar(caminho: str) -> pd.DataFrame:
    d = pd.read_excel(caminho)
    d["semana"] = pd.to_datetime(d["semana"])
    return d.sort_values(["unidade", "semana"])


def validacao(d: pd.DataFrame) -> pd.DataFrame:
    """Reproduz os numeros do issue. Ver ressalva no docstring do modulo."""
    linhas = []
    for a, b, nota in [
        ("eficiencia", "cvs_real", "ALTO POR CONSTRUCAO: cvs_real e o numerador da eficiencia"),
        ("eficiencia", "cvs_esperado", "BAIXO POR CONSTRUCAO: cvs_esperado e o denominador"),
        ("delta_pp", "cvs_real", "delta = real - esperado, mesma ressalva"),
        ("cvs_esperado", "cvs_real", "este SIM e informativo: mix de leads prediz conversao?"),
        ("pct_quente", "cvs_real", "idem: so o mix"),
        ("eficiencia", "n_leads", "eficiencia depende do tamanho da celula? (deveria dar ~0)"),
    ]:
        s = d[[a, b]].dropna()
        pr, pp = stats.pearsonr(s[a], s[b])
        sr, sp = stats.spearmanr(s[a], s[b])
        linhas.append({"x": a, "y": b, "n": len(s), "pearson": round(pr, 4),
                       "p": round(pp, 6), "spearman": round(sr, 4), "nota": nota})
    return pd.DataFrame(linhas)


def persistencia(d: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """A eficiencia da unidade numa semana prediz a da semana seguinte?

    E o teste decisivo. Se a metrica captura atendimento (atributo estavel da
    unidade), persiste. Se e o acaso da semana, nao persiste.
    """
    d = d.sort_values(["unidade", "semana"]).copy()
    d["ef_prox"] = d.groupby("unidade")["eficiencia"].shift(-1)
    d["semana_prox"] = d.groupby("unidade")["semana"].shift(-1)
    # so pares de semanas consecutivas
    consec = (d["semana_prox"] - d["semana"]).dt.days == 7
    par = d[consec & d["ef_prox"].notna()]
    pr, pp = stats.pearsonr(par["eficiencia"], par["ef_prox"])
    sr, sp = stats.spearmanr(par["eficiencia"], par["ef_prox"])

    # decomposicao de variancia: entre unidades vs dentro (semana a semana)
    grande = d["eficiencia"].mean()
    med_un = d.groupby("unidade")["eficiencia"].transform("mean")
    var_entre = ((med_un - grande) ** 2).mean()
    var_dentro = ((d["eficiencia"] - med_un) ** 2).mean()
    icc = var_entre / (var_entre + var_dentro)

    # split-half: semanas pares vs impares, por unidade
    d["metade"] = (d.groupby("unidade").cumcount() % 2)
    sh = d.pivot_table(index="unidade", columns="metade", values="eficiencia", aggfunc="mean")
    sh = sh.dropna()
    n_sem = d.groupby("unidade")["semana"].nunique()
    sh = sh[sh.index.isin(n_sem[n_sem >= MIN_SEMANAS].index)]
    shr = stats.pearsonr(sh[0], sh[1]) if len(sh) > 3 else (np.nan, np.nan)
    # correcao de Spearman-Brown (split-half subestima a confiabilidade total)
    sb = 2 * shr[0] / (1 + shr[0]) if np.isfinite(shr[0]) else np.nan

    resumo = {
        "pares_consecutivos": len(par),
        "persistencia_pearson": round(pr, 4), "p": round(pp, 6),
        "persistencia_spearman": round(sr, 4),
        "var_entre_unidades": round(var_entre, 4),
        "var_dentro_unidade": round(var_dentro, 4),
        "ICC (fracao entre unidades)": round(icc, 4),
        "split_half_r": round(shr[0], 4) if np.isfinite(shr[0]) else np.nan,
        "split_half_spearman_brown": round(sb, 4) if np.isfinite(sb) else np.nan,
        "unidades_no_split_half": len(sh),
    }
    return par[["unidade", "semana", "eficiencia", "ef_prox"]], resumo


def ranking(d: pd.DataFrame) -> pd.DataFrame:
    """Ranking por unidade, agregando de volta (pesa por leads, nao media de medias)."""
    g = d.groupby("unidade").apply(lambda x: pd.Series({
        "semanas": x["semana"].nunique(),
        "n_leads": int(x["n_leads"].sum()),
        "agend_real": int(x["agend_real"].sum()),
        "agend_esperado": round(x["agend_esperado"].sum(), 1),
        "cvs_real": round(100 * x["agend_real"].sum() / x["n_leads"].sum(), 2),
        "cvs_esperado": round(100 * x["agend_esperado"].sum() / x["n_leads"].sum(), 2),
        "eficiencia": round(x["agend_real"].sum() / max(x["agend_esperado"].sum(), 1e-9), 3),
        "ef_desvio_semanal": round(x["eficiencia"].std(), 3),
        "ef_min": round(x["eficiencia"].min(), 2),
        "ef_max": round(x["eficiencia"].max(), 2),
    })).reset_index()
    g["delta_pp"] = (g["cvs_real"] - g["cvs_esperado"]).round(2)
    return g.sort_values("eficiencia", ascending=False)


def main(caminho: str) -> int:
    d = carregar(caminho)
    print(f"{len(d)} celulas | {d.unidade.nunique()} unidades | {d.semana.nunique()} semanas "
          f"({d.semana.min().date()} a {d.semana.max().date()})\n")

    print("=" * 76)
    print("VALIDACAO — reproduzindo os numeros do issue")
    print("=" * 76)
    val = validacao(d)
    print(val.to_string(index=False))

    print("\n" + "=" * 76)
    print("CONFIABILIDADE — a metrica mede algo estavel?")
    print("=" * 76)
    pares, resumo = persistencia(d)
    for k, v in resumo.items():
        print(f"  {k:32s} {v}")

    print("\n" + "=" * 76)
    print("RANKING POR UNIDADE")
    print("=" * 76)
    rk = ranking(d)
    print(rk.to_string(index=False))

    # matriz pivotada — o que foi pedido
    matriz = d.pivot(index="unidade", columns="semana", values="eficiencia")
    matriz.columns = [c.strftime("%d/%m") for c in matriz.columns]
    matriz_leads = d.pivot(index="unidade", columns="semana", values="n_leads")
    matriz_leads.columns = [c.strftime("%d/%m") for c in matriz_leads.columns]

    xlsx = OUT / "matriz_eficiencia.xlsx"
    with pd.ExcelWriter(xlsx, engine="xlsxwriter") as xw:
        matriz.round(3).to_excel(xw, sheet_name="matriz_eficiencia")
        matriz_leads.to_excel(xw, sheet_name="matriz_n_leads")
        rk.to_excel(xw, sheet_name="ranking_unidade", index=False)
        d.to_excel(xw, sheet_name="celulas", index=False)
        val.to_excel(xw, sheet_name="validacao", index=False)
        pd.DataFrame([resumo]).T.rename(columns={0: "valor"}).to_excel(xw, sheet_name="confiabilidade")
        pares.to_excel(xw, sheet_name="pares_semana_seguinte", index=False)
    print(f"\nExcel: {xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
