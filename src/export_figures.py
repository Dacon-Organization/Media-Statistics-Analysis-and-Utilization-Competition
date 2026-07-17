"""논문형 PDF용 figure 일괄 export — F3~F6 (P6-B-1).

목적: `docs/report/p6-pdf-structure.md` §2 선정표의 노트북 인라인 figure 4종을
  `assets/`에 dpi=200 PNG로 재생성한다. 노트북에 savefig 셀을 추가하지 않고
  (§2 export 규칙 — 노트북 출력·git diff 오염 방지) 기존 src 모듈을 import해
  동일 계산을 다시 수행한 뒤, 노트북과 동일한 플로팅 코드로 저장한다.

대상 (원천 노트북 → 산출 파일):
  F3  `23-alignment-trend.ipynb` §4   → assets/fig3_alignment_trend.png
      정렬법 잠재평균 추세(α̂ + 95% CI, 2019→2020 음영). 주모형(연도균등, B=200).
  F4  `24-trend-apc.ipynb` §6         → assets/fig4_apc_profile.png
      APC 3효과 프로파일(기간 2종 vs 정렬추세 · 연령 · 코호트).
  F5  `03-health-index.ipynb` §3·§4   → assets/fig5_nchi_trend.png
      NCHI 추세(fixed8 주지표·incl 보조) + 페르소나 가중 구성비(2패널).
  F6  `04-personas-kmeans.ipynb` §5   → assets/fig6_personas.png
      페르소나 × 매체 이용률 히트맵(가중%, 고정풀 8매체).
  F10 `26-mk-sen-deep-dive.ipynb` §2·§4 → assets/fig10_mk_inference.png  (P6-B-7 추가)
      MK 추론 이층 구조: 순열 정확분포(관측 S·기각역) + 부트스트랩 τ 분포(P(S>0)).
  F11 `28-cohort-gradient.ipynb` §2·§5  → assets/fig11_cohort_age_concordance.png  (P6-B-7 추가)
      종단 IE 코호트 구배(음) ↔ 횡단 2025 연령 구배(양) — 부호 정합 2패널.

표기 규율(p6-pdf-structure §3.5·§4): F3·F4의 SD 단위 수치는 모형 의존 —
  축 라벨에 "2019=0, 2019-SD 단위"를 명기하고 본문 헤드라인 인용은 금지.
  F5·F6의 NCHI·다양성 절대값은 formative 설계 의존 — "방향성만" 제목 유지.

실행: python src/export_figures.py [fig3 fig4 fig5 fig6]
  (인자 없으면 4종 전부. 입력: data/processed/audience_harmonized.parquet)
의존: numpy, pandas, matplotlib, statsmodels(F4) — 모두 기설치. 신규 의존 없음.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 스크립트 전용 headless 백엔드(노트북 인라인 정책과 무관)
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import alignment as al  # noqa: E402
import harmonize as hz  # noqa: E402
import health_index_panel as hp  # noqa: E402
import news_health_features as nf  # noqa: E402
import trend_apc as T  # noqa: E402

ASSETS = ROOT / "assets"
DPI = 200  # p6-pdf-structure §2 export 규칙


def _setup_korean_font() -> None:
    """한글 폰트 설정(노트북 공통 _kfont와 동일 탐색 순서)."""
    for nm in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "Gulim"]:
        try:
            font_manager.findfont(nm, fallback_to_default=False)
            plt.rcParams["font.family"] = nm
            break
        except Exception:
            continue
    plt.rcParams["axes.unicode_minus"] = False


def _save(fig, filename: str) -> Path:
    """assets/에 dpi=200·tight로 저장(§2 규칙) 후 경로 반환."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = ASSETS / filename
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  → 저장: {out.relative_to(ROOT)} ({out.stat().st_size/1024:.0f} KB)")
    return out


def load_panel() -> pd.DataFrame:
    """하모나이즈 패널 로드 + 행수 게이트(노트북 공통 assert)."""
    panel = pd.read_parquet(al.PARQUET)
    assert len(panel) == 90996, f"행수 불일치: {len(panel):,}"
    return panel


# ─────────────────── F3. 정렬법 잠재평균 추세 (23 §4) ───────────────────
def export_fig3(panel: pd.DataFrame) -> Path:
    """주모형(3지표·연도균등, B=200) 정렬 잠재평균 추세 — 23 §4 인라인 fig 재현."""
    print("[F3] 정렬법 주모형 실행(부트스트랩 B=200 — 수 분 소요)…")
    main3 = al.run_alignment(panel, al.CORE3, al.YEARS_ALL,
                             "주모형: 3지표·연도균등(2019~2025)",
                             weight_mode="yeareq", B=200)

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    yrs = np.array(main3.years)
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.axvspan(2019, 2020, color="0.92", zorder=0)  # 기준연도 직후 계단(재검증 우선)
    ax.errorbar(yrs, main3.alpha, yerr=1.96 * main3.alpha_se, fmt="o-", lw=1.8,
                capsize=4, color="#1f77b4", label="주모형(연도균등)")
    for x, y in zip(yrs, main3.alpha):
        ax.annotate(f"{y:+.3f}", (x, y), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=9)
    ax.set_xlabel("연도")
    # α̂는 Malgun Gothic에 결합 악센트 글리프가 없어 mathtext로 표기
    ax.set_ylabel(r"잠재평균 $\hat{\alpha}$ (2019=0, 2019-SD 단위)")
    ax.set_title(f"언론 신뢰성(credibility) alignment-adjusted 잠재평균 추세 — "
                 f"비동등 {main3.noninv_prop*100:.1f}% (≤20% → 비교 정당)")
    ax.legend(loc="lower right")
    ax.margins(x=0.04)
    fig.tight_layout()
    return _save(fig, "fig3_alignment_trend.png")


# ─────────────────── F4. APC 3효과 프로파일 (24 §6) ───────────────────
def export_fig4(panel: pd.DataFrame) -> Path:
    """기간효과 2종(HAPC·IE) vs 정렬추세 + 연령·코호트 편차 — 24 §6 인라인 fig 재현."""
    print("[F4] 정렬 점추정 + HAPC-GLMM + IE 실행…")
    years, alpha = T.latent_trend_points(panel)
    frame = T.make_apc_frame(panel)  # 2022 cap=6,000 (HAPC용)
    hapc = T.hapc_mixed(frame)
    ie = T.intrinsic_estimator(frame)
    pe_h = np.array([hapc["period_re"].get(y, np.nan) for y in T.YEARS_ALL])
    pe_i = np.array([ie["period"].get(y, np.nan) for y in T.YEARS_ALL])
    r_hapc_align = np.corrcoef(pe_h, alpha)[0, 1]
    r_ie_align = np.corrcoef(pe_i, alpha)[0, 1]
    print(f"  기간효과 상관: HAPC-정렬 = {r_hapc_align:+.3f} · IE-정렬 = {r_ie_align:+.3f}")

    def z(v):
        v = np.asarray(v, float)
        return (v - v.mean()) / v.std(ddof=0)

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
    # (1) 기간 — 표준화 형상 비교
    # α̂는 Malgun Gothic에 결합 악센트 글리프가 없어 mathtext로 표기
    axes[0].plot(T.YEARS_ALL, z(alpha), "o-", color="#1f77b4",
                 label=r"정렬 $\hat{\alpha}$(23)")
    axes[0].plot(T.YEARS_ALL, z(pe_h), "s--", color="#ff7f0e",
                 label=f"HAPC (r={r_hapc_align:+.2f})")
    axes[0].plot(T.YEARS_ALL, z(pe_i), "^--", color="#2ca02c",
                 label=f"IE (r={r_ie_align:+.2f})")
    axes[0].set_title("기간효과 — 정렬추세와 형상 일치")
    axes[0].set_xlabel("연도")
    axes[0].set_ylabel("표준화 값")
    axes[0].legend(fontsize=8.5)

    # (2) 연령
    ages = sorted(ie["age"])
    avals = [ie["age"][a] for a in ages]
    axes[1].axhline(0, color="gray", lw=0.8, ls="--")
    axes[1].plot(ages, avals, "o-", color="#9467bd")
    axes[1].set_ylim(-0.45, 0.45)  # 코호트와 동일 스케일 → 납작함 대비
    axes[1].set_title(f"연령효과(IE) — 범위 {max(avals)-min(avals):.3f}, 미미")
    axes[1].set_xlabel("연령군(5년)")
    axes[1].set_ylabel("편차(cred_mean)")

    # (3) 코호트 (소표본 구분)
    coh_n = frame["cohort5"].value_counts().to_dict()
    cohs = sorted(ie["cohort"])
    big = [c for c in cohs if coh_n.get(c, 0) >= 200]
    axes[2].axhline(0, color="gray", lw=0.8, ls="--")
    axes[2].plot(big, [ie["cohort"][c] for c in big], "o-", color="#d62728",
                 label="N>=200")
    small = [c for c in cohs if c not in big]
    axes[2].plot(small, [ie["cohort"][c] for c in small], "x", color="0.6", ms=8,
                 label="N<200 (해석 제외)")
    axes[2].set_ylim(-0.45, 0.45)
    axes[2].set_title("코호트효과(IE) — 젊을수록 낮은 세대 구배")
    axes[2].set_xlabel("출생코호트(5년)")
    axes[2].legend(fontsize=8.5)
    fig.tight_layout()
    return _save(fig, "fig4_apc_profile.png")


# ─────────────── F5. NCHI 추세 + 페르소나 구성비 (03 §3·§4) ───────────────
def export_fig5(panel: pd.DataFrame) -> Path:
    """NCHI 추세(fixed8·incl)와 페르소나 가중 구성비 — 03 §3·§4 인라인 fig 2패널 합본.

    p6-pdf-structure §2 F5 정의("NCHI 추세 … 페르소나 구성비")에 따라 두 인라인
    figure를 좌우 패널로 합쳐 1개 파일로 export한다.
    """
    print("[F5] NCHI 연도별 지수 + 페르소나 구성비 산출…")
    nchi_fixed = hp.nchi_by_year(panel, diversity_version="fixed8")
    nchi_incl = hp.nchi_by_year(panel, diversity_version="incl")

    # 응답자 단위 점수 → pooled 임계값 고정 → 연도별 가중 구성비(03 §4와 동일)
    T_resp = hp._trust_score_respondent(panel)
    D_resp = nf._scale_1_100(pd.to_numeric(panel["richness_fixed8"], errors="coerce"))
    persona = nf.persona_quadrant(T_resp, D_resp)
    pdf = pd.DataFrame({"year": panel["year"].to_numpy(),
                        "persona": persona.to_numpy(),
                        "w": panel["wt_year_eq"].to_numpy()}).dropna(subset=["persona"])
    order = ["건강한 소비자", "비판적 탐색형", "신뢰편향형", "이중취약형"]
    share = pdf.groupby(["year", "persona"])["w"].sum().unstack(fill_value=0)
    share = (share.div(share.sum(axis=1), axis=0) * 100)[order]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 4.4))
    # (좌) NCHI 추세 — fixed8 vs incl
    ax1.plot(nchi_fixed.index, nchi_fixed["nchi"], marker="o", lw=2.4,
             color="#8250df", label="NCHI (다양성 fixed8, 주지표)")
    ax1.plot(nchi_incl.index, nchi_incl["nchi"], marker="s", lw=2.0, ls="--",
             color="#cf222e", label="NCHI (다양성 incl, 보조)")
    ax1.set_title("뉴스 소비 건강지수 NCHI 추세 (2019~2025) - 방향성 위주 해석",
                  fontsize=12, weight="bold")
    ax1.set_xlabel("연도")
    ax1.set_ylabel("NCHI = sqrt(신뢰 x 다양성)")
    ax1.set_ylim(28, 45)
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=9)

    # (우) 페르소나 구성비 추세 — 누적 영역
    colors = {"건강한 소비자": "#2da44e", "비판적 탐색형": "#0969da",
              "신뢰편향형": "#bf8700", "이중취약형": "#cf222e"}
    ax2.stackplot(share.index, [share[c] for c in order],
                  labels=order, colors=[colors[c] for c in order], alpha=0.85)
    ax2.set_title("페르소나 구성비 추세 (2019~2025) - 방향성만 해석",
                  fontsize=12, weight="bold")
    ax2.set_xlabel("연도")
    ax2.set_ylabel("가중 구성비 (%)")
    ax2.set_ylim(0, 100)
    ax2.margins(x=0)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig5_nchi_trend.png")


# ─────────────── F6. 페르소나 × 매체 이용률 히트맵 (04 §5) ───────────────
def export_fig6(panel: pd.DataFrame) -> Path:
    """페르소나 4유형 × 고정풀 8매체 가중 이용률 히트맵 — 04 §5 인라인 fig 재현."""
    print("[F6] 페르소나 프로파일(가중 이용률) 산출…")
    W = panel["wt_year_eq"]
    T_resp = hp._trust_score_respondent(panel)
    D_resp = nf._scale_1_100(pd.to_numeric(panel["richness_fixed8"], errors="coerce"))
    persona_rule = nf.persona_quadrant(T_resp, D_resp)

    order = ["건강한 소비자", "비판적 탐색형", "신뢰편향형", "이중취약형"]
    USE8 = ["use_paper", "use_magazine", "use_tv", "use_radio",
            "use_internet", "use_messenger", "use_sns", "use_video"]
    ulbl = ["종이신문", "잡지", "TV", "라디오", "인터넷", "메신저", "SNS", "동영상"]
    mat = []
    for lab in order:
        mm = persona_rule == lab
        ww = W[mm]
        mat.append([nf.wmean(pd.to_numeric(panel[c], errors="coerce")[mm], ww) * 100
                    for c in USE8])
    mat = pd.DataFrame(mat, index=order, columns=ulbl)

    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    im = ax.imshow(mat.values, cmap="YlGnBu", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(ulbl)))
    ax.set_xticklabels(ulbl, fontsize=9)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=9)
    for i in range(len(order)):
        for j in range(len(ulbl)):
            v = mat.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8,
                    color="white" if v > 55 else "black")
    ax.set_title("페르소나 x 매체 이용률 (가중%) - 저다양 유형은 TV 편중",
                 fontsize=12, weight="bold")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="이용률 %")
    fig.tight_layout()
    return _save(fig, "fig6_personas.png")


# ─────────── F10. MK 추론 이층 구조 — 순열 정확분포 + 부트스트랩 (26 §2·§4) ───────────
def export_fig10(panel: pd.DataFrame) -> Path:
    """MK 이층 보고 시각화 — 26 §2(순열 정확분포)·§4(부트스트랩 τ) 인라인 fig 합본.

    본문 4.3절("유의하다" 대신 정직하게)의 수치 짝: 점추정 p=0.381(왼쪽)이 왜
    비유의인지(n=7 기각역 |S|>=15)와, 추정 불확실성 전파 후에도 방향이 일관됨
    (P(S>0)=1.00, 오른쪽)을 한 그림으로 보인다. 판정 로직은 trend_apc SSOT 사용.
    """
    from itertools import permutations

    print("[F10] MK 순열 정확분포(7!=5,040) + 부트스트랩 전파(mk_with_uncertainty, B=150)…")
    years, alpha = T.latent_trend_points(panel)
    mk = T.mann_kendall(alpha)
    S_obs = mk["S"]

    def s_stat(a):
        a = np.asarray(a, float)
        return int(sum(np.sign(a[i + 1:] - a[i]).sum() for i in range(len(a) - 1)))

    S_null = np.array([s_stat(perm) for perm in permutations(alpha)])
    vals, counts = np.unique(S_null, return_counts=True)
    pmf = counts / counts.sum()
    tail = {s: float((np.abs(S_null) >= s).mean()) for s in range(1, 22, 2)}
    crit = min(s for s, pv in tail.items() if pv <= 0.05)

    taus, s_pos, _ = T.mk_with_uncertainty(panel, B=150)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 4.0))
    colors = ["#f4a3a3" if abs(v) >= crit else "#a6c8e0" for v in vals]
    ax1.bar(vals, pmf, width=1.6, color=colors)
    ax1.axvline(S_obs, color="#c00", lw=2,
                label=f"관측 S = {S_obs:+d} (정확 p = {mk['p_exact']:.3f})")
    ax1.set_xlabel("S (연도쌍 부호 합, -21~+21)")
    ax1.set_ylabel("정확 확률 (7! = 5,040 순열)")
    ax1.set_title(f"점추정 — MK 귀무 정확분포, 양측 5% 기각역 |S| ≥ {crit}")
    ax1.legend(fontsize=9)

    ax2.hist(taus, bins=21, color="#4c78a8", edgecolor="white")
    ax2.axvline(0, color="#c00", lw=2, label="τ = 0 (무추세)")
    ax2.axvline(np.mean(taus), color="#1a7f37", lw=2, ls="--",
                label=f"평균 τ = {np.mean(taus):+.3f}")
    ax2.set_xlabel("부트스트랩 τ (추정 불확실성 전파, B=150)")
    ax2.set_ylabel("빈도")
    ax2.set_title(f"방향 일관성 — P(S>0) = {s_pos:.2f}")
    ax2.legend(fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig10_mk_inference.png")


# ─────── F11. 종단 코호트 구배 ↔ 횡단 연령 구배 부호 정합 (28 §2·§5) ───────
def export_fig11(panel: pd.DataFrame) -> Path:
    """상호 외적 타당도 시각화 — 28 §2(IE 코호트 구배)·§5(2025 횡단 연령 구배) 합본.

    본문 5.3절의 수치 짝: 종단 IE 코호트 편차는 젊을수록 낮고(음의 구배, §3.4의
    -0.891), 횡단 2025 연령대별 cred_mean은 고령일수록 높다(양의 구배) — 서로
    독립 산출된 두 트랙의 부호 정합. 소표본 셀(N<200)은 28과 동일 규칙으로 제외.
    """
    print("[F11] IE 재적합(코호트 편차) + 2025 횡단 연령대 가중 cred_mean…")
    MIN_N = 200  # 소표본 셀 제외 임계(28·trend_apc.write_results와 동일)
    frame = T.make_apc_frame(panel)
    ie = T.intrinsic_estimator(frame)
    coh_n = frame["cohort5"].value_counts().to_dict()
    big = sorted((k, v) for k, v in ie["cohort"].items() if coh_n.get(k, 0) >= MIN_N)
    small = sorted((k, v) for k, v in ie["cohort"].items() if coh_n.get(k, 0) < MIN_N)
    cb = np.array([k for k, _ in big], float)
    cv = np.array([v for _, v in big])
    coh_grad = float(np.corrcoef(cb, cv)[0, 1])

    p25 = panel[panel["year"] == 2025]
    cred25 = p25[["cred_fair", "cred_professional", "cred_accurate"]].apply(
        pd.to_numeric, errors="coerce").mean(axis=1)
    age_band = (pd.to_numeric(p25["age"], errors="coerce") // 10 * 10)
    w25 = p25["wt_year_eq"]
    xs, ys = [], []
    for band in sorted(age_band.dropna().unique()):
        mm = (age_band == band) & cred25.notna()
        if mm.sum() < 100:
            continue
        xs.append(int(band))
        ys.append(float(np.average(cred25[mm], weights=w25[mm])))
    cross_grad = float(np.corrcoef(xs, ys)[0, 1])
    print(f"  구배: 종단 코호트 {coh_grad:+.3f}(음) ↔ 횡단 연령 {cross_grad:+.3f}(양)")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 4.0))
    ax1.axhline(0, color="gray", lw=0.8, ls="--")
    ax1.plot(cb, cv, "o-", color="#d62728", label=f"N≥{MIN_N} 셀 ({len(big)}개)")
    if small:
        ax1.plot([k for k, _ in small], [v for _, v in small], "x", color="0.6",
                 ms=8, label=f"N<{MIN_N} 소표본 — 해석 제외")
    ax1.set_xlabel("출생코호트(5년 묶음 시작연도)")
    ax1.set_ylabel("IE 코호트 편차 (cred_mean 단위)")
    ax1.set_title(f"종단(7개년) — 젊은 코호트일수록 낮음 (구배 {coh_grad:+.3f})")
    ax1.legend(fontsize=9)

    ax2.plot(xs, ys, "s-", color="#0969da")
    for x, y in zip(xs, ys):
        ax2.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=8.5)
    ax2.set_xticks(xs)
    ax2.set_xticklabels([f"{x}대" for x in xs])
    ax2.set_xlabel("연령대 (2025 횡단면)")
    ax2.set_ylabel("cred_mean (가중, 5점 척도)")
    ax2.set_title(f"횡단(2025) — 고령일수록 높음 (구배 {cross_grad:+.3f})")
    ax2.margins(x=0.06)
    fig.tight_layout()
    return _save(fig, "fig11_cohort_age_concordance.png")


EXPORTERS = {
    "fig3": export_fig3,
    "fig4": export_fig4,
    "fig5": export_fig5,
    "fig6": export_fig6,
    "fig10": export_fig10,
    "fig11": export_fig11,
}


def main() -> None:
    targets = sys.argv[1:] or list(EXPORTERS)
    unknown = [t for t in targets if t not in EXPORTERS]
    if unknown:
        raise SystemExit(f"알 수 없는 대상 {unknown} — 사용 가능: {list(EXPORTERS)}")

    _setup_korean_font()
    panel = load_panel()
    print(f"패널 {len(panel):,}행 · 연도 {hz.YEARS} · 산출 대상 {targets}")

    outputs = [EXPORTERS[t](panel) for t in targets]
    print(f"\n완료 — {len(outputs)}개 figure export (dpi={DPI}, bbox_inches='tight')")


if __name__ == "__main__":
    main()
