"""P5 Evaluation — 통합 평가 서사 종합 시각 패널.

CRISP-DM P5(Evaluation) 산출물. P4·P2의 흩어진 결과를 하나의 평가 스토리라인으로
종합하는 [`docs/design/p5-evaluation.md`]의 동반 figure를 그린다.

※️ 중요: 본 스크립트는 **재계산이 아니라 인용 상수**(출처 문서의 이미 산출된 수치)로
   종합 패널을 그린다. 따라서 parquet(하모나이즈 산출물)을 필요로 하지 않는다.
   원수치 재생성은 각 출처 스크립트(mgcfa_invariance / mgcfa_semopy_crossval /
   alignment / trend_apc / eda_overview)를 직접 실행한다.

패널:
  ① 증거 사다리(p5_evidence_ladder.png) — ①데이터구조→②교차검증→③측정동등→④정렬추세→⑤추세·세대
     5단계가 하위→상위로 다음을 정당화하는 구조 + 각 단계 핵심수치.
  ② 삼각검증(p5_triangulation.png) — 정렬 잠재평균 / 단일문항 / 합성 cred_mean 세 궤적을
     공통 z-표준화로 겹쳐 종점 방향·2025 반등 변곡점 일치 시각화 + APC 기간효과 동행.

검증 게이트(data-spec.md §6): 인용 수치는 KPF 원자료 재검증 전 보고서·웹데모 직접 인용 신중.
   본 figure는 '근거 종합' 시각이며 방향·일관성 해석 위주.

실행: python src/p5_evaluation.py   (parquet 불요)
의존: numpy, matplotlib.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")  # 헤드리스 PNG 저장
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# 콘솔 cp949 회피
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs/design/figures"
FIG.mkdir(parents=True, exist_ok=True)

YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

# ── 인용 상수(재계산 아님; 출처 docs/design/*.md) ────────────────────────────
# alignment-trust-trend.md §1 — 정렬 잠재평균 α(2019=0, 2019-SD 단위)
ALIGN_ALPHA = {2019: 0.000, 2020: 0.354, 2021: 0.474, 2022: 0.453,
               2023: 0.394, 2024: 0.298, 2025: 0.671}
# alignment-trust-trend.md §4 — 단일문항 trust_news_overall(1~5, wt_year_eq; 2019 부재)
TRUST_SINGLE = {2020: 3.297, 2021: 3.322, 2022: 3.151,
                2023: 3.272, 2024: 3.360, 2025: 3.436}
# eda-overview.md §1-③ — 합성 cred_mean(3지표 평균, 1~5, wt_year_eq)
CRED_MEAN = {2019: 3.034, 2020: 3.249, 2021: 3.305, 2022: 3.211,
             2023: 3.190, 2024: 3.176, 2025: 3.390}
# trend-apc-results.md §1·§2.1 — 기간효과(정렬추세와 삼각검증)
PERIOD_HAPC = {2019: -0.206, 2020: 0.003, 2021: 0.067, 2022: 0.014,
               2023: -0.001, 2024: -0.053, 2025: 0.176}
PERIOD_IE = {2019: -0.194, 2020: 0.026, 2021: 0.079, 2022: -0.008,
             2023: -0.027, 2024: -0.047, 2025: 0.171}

# 증거 사다리 단계(하위 토대 → 상위 결론). 출처 문서·핵심수치·판정.
LADDER = [
    ("① 데이터 구조·단일차원성",
     "핵심3지표 상관 .55~.64 · Cronbach α 0.70~0.82(7개년)",
     "단일요인(credibility) 구성 타당 → CFA 입력 정당", "EDA⑤ / semopy§4", "ok"),
    ("② 추정 엔진 교차검증",
     "직접구현 ↔ semopy 표준적재 최대차 0.0003(3지표)·0.0001(4지표)",
     "추정이 특정 라이브러리 산물 아님 → 동등제약 결과 신뢰", "semopy§1·§5", "ok"),
    ("③ 측정 동등(MGCFA)",
     "metric ΔCFI -0.0008~-0.0018(강지지) · scalar -0.0063~-0.0100(부분)",
     "요인부하 연도불변 → 잠재평균 비교 1차 자격", "invariance§1·§6", "partial"),
    ("④ 정렬 잠재평균 추세",
     "α 2019=0 → 2025 +0.671SD · 비동등 2.4%(≤20%)",
     "alignment-adjusted 잠재평균 비교 정당 → 추세 보고 가능", "alignment§1", "ok"),
    ("⑤ 추세검정·세대효과",
     "MK τ=+0.333(P(S>0)=1.00) · 기간효과 r=+0.99/+0.96",
     "상승 = 기간(시대) 효과 확정 · 코호트 구배 -0.891 별개", "trend-apc§1·§2", "ok"),
]

COL = {
    "ok": "#1b7837",        # 통과(녹)
    "partial": "#b8860b",   # 부분(황)
    "rung": "#e9f1ec",
    "rung_edge": "#9ec6ad",
    "ink": "#1a1a1a",
    "sub": "#555555",
    "A": "#08519c",         # 정렬 잠재(파)
    "B": "#d94801",         # 단일문항(주황)
    "C": "#6a51a3",         # 합성(보라)
    "period": "#999999",
    "rebound": "#cc2b2b",
}


def setup_korean_font() -> str:
    """Windows 한글 폰트 설정(eda_overview.py와 동일 정책)."""
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


def _zscore(d: dict[int, float]) -> dict[int, float]:
    """가용연도만으로 z-표준화(궤적 겹쳐보기용; 척도 다른 3지표 비교)."""
    vals = np.array(list(d.values()), dtype=float)
    mu, sd = vals.mean(), vals.std(ddof=0)
    sd = sd if sd > 0 else 1.0
    return {k: (v - mu) / sd for k, v in d.items()}


# ── 패널 ① 증거 사다리 ──────────────────────────────────────────────────────
def panel_evidence_ladder() -> Path:
    fig, ax = plt.subplots(figsize=(12.5, 8.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    n = len(LADDER)
    y0, y1 = 1.0, 8.4
    step = (y1 - y0) / n
    box_h = step * 0.80

    for i, (title, num, justify, src, status) in enumerate(LADDER):
        y = y0 + i * step  # i=0 토대(아래) → 위로 결론
        edge = COL[status]
        box = FancyBboxPatch(
            (0.5, y), 8.6, box_h,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=2.0, edgecolor=edge, facecolor=COL["rung"], zorder=3,
        )
        ax.add_patch(box)
        cy = y + box_h / 2
        ax.text(0.78, cy + box_h * 0.20, title, fontsize=12.5, fontweight="bold",
                color=COL["ink"], va="center", ha="left", zorder=4)
        ax.text(0.82, cy - box_h * 0.16, num, fontsize=10.0, color=COL["sub"],
                va="center", ha="left", zorder=4)
        ax.text(0.82, cy - box_h * 0.43, f"→ {justify}", fontsize=9.3,
                color=edge, va="center", ha="left", zorder=4, style="italic")
        # 판정 배지 + 출처
        verdict = "통과" if status == "ok" else "부분"
        ax.text(8.95, cy + box_h * 0.18, verdict, fontsize=10.5, fontweight="bold",
                color=edge, va="center", ha="right", zorder=4)
        ax.text(8.95, cy - box_h * 0.30, src, fontsize=8.2, color=COL["sub"],
                va="center", ha="right", zorder=4)
        # 정당화 화살표(아래 단계 → 위 단계)
        if i < n - 1:
            ny = y0 + (i + 1) * step
            arr = FancyArrowPatch(
                (4.8, y + box_h + 0.02), (4.8, ny - 0.02),
                arrowstyle="-|>", mutation_scale=16, linewidth=1.6,
                color="#777777", zorder=2,
            )
            ax.add_patch(arr)

    # 축 라벨(토대↔결론)
    ax.text(9.55, y0 + box_h / 2, "토대", fontsize=10, color=COL["sub"],
            rotation=90, va="center", ha="center")
    ax.text(9.55, y0 + (n - 1) * step + box_h / 2, "결론", fontsize=10,
            color=COL["ink"], rotation=90, va="center", ha="center", fontweight="bold")

    ax.text(0.5, 9.55, "P5 증거 사다리 — 하위 단계가 상위 단계를 정당화",
            fontsize=16, fontweight="bold", color=COL["ink"], ha="left", va="center")
    ax.text(0.5, 9.05,
            "언론 신뢰성(credibility) 2019→2025 상승 결론은 5단계 사다리 전 칸 통과로 성립 "
            "(녹=통과 · 황=부분/scalar 보수적 미확정)",
            fontsize=10.5, color=COL["sub"], ha="left", va="center")
    ax.text(0.5, 0.45,
            "※ 검증 게이트(data-spec §6): 인용 수치는 KPF 원자료 재검증 전 직접 인용 신중. "
            "정렬 알고리즘·완전 동등제약 χ² 재현은 R sirt/Mplus 영역(범위 외).",
            fontsize=8.6, color=COL["sub"], ha="left", va="center", style="italic")

    out = FIG / "p5_evidence_ladder.png"
    fig.savefig(out, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


# ── 패널 ② 삼각검증 ─────────────────────────────────────────────────────────
def panel_triangulation() -> Path:
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(13.6, 5.8), gridspec_kw={"width_ratios": [1.05, 1.0]})

    # 좌: 세 궤적 z-표준화 겹침
    zA, zB, zC = _zscore(ALIGN_ALPHA), _zscore(TRUST_SINGLE), _zscore(CRED_MEAN)
    for d, z, c, lbl, mk in [
        (ALIGN_ALPHA, zA, COL["A"], "A. 정렬 잠재평균 α (2019-SD)", "o"),
        (TRUST_SINGLE, zB, COL["B"], "B. 단일문항 trust_news_overall (1~5)", "s"),
        (CRED_MEAN, zC, COL["C"], "C. 합성 cred_mean (1~5)", "^"),
    ]:
        xs = list(d.keys())
        ys = [z[k] for k in xs]
        axL.plot(xs, ys, marker=mk, color=c, linewidth=2.3, markersize=7,
                 label=lbl, zorder=3)
    # 2025 반등 강조
    axL.axvspan(2024, 2025, color=COL["rebound"], alpha=0.07, zorder=0)
    axL.annotate("2025 반등\n(A·C 2024 저점 → 2025 최고)",
                 xy=(2025, zA[2025]), xytext=(2022.4, 1.55),
                 fontsize=9.2, color=COL["rebound"], fontweight="bold",
                 ha="left", va="center",
                 arrowprops=dict(arrowstyle="->", color=COL["rebound"], lw=1.4))
    axL.axhline(0, color="#bbbbbb", linewidth=0.8, zorder=1)
    axL.set_title("삼각검증 — 세 궤적 z-표준화 겹침(종점 방향·반등 일치)",
                  fontsize=12.5, fontweight="bold")
    axL.set_xlabel("연도")
    axL.set_ylabel("z-표준화 값(척도 차 제거)")
    axL.set_xticks(YEARS)
    axL.legend(fontsize=8.6, loc="lower left", framealpha=0.9)
    axL.grid(True, alpha=0.25)
    axL.text(0.012, -0.205,
             "MK τ 부호 전부 양(+): A +0.333 · B +0.467 · C +0.143 | "
             "단년 저점 시점은 A=2024·B=2022로 어긋남 → 종점 방향만 비교(§3.2)",
             transform=axL.transAxes, fontsize=8.0, color=COL["sub"], style="italic")

    # 우: APC 기간효과 동행(정렬추세 vs HAPC vs IE)
    xs = YEARS
    axR.plot(xs, [ALIGN_ALPHA[y] for y in xs], marker="o", color=COL["A"],
             linewidth=2.3, markersize=7, label="정렬 잠재평균 α(2019=0)", zorder=3)
    axR.plot(xs, [PERIOD_HAPC[y] for y in xs], marker="D", color="#2c7fb8",
             linewidth=1.9, markersize=6, label="APC 기간효과 HAPC (r=+0.990)",
             linestyle="--", zorder=3)
    axR.plot(xs, [PERIOD_IE[y] for y in xs], marker="v", color="#7fcdbb",
             linewidth=1.9, markersize=6, label="APC 기간효과 IE (r=+0.960)",
             linestyle="--", zorder=3)
    axR.axhline(0, color="#bbbbbb", linewidth=0.8, zorder=1)
    axR.set_title("'상승 = 기간(시대) 효과' — 정렬추세 ↔ APC 기간효과 동행",
                  fontsize=12.5, fontweight="bold")
    axR.set_xlabel("연도")
    axR.set_ylabel("효과(좌: 2019-SD · APC: 편차)")
    axR.set_xticks(YEARS)
    axR.legend(fontsize=8.6, loc="upper left", framealpha=0.9)
    axR.grid(True, alpha=0.25)
    axR.text(0.012, -0.205,
             "기간효과가 정렬추세와 강정합(r~0.99) → 상승은 노화(연령)·표본 세대구성 아닌 시대 효과. "
             "코호트 구배 -0.891은 별개 발견(trend-apc §3).",
             transform=axR.transAxes, fontsize=8.0, color=COL["sub"], style="italic")

    fig.suptitle("P5 삼각검증 — 서로 다른 척도·방법이 같은 종점 방향·반등을 가리킨다",
                 fontsize=15, fontweight="bold", y=1.005)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    out = FIG / "p5_triangulation.png"
    fig.savefig(out, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main() -> None:
    used = setup_korean_font()
    print(f"[P5] 한글 폰트: {used}")
    print("[P5] 인용 상수 기반 종합 패널 생성(재계산 아님; parquet 불요)")
    p1 = panel_evidence_ladder()
    print(f"  ✓ {p1.relative_to(ROOT)}")
    p2 = panel_triangulation()
    print(f"  ✓ {p2.relative_to(ROOT)}")
    # 자기점검: 종점 방향 부호 일치(삼각검증 핵심 불변식)
    endA = ALIGN_ALPHA[2025] - ALIGN_ALPHA[2019]
    endB = TRUST_SINGLE[2025] - TRUST_SINGLE[2020]
    endC = CRED_MEAN[2025] - CRED_MEAN[2019]
    assert endA > 0 and endB > 0 and endC > 0, "종점 방향 부호 불일치 — 인용 상수 점검"
    print(f"[P5] 자기점검 통과 — 종점 방향 부호 일치(A={endA:+.3f}, B={endB:+.3f}, C={endC:+.3f})")


if __name__ == "__main__":
    main()
