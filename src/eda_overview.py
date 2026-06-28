"""P2 — 7개년(2019~2025) 통합 EDA 시각화 (신뢰성 배터리 포함 패널).

CRISP-DM P2(Data Understanding) 산출물. `src/harmonize.py`가 만든 하모나이즈 패널
(`data/processed/audience_harmonized.parquet`, 90,996행)을 입력으로 6개 패널을 그린다.

패널:
  ① 표본 구조      — 연도별 N(2022 지배) + 가중치 효과(wt vs wt_year_eq 연도합)
  ② 인구통계 분포  — 성·연령군·학력·소득의 연도 간 구성 변화(wt_year_eq, 2022 전후)
  ③ 신뢰 시계열    — trust 단일문항 + credibility 6지표 가중평균(wt_year_eq), 가용연도만
  ④ 지표 가용성    — 연도×변수 non-NA 비율 히트맵(결측 구조)
  ⑤ 상관/분포      — credibility 3지표 상관·연도별 분포 + 신뢰 vs 인구통계 교차
  ⑥ P4 연결        — 정렬 잠재추세·APC 기간효과 요약(P4 산출 인용, 본 스크립트 비재계산)

가중치 원칙(05 §6): 추세·평균은 wt_year_eq(2022 표본지배 제거), 분포는 wt_year_eq 가중.

⚠️ 검증 게이트(data-spec.md §6): 분석 수치는 KPF 원자료 재검증 전 보고서·웹데모 직접
   인용 신중. 본 패널은 '데이터 이해'용 탐색 시각화이며 인용 수치는 재검증 대상.

실행: python src/eda_overview.py   (선행: python src/harmonize.py)
의존: pandas, numpy, matplotlib, (seaborn 있으면 사용·없으면 matplotlib 폴백).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # 헤드리스 PNG 저장
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 콘솔 cp949 회피
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data/processed/audience_harmonized.parquet"
FIG = ROOT / "docs/design/figures"
FIG.mkdir(parents=True, exist_ok=True)

YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
WCOL = "wt_year_eq"  # 연도균등 가중치(2022 표본지배 제거)

CRED6 = ["cred_fair", "cred_professional", "cred_accurate",
         "cred_trustworthy", "press_free", "media_influence"]
CRED_CORE3 = ["cred_fair", "cred_professional", "cred_accurate"]
CRED_LABEL = {
    "cred_fair": "공정성", "cred_professional": "전문성", "cred_accurate": "정확성",
    "cred_trustworthy": "신뢰성(직접)", "press_free": "언론자유", "media_influence": "영향력",
}
TRUST_SINGLE = ["trust_news_overall", "trust_news_used", "trust_society"]
TRUST_LABEL = {"trust_news_overall": "뉴스 전반신뢰", "trust_news_used": "이용매체 신뢰",
               "trust_society": "사회 일반신뢰"}

# ── P4 산출 인용값(재계산 아님; 출처 docs/design/*.md) ──────────────────────
# alignment-trust-trend.md §1 (credibility 3지표, 연도균등 정렬, 2019=0 기준, 2019-SD 단위)
P4_ALIGN_ALPHA = {2019: 0.000, 2020: 0.354, 2021: 0.474, 2022: 0.453,
                  2023: 0.394, 2024: 0.298, 2025: 0.671}
# trend-apc-results.md §1·§2.1 기간효과(정렬추세와 삼각검증, HAPC↔정렬 r=+0.99, IE↔정렬 r=+0.96)
P4_PERIOD_HAPC = {2019: -0.206, 2020: 0.003, 2021: 0.067, 2022: 0.014,
                  2023: -0.001, 2024: -0.053, 2025: 0.176}
P4_PERIOD_IE = {2019: -0.194, 2020: 0.026, 2021: 0.079, 2022: -0.008,
                2023: -0.027, 2024: -0.047, 2025: 0.171}
P4_NONINVAR_PCT = 2.4   # 비동등 비율(≤20% → 정렬 잠재평균 비교 정당)
P4_MK_TAU = 0.333       # Mann-Kendall τ(정렬 잠재평균)
P4_MK_P = 0.3813        # MK 정확 p(증가 경향·비유의, n작음)


def setup_korean_font() -> str:
    """Windows 한글 폰트 설정. 없으면 기본 폰트(한글 깨짐 경고만)."""
    for name in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "Gulim"]:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return name
        except Exception:  # noqa: BLE001
            continue
    plt.rcParams["axes.unicode_minus"] = False
    return "(기본 폰트 — 한글 깨질 수 있음)"


# ── 가중 집계 헬퍼 ──────────────────────────────────────────────────────────
def wmean(df: pd.DataFrame, col: str, wcol: str = WCOL) -> float:
    sub = df[[col, wcol]].dropna()
    if len(sub) == 0 or sub[wcol].sum() == 0:
        return np.nan
    return float(np.average(sub[col], weights=sub[wcol]))


def wmean_by_year(df: pd.DataFrame, col: str, wcol: str = WCOL) -> pd.Series:
    """연도별 가중평균(유효 응답 0인 연도는 NaN → 시계열에서 자동 단절)."""
    return pd.Series({y: wmean(df[df["year"] == y], col, wcol) for y in YEARS})


def wcomp_by_year(df: pd.DataFrame, col: str, wcol: str = WCOL) -> pd.DataFrame:
    """연도별 범주 구성비(가중, 합=1). index=연도, columns=범주값."""
    rows = {}
    for y in YEARS:
        sub = df[df["year"] == y][[col, wcol]].dropna()
        g = sub.groupby(col)[wcol].sum()
        rows[y] = (g / g.sum()) if g.sum() > 0 else g
    return pd.DataFrame(rows).T.reindex(YEARS)


AGE_BINS = [0, 29, 39, 49, 59, 200]
AGE_LBL = ["19–29", "30–39", "40–49", "50–59", "60+"]
EDU_LBL = {1: "중졸이하", 2: "고졸", 3: "대재이상", 4: "대학원"}
SEX_LBL = {1: "남성", 2: "여성"}
INC7_LBL = {1: "~100만", 2: "100–200", 3: "200–300", 4: "300–400",
            5: "400–500", 6: "500–600", 7: "600만+"}

# ── 패널 ────────────────────────────────────────────────────────────────────
def panel1_sample_structure(df: pd.DataFrame) -> Path:
    """① 연도별 N + 가중치 효과(wt vs wt_year_eq 연도합)."""
    n_by_year = df.groupby("year").size().reindex(YEARS)
    wsum = df.groupby("year")[["wt", WCOL]].sum().reindex(YEARS)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    colors = ["#9aa7b5" if y != 2022 else "#d1495b" for y in YEARS]
    axes[0].bar([str(y) for y in YEARS], n_by_year.values, color=colors)
    for i, v in enumerate(n_by_year.values):
        axes[0].text(i, v + 800, f"{v:,}", ha="center", fontsize=9)
    axes[0].set_title("① 연도별 표본 N — 2022 개인용 표본 지배(N=58,936)", fontsize=12)
    axes[0].set_ylabel("응답자 수")
    axes[0].set_ylim(0, 66000)

    x = np.arange(len(YEARS)); w = 0.38
    axes[1].bar(x - w / 2, wsum["wt"].values, w, label="wt(원가중) 연도합", color="#9aa7b5")
    axes[1].bar(x + w / 2, wsum[WCOL].values, w, label="wt_year_eq 연도합", color="#2e86ab")
    axes[1].axhline(len(df) / len(YEARS), ls="--", c="#444",
                    label=f"균등목표 N/T={len(df)/len(YEARS):,.0f}")
    axes[1].set_xticks(x); axes[1].set_xticklabels([str(y) for y in YEARS])
    axes[1].set_title("가중치 효과 — wt_year_eq는 연도기여 균등화(2022 지배 제거)", fontsize=12)
    axes[1].set_ylabel("가중치 합"); axes[1].legend(fontsize=8)
    fig.tight_layout()
    out = FIG / "eda_p1_sample_structure.png"
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def panel2_demographics(df: pd.DataFrame) -> Path:
    """② 인구통계 구성비(가중) 연도 추이 — 성·연령군·학력·소득(2022 전후 안정성)."""
    age_grp = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LBL)
    dfa = df.assign(age_grp=age_grp)

    specs = [
        ("sex", wcomp_by_year(df, "sex"), SEX_LBL, "성별"),
        ("age_grp", None, None, "연령군"),
        ("edu", wcomp_by_year(df, "edu"), EDU_LBL, "학력(4단계)"),
        ("income_band7", wcomp_by_year(df, "income_band7"), INC7_LBL, "가구소득(7밴드)"),
    ]
    # 연령군은 범주형이라 별도 가중 구성비
    age_comp = {}
    for y in YEARS:
        sub = dfa[dfa["year"] == y][["age_grp", WCOL]].dropna()
        g = sub.groupby("age_grp", observed=False)[WCOL].sum()
        age_comp[y] = g / g.sum() if g.sum() > 0 else g
    age_df = pd.DataFrame(age_comp).T.reindex(YEARS)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8.4))
    cmap = plt.get_cmap("Set2")
    for ax, (col, comp, lbl, title) in zip(axes.ravel(), specs):
        comp = age_df if col == "age_grp" else comp
        cats = list(comp.columns)
        bottom = np.zeros(len(YEARS))
        for j, c in enumerate(cats):
            vals = comp[c].fillna(0).values * 100
            name = (lbl.get(c, str(c)) if lbl else str(c))
            ax.bar([str(y) for y in YEARS], vals, bottom=bottom,
                   label=name, color=cmap(j % 8), edgecolor="white", linewidth=0.4)
            bottom += vals
        ax.set_title(f"② {title} 구성비(가중 %)", fontsize=11)
        ax.set_ylim(0, 100); ax.set_ylabel("%")
        ax.legend(fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.08))
        ax.axvspan(2.5, 3.5, color="#d1495b", alpha=0.06)  # 2022 위치 강조
    fig.suptitle("인구통계 구성비 연도 추이 — 2022(붉은 띠) 전후 구성 안정성 점검", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = FIG / "eda_p2_demographics.png"
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def panel3_trust_timeseries(df: pd.DataFrame) -> Path:
    """③ 신뢰 단일문항 + credibility 배터리 가중평균 시계열(가용연도만)."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    # (a) 단일문항 신뢰 3종
    for col in TRUST_SINGLE:
        s = wmean_by_year(df, col)
        axes[0].plot(YEARS, s.values, marker="o", label=TRUST_LABEL[col])
    axes[0].set_title("③a 단일문항 신뢰 가중평균(1~5) — 2019 구조적 부재", fontsize=11)
    axes[0].set_xlabel("연도"); axes[0].set_ylabel("가중평균(1~5)")
    axes[0].set_ylim(2.4, 3.6); axes[0].grid(alpha=0.3); axes[0].legend(fontsize=8)
    axes[0].axvspan(2018.5, 2019.5, color="#999", alpha=0.12)

    # (b) credibility 6지표
    for col in CRED6:
        s = wmean_by_year(df, col)
        ls = "-" if col in CRED_CORE3 else "--"
        lw = 2.2 if col in CRED_CORE3 else 1.4
        axes[1].plot(YEARS, s.values, marker="o", ls=ls, lw=lw, label=CRED_LABEL[col])
    axes[1].set_title("③b credibility 배터리 가중평균(1~5) — 핵심3지표(실선) 7개년", fontsize=11)
    axes[1].set_xlabel("연도"); axes[1].set_ylabel("가중평균(1~5)")
    axes[1].grid(alpha=0.3); axes[1].legend(fontsize=7, ncol=2)
    fig.tight_layout()
    out = FIG / "eda_p3_trust_timeseries.png"
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def panel4_availability(df: pd.DataFrame) -> Path:
    """④ 연도×변수 non-NA 비율 히트맵(결측·가용 구조)."""
    cols = (["sex", "age", "edu", "income_band7", "job", "region",
             "media_main_route_code"] + TRUST_SINGLE + CRED6)
    mat = pd.DataFrame(
        {c: [df[df["year"] == y][c].notna().mean() for y in YEARS] for c in cols},
        index=YEARS,
    ).T  # 행=변수, 열=연도

    fig, ax = plt.subplots(figsize=(9.5, 8.2))
    im = ax.imshow(mat.values, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(YEARS))); ax.set_xticklabels(YEARS)
    ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols, fontsize=9)
    for i in range(len(cols)):
        for j in range(len(YEARS)):
            v = mat.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=7.5, color="white" if v > 0.55 else "#333")
    ax.set_title("④ 지표 가용성 — 연도×변수 non-NA 비율(0=전무·결측구조)", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="non-NA 비율")
    fig.tight_layout()
    out = FIG / "eda_p4_availability.png"
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def panel5_corr_dist(df: pd.DataFrame) -> Path:
    """⑤ credibility 3지표 상관·연도별 분포 + 신뢰 vs 인구통계 교차."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7))

    # (a) 핵심3지표 상관(가중 풀, 완전케이스)
    cc = df[CRED_CORE3].dropna()
    corr = np.corrcoef(cc.values.T)
    im = axes[0].imshow(corr, cmap="RdYlBu_r", vmin=0, vmax=1)
    axes[0].set_xticks(range(3)); axes[0].set_yticks(range(3))
    lbls = [CRED_LABEL[c] for c in CRED_CORE3]
    axes[0].set_xticklabels(lbls, fontsize=9); axes[0].set_yticklabels(lbls, fontsize=9)
    for i in range(3):
        for j in range(3):
            axes[0].text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center", fontsize=10)
    axes[0].set_title("⑤a 핵심3지표 상관(완전케이스)", fontsize=11)
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    # (b) cred_mean 연도별 분포(박스) — 합성평균(metric 동등 지지)
    df = df.assign(cred_mean=df[CRED_CORE3].mean(axis=1))
    data = [df[df["year"] == y]["cred_mean"].dropna().values for y in YEARS]
    axes[1].boxplot(data, tick_labels=[str(y) for y in YEARS], showfliers=False)
    axes[1].set_title("⑤b cred_mean(3지표 평균) 연도 분포", fontsize=11)
    axes[1].set_ylabel("1~5"); axes[1].grid(alpha=0.3, axis="y")

    # (c) cred_mean × 학력·연령군(가중평균) — 신뢰 vs 인구통계 교차
    age_grp = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LBL)
    dfa = df.assign(age_grp=age_grp)
    edu_means = [wmean(df[df["edu"] == e], "cred_mean") for e in [1, 2, 3, 4]]
    age_means = [wmean(dfa[dfa["age_grp"] == g], "cred_mean") for g in AGE_LBL]
    x1 = np.arange(4); x2 = np.arange(len(AGE_LBL)) + 5
    axes[2].bar(x1, edu_means, color="#2e86ab", label="학력")
    axes[2].bar(x2, age_means, color="#e8a13a", label="연령군")
    axes[2].set_xticks(list(x1) + list(x2))
    axes[2].set_xticklabels([EDU_LBL[e] for e in [1, 2, 3, 4]] + AGE_LBL,
                            rotation=40, ha="right", fontsize=8)
    axes[2].set_ylim(2.6, 3.4); axes[2].set_ylabel("cred_mean 가중평균")
    axes[2].set_title("⑤c 신뢰성 × 학력·연령군", fontsize=11); axes[2].legend(fontsize=8)
    fig.tight_layout()
    out = FIG / "eda_p5_corr_dist.png"
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def panel6_p4_link() -> Path:
    """⑥ P4 연결 — 정렬 잠재추세 + APC 기간효과(P4 산출 인용, 비재계산)."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    a = [P4_ALIGN_ALPHA[y] for y in YEARS]
    axes[0].plot(YEARS, a, marker="o", color="#d1495b", lw=2.2)
    axes[0].axhline(0, ls="--", c="#888")
    for y in YEARS:
        axes[0].annotate(f"{P4_ALIGN_ALPHA[y]:+.2f}", (y, P4_ALIGN_ALPHA[y]),
                         textcoords="offset points", xytext=(0, 7), fontsize=8, ha="center")
    axes[0].set_title("⑥a 정렬 잠재평균 추세 α (2019=0, SD단위)\n"
                      f"비동등 {P4_NONINVAR_PCT}% → 비교 정당 · MK τ={P4_MK_TAU:+.2f}(p={P4_MK_P:.3f})",
                      fontsize=10.5)
    axes[0].set_xlabel("연도"); axes[0].set_ylabel("잠재평균 α(2019-SD)")
    axes[0].grid(alpha=0.3); axes[0].axvspan(2018.5, 2019.5, color="#999", alpha=0.12)

    h = [P4_PERIOD_HAPC[y] for y in YEARS]; ie = [P4_PERIOD_IE[y] for y in YEARS]
    axes[1].plot(YEARS, h, marker="s", label="기간효과 HAPC", color="#2e86ab")
    axes[1].plot(YEARS, ie, marker="^", label="기간효과 IE", color="#e8a13a")
    axes[1].axhline(0, ls="--", c="#888")
    axes[1].set_title("⑥b APC 기간(Period) 효과 — 정렬추세와 삼각검증\n"
                      "HAPC↔정렬 r=+0.99 · IE↔정렬 r=+0.96 → '시대(기간) 효과'", fontsize=10.5)
    axes[1].set_xlabel("연도"); axes[1].set_ylabel("기간효과(중심화)")
    axes[1].grid(alpha=0.3); axes[1].legend(fontsize=8)
    fig.tight_layout()
    out = FIG / "eda_p6_p4_link.png"
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def main() -> None:
    if not PARQUET.exists():
        raise SystemExit(
            f"입력 없음: {PARQUET}\n  → 먼저 `python src/harmonize.py`로 패널을 빌드하세요.")
    font = setup_korean_font()
    df = pd.read_parquet(PARQUET)
    assert len(df) == 90996, f"행수 불일치: {len(df):,} (기대 90,996)"

    print(f"폰트: {font} | 패널 로드: {len(df):,}행 × {df.shape[1]}컬럼")
    outs = [
        panel1_sample_structure(df),
        panel2_demographics(df),
        panel3_trust_timeseries(df),
        panel4_availability(df),
        panel5_corr_dist(df),
        panel6_p4_link(),
    ]
    print("\n생성된 figure:")
    for p in outs:
        print(f"  - {p.relative_to(ROOT)}  ({p.stat().st_size/1024:.0f} KB)")

    # 자기점검 요약(콘솔)
    print("\n[자기점검] 연도별 N 합 =", f"{df.groupby('year').size().sum():,}")
    print("[자기점검] credibility 핵심3지표 가용연도(non-NA>0):")
    for c in CRED_CORE3:
        yrs = [y for y in YEARS if df[df["year"] == y][c].notna().sum() > 0]
        print(f"  {c}: {yrs}")
    print("[참고] 단일문항 trust_news_overall 가용연도:",
          [y for y in YEARS if df[df["year"] == y]["trust_news_overall"].notna().sum() > 0])


if __name__ == "__main__":
    main()
