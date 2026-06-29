# -*- coding: utf-8 -*-
"""뉴스 소비 건강지수 — 7개년 패널 어댑터 (P4 종단 지수화, A 트랙 ③).

목적: `harmonize.py`가 산출한 7개년(2019~2025) 통합 패널
  (`data/processed/audience_harmonized.parquet`)을 입력으로,
  **연도별** 신뢰지수·다양성지수·NCHI를 산출한다.

설계 원칙 — **thin 어댑터**:
  · 공통 수학(`_scale_1_100`·`nchi`·`wmean`·`cronbach_alpha`·`persona_quadrant`)은
    `news_health_features.py`(2025 단년 SSOT)에서 **import**한다. 재구현 금지.
  · 본 모듈은 "패널 어댑터"만 담당 — 입력 스키마 정렬·연도 집계·2버전 병기.
  · 2025 단년 모듈(`news_health_features.py`)은 이력보존을 위해 그대로 둔다.

지수 정의(근거):
  · 신뢰지수 = credibility 핵심3{공정·전문·정확}(`harmonize.CRED_FACTOR_CORE3`)의
    pooled z평균 → `_scale_1_100`. 신뢰축은 **reflective** → MGCFA(21·22 노트북)에서
    측정불변(metric+)이 지지되어 **연도 비교 가능**(mgcfa-invariance-results.md).
  · 다양성지수 = `richness_fixed8`(7개년 공통 8매체 고정풀) 기반 → `_scale_1_100`.
    ⚠️ 다양성축은 **formative** → 절대수준 비교 금지·**방향성만** 해석
    (06-research-diversity-harmonization-brief.md §결과 R4). 신설포함
    (`richness_incl`) 2버전 병기.
  · NCHI = 연도별 √(신뢰 × 다양성) 기하평균(`news_health_features.nchi`).

가중치: `wt_year_eq`(연도기여 균등화, 2022 표본지배 보정; harmonize 05 §6) 기본.

⚠️ 산출 수치는 KPF 원자료 재검증·측정 비동등 검정 전 보고서/웹데모 직접 인용 신중(검증 게이트).

실행: python src/health_index_panel.py   (self-validation 포함)
의존: pandas, numpy, pyarrow. news_health_features·harmonize 재사용.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001 — 일부 환경(파이프)에서는 reconfigure 미지원
    pass

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import harmonize as hz  # noqa: E402  — 패널 경로·credibility 핵심3 스펙(SSOT)
import news_health_features as nf  # noqa: E402  — 공통 수학(재구현 금지)

CORE3 = hz.CRED_FACTOR_CORE3       # ["cred_fair", "cred_professional", "cred_accurate"]
YEARS = hz.YEARS                   # [2019, ..., 2025]
DEFAULT_WEIGHT = "wt_year_eq"      # 2022 표본지배 보정 가중


# ── 로딩 ──────────────────────────────────────────────────────────────
def load_panel(path: Path | None = None) -> pd.DataFrame:
    """하모나이즈 패널 로드. 산출물이 없으면 harmonize 재생성을 안내한다."""
    pq = path or hz.OUT_PARQUET
    if not pq.exists():
        raise FileNotFoundError(
            f"패널 산출물이 없습니다: {pq}\n"
            "  → 먼저 `python src/harmonize.py` 를 실행해 패널을 생성하세요."
        )
    return pd.read_parquet(pq)


# ── 연도 집계 헬퍼 ────────────────────────────────────────────────────
def _by_year_wmean(panel: pd.DataFrame, value: pd.Series, weight_col: str) -> pd.Series:
    """value(응답자 단위)를 연도별 가중평균(wmean) → year 인덱스 Series."""
    df = pd.DataFrame({"year": panel["year"].to_numpy(),
                       "v": value.to_numpy(),
                       "w": panel[weight_col].to_numpy()})
    out = {y: nf.wmean(g["v"], g["w"]) for y, g in df.groupby("year")}
    return pd.Series(out, name="value").sort_index()


def _valid_n_by_year(panel: pd.DataFrame, value: pd.Series) -> pd.Series:
    """연도별 유효(non-NA) 응답 수."""
    s = pd.DataFrame({"year": panel["year"].to_numpy(), "v": value.to_numpy()})
    return s.groupby("year")["v"].apply(lambda x: int(x.notna().sum())).sort_index()


# ── 신뢰지수 (reflective, 연도 비교 가능) ─────────────────────────────
def _trust_score_respondent(panel: pd.DataFrame) -> pd.Series:
    """응답자 단위 신뢰 원점수: credibility 핵심3 pooled z평균 → _scale_1_100.

    pooled 표준화(7개년 공통 척도) — MGCFA 측정불변이 전제이므로 연도 통합 z가 정당.
    """
    sub = panel[CORE3].apply(pd.to_numeric, errors="coerce")
    std = sub.std(ddof=0).replace(0, np.nan)
    z = (sub - sub.mean()) / std            # pooled z (열별)
    raw = z.mean(axis=1)                     # 핵심3 z평균(reflective 합성)
    return nf._scale_1_100(raw)             # pooled [1,100]


def trust_index_panel(panel: pd.DataFrame, weight_col: str = DEFAULT_WEIGHT) -> pd.DataFrame:
    """연도별 신뢰지수(1~100). cred 핵심3 z평균 → _scale_1_100 → 연도 가중평균.

    신뢰축=reflective → 측정불변 검정(MGCFA 21·22) 통과 → **연도 비교 가능**.
    반환: index=year, columns=[trust_index, n_valid].
    """
    score = _trust_score_respondent(panel)
    out = pd.DataFrame({
        "trust_index": _by_year_wmean(panel, score, weight_col),
        "n_valid": _valid_n_by_year(panel, score),
    })
    return out


# ── 다양성지수 (formative, 방향성만) ──────────────────────────────────
def diversity_index_panel(panel: pd.DataFrame, weight_col: str = DEFAULT_WEIGHT) -> pd.DataFrame:
    """연도별 다양성지수(1~100). richness_fixed8 기반 → _scale_1_100. 신설포함 2버전 병기.

    ⚠️ formative 구성 → 절대수준 비교 금지·**방향성(추세)만** 해석(06 §결과 R4).
      · diversity_index_fixed8: 7개년 공통 8매체 고정풀(0~8) 기반 → 종단 비교 주지표.
      · diversity_index_incl: 신설 디지털매체(숏폼·OTT·AI) 포함(0~11). 부재연도는
        richness_fixed8과 동일 → fixed8 대비 '신설 기여'를 가시화하는 보조 버전.
    반환: index=year, columns=[diversity_index_fixed8, diversity_index_incl, n_valid].
    """
    fixed = nf._scale_1_100(pd.to_numeric(panel["richness_fixed8"], errors="coerce"))
    incl = nf._scale_1_100(pd.to_numeric(panel["richness_incl"], errors="coerce"))
    out = pd.DataFrame({
        "diversity_index_fixed8": _by_year_wmean(panel, fixed, weight_col),
        "diversity_index_incl": _by_year_wmean(panel, incl, weight_col),
        "n_valid": _valid_n_by_year(panel, fixed),
    })
    return out


# ── NCHI (기하평균) ───────────────────────────────────────────────────
def nchi_by_year(panel: pd.DataFrame, weight_col: str = DEFAULT_WEIGHT,
                 diversity_version: str = "fixed8") -> pd.DataFrame:
    """연도별 NCHI = √(신뢰 × 다양성) 기하평균. 기하평균은 news_health_features.nchi 재사용.

    diversity_version: "fixed8"(주지표·종단) | "incl"(신설포함 보조).
    반환: index=year, columns=[trust_index, diversity_index, nchi].
    ⚠️ NCHI 절대수준은 다양성 formative 한계를 상속 → 종단은 방향성 위주로 해석.
    """
    t = trust_index_panel(panel, weight_col)["trust_index"]
    dcol = f"diversity_index_{diversity_version}"
    d = diversity_index_panel(panel, weight_col)[dcol]
    out = pd.DataFrame({"trust_index": t, "diversity_index": d})
    out["nchi"] = nf.nchi(t, d, method="geometric")  # year 인덱스 정렬
    return out


# ── self-validation ───────────────────────────────────────────────────
def _check_range(name: str, df: pd.DataFrame, cols: list[str]) -> bool:
    """연도별 지수가 [1,100] 범위·NA 없음인지 점검."""
    ok = True
    for c in cols:
        s = df[c]
        na = int(s.isna().sum())
        lo, hi = s.min(), s.max()
        in_range = bool(s.dropna().between(1, 100).all())
        flag = "OK" if (na == 0 and in_range) else "FAIL"
        if flag == "FAIL":
            ok = False
        print(f"  [{flag}] {name}.{c}: 범위[{lo:.1f}, {hi:.1f}] NA={na}")
    return ok


def _validate_2025_direction(panel: pd.DataFrame) -> None:
    """2025 패널값이 news_health_features 2025 단년 산출과 **방향 정합**인지 검증.

    패널(cred 핵심3 z평균)과 2025 모듈(TRUST_CORE 22문항 z평균)은 문항군이 달라
    절대값은 다르지만, 동일 응답자 척도이므로 **양(+)의 상관**이면 방향 정합으로 본다.
    다양성도 둘 다 richness 기반 → 양의 상관 기대.
    """
    try:
        df25 = nf.load_2025()
    except Exception as e:  # noqa: BLE001 — 2025 .sav/parquet 미가용 시 스킵
        print(f"  [SKIP] 2025 단년 데이터 미가용 → 방향 정합 검증 생략 ({e})")
        return

    p25 = panel[panel["year"] == 2025].copy()
    # resp_id "2025_{i}" 의 i = 2025 build 시 positional index → df25.iloc 정렬키.
    pos = p25["resp_id"].str.split("_").str[1].astype(int).to_numpy()
    if pos.max() >= len(df25) or len(p25) != len(df25):
        print(f"  [SKIP] 패널 2025({len(p25)})↔단년({len(df25)}) 정렬 불가 → 방향 검증 생략")
        return

    # 신뢰: 패널 cred3 z평균 vs 단년 trust_index (응답자 단위)
    panel_trust = _trust_score_respondent(panel)[p25.index].to_numpy()
    nf_trust = nf.trust_index(df25).to_numpy()[pos]
    # 다양성: 패널 richness_fixed8 vs 단년 diversity richness
    panel_div = pd.to_numeric(p25["richness_fixed8"], errors="coerce").to_numpy()
    nf_div = nf.diversity_index(df25).to_numpy()[pos]

    def _corr(a: np.ndarray, b: np.ndarray) -> float:
        m = ~(np.isnan(a) | np.isnan(b))
        return float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 2 else np.nan

    rt, rd = _corr(panel_trust, nf_trust), _corr(panel_div, nf_div)
    ft = "OK" if rt > 0 else "FAIL"
    fd = "OK" if rd > 0 else "FAIL"
    print(f"  [{ft}] 2025 신뢰 방향 정합: corr(패널 cred3, 단년 22문항)={rt:+.3f} (>0 기대)")
    print(f"  [{fd}] 2025 다양성 방향 정합: corr(패널 richness8, 단년 richness)={rd:+.3f} (>0 기대)")


def main() -> None:
    panel = load_panel()
    print("=" * 64)
    print(f"패널 로드: {hz.OUT_PARQUET.relative_to(ROOT)}  행수={len(panel):,}")

    trust = trust_index_panel(panel)
    div = diversity_index_panel(panel)
    nchi_fixed = nchi_by_year(panel, diversity_version="fixed8")
    nchi_incl = nchi_by_year(panel, diversity_version="incl")

    print("\n[연도별 신뢰지수 — cred 핵심3(reflective·연도 비교 가능)]")
    print(trust.to_string(float_format=lambda x: f"{x:.1f}"))

    print("\n[연도별 다양성지수 — richness_fixed8(formative·방향성만) + 신설포함]")
    print(div.to_string(float_format=lambda x: f"{x:.1f}"))

    print("\n[연도별 NCHI = √(신뢰×다양성) — 다양성 fixed8 주지표]")
    print(nchi_fixed.to_string(float_format=lambda x: f"{x:.1f}"))
    print("\n[연도별 NCHI — 다양성 신설포함(incl) 보조]")
    print(nchi_incl.to_string(float_format=lambda x: f"{x:.1f}"))

    # ── self-validation ──────────────────────────────────────
    print("\n" + "-" * 64)
    print("[self-validation] 연도별 지수 범위·NA 점검")
    ok = True
    ok &= _check_range("trust", trust, ["trust_index"])
    ok &= _check_range("diversity", div, ["diversity_index_fixed8", "diversity_index_incl"])
    ok &= _check_range("nchi", nchi_fixed, ["trust_index", "diversity_index", "nchi"])
    miss = [y for y in YEARS if y not in trust.index]
    print(f"  [{'OK' if not miss else 'FAIL'}] 연도 커버리지: "
          f"{sorted(trust.index.tolist())} (누락={miss or '없음'})")

    print("\n[self-validation] 2025 패널↔단년 방향 정합")
    _validate_2025_direction(panel)

    print("\n" + "=" * 64)
    print(f"self-validation(범위/NA/커버리지): {'전부 통과' if ok else '실패 항목 있음 — 위 FAIL 확인'}")
    print("⚠️ 다양성·NCHI 절대수준은 formative 한계 → 종단 해석은 방향성 위주(06 §결과 R4).")
    print("=" * 64)


if __name__ == "__main__":
    main()
