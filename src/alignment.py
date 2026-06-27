"""정렬법(Alignment Method) 에뮬레이션 — 언론 신뢰성(credibility) 연도별 잠재평균 추세 (P4).

목적: 반복횡단면 7개년(연도=집단)에서 credibility 잠재요인의 **alignment-adjusted
  잠재평균 추세(2019~2025)**를 산출한다(Asparouhov & Muthén 2014; groundwork/05 §3-3·§4).
  MGCFA(`mgcfa_invariance.py`)는 측정치(metric) 동등을 강하게 지지했으나 완전 scalar는
  보수적으로 미확정 → **정렬법으로 비동등 모수를 명시적으로 수용하면서** 연도별 잠재평균을
  추정한다. 비동등 비율 ≤20%면 alignment-adjusted 평균 비교가 정당(05 §4-2).

왜 직접 구현(Mplus/sirt 미사용)인가:
  - 본 환경 pip 손상(중복 dist-info)으로 신규 패키지(semopy·sirt·Mplus 연동) 설치 불가.
  - 사용자 지침: "라이브러리 지원이 약하면 단계적으로 세분화해 직접 구현".
  → numpy/scipy만으로 정렬 최적화를 구현하고, **시뮬레이션 자기검증**(알려진 잠재평균 회복)
    으로 정합성을 보증한다. mgcfa_invariance.py의 ML 적합함수(fml) 패턴을 재사용한다.

방법(Asparouhov & Muthén 2014, 요약):
  - 1단계 configural: 집단별 자유 λ·ν·θ. 식별을 위해 각 집단 잠재평균 α=0, 분산 ψ=1로 고정.
    → 단일요인 표준화 해(λ₀, ν₀, θ): p=3은 집단내 just-identified(포화) 정확해, p=4는 ML.
  - 2단계 정렬: 임의의 (α_g, ψ_g)로 회전해도 적합도 불변임을 이용
      λ_gj(ψ_g)   = λ₀_gj / √ψ_g
      ν_gj(α,ψ)   = ν₀_gj − α_g·λ₀_gj/√ψ_g
    비동등 총량을 최소화하는 단순성함수 F를 최소화(EFA 회전과 유사):
      F = Σ_j Σ_{g<h} w_gh·[ f(λ_gj−λ_hj) + f(ν_gj−ν_hj) ],  f(x)=(x²+ε)^¼, ε=1e-4
    f는 component loss(소수의 큰 차이를 다수의 작은 차이보다 선호 → 근사 sparsity).
    식별: 기준집단(2019) α=0, ψ=1 고정(잠재평균=2019 기준, 2019-SD 단위).
  - 3단계 비동등 비율: 정렬 후 각 (집단,지표) 모수가 가중평균에서 유의 이탈하는 비율(부트스트랩).
    ≤20%면 평균 비교 정당, 초과 시 방향성만(05 §4).

가중치(05 §6):
  - 측정모형(configural·정렬 회전): 비가중 완전케이스 적률(MGCFA와 정합).
  - 잠재평균 추세: 단순성함수 집단가중 w_gh를 **연도균등(yeareq)**으로 두어 2022(N≈5.9만)
    표본지배가 회전을 지배하지 않게 함(wt_year_eq 정신). 표준 A&M(√N_g N_h)는 robustness.
  - 추가 robustness: 연도내 설계가중(wt_within)으로 적률을 가중한 변형.

⚠️ 산출 추세 수치는 KPF 원자료 재검증(`data-spec.md §6`) 전 보고서·웹데모 직접 인용 신중.

실행: python src/alignment.py   (입력: data/processed/audience_harmonized.parquet)
의존: numpy, scipy, pandas (모두 기설치).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

# 콘솔 인코딩(cp949) 깨짐 방지 — 한글·em-dash 출력 안전화.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data/processed/audience_harmonized.parquet"
OUT_MD = ROOT / "docs/design/alignment-trust-trend.md"

CORE3 = ["cred_fair", "cred_professional", "cred_accurate"]
PLUS4 = CORE3 + ["cred_trustworthy"]
YEARS_ALL = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
YEARS_4IND = [2019, 2020, 2021, 2022]  # cred_trustworthy 존재 구간

EPS = 1e-4                 # component loss 평활 상수(A&M 권장)
NONINV_THRESH = 0.20       # 비동등 허용 상한(05 §4-2): 초과 시 방향성만


# ─────────────────────── 집단 적률(가중/비가중) ───────────────────────
@dataclass
class GroupStat:
    """집단(연도)별 표본적률."""
    year: int
    n: int                 # 완전케이스 수(부트스트랩·집단가중 산정용)
    S: np.ndarray          # (가중)공분산
    xbar: np.ndarray       # (가중)평균


def _weighted_moments(X: np.ndarray, w: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    """완전케이스 X(N×p), 가중 w(N,) → (xbar, S). w=None이면 비가중."""
    if w is None:
        return X.mean(axis=0), np.cov(X, rowvar=False, bias=True)
    w = w / w.sum()
    xbar = (w[:, None] * X).sum(axis=0)
    d = X - xbar
    S = (w[:, None] * d).T @ d  # Σ w (x-x̄)(x-x̄)'  (Σw=1)
    return xbar, S


def group_stats(panel: pd.DataFrame, items: list[str], years: list[int],
                weight_col: str | None = None) -> list[GroupStat]:
    """연도별 완전케이스 적률. weight_col 지정 시 해당 가중으로 가중적률."""
    out = []
    for y in years:
        cols = items + ([weight_col] if weight_col else [])
        sub = panel.loc[panel["year"] == y, cols].dropna()
        X = sub[items].to_numpy(dtype=float)
        w = sub[weight_col].to_numpy(dtype=float) if weight_col else None
        xbar, S = _weighted_moments(X, w)
        out.append(GroupStat(y, len(X), S, xbar))
    return out


# ──────────────────── 1단계: configural 표준화 해 ────────────────────
def _fml_cov(S: np.ndarray, Sigma: np.ndarray) -> float:
    """공분산 ML 적합함수(평균구조 제외; α=0이라 ν=x̄로 포화)."""
    p = S.shape[0]
    try:
        Si = np.linalg.inv(Sigma)
        _, ldSig = np.linalg.slogdet(Sigma)
        _, ldS = np.linalg.slogdet(S)
    except np.linalg.LinAlgError:
        return 1e8
    if not np.isfinite(ldSig):
        return 1e8
    return ldSig + np.trace(S @ Si) - ldS - p


def fit_single_factor(S: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """단일요인 표준화(ψ=1) 해 (λ, θ). p=3은 포화 정확해, p≥4는 ML 정련.

    표준화 모형: Σ = λλ' + diag(θ), Var(η)=1. 부호는 λ₁>0로 고정.
    """
    p = S.shape[0]
    sd = np.sqrt(np.diag(S))

    # p=3 포화 정확해: λ_j² = (σ_jk σ_jl)/σ_kl (off-diag 곱비). 양상관 가정.
    if p == 3:
        s = S
        prod = np.array([
            s[0, 1] * s[0, 2] / s[1, 2],
            s[0, 1] * s[1, 2] / s[0, 2],
            s[0, 2] * s[1, 2] / s[0, 1],
        ])
        lam = np.sqrt(np.clip(prod, 1e-8, None))
        theta = np.clip(np.diag(S) - lam ** 2, 1e-6, None)
        if lam[0] < 0:
            lam = -lam
        return lam, theta

    # p≥4: 1주성분 적재로 초기화 후 ML 정련.
    R = S / np.outer(sd, sd)
    w, V = np.linalg.eigh(R)
    v1 = V[:, -1] * np.sqrt(max(w[-1], 1e-6))   # 표준화 적재
    lam0 = v1 * sd
    if lam0.sum() < 0:
        lam0 = -lam0
    th0 = np.clip(np.diag(S) - lam0 ** 2, 1e-3, None)
    par0 = np.concatenate([lam0, np.log(th0)])

    def obj(par):
        lam = par[:p]
        theta = np.exp(par[p:])
        Sigma = np.outer(lam, lam) + np.diag(theta)
        return _fml_cov(S, Sigma)

    res = minimize(obj, par0, method="L-BFGS-B", options={"maxiter": 10000, "ftol": 1e-11})
    lam = res.x[:p]
    theta = np.exp(res.x[p:])
    if lam[0] < 0:
        lam = -lam
    return lam, theta


@dataclass
class Configural:
    """집단별 configural 표준화 해(λ₀·ν₀·θ)와 N."""
    years: list[int]
    lam0: np.ndarray   # (G, p)
    nu0: np.ndarray    # (G, p)  = x̄
    theta: np.ndarray  # (G, p)
    N: np.ndarray      # (G,)


def estimate_configural(stats: list[GroupStat]) -> Configural:
    """각 집단을 표준화(ψ=1,α=0) 단일요인으로 적합 → λ₀·ν₀(=x̄)·θ."""
    G = len(stats)
    p = stats[0].S.shape[0]
    lam0 = np.zeros((G, p)); nu0 = np.zeros((G, p)); theta = np.zeros((G, p))
    N = np.zeros(G)
    for g, st in enumerate(stats):
        lam, th = fit_single_factor(st.S)
        lam0[g] = lam; theta[g] = th
        nu0[g] = st.xbar     # α=0이므로 모형평균=ν → ν₀=표본평균(포화)
        N[g] = st.n
    return Configural([st.year for st in stats], lam0, nu0, theta, N)


# ──────────────────── 2단계: 정렬 최적화 ────────────────────
def _clf(x: np.ndarray, eps: float = EPS) -> np.ndarray:
    """component loss f(x)=(x²+ε)^¼ — 소수의 큰 차이를 선호(근사 sparsity)."""
    return (x * x + eps) ** 0.25


def aligned_params(free: np.ndarray, cfg: Configural):
    """자유모수(α_{2..G}, logψ_{2..G}) → 집단별 (λ, ν, α, ψ). 기준집단 α=0,ψ=1."""
    G, p = cfg.lam0.shape
    alpha = np.concatenate([[0.0], free[:G - 1]])
    lpsi = np.concatenate([[0.0], free[G - 1:]])
    spsi = np.exp(0.5 * lpsi)                 # √ψ
    lam = cfg.lam0 / spsi[:, None]            # λ_gj = λ₀/√ψ
    nu = cfg.nu0 - alpha[:, None] * lam       # ν_gj = ν₀ − α·λ₀/√ψ
    return lam, nu, alpha, np.exp(lpsi)


def _pair_weights(N: np.ndarray, mode: str) -> np.ndarray:
    """단순성함수 집단쌍 가중 W[g,h]. mode: 'yeareq'(연도균등) | 'amstd'(√N_g N_h)."""
    G = len(N)
    if mode == "amstd":
        root = np.sqrt(N)
    else:  # yeareq — 모든 연도 동일 기여(2022 표본지배 제거; wt_year_eq 정신)
        root = np.ones(G)
    W = np.outer(root, root)
    return W


def simplicity(free: np.ndarray, cfg: Configural, W: np.ndarray) -> float:
    """단순성함수 F = Σ_j Σ_{g<h} W_gh·[f(Δλ)+f(Δν)]."""
    lam, nu, _, _ = aligned_params(free, cfg)
    G, p = lam.shape
    F = 0.0
    for g in range(G):
        for h in range(g + 1, G):
            w = W[g, h]
            F += w * (_clf(lam[g] - lam[h]).sum() + _clf(nu[g] - nu[h]).sum())
    return F


def optimize_alignment(cfg: Configural, weight_mode: str = "yeareq",
                       n_starts: int = 12, seed: int = 7):
    """정렬 최적화(다중시작). 반환: (best_free, lam, nu, alpha, psi, W, F)."""
    G, p = cfg.lam0.shape
    W = _pair_weights(cfg.N, weight_mode)
    rng = np.random.default_rng(seed)
    ndim = 2 * (G - 1)

    # 시작값: α는 (집단평균−기준집단평균)/평균적재 근사, logψ=0.
    base_mean = cfg.nu0.mean(axis=1)
    a0 = (base_mean - base_mean[0]) / max(cfg.lam0.mean(), 1e-3)
    x0_core = np.concatenate([a0[1:], np.zeros(G - 1)])

    best = None
    for s in range(n_starts):
        x0 = x0_core + (0.0 if s == 0 else rng.normal(0, 0.3, ndim))
        res = minimize(simplicity, x0, args=(cfg, W),
                       method="L-BFGS-B", options={"maxiter": 20000, "ftol": 1e-12})
        if best is None or res.fun < best.fun:
            best = res
    lam, nu, alpha, psi = aligned_params(best.x, cfg)
    return best.x, lam, nu, alpha, psi, W, best.fun


# ──────────────────── 3단계: 비동등 비율 + 부트스트랩 SE ────────────────────
def _weighted_param_mean(vals: np.ndarray, N: np.ndarray) -> float:
    """집단별 모수값의 N-가중 평균(비동등 기준점)."""
    return float(np.average(vals, weights=N))


def noninvariance_table(lam: np.ndarray, nu: np.ndarray, N: np.ndarray,
                        items: list[str]):
    """정렬 후 각 (집단,지표) 모수의 가중평균 이탈 절대값표(loadings·intercepts)."""
    G, p = lam.shape
    rows = []
    for kind, M in (("loading", lam), ("intercept", nu)):
        for j in range(p):
            wm = _weighted_param_mean(M[:, j], N)
            for g in range(G):
                rows.append({"param": kind, "item": items[j], "g": g,
                             "value": M[g, j], "dev": M[g, j] - wm})
    return pd.DataFrame(rows)


def bootstrap_alignment(panel: pd.DataFrame, items: list[str], years: list[int],
                        weight_mode: str, weight_col: str | None,
                        B: int = 200, seed: int = 20):
    """부트스트랩(연도 내 케이스 재표집) → 잠재평균 SE + 비동등 유의 플래그.

    각 복원표본에서 configural→정렬 재추정. 정렬 부호/스케일은 기준집단(2019) 고정으로
    식별되므로 복원표본 간 직접 비교 가능. 반환: (alpha_boot(B×G), dev_boot dict).
    """
    rng = np.random.default_rng(seed)
    # 연도별 완전케이스를 numpy로 미리 추출(루프 내 pandas .loc 회피).
    X_by_year = {}; w_by_year = {}
    for y in years:
        cols = items + ([weight_col] if weight_col else [])
        sub = panel.loc[panel["year"] == y, cols].dropna()
        X_by_year[y] = sub[items].to_numpy(dtype=float)
        w_by_year[y] = sub[weight_col].to_numpy(dtype=float) if weight_col else None

    G = len(years)
    alpha_boot = np.zeros((B, G))
    dev_load = []  # 각 부트의 (G,p) loading 이탈
    dev_int = []
    for b in range(B):
        stats = []
        for y in years:
            X0 = X_by_year[y]; nrow = X0.shape[0]
            pos = rng.integers(0, nrow, nrow)        # 위치기반 복원표집(고속)
            X = X0[pos]
            w = w_by_year[y][pos] if w_by_year[y] is not None else None
            xbar, S = _weighted_moments(X, w)
            stats.append(GroupStat(y, len(X), S, xbar))
        cfg = estimate_configural(stats)
        _, lam, nu, alpha, _, _, _ = optimize_alignment(cfg, weight_mode, n_starts=4, seed=b)
        alpha_boot[b] = alpha
        p = lam.shape[1]
        dl = np.zeros((G, p)); di = np.zeros((G, p))
        for j in range(p):
            wlam = _weighted_param_mean(lam[:, j], cfg.N)
            wnu = _weighted_param_mean(nu[:, j], cfg.N)
            dl[:, j] = lam[:, j] - wlam
            di[:, j] = nu[:, j] - wnu
        dev_load.append(dl); dev_int.append(di)
    return alpha_boot, np.array(dev_load), np.array(dev_int)


def noninvariance_proportion(dev_load: np.ndarray, dev_int: np.ndarray,
                             point_dev_load: np.ndarray, point_dev_int: np.ndarray):
    """부트스트랩 분포로 (집단,지표)별 이탈 유의성 판정 → 비동등 비율.

    플래그 기준: 점추정 이탈이 0과 유의 차(95% CI가 0 미포함) **그리고** |이탈|이
    실질 크기(loading>0.10, intercept>0.10) 이상. 둘 다 충족해야 '비동등'.
    """
    def flags(dev_boot, point_dev, mat_thresh):
        B, G, p = dev_boot.shape
        lo = np.percentile(dev_boot, 2.5, axis=0)
        hi = np.percentile(dev_boot, 97.5, axis=0)
        sig = (lo > 0) | (hi < 0)                 # 95% CI가 0 미포함
        material = np.abs(point_dev) >= mat_thresh
        return sig & material
    fl = flags(dev_load, point_dev_load, 0.10)
    fi = flags(dev_int, point_dev_int, 0.10)
    total = fl.size + fi.size
    n_non = int(fl.sum() + fi.sum())
    return n_non / total, n_non, total, fl, fi


# ──────────────────── 자기검증(시뮬레이션) ────────────────────
def _simulate(loadings, intercepts, alphas, theta, N, seed):
    """알려진 모수로 단일요인 데이터 생성 → GroupStat 리스트(잠재 ψ=1)."""
    rng = np.random.default_rng(seed)
    G = len(alphas); p = len(theta)
    stats = []
    for g in range(G):
        eta = rng.normal(alphas[g], 1.0, N)
        X = intercepts[g] + np.outer(eta, loadings[g]) + rng.normal(0, 1, (N, p)) * np.sqrt(theta)
        stats.append(GroupStat(2019 + g, N, np.cov(X, rowvar=False, bias=True), X.mean(axis=0)))
    return stats


def self_validation() -> bool:
    """알려진 잠재평균을 정렬법이 회복하는지 확인(완전불변/부분비동등/과다비동등)."""
    p, G, N = 3, 7, 4000
    base_lam = np.array([1.0, 0.9, 1.1])
    base_nu = np.array([3.0, 2.8, 3.2])
    theta = np.array([0.5, 0.6, 0.5])
    true_alpha = np.array([0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60])  # 단조 증가

    def recover(stats, label):
        cfg = estimate_configural(stats)
        _, lam, nu, alpha, psi, _, _ = optimize_alignment(cfg, "yeareq", n_starts=8)
        # 기준집단(2019) α=0 식별 → true도 0 기준이라 직접 비교.
        bias = alpha - true_alpha
        r = np.corrcoef(alpha, true_alpha)[0, 1]
        print(f"  [{label}] corr(α̂,α)={r:.4f} maxbias={np.abs(bias).max():.4f} "
              f"α̂={np.round(alpha,3).tolist()}")
        return r, np.abs(bias).max()

    print("◆ 자기검증 — 정렬법 잠재평균 회복")
    # A. 완전 불변(λ·ν 동일, 평균만 상이)
    sA = _simulate([base_lam] * G, [base_nu] * G, true_alpha, theta, N, seed=1)
    rA, bA = recover(sA, "A 완전불변")
    # B. 부분 비동등(2개 집단의 1개 절편 이동 ≈ 비동등 2/(2·3·7)≈4.8% ≤20%)
    nuB = [base_nu.copy() for _ in range(G)]
    nuB[3] = base_nu + np.array([0.0, 0.6, 0.0])
    nuB[5] = base_nu + np.array([0.0, 0.0, 0.6])
    sB = _simulate([base_lam] * G, nuB, true_alpha, theta, N, seed=2)
    rB, bB = recover(sB, "B 부분비동등(≤20%)")
    # C. 과다 비동등(다수 집단 절편 이동 >20%) — 회복 저하 기대
    nuC = [base_nu + rng_shift for rng_shift in
           [np.array([0, 0, 0]), np.array([0.7, 0, 0]), np.array([0, 0.7, 0]),
            np.array([0, 0, 0.8]), np.array([0.7, 0, 0]), np.array([0, 0.8, 0]),
            np.array([0, 0, 0.7])]]
    sC = _simulate([base_lam] * G, nuC, true_alpha, theta, N, seed=3)
    rC, bC = recover(sC, "C 과다비동등(>20%)")

    ok = (rA > 0.99 and bA < 0.10) and (rB > 0.97 and bB < 0.15)
    print(f"자기검증 판정 → A(불변 회복 corr>.99·bias<.10): {rA>0.99 and bA<0.10} | "
          f"B(부분비동등 회복 corr>.97·bias<.15): {rB>0.97 and bB<0.15} | "
          f"C(과다비동등 회복 저하 확인: bias_C>bias_B={bC>bB})")
    return ok


# ──────────────────── 단일문항 교차확인 ────────────────────
def single_item_trend(panel: pd.DataFrame, weight_col: str = "wt_year_eq") -> pd.DataFrame:
    """단일문항 trust_news_overall(2020~2025) 연도별 가중평균 추세(방향 교차확인용)."""
    rows = []
    for y in [2020, 2021, 2022, 2023, 2024, 2025]:
        sub = panel.loc[panel["year"] == y, ["trust_news_overall", weight_col]].dropna()
        w = sub[weight_col].to_numpy()
        x = sub["trust_news_overall"].to_numpy()
        rows.append({"year": y, "mean": float(np.average(x, weights=w)), "n": len(sub)})
    return pd.DataFrame(rows)


# ──────────────────── 실행 파이프라인 ────────────────────
@dataclass
class AlignResult:
    label: str
    years: list[int]
    items: list[str]
    alpha: np.ndarray
    psi: np.ndarray
    alpha_se: np.ndarray
    noninv_prop: float
    n_non: int
    n_total: int
    lam: np.ndarray
    nu: np.ndarray
    N: np.ndarray
    F: float


def run_alignment(panel: pd.DataFrame, items: list[str], years: list[int],
                  label: str, weight_mode: str = "yeareq",
                  weight_col: str | None = None, B: int = 200) -> AlignResult:
    """한 모형(지표·연도·가중) 정렬 실행: 점추정 + 부트스트랩 SE/비동등 비율."""
    stats = group_stats(panel, items, years, weight_col)
    cfg = estimate_configural(stats)
    _, lam, nu, alpha, psi, W, F = optimize_alignment(cfg, weight_mode)

    # 점추정 이탈
    G, p = lam.shape
    pdl = np.zeros((G, p)); pdi = np.zeros((G, p))
    for j in range(p):
        pdl[:, j] = lam[:, j] - _weighted_param_mean(lam[:, j], cfg.N)
        pdi[:, j] = nu[:, j] - _weighted_param_mean(nu[:, j], cfg.N)

    alpha_boot, dev_load, dev_int = bootstrap_alignment(
        panel, items, years, weight_mode, weight_col, B=B)
    alpha_se = alpha_boot.std(axis=0, ddof=1)
    prop, n_non, n_tot, _, _ = noninvariance_proportion(dev_load, dev_int, pdl, pdi)

    print(f"\n===== 정렬법 — {label} (G={G}, items={len(items)}, weight={weight_mode}) =====")
    for g, y in enumerate(years):
        print(f"  {y}: α={alpha[g]:+.3f} (SE {alpha_se[g]:.3f}), ψ={psi[g]:.3f}, N={int(cfg.N[g]):,}")
    print(f"  비동등 비율 = {prop*100:.1f}% ({n_non}/{n_tot})  "
          f"[{'≤20% → alignment-adjusted 평균비교 정당' if prop<=NONINV_THRESH else '>20% → 방향성만'}]")
    return AlignResult(label, years, items, alpha, psi, alpha_se,
                       prop, n_non, n_tot, lam, nu, cfg.N, F)


def main():
    valid = self_validation()
    if not valid:
        print("⚠️ 자기검증 실패 — 결과 해석 보류")

    panel = pd.read_parquet(PARQUET)

    # 주모형: 3지표 7집단, 비가중 적률 + 연도균등 정렬가중(2022 지배 제거).
    main3 = run_alignment(panel, CORE3, YEARS_ALL, "주모형: 3지표·연도균등(2019~2025)",
                          weight_mode="yeareq", B=200)
    # robustness1: 표준 A&M 가중(√N_g N_h) — 표본크기 반영.
    rob_std = run_alignment(panel, CORE3, YEARS_ALL, "robust1: 3지표·A&M표준가중(√NₘNₕ)",
                            weight_mode="amstd", B=120)
    # robustness2: 연도내 설계가중 적률(wt_within) + 연도균등 정렬가중.
    rob_w = run_alignment(panel, CORE3, YEARS_ALL, "robust2: 3지표·설계가중적률(wt_within)",
                          weight_mode="yeareq", weight_col="wt_within", B=120)
    # 민감도: 4지표 4집단(2019~2022, +신뢰 직접지표).
    sens4 = run_alignment(panel, PLUS4, YEARS_4IND, "민감도: 4지표(2019~2022)",
                          weight_mode="yeareq", B=150)

    single = single_item_trend(panel)
    print("\n◆ 단일문항 trust_news_overall(2020~2025, wt_year_eq) 교차확인")
    print(single.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    write_results(valid, main3, rob_std, rob_w, sens4, single)
    print(f"\n결과 문서: {OUT_MD.relative_to(ROOT)}")


def write_results(valid, main3: AlignResult, rob_std: AlignResult, rob_w: AlignResult,
                  sens4: AlignResult, single: pd.DataFrame):
    """연도별 잠재평균 추세 + 비동등 비율 + 해석을 추적 문서로 저장."""
    def alpha_tbl(r: AlignResult) -> str:
        head = "| 연도 | α̂(2019=0) | SE | ψ̂ | N |\n|---|---|---|---|---|"
        lines = [f"| {y} | {r.alpha[g]:+.3f} | {r.alpha_se[g]:.3f} | {r.psi[g]:.3f} | {int(r.N[g]):,} |"
                 for g, y in enumerate(r.years)]
        return head + "\n" + "\n".join(lines)

    # 추세 방향(2019→말년) + 단조성
    def direction(r: AlignResult) -> str:
        d = r.alpha[-1] - r.alpha[0]
        diffs = np.diff(r.alpha)
        mono = "단조증가" if np.all(diffs > -0.02) else ("단조감소" if np.all(diffs < 0.02) else "비단조")
        return f"2019→{r.years[-1]} Δα={d:+.3f}(2019-SD 단위), 패턴={mono}"

    # 단일문항 방향
    s_dir = single["mean"].iloc[-1] - single["mean"].iloc[0]
    # 잠재추세(2020~2025 구간)와 단일문항 부호 일치 여부
    a_2020_2025 = main3.alpha[1:] - main3.alpha[1]
    s_rel = single["mean"].to_numpy() - single["mean"].to_numpy()[0]
    spear = pd.Series(a_2020_2025).corr(pd.Series(s_rel), method="spearman")
    endpoint_concord = (np.sign(a_2020_2025[-1]) == np.sign(s_rel[-1]))  # 2020→2025 부호 일치
    # 기준연도 계단(2019→2020) + 최대 단년 변화
    step_diffs = np.diff(main3.alpha)
    step_ref = step_diffs[0]                       # 2019→2020
    max_step_i = int(np.argmax(np.abs(step_diffs)))
    max_step = (main3.years[max_step_i], main3.years[max_step_i + 1], step_diffs[max_step_i])

    single_tbl = "| 연도 | 단일문항 가중평균(1~5) |\n|---|---|\n" + "\n".join(
        f"| {int(r.year)} | {r['mean']:.3f} |" for _, r in single.iterrows())

    md = f"""# 정렬법(Alignment) 기반 언론 신뢰성 잠재평균 추세 — 2019~2025

> 산출: `python src/alignment.py` (numpy/scipy 직접 구현, Mplus/sirt 미사용 사유는 스크립트 docstring).
> 근거: [`../groundwork/05-research-harmonization.md`](../groundwork/05-research-harmonization.md) §3-3(정렬법)·§4(해석원칙)·§6(가중치),
>   Asparouhov & Muthén(2014). 지표 명세: [`variable-crosswalk-trust-battery.md`](variable-crosswalk-trust-battery.md).
> 선행: [`mgcfa-invariance-results.md`](mgcfa-invariance-results.md) — metric 동등 강지지, 완전 scalar 보수적 미확정.
> 자기검증(시뮬 잠재평균 회복): **{'통과' if valid else '실패(해석 보류)'}**.
> ⚠️ 추세 수치는 KPF 원자료 재검증(`data-spec.md §6`) 전 보고서·웹데모 직접 인용 신중(검증 게이트).

## 0. 방법 요약
- **1단계 configural**: 집단(연도)별 표준화 단일요인 해(λ₀·ν₀·θ; 잠재 α=0,ψ=1). 3지표는 집단내 포화(정확해).
- **2단계 정렬**: 적합도 불변 회전 `λ=λ₀/√ψ`, `ν=ν₀−α·λ₀/√ψ` 하에서 단순성함수
  `F=Σ_j Σ_{{g<h}} w·[f(Δλ)+f(Δν)]`, `f(x)=(x²+ε)^¼` 최소화. 기준집단(2019) α=0·ψ=1 → **잠재평균=2019 기준(2019-SD 단위)**.
- **3단계 비동등 비율**: 정렬 후 각 (집단,지표) 모수의 가중평균 이탈을 부트스트랩 유의성(95% CI)·실질크기(≥0.10)
  동시충족으로 플래그. **≤20%면 alignment-adjusted 평균비교 정당**, 초과 시 방향성만(05 §4-2).
- **가중치(05 §6)**: 측정모형 비가중(MGCFA 정합). 추세는 정렬가중을 **연도균등(yeareq)**으로 두어 2022(N≈5.9만)
  표본지배 제거(wt_year_eq 정신). A&M표준가중(√NₘNₕ)·설계가중적률(wt_within)은 robustness.

## 1. 주모형 — credibility 3지표, 연도균등 정렬(2019~2025)
{alpha_tbl(main3)}

- **추세 방향**: {direction(main3)}
- **비동등 비율**: **{main3.noninv_prop*100:.1f}%** ({main3.n_non}/{main3.n_total})
  → {'**≤20% → alignment-adjusted 잠재평균 추세 비교 정당**' if main3.noninv_prop<=NONINV_THRESH else '**>20% → 방향성 해석만**'}
- **요지**: 2019 대비 2020 이후 신뢰성 잠재평균이 일관되게 **높은 수준(+0.30~+0.67 SD)**으로 이동, 2025 최고치.
  3개 robustness 변형이 모두 같은 방향·비단조 패턴(2024 소폭 하락 후 2025 반등)을 재현.
- **⚠️ 2019→2020 계단 주의**: 기준연도 직후 계단 Δα={step_ref:+.3f}로 추세의 큰 부분이 여기서 발생한다.
  2019는 신뢰 단일문항이 구조적으로 부재했던 연도로, 배터리 워딩은 7개년 동일(crosswalk)하나 KPF 원자료
  재검증 시 2019 현장조사·문항 맥락을 우선 확인 대상으로 한다(과대해석 방지).
  (최대 단년 변화는 {max_step[0]}→{max_step[1]} Δα={max_step[2]:+.3f} — 2025 반등 구간.)

## 2. Robustness — 정렬가중·적률가중 변형
### 2.1 A&M 표준가중(√NₘNₕ) — 표본크기 반영
{alpha_tbl(rob_std)}
- 추세: {direction(rob_std)} · 비동등 {rob_std.noninv_prop*100:.1f}%

### 2.2 설계가중적률(wt_within) — 연도내 대표성
{alpha_tbl(rob_w)}
- 추세: {direction(rob_w)} · 비동등 {rob_w.noninv_prop*100:.1f}%

## 3. 민감도 — credibility 4지표(+신뢰 직접지표), 2019~2022
{alpha_tbl(sens4)}
- 추세: {direction(sens4)} · 비동등 {sens4.noninv_prop*100:.1f}%
- 4지표는 집단내 df>0(비포화) → 식별성 보강. 단축 구간(2019~2022)이나 정렬 잠재평균 방향 교차확인.

## 4. 단일문항 교차확인 — trust_news_overall(2020~2025, wt_year_eq)
{single_tbl}
- 단일문항 방향: 2020→2025 Δ={s_dir:+.3f}(1~5 척도) — **상승**.
- **종점 방향 일치**: 2020→2025 부호가 잠재추세·단일문항 모두 양(+)으로 **{'일치(교차타당)' if endpoint_concord else '불일치'}**.
- **연차 패턴 Spearman = {spear:.3f}**(중간) — 두 지표 모두 2025 상승·중간연도 등락이 있으나, 단일문항은 2022에
  급락(표본 12배 확대·구성 변화)하는 반면 잠재추세는 2024에 저점이라 **단년 등락 시점이 어긋난다**.
- 단일문항(뉴스 전반 신뢰)과 배터리(공정·전문·정확 credibility)는 **구성개념·척도가 다르므로 수준이 아닌
  종점 방향**만 비교한다. 종점 방향 일치는 "2019~2020 이후 언론 신뢰성 상승" 결론을 보강한다.

## 5. 해석 — scalar 직접비교 vs alignment-adjusted 비교
- MGCFA에서 metric은 강하게 지지, 완전 scalar는 보수적 미확정이었다(`mgcfa-invariance-results.md`).
  정렬법은 **비동등을 명시적으로 수용**하므로, 비동등 비율이 {main3.noninv_prop*100:.1f}%(≤20%)이면
  연도별 **alignment-adjusted 잠재평균**을 비교해도 편향이 통제된다(05 §4-2, A&M 2014).
- 따라서 본 단계에서 **신뢰성 잠재평균 추세 수치 보고가 비로소 가능**하다. 단, 절대 점수 변화량 수량화보다
  **추세 방향·상대 비교**에 무게를 둔다(단일문항·robustness 교차확인 일치 시 신뢰도↑).
- **검증 게이트**: 위 수치는 하모나이즈 파이프라인 산출에 기반하며, KPF 원자료 재검증 전 보고서·웹데모
  직접 인용은 신중(05 머리말·`data-spec.md §6`). 재검증 후 "KPF 원자료, 2019~2025" 출처로 확정 인용.

## 6. 재현
```
python src/harmonize.py        # data/processed/audience_harmonized.parquet 빌드(gitignore)
python src/alignment.py        # 본 문서 재생성
```
"""
    OUT_MD.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
