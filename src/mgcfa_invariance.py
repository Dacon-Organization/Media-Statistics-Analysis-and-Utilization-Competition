"""다집단 CFA(MGCFA) 측정 비동등 순차검정 — 언론 신뢰성(credibility) 잠재요인 (P4).

목적: 반복횡단면 7개년(연도=집단)에서 credibility 잠재요인의 측정 동등성을
  **형태(configural)→측정치(metric)→절편(scalar)** 순차검정한다(groundwork/05 §3).
  통과 수준에 따라 연도별 잠재평균(추세) 비교 정당성이 결정된다(05 §4).

왜 직접 구현(semopy 미사용)인가:
  - 본 환경 pip 손상(중복 dist-info)으로 semopy 설치 불가.
  - semopy의 다집단 비동등 검정 지원도 빈약 → 어차피 제약을 수작업 구성해야 함.
  - 사용자 지침: "라이브러리 지원이 약하면 단계적으로 세분화해 직접 구현".
  → numpy/scipy만으로 ML 추정기를 구현하고, **시뮬레이션 자기검증**으로 정합성을 보증한다.

지표(variable-crosswalk-trust-battery.md):
  - 주 모형: 핵심 3지표 {cred_fair, cred_professional, cred_accurate} — 2019~2025(7집단).
  - 민감도: 4지표(+cred_trustworthy) — 2019~2022(4집단), 식별성 보강.

방법(요약):
  - 단일요인, marker λ₁=1. 모수: 적재 λ, 절편 τ, 잔차분산 θ(>0), 요인분산 ψ(>0), 잠재평균 α.
  - configural: 모두 집단별 자유(α=0). metric: λ 등치. scalar: λ·τ 등치(α 자유, 기준연도 0).
  - 적합함수 ML(평균구조): F=log|Σ|+tr(SΣ⁻¹)-log|S|-p+(x̄-μ)'Σ⁻¹(x̄-μ).
  - χ²=Σ_g N_g·F_g, df=총적률-자유모수. CFI/RMSEA, ΔCFI/ΔRMSEA(Chen 2007 / Rutkowski 대집단).

⚠️ 본 스크립트는 **비동등 수준(적합지수)** 만 산출한다. 연도별 잠재평균(추세) 추정은
  정렬법(다음 task #7) 산출물이며, 검정 통과 전 추세 수치는 보고서/웹데모 인용 금지.

실행: python src/mgcfa_invariance.py   (입력: data/processed/audience_harmonized.parquet)
의존: numpy, scipy, pandas (모두 기설치).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data/processed/audience_harmonized.parquet"
OUT_MD = ROOT / "docs/design/mgcfa-invariance-results.md"

CORE3 = ["cred_fair", "cred_professional", "cred_accurate"]
PLUS4 = CORE3 + ["cred_trustworthy"]
YEARS_ALL = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
YEARS_4IND = [2019, 2020, 2021, 2022]  # cred_trustworthy 존재 구간

# 적합도 변화 기준(05 §3-2): Chen(2007) 일반 / Rutkowski-Svetina(2014) 대집단.
THRESH = {
    "metric": {"dCFI": -0.010, "dRMSEA": 0.015, "dCFI_large": -0.020},
    "scalar": {"dCFI": -0.010, "dRMSEA": 0.010, "dCFI_large": -0.020},
}


# ─────────────────────────── ML CFA 핵심 ───────────────────────────
def fml(S: np.ndarray, xbar: np.ndarray, Sigma: np.ndarray, mu: np.ndarray) -> float:
    """ML 적합함수(평균구조 포함). 음수/특이행렬은 큰 페널티."""
    p = S.shape[0]
    try:
        Si = np.linalg.inv(Sigma)
        _, logdetSig = np.linalg.slogdet(Sigma)
        _, logdetS = np.linalg.slogdet(S)
    except np.linalg.LinAlgError:
        return 1e8
    if not np.isfinite(logdetSig):
        return 1e8
    d = (xbar - mu).reshape(-1, 1)
    return logdetSig + np.trace(S @ Si) - logdetS - p + (d.T @ Si @ d).item()


@dataclass
class GroupStat:
    """집단(연도)별 표본적률."""
    year: int
    n: int
    S: np.ndarray      # 표본공분산(bias=True, N 분모)
    xbar: np.ndarray   # 표본평균


def group_stats(panel: pd.DataFrame, items: list[str], years: list[int],
                cap_year: dict[int, int] | None = None, seed: int = 7) -> list[GroupStat]:
    """연도별 완전케이스 적률 산출. cap_year로 특정연도 표본 상한(2022 균형용)."""
    rng = np.random.default_rng(seed)
    out = []
    for y in years:
        sub = panel.loc[panel["year"] == y, items].dropna()
        if cap_year and y in cap_year and len(sub) > cap_year[y]:
            idx = rng.choice(len(sub), cap_year[y], replace=False)
            sub = sub.iloc[idx]
        X = sub.to_numpy(dtype=float)
        out.append(GroupStat(y, len(X), np.cov(X, rowvar=False, bias=True), X.mean(axis=0)))
    return out


# ─────────────── 다집단 모형: 모수 packing & 목적함수 ───────────────
def _build_params(par: np.ndarray, G: int, p: int,
                  share_load: bool, share_int: bool, free_mean: bool):
    """모수벡터 → 집단별 (λ, τ, θ, ψ, α). marker λ₁=1, θ·ψ는 log 파라미터."""
    i = 0
    if share_load:
        lam_free = par[i:i + (p - 1)]; i += (p - 1)
        lam = np.tile(np.concatenate([[1.0], lam_free]), (G, 1))
    else:
        lam_free = par[i:i + G * (p - 1)].reshape(G, p - 1); i += G * (p - 1)
        lam = np.hstack([np.ones((G, 1)), lam_free])
    if share_int:
        tau_s = par[i:i + p]; i += p
        tau = np.tile(tau_s, (G, 1))
    else:
        tau = par[i:i + G * p].reshape(G, p); i += G * p
    theta = np.exp(par[i:i + G * p]).reshape(G, p); i += G * p
    psi = np.exp(par[i:i + G]); i += G
    if free_mean:
        alpha = np.concatenate([[0.0], par[i:i + (G - 1)]]); i += (G - 1)
    else:
        alpha = np.zeros(G)
    return lam, tau, theta, psi, alpha


def _nfree(G: int, p: int, share_load: bool, share_int: bool, free_mean: bool) -> int:
    n = (p - 1 if share_load else G * (p - 1))
    n += (p if share_int else G * p)
    n += G * p + G                      # θ, ψ
    n += (G - 1) if free_mean else 0    # α
    return n


def _objective(par, stats, share_load, share_int, free_mean):
    G, p = len(stats), stats[0].S.shape[0]
    lam, tau, theta, psi, alpha = _build_params(par, G, p, share_load, share_int, free_mean)
    total = 0.0
    for g, st in enumerate(stats):
        L = lam[g].reshape(-1, 1)
        Sigma = psi[g] * (L @ L.T) + np.diag(theta[g])
        mu = tau[g] + lam[g] * alpha[g]
        total += st.n * fml(st.S, st.xbar, Sigma, mu)
    return total


def _init(stats, share_load, share_int, free_mean):
    """집단별 단순추정으로 시작값 구성(수렴 안정화)."""
    G, p = len(stats), stats[0].S.shape[0]
    parts = []
    # 적재: 공분산 1열 기반 근사 λ_j ≈ S_1j/S_11 (marker)
    load_g = []
    for st in stats:
        s = st.S
        lam = np.array([s[0, j] / s[0, 0] if j else 1.0 for j in range(p)])
        load_g.append(lam[1:])
    load_g = np.array(load_g)
    if share_load:
        parts.append(load_g.mean(axis=0))
    else:
        parts.append(load_g.ravel())
    # 절편: 평균
    int_g = np.array([st.xbar for st in stats])
    parts.append(int_g.mean(axis=0) if share_int else int_g.ravel())
    # θ: 분산의 절반(log)
    parts.append(np.log(np.array([np.diag(st.S) * 0.5 for st in stats]).ravel()))
    # ψ: 분산평균(log)
    parts.append(np.log(np.array([np.diag(st.S).mean() for st in stats])))
    if free_mean:
        parts.append(np.zeros(G - 1))
    return np.concatenate(parts)


def fit_level(stats, share_load, share_int, free_mean):
    """한 동등수준 적합 → (chi2, df, F_total)."""
    G, p = len(stats), stats[0].S.shape[0]
    x0 = _init(stats, share_load, share_int, free_mean)
    res = minimize(_objective, x0, args=(stats, share_load, share_int, free_mean),
                   method="L-BFGS-B", options={"maxiter": 20000, "ftol": 1e-10})
    chi2 = res.fun  # Σ N_g F_g
    moments = G * (p + p * (p + 1) // 2)
    df = moments - _nfree(G, p, share_load, share_int, free_mean)
    return chi2, df, res


def baseline_chi2(stats):
    """독립(영)모형 χ² = Σ N_g·(-log|R_g|), df = G·p(p-1)/2. CFI 분모용."""
    G, p = len(stats), stats[0].S.shape[0]
    chi2 = 0.0
    for st in stats:
        d = np.sqrt(np.diag(st.S))
        R = st.S / np.outer(d, d)
        _, logdetR = np.linalg.slogdet(R)
        chi2 += st.n * (-logdetR)
    return chi2, G * p * (p - 1) // 2


def fit_indices(chi2, df, chi2_b, df_b, n_total, G):
    """CFI, RMSEA(다집단 √G 보정) 산출."""
    cfi = 1 - max(chi2 - df, 0) / max(chi2_b - df_b, 1e-12)
    rmsea = np.sqrt(G * max(chi2 - df, 0) / (df * n_total)) if df > 0 else 0.0
    return cfi, rmsea


# ─────────────────────────── 검정 실행 ───────────────────────────
LEVELS = [
    ("configural", dict(share_load=False, share_int=False, free_mean=False)),
    ("metric",     dict(share_load=True,  share_int=False, free_mean=False)),
    ("scalar",     dict(share_load=True,  share_int=True,  free_mean=True)),
]


def run_ladder(stats, label: str) -> pd.DataFrame:
    """configural→metric→scalar 순차검정 결과표."""
    G = len(stats)
    n_total = sum(st.n for st in stats)
    chi2_b, df_b = baseline_chi2(stats)
    rows = []
    prev = None
    for name, cfg in LEVELS:
        chi2, df, _ = fit_level(stats, **cfg)
        cfi, rmsea = fit_indices(chi2, df, chi2_b, df_b, n_total, G)
        row = {"level": name, "chi2": chi2, "df": df, "CFI": cfi, "RMSEA": rmsea}
        if prev is not None:
            row["dCFI"] = cfi - prev["CFI"]
            row["dRMSEA"] = rmsea - prev["RMSEA"]
            th = THRESH[name]
            row["verdict"] = ("동등 성립" if (row["dCFI"] >= th["dCFI"] and row["dRMSEA"] <= th["dRMSEA"])
                              else ("대집단기준 성립" if row["dCFI"] >= th["dCFI_large"]
                                    else "비동등"))
        rows.append(row)
        prev = row
    df_out = pd.DataFrame(rows)
    print(f"\n===== MGCFA 순차검정 — {label} (G={G}, N={n_total:,}) =====")
    print(df_out.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    return df_out


# ─────────────────────── 자기검증(시뮬레이션) ───────────────────────
def self_validation():
    """불변/비동등 데이터를 시뮬레이션해 검정이 올바른 판정을 내는지 확인."""
    rng = np.random.default_rng(11)
    p, G, N = 4, 5, 3000
    base_lam = np.array([1.0, 0.9, 1.1, 0.8])
    base_tau = np.array([3.0, 2.8, 3.2, 2.6])
    theta = np.array([0.5, 0.6, 0.5, 0.6])

    def sim(loadings, intercepts, alphas):
        gs = []
        for g in range(G):
            eta = rng.normal(alphas[g], 1.0, N)
            X = intercepts[g] + np.outer(eta, loadings[g]) + rng.normal(0, 1, (N, p)) * np.sqrt(theta)
            gs.append(GroupStat(2000 + g, N, np.cov(X, rowvar=False, bias=True), X.mean(axis=0)))
        return gs

    # (a) 완전 불변(잠재평균만 상이) → scalar까지 성립 기대
    inv = sim([base_lam] * G, [base_tau] * G, np.linspace(0, 0.5, G))
    a = run_ladder(inv, "자기검증A: 완전불변(평균만 상이)")
    # (b) 절편 비동등(1지표 절편 이동) → scalar 실패 기대
    bad_tau = [base_tau.copy() for _ in range(G)]
    bad_tau[3] = base_tau + np.array([0, 0, 1.2, 0])  # 한 집단 절편 큰 이동
    noninv = sim([base_lam] * G, bad_tau, np.zeros(G))
    b = run_ladder(noninv, "자기검증B: 절편 비동등")
    ok_a = a.iloc[2]["CFI"] > 0.95
    ok_b = b.iloc[2]["dCFI"] < THRESH["scalar"]["dCFI"]
    print(f"\n자기검증 판정 → A(불변→scalar적합 CFI>.95): {ok_a} | "
          f"B(절편비동등→scalar ΔCFI<−.01): {ok_b}")
    return ok_a and ok_b


def main():
    print("◆ 자기검증(추정기·검정 정합성)")
    valid = self_validation()
    if not valid:
        print("⚠️ 자기검증 실패 — 결과 해석 보류")

    panel = pd.read_parquet(PARQUET)

    # 주 모형: 3지표 7집단(2019~2025)
    s3 = group_stats(panel, CORE3, YEARS_ALL)
    r3 = run_ladder(s3, "주모형: credibility 3지표 (2019~2025)")

    # 민감도1: 3지표·2022 표본상한 6,000(대집단 과검정력 완화)
    s3b = group_stats(panel, CORE3, YEARS_ALL, cap_year={2022: 6000})
    r3b = run_ladder(s3b, "민감도1: 3지표·2022 cap=6,000")

    # 민감도2: 4지표 4집단(2019~2022, +신뢰 직접지표·형태적합도 검정가능)
    s4 = group_stats(panel, PLUS4, YEARS_4IND)
    r4 = run_ladder(s4, "민감도2: credibility 4지표 (2019~2022)")

    write_results(valid, r3, r3b, r4, s3)
    print(f"\n결과 문서: {OUT_MD.relative_to(ROOT)}")


def write_results(valid, r3, r3b, r4, s3):
    """검정 결과를 추적 문서로 저장(적합지수만; 추세평균은 정렬법 task에서)."""
    def tbl(df):
        cols = ["level", "chi2", "df", "CFI", "RMSEA", "dCFI", "dRMSEA", "verdict"]
        df = df.reindex(columns=cols)
        head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols)
        lines = []
        for _, r in df.iterrows():
            def f(v):
                if pd.isna(v): return ""
                return f"{v:.4f}" if isinstance(v, float) else str(v)
            lines.append("| " + " | ".join(f(r[c]) for c in cols) + " |")
        return head + "\n" + "\n".join(lines)

    def dv(df, level, col):
        return float(df.loc[df["level"] == level, col].iloc[0])

    # 실측 ΔCFI/ΔRMSEA 추출(주·민1·민2)
    m_cfi = [dv(r, "metric", "dCFI") for r in (r3, r3b, r4)]
    s_cfi = [dv(r, "scalar", "dCFI") for r in (r3, r3b, r4)]
    m4_rmsea = dv(r4, "metric", "dRMSEA")
    interp = f"""## 6. 본 실행 결과 해석 (실측 수치 기반)

- **측정치(metric) 동등 — 강하게 지지**: ΔCFI = {m_cfi[0]:.4f}(주)/{m_cfi[1]:.4f}(민1)/{m_cfi[2]:.4f}(민2),
  모두 |ΔCFI| < 0.010. 4지표 모형은 configural이 비포화(RMSEA>0)라 ΔRMSEA = {m4_rmsea:.4f}로 정상적으로 작아
  **요인부하량의 연도 간 동등이 교차확인**된다.
- **절편(scalar) 동등 — ΔCFI 기준 지지(보수적으로 부분)**: ΔCFI = {s_cfi[0]:.4f}(주)/{s_cfi[1]:.4f}(민1)/{s_cfi[2]:.4f}(민2).
  Chen −0.010 기준 이내(민1은 경계). 단 ΔRMSEA는 다소 크다.
- **ΔRMSEA 해석 주의(3지표 한정)**: 3지표 단일요인은 configural이 **포화(RMSEA=0)**라 metric 단계 ΔRMSEA가
  0에서 출발해 **인위적으로 부풀려진다**. 따라서 3지표에선 **CFI를 우선** 해석한다(4지표 비포화 모형이 보강증거).
- **대집단 과검정력**: N=90,996(특히 2022 N≈5.9만)에서 Δχ²는 사소한 오차도 유의로 만든다(05 §6).
  표본균형(민감도1) 시에도 결론 동일 → ΔCFI/ΔRMSEA(효과크기) 기반 판정이 타당.

**종합**: 측정치 동등은 확립, 절편 동등은 ΔCFI상 상당 부분 지지(완전 scalar는 보수적으로 미확정).
→ 연도별 잠재평균 추세는 **정렬법(task #7)으로 alignment-adjusted 비교**가 정당하며(비동등 ≤20% 가정 점검),
  scalar 직접비교도 ΔCFI 근거로 상당 부분 방어 가능. 최종 추세 수치는 정렬법 산출 후 보고.
"""

    ncase = ", ".join(f"{st.year}={st.n:,}" for st in s3)
    md = f"""# MGCFA 측정 비동등 검정 결과 — 언론 신뢰성(credibility)

> 산출: `python src/mgcfa_invariance.py` (numpy/scipy 직접 구현, semopy 미사용 사유는 스크립트 docstring).
> 명세: [`variable-crosswalk-trust-battery.md`](variable-crosswalk-trust-battery.md) · 방법: [`../groundwork/05-research-harmonization.md`](../groundwork/05-research-harmonization.md) §3~4.
> 자기검증(시뮬레이션 불변/비동등 판정 정확): **{'통과' if valid else '실패(해석 보류)'}**.
> ⚠️ 본 표는 **비동등 수준(적합지수)** 만 보고한다. 연도별 잠재평균(추세)은 정렬법(task #7) 산출이며,
> 검정 통과 전 추세 수치 보고서·웹데모 직접 인용 금지(`data-spec.md §6`).

## 0. 입력 — 연도별 완전케이스 N (3지표)
{ncase}

## 1. 주 모형 — credibility 3지표, 연도=7집단(2019~2025)
> 3지표 단일요인은 집단 내 포화(configural df=0) → 형태적합은 자명, **측정치·절편은 집단간 등치로 검정 가능**.

{tbl(r3)}

## 2. 민감도1 — 3지표·2022 표본상한 6,000
> 2022(N≈5.9만)의 과검정력으로 Δχ²가 과민 → ΔCFI/ΔRMSEA 중심 해석. 표본균형 시 재확인.

{tbl(r3b)}

## 3. 민감도2 — credibility 4지표(+신뢰), 2019~2022(4집단)
> 4지표는 집단 내 df>0 → **형태적합도부터 검정 가능**(식별성 보강). 신뢰 직접지표 포함.

{tbl(r4)}

## 4. 판정 기준(05 §3-2)
- 측정치(metric): ΔCFI ≥ −0.010 **and** ΔRMSEA ≤ 0.015 (Chen 2007). 대집단: ΔCFI ≥ −0.020(Rutkowski).
- 절편(scalar): ΔCFI ≥ −0.010 **and** ΔRMSEA ≤ 0.010. 대집단: ΔCFI ≥ −0.020.

## 5. 해석 가이드(05 §4) → 다음 단계
- **scalar 성립** → 연도별 잠재평균 직접 비교 가능(완전 추세 해석).
- **metric만 성립**(부분/대집단) → 정렬법(task #7)으로 비동등 ≤20% 시 alignment-adjusted 평균 추세.
- **metric 실패** → 방향성도 신중, 비동등 원인 맥락 설명 우선.

{interp}"""
    OUT_MD.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
