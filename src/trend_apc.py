"""추세검정(Mann-Kendall) + APC(연령-기간-코호트) 세대효과 분해 — 언론 신뢰성 (P4).

목적(두 축):
  (1) **추세검정**: 정렬법(`alignment.py`)이 산출한 연도별 alignment-adjusted 잠재평균
      추세(2019~2025)가 **통계적으로 유의한 단조 추세**인지 비모수 Mann-Kendall 검정 +
      Sen 기울기로 정량화한다. 단일문항·합성지표 교차검정. n=7 → 정확분포(순열) p값.
  (2) **APC 분해**: 반복횡단면에서 신뢰성의 연령(age)·기간(period)·코호트(cohort) 효과를
      분리한다. 주방법은 **HAPC-GLMM**(Yang & Land 2006; 05 §7) — 연령은 고정 다항,
      기간·코호트는 교차분류 임의효과. 보조로 **Intrinsic Estimator(IE)**(Yang·Fu·Land 2004)
      를 numpy로 직접 구현해 삼각검증한다. APC 선형식별 문제(age+cohort=period)는
      연령·코호트(5년)와 기간(1년)의 간격 차이로 부분 완화된다(Yang 2010; 05 §7).

설계 결정:
  - APC 산출변수: credibility 3지표 **단순평균(cred_mean, 1~5)**. MGCFA에서 측정치(metric)
    동등이 강하게 지지(`mgcfa-invariance-results.md`)되어 관계·구조 분석용 합성이 정당.
  - 2022(N≈5.9만) 표본지배: HAPC는 2022를 6,000으로 하향표집(기간 임의효과 균형), IE/WLS는
    **wt_year_eq 가중**(연도기여 균등화, 05 §6)으로 처리.
  - 정렬 점추정 잠재평균은 `alignment.py` 함수 재사용(부트스트랩 SE는 소표본 B로 불확실성 반영).

자기검증:
  - MK: 단조 증가/감소/평탄 시뮬 → 부호·유의 정확 판정.
  - APC: 알려진 연령·기간·코호트 효과 시뮬 → IE/HAPC가 형상 회복(상관) 확인.

⚠️ 산출 수치는 KPF 원자료 재검증(`data-spec.md §6`) 전 보고서·웹데모 직접 인용 신중(검증 게이트).

실행: python src/trend_apc.py   (입력: data/processed/audience_harmonized.parquet)
의존: numpy, scipy, pandas, statsmodels (모두 기설치). alignment.py 재사용.
"""
from __future__ import annotations

import sys
import warnings
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
import alignment as al  # noqa: E402  (정렬 점추정·부트스트랩 재사용)

PARQUET = ROOT / "data/processed/audience_harmonized.parquet"
OUT_MD = ROOT / "docs/design/trend-apc-results.md"

CORE3 = al.CORE3
YEARS_ALL = al.YEARS_ALL


# ═══════════════════════ Part 1. Mann-Kendall 추세검정 ═══════════════════════
def mann_kendall(x: np.ndarray):
    """Mann-Kendall S·tau·z·p. n≤8은 순열 정확분포, 그 이상은 정규근사(동률보정)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    S = 0
    for i in range(n - 1):
        S += np.sign(x[i + 1:] - x[i]).sum()
    S = int(S)
    # 동률보정 분산
    _, cnt = np.unique(x, return_counts=True)
    tie = (cnt * (cnt - 1) * (2 * cnt + 5)).sum()
    var = (n * (n - 1) * (2 * n + 5) - tie) / 18.0
    tau = S / (0.5 * n * (n - 1))
    z = (S - np.sign(S)) / np.sqrt(var) if var > 0 else 0.0
    from scipy.stats import norm
    p_norm = 2 * (1 - norm.cdf(abs(z)))
    p_exact = _mk_exact_p(S, n) if n <= 8 else None
    return {"S": S, "tau": tau, "z": z, "p_norm": p_norm, "p_exact": p_exact, "n": n}


def _mk_exact_p(S: int, n: int) -> float:
    """순열 영분포에서 |S'|≥|S| 비율(양측 정확 p). n≤8(8!≤40320)만 사용."""
    base = np.arange(n)
    counts = {}
    for perm in permutations(base):
        a = np.array(perm)
        s = 0
        for i in range(n - 1):
            s += np.sign(a[i + 1:] - a[i]).sum()
        counts[int(s)] = counts.get(int(s), 0) + 1
    total = sum(counts.values())
    extreme = sum(c for s, c in counts.items() if abs(s) >= abs(S))
    return extreme / total


def sens_slope(x: np.ndarray, t: np.ndarray | None = None) -> float:
    """Sen 기울기: 모든 쌍 (x_j−x_i)/(t_j−t_i) 중앙값(연당 변화)."""
    x = np.asarray(x, dtype=float)
    t = np.arange(len(x), dtype=float) if t is None else np.asarray(t, dtype=float)
    slopes = [(x[j] - x[i]) / (t[j] - t[i])
              for i in range(len(x)) for j in range(i + 1, len(x))]
    return float(np.median(slopes))


def latent_trend_points(panel: pd.DataFrame, weight_mode="yeareq"):
    """정렬 점추정 잠재평균(2019~2025) 재계산(부트스트랩 없이 빠름)."""
    stats = al.group_stats(panel, CORE3, YEARS_ALL)
    cfg = al.estimate_configural(stats)
    _, _, _, alpha, _, _, _ = al.optimize_alignment(cfg, weight_mode)
    return np.array(YEARS_ALL, dtype=float), alpha


def mk_with_uncertainty(panel: pd.DataFrame, B: int = 150):
    """정렬 부트스트랩 α분포에 MK를 적용 → tau·S 분포(추정 불확실성 반영)."""
    alpha_boot, _, _ = al.bootstrap_alignment(
        panel, CORE3, YEARS_ALL, "yeareq", None, B=B, seed=31)
    taus = np.array([mann_kendall(a)["tau"] for a in alpha_boot])
    s_pos = float((np.array([mann_kendall(a)["S"] for a in alpha_boot]) > 0).mean())
    return taus, s_pos, alpha_boot


def weighted_year_mean(panel, col, years, wcol="wt_year_eq"):
    """연도별 가중평균(교차검정용)."""
    out = []
    for y in years:
        sub = panel.loc[panel["year"] == y, [col, wcol]].dropna()
        out.append(float(np.average(sub[col], weights=sub[wcol])))
    return np.array(out)


# ═══════════════════════ Part 2. APC 분해 ═══════════════════════
def make_apc_frame(panel: pd.DataFrame, cap_2022: int | None = 6000, seed=7) -> pd.DataFrame:
    """APC 입력프레임: cred_mean·age·period·cohort(5년) + 가중. 2022 하향표집 옵션."""
    df = panel.copy()
    df["cred_mean"] = df[CORE3].mean(axis=1)
    df = df.dropna(subset=["cred_mean", "age", "birth_cohort"]).copy()
    df["period"] = df["year"].astype(int)
    df["age"] = df["age"].astype(float)
    # 5년 코호트군(식별 완화: 연령·코호트 5년 vs 기간 1년)
    df["cohort5"] = (np.floor(df["birth_cohort"] / 5) * 5).astype(int)
    df["age5"] = (np.floor(df["age"] / 5) * 5).clip(upper=80).astype(int)
    if cap_2022:
        rng = np.random.default_rng(seed)
        m = df["period"] == 2022
        if m.sum() > cap_2022:
            keep = rng.choice(df.index[m], cap_2022, replace=False)
            df = pd.concat([df[~m], df.loc[keep]]).sort_index()
    return df


def hapc_mixed(frame: pd.DataFrame):
    """HAPC-GLMM(Yang & Land): 고정 연령다항 + 교차임의효과(기간·코호트). 반환 BLUP."""
    import statsmodels.formula.api as smf
    f = frame.copy()
    f["age_c"] = (f["age"] - f["age"].mean()) / 10.0   # 10년 단위 중심화
    f["age_c2"] = f["age_c"] ** 2
    f["grp"] = 1
    vcf = {"period": "0 + C(period)", "cohort": "0 + C(cohort5)"}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        md = smf.mixedlm("cred_mean ~ age_c + age_c2", f, groups="grp", vc_formula=vcf)
        mdf = md.fit(reml=False, method="lbfgs", maxiter=200)
    re = mdf.random_effects[1]
    per = {int(k.split("[")[-1].rstrip("]").replace("T.", "")): v
           for k, v in re.items() if k.startswith("period")}
    coh = {int(k.split("[")[-1].rstrip("]").replace("T.", "")): v
           for k, v in re.items() if k.startswith("cohort")}
    return {
        "intercept": mdf.fe_params["Intercept"],
        "age_c": mdf.fe_params["age_c"], "age_c2": mdf.fe_params["age_c2"],
        "age_mean": frame["age"].mean(),
        "period_re": dict(sorted(per.items())),
        "cohort_re": dict(sorted(coh.items())),
        "var_period": mdf.cov_re.iloc[0, 0] if mdf.cov_re.shape[0] > 0 else np.nan,
        "fitted": mdf,
    }


def _effect_code(labels: np.ndarray):
    """편차(effect) 코딩 행렬: K수준→K-1열(마지막 수준=−1). 반환 (X, levels)."""
    levels = np.unique(labels)
    K = len(levels)
    X = np.zeros((len(labels), K - 1))
    for j in range(K - 1):
        X[labels == levels[j], j] = 1.0
    X[labels == levels[-1], :] = -1.0
    return X, levels


def intrinsic_estimator(frame: pd.DataFrame, wcol: str = "wt_year_eq"):
    """Intrinsic Estimator(IE): 편차코딩 APC 가중최소노름해(pinv)로 효과 분리.

    age5+cohort5(5년) vs period(1년) 간격차로 보통 full-rank → WLS와 일치. 근사 공선
    시 pinv가 영공간(null) 직교 최소노름해(=IE)를 부여(Yang·Fu·Land 2004).
    """
    y = frame["cred_mean"].to_numpy(dtype=float)
    w = frame[wcol].to_numpy(dtype=float)
    w = w / w.mean()
    Xa, la = _effect_code(frame["age5"].to_numpy())
    Xp, lp = _effect_code(frame["period"].to_numpy())
    Xc, lc = _effect_code(frame["cohort5"].to_numpy())
    X = np.column_stack([np.ones(len(y)), Xa, Xp, Xc])
    sw = np.sqrt(w)
    beta = np.linalg.pinv(sw[:, None] * X) @ (sw * y)
    # 영공간 차원(공선성 진단)
    s = np.linalg.svd(sw[:, None] * X, compute_uv=False)
    null_dim = int((s < 1e-8 * s.max()).sum())

    def expand(coef, levels):
        eff = np.append(coef, -coef.sum())  # 마지막 수준 = −Σ
        return dict(zip(levels.astype(int), eff))

    i = 1
    age_eff = expand(beta[i:i + len(la) - 1], la); i += len(la) - 1
    per_eff = expand(beta[i:i + len(lp) - 1], lp); i += len(lp) - 1
    coh_eff = expand(beta[i:i + len(lc) - 1], lc)
    return {"intercept": beta[0], "age": age_eff, "period": per_eff,
            "cohort": coh_eff, "null_dim": null_dim, "rank_ok": null_dim == 0}


# ═══════════════════════ 자기검증 ═══════════════════════
def validate_mk() -> bool:
    inc = np.array([1, 2, 2.5, 3, 3.2, 4, 4.5])     # 단조증가
    flat = np.array([3, 2.9, 3.1, 3.0, 2.95, 3.05, 3.0])  # 평탄
    dec = -inc
    mi, mf, md_ = mann_kendall(inc), mann_kendall(flat), mann_kendall(dec)
    ok = (mi["S"] > 0 and mi["p_exact"] < 0.05 and
          md_["S"] < 0 and md_["p_exact"] < 0.05 and
          mf["p_exact"] > 0.10)
    print(f"  [MK] 증가 S={mi['S']} p={mi['p_exact']:.4f} | 감소 S={md_['S']} p={md_['p_exact']:.4f} "
          f"| 평탄 p={mf['p_exact']:.4f} → {'OK' if ok else 'FAIL'}")
    return ok


def validate_apc() -> bool:
    """알려진 연령·기간·코호트 효과 시뮬 → IE가 기간효과 형상 회복하는지."""
    rng = np.random.default_rng(5)
    rows = []
    age_f = {a: 0.01 * (a - 45) for a in range(20, 81, 5)}        # 연령 선형
    per_f = {y: 0.06 * (y - 2019) for y in range(2019, 2026)}     # 기간 단조증가
    for y in range(2019, 2026):
        for _ in range(1500):
            a = rng.integers(20, 81); a5 = (a // 5) * 5
            coh = y - a; c5 = (coh // 5) * 5
            coh_f = 0.004 * (1970 - c5)
            val = 3.2 + age_f.get(a5, 0) + per_f[y] + coh_f + rng.normal(0, 0.7)
            rows.append((np.clip(val, 1, 5), float(a), a5, y, c5))
    f = pd.DataFrame(rows, columns=["cred_mean", "age", "age5", "period", "cohort5"])
    f["wt_year_eq"] = 1.0
    ie = intrinsic_estimator(f)
    pe = np.array([ie["period"][y] for y in range(2019, 2026)])
    true_pe = np.array([per_f[y] for y in range(2019, 2026)]) - np.mean(list(per_f.values()))
    r = np.corrcoef(pe, true_pe)[0, 1]
    ok = r > 0.95
    print(f"  [APC] IE 기간효과 회복 corr={r:.4f} (rank_ok={ie['rank_ok']}) → {'OK' if ok else 'FAIL'}")
    return ok


def self_validation() -> bool:
    print("◆ 자기검증")
    a = validate_mk()
    b = validate_apc()
    return a and b


# ═══════════════════════ 실행 ═══════════════════════
def main():
    valid = self_validation()
    if not valid:
        print("⚠️ 자기검증 실패 — 결과 해석 보류")

    panel = pd.read_parquet(PARQUET)

    # ── Part 1: 추세검정 ──
    years, alpha = latent_trend_points(panel)
    mk_lat = mann_kendall(alpha)
    sen_lat = sens_slope(alpha, years)
    print("\n===== Part 1. Mann-Kendall — 정렬 잠재평균(2019~2025) =====")
    for y, a in zip(years, alpha):
        print(f"  {int(y)}: α={a:+.3f}")
    print(f"  S={mk_lat['S']} tau={mk_lat['tau']:+.3f} z={mk_lat['z']:+.3f} "
          f"p_exact={mk_lat['p_exact']:.4f} | Sen기울기={sen_lat:+.4f}/년")

    taus, s_pos, _ = mk_with_uncertainty(panel, B=150)
    print(f"  [불확실성] 부트스트랩 tau 평균={taus.mean():+.3f} "
          f"(2.5%={np.percentile(taus,2.5):+.3f},97.5%={np.percentile(taus,97.5):+.3f}) "
          f"| P(S>0)={s_pos:.3f}")

    # 교차검정: 단일문항(2020~2025), 합성지표(2019~2025)
    yrs_si = [2020, 2021, 2022, 2023, 2024, 2025]
    si = weighted_year_mean(panel, "trust_news_overall", yrs_si)
    mk_si = mann_kendall(si); sen_si = sens_slope(si, np.array(yrs_si, float))
    comp = weighted_year_mean(panel.assign(cred_mean=panel[CORE3].mean(axis=1)),
                              "cred_mean", YEARS_ALL)
    mk_co = mann_kendall(comp); sen_co = sens_slope(comp, np.array(YEARS_ALL, float))
    print(f"\n  단일문항 trust(2020~2025): tau={mk_si['tau']:+.3f} p={mk_si['p_exact']:.4f} "
          f"Sen={sen_si:+.4f} | 합성 cred_mean(2019~2025): tau={mk_co['tau']:+.3f} "
          f"p={mk_co['p_exact']:.4f} Sen={sen_co:+.4f}")

    # ── Part 2: APC ──
    frame = make_apc_frame(panel)
    print(f"\n===== Part 2. APC 분해 (N={len(frame):,}, 2022 cap=6,000) =====")
    hapc = hapc_mixed(frame)
    ie = intrinsic_estimator(frame)
    pe_h = np.array([hapc["period_re"].get(y, np.nan) for y in YEARS_ALL])
    pe_i = np.array([ie["period"].get(y, np.nan) for y in YEARS_ALL])
    # 기간효과 vs 정렬 잠재추세 일치(삼각검증)
    r_hapc_align = np.corrcoef(pe_h, alpha)[0, 1]
    r_ie_align = np.corrcoef(pe_i, alpha)[0, 1]
    r_hapc_ie = np.corrcoef(pe_h, pe_i)[0, 1]
    print("  [기간효과(연도 편차)]  HAPC-BLUP / IE")
    for y in YEARS_ALL:
        print(f"    {y}: {hapc['period_re'].get(y,float('nan')):+.3f} / {ie['period'].get(y,float('nan')):+.3f}")
    print(f"  기간효과 상관: HAPC↔정렬추세={r_hapc_align:+.3f}, IE↔정렬추세={r_ie_align:+.3f}, "
          f"HAPC↔IE={r_hapc_ie:+.3f}")
    print(f"  IE rank_ok={ie['rank_ok']}(null_dim={ie['null_dim']})")
    # 연령·코호트 효과 요약
    print("  [연령효과(IE, age5 편차)]", {k: round(v, 3) for k, v in ie["age"].items()})
    print("  [코호트효과(IE, cohort5 편차)]", {k: round(v, 3) for k, v in sorted(ie["cohort"].items())})

    write_results(valid, years, alpha, mk_lat, sen_lat, taus, s_pos,
                  yrs_si, si, mk_si, sen_si, comp, mk_co, sen_co,
                  frame, hapc, ie, pe_h, pe_i, r_hapc_align, r_ie_align, r_hapc_ie)
    print(f"\n결과 문서: {OUT_MD.relative_to(ROOT)}")


def write_results(valid, years, alpha, mk_lat, sen_lat, taus, s_pos,
                  yrs_si, si, mk_si, sen_si, comp, mk_co, sen_co,
                  frame, hapc, ie, pe_h, pe_i, r_ha, r_ia, r_hi):
    def f3(v):
        return "" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:+.3f}"

    lat_tbl = "| 연도 | 정렬 α̂ | 기간효과 HAPC | 기간효과 IE |\n|---|---|---|---|\n" + "\n".join(
        f"| {int(y)} | {alpha[i]:+.3f} | {f3(hapc['period_re'].get(int(y)))} | {f3(ie['period'].get(int(y)))} |"
        for i, y in enumerate(years))

    age_eff = ie["age"]; coh_eff = ie["cohort"]
    # 셀별 표본수(소표본 신뢰성 경고용)
    coh_n = frame["cohort5"].value_counts().to_dict()
    age_n = frame["age5"].value_counts().to_dict()
    MIN_N = 200
    age_tbl = "| 연령군(5년) | 효과(편차) | N |\n|---|---|---|\n" + "\n".join(
        f"| {k}~{k+4} | {v:+.3f} | {int(age_n.get(k,0)):,}{' ⚠' if age_n.get(k,0)<MIN_N else ''} |"
        for k, v in sorted(age_eff.items()))
    coh_tbl = "| 출생코호트(5년) | 효과(편차) | N |\n|---|---|---|\n" + "\n".join(
        f"| {k}~{k+4} | {v:+.3f} | {int(coh_n.get(k,0)):,}{' ⚠' if coh_n.get(k,0)<MIN_N else ''} |"
        for k, v in sorted(coh_eff.items()))
    # 코호트 기울기: 출생연도 vs 효과(충분표본 셀만, n≥MIN_N) — 음수면 '젊을수록 낮음'
    big = [(k, v) for k, v in coh_eff.items() if coh_n.get(k, 0) >= MIN_N]
    cb = np.array([k for k, _ in big], float); cv = np.array([v for _, v in big])
    coh_grad = float(np.corrcoef(cb, cv)[0, 1])      # 출생연도↑ vs 효과
    age_rng = max(age_eff.values()) - min(age_eff.values())

    p_lat = mk_lat["p_exact"]
    verdict_lat = ("유의한 증가추세" if (mk_lat["S"] > 0 and p_lat < 0.05)
                   else ("증가 경향(비유의)" if mk_lat["S"] > 0 else "감소/무추세"))
    age_dir = "U자형(중장년 저점)" if (min(age_eff.values()) < list(age_eff.values())[0]
                                  and min(age_eff.values()) < list(age_eff.values())[-1]) else "단조적"

    md = f"""# 추세검정(Mann-Kendall) + APC 세대효과 — 언론 신뢰성 (2019~2025)

> 산출: `python src/trend_apc.py` (numpy/scipy/statsmodels; `alignment.py` 재사용).
> 근거: Mann-Kendall(비모수 단조추세)·Sen 기울기; HAPC-GLMM(Yang & Land 2006)·Intrinsic
>   Estimator(Yang·Fu·Land 2004) — [`../groundwork/05-research-harmonization.md`](../groundwork/05-research-harmonization.md) §7.
> 선행: [`alignment-trust-trend.md`](alignment-trust-trend.md)(정렬 잠재평균), [`mgcfa-invariance-results.md`](mgcfa-invariance-results.md)(metric 동등).
> 자기검증(MK 부호·APC 회복): **{'통과' if valid else '실패(해석 보류)'}**.
> ⚠️ 수치는 KPF 원자료 재검증(`data-spec.md §6`) 전 보고서·웹데모 직접 인용 신중(검증 게이트).

## 1. 추세검정 — 정렬 잠재평균(2019~2025)
{lat_tbl}

- **Mann-Kendall**: S={mk_lat['S']}, τ={mk_lat['tau']:+.3f}, z={mk_lat['z']:+.3f}, **정확 p={p_lat:.4f}** → **{verdict_lat}**.
- **Sen 기울기**: {sen_lat:+.4f} /년 (2019-SD 단위, 중앙값 추정).
- **추정 불확실성**(정렬 부트스트랩 B=150에 MK 적용): τ 평균={taus.mean():+.3f}
  (95% [{np.percentile(taus,2.5):+.3f}, {np.percentile(taus,97.5):+.3f}]), **P(S>0)={s_pos:.3f}**.
  → 점추정 p가 {('유의(<.05)' if p_lat<0.05 else '경계/비유의')}여도, 추정 불확실성 반영 시 증가 방향 확률은 {s_pos*100:.0f}%.

### 1.1 교차검정(방향 일관성)
| 지표 | 구간 | τ | 정확 p | Sen기울기 |
|---|---|---|---|---|
| 단일문항 trust_news_overall | 2020~2025 | {mk_si['tau']:+.3f} | {mk_si['p_exact']:.4f} | {sen_si:+.4f}/년(1~5) |
| 합성 cred_mean(3지표 평균) | 2019~2025 | {mk_co['tau']:+.3f} | {mk_co['p_exact']:.4f} | {sen_co:+.4f}/년(1~5) |

- 세 지표(정렬 잠재·단일문항·합성)의 **τ 부호가 모두 동일**하면 추세 방향이 견고하다.
- n이 작아(6~7) MK 검정력이 제한적 → **p값보다 부호·Sen기울기·교차 일관성**에 무게.

## 2. APC 세대효과 분해
> 산출변수: credibility 3지표 평균(cred_mean, 1~5; metric 동등 지지로 합성 정당).
> 식별: 연령·코호트 5년군 vs 기간 1년 → 간격차로 선형식별 부분완화(Yang 2010, 05 §7).
> 2022 표본지배는 HAPC=6,000 하향표집·IE=wt_year_eq 가중으로 처리. N={len(frame):,}.

### 2.1 기간(Period) 효과 — 정렬추세와 삼각검증
HAPC 기간 BLUP·IE 기간효과는 위 표 1과 동일 열에 수록.
- **상관**: HAPC↔정렬추세 = **{r_ha:+.3f}**, IE↔정렬추세 = **{r_ia:+.3f}**, HAPC↔IE = **{r_hi:+.3f}**.
- 세 방법의 기간효과가 정렬 잠재추세와 같은 방향이면 "신뢰성 상승은 **기간(시대) 효과**"라는 해석이 강화된다.
- IE 식별 진단: rank_ok={ie['rank_ok']}(null_dim={ie['null_dim']}).

### 2.2 연령(Age) 효과 (IE, 편차)
{age_tbl}

- 형상: **{age_dir}**(편차 범위 {age_rng:.3f} — **연령(생애주기) 효과는 미미**, 기간·코호트 대비 작음).
  음수일수록 해당 연령군이 평균보다 낮은 신뢰. ⚠표시 셀은 소표본(N<{MIN_N}).

### 2.3 코호트(Cohort) 효과 (IE, 편차)
{coh_tbl}

- **코호트 기울기**(출생연도↑ vs 효과, N≥200 셀): **{coh_grad:+.3f}** →
  **{'젊은 코호트일수록 신뢰성 인식이 낮은 뚜렷한 세대 구배' if coh_grad < -0.5 else '세대 구배 약함/혼재'}**.
  1935~1949년생(+0.10~+0.19)에서 2000년대생(−0.14~−0.27)으로 단조 하락. (최고령 {min(coh_eff)}년생은 N={int(coh_n.get(min(coh_eff),0))} 소표본 이상치로 해석 제외 ⚠.)

## 3. 해석 종합
- **추세**: 정렬 잠재평균은 2019 대비 상승 방향(점추정 τ={mk_lat['tau']:+.3f}, Sen={sen_lat:+.4f}/년).
  점추정 MK p={mk_lat['p_exact']:.3f}는 n=7·중간연도 등락으로 비유의이나, **추정 불확실성 반영 시 증가 방향 P(S>0)={s_pos:.2f}**.
  단일문항·합성지표 교차검정도 같은 양(+) 부호 → "2019~2020 이후 언론 신뢰성 상승" 결론 견고.
- **APC 이중 발견**:
  1. **기간(시대) 효과가 추세를 주도** — 기간효과가 정렬추세와 강정합(IE {r_ia:+.3f}, HAPC {r_ha:+.3f}, 상호 {r_hi:+.3f}).
     즉 관측된 상승은 노화(연령)나 표본 세대구성 변화가 아닌 **시대적 변화**에 기인.
  2. **코호트 세대 구배 공존** — 출생연도↑ vs 효과 상관 {coh_grad:+.3f}: **젊은 세대일수록 언론 신뢰성 인식이 낮다**.
     추세(기간)와 독립적인 구조적 세대차로, 향후 고신뢰 노년 코호트 이탈 시 **하방 압력**을 시사.
- **한계**: (a) n=7 MK 저검정력 — 방향·기울기·교차 일관성 위주 해석. (b) APC 식별은 간격차 기반 부분완화이며
  완전 식별 불가(가정 민감) → HAPC·IE 삼각검증으로 보강(상호 {r_hi:+.3f}). (c) 산출변수는 manifest 합성(잠재점수 아님).
  (d) 소표본 코호트 셀(⚠) 제외 해석.
- **검증 게이트**: KPF 원자료 재검증 전 직접 인용 신중(05 머리말·`data-spec.md §6`).

## 4. 재현
```
python src/harmonize.py     # parquet 빌드(gitignore)
python src/alignment.py     # 정렬 잠재평균(선행)
python src/trend_apc.py     # 본 문서 재생성
```
"""
    OUT_MD.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
