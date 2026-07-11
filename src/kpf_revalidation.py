# -*- coding: utf-8 -*-
"""KPF 원자료 재검증 1순위 — 신뢰 절대수준 + 2019→2020 계단 진단.

data-spec.md §6 검증 게이트 해소용. harmonize.py를 SSOT로 import(재구현 금지)하여
.sav 원자료에서 **원척도(5점)·연도별 공식가중(WT)** 수치를 산출한다.

산출(비교 대상):
  A. 연도별 신뢰 절대수준 — trust_news_overall(단일문항)·cred 핵심3지표·cred_mean의
     가중평균(원척도) + '신뢰한다'(4~5점) 가중비율. → KPF 보고서 통계표와 대조.
  B. 2019→2020 계단 진단 — 문항 라벨(워딩)·값 라벨(척도) 원문 대조,
     문항별 응답분포(1~5 가중 구성비) 변화, 2019 wt1↔wt2 가중치 민감도.
  C. 파이프라인 재현 대조 — cred_mean 연도 가중평균이 eda-overview §1-③의
     3.034→3.249→3.305→3.211→3.190→3.176→3.390과 일치하는지 assert.
     (wt_year_eq는 WT의 연도내 상수배 → 연도내 가중평균은 WT와 동일해야 함)

실행: python src/kpf_revalidation.py
출력: data/interim/revalidation/*.csv (gitignore, 재생성물) + stdout 리포트.
결과 문서(SSOT): docs/design/kpf-revalidation.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harmonize import (  # noqa: E402 — SSOT import(재구현 금지)
    CRED_BATTERY,
    CRED_FACTOR_CORE3,
    SAV_BY_YEAR,
    SRC,
    WEIGHT_BY_YEAR,
    YEARS,
    _num,
    read_sav_any,
    recode_trust,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/interim/revalidation"

# eda-overview.md §1-③ cred_mean 연도 가중평균(파이프라인 산출, 재현 대조 기준값).
PIPELINE_CRED_MEAN = {
    2019: 3.034, 2020: 3.249, 2021: 3.305, 2022: 3.211,
    2023: 3.190, 2024: 3.176, 2025: 3.390,
}


def wmean(x: pd.Series, w: pd.Series) -> float:
    """유효응답만으로 가중평균(결측은 가중치에서도 제외)."""
    m = x.notna() & w.notna()
    if m.sum() == 0:
        return np.nan
    return float(np.average(x[m], weights=w[m]))


def wshare_45(x: pd.Series, w: pd.Series) -> float:
    """'신뢰한다'(4~5점) 가중비율(%) — KPF 보도자료의 '신뢰 비율' 정의와 동일 형식."""
    m = x.notna() & w.notna()
    if m.sum() == 0:
        return np.nan
    return float(np.average((x[m] >= 4).astype(float), weights=w[m]) * 100)


def wdist(x: pd.Series, w: pd.Series) -> dict[int, float]:
    """1~5 각 응답의 가중 구성비(%)."""
    m = x.notna() & w.notna()
    tot = w[m].sum()
    return {k: float(w[m & (x == k)].sum() / tot * 100) for k in [1, 2, 3, 4, 5]}


def load_year(year: int):
    """원자료 로드 + 공식가중치·재검증 대상 변수만 추출."""
    df, meta, enc = read_sav_any(SAV_BY_YEAR[year])
    wt = _num(df[WEIGHT_BY_YEAR[year]])
    return df, meta, enc, wt


def section_a_levels() -> pd.DataFrame:
    """A. 연도별 신뢰 절대수준(원척도·공식 WT 가중)."""
    rows = []
    for year in YEARS:
        df, _, _, wt = load_year(year)
        row: dict = {"year": year, "N": len(df)}
        # 단일문항: 언론 전반 신뢰(trust_news_overall)
        src = SRC["trust_news_overall"][year]
        if src is not None:
            x = recode_trust(df[src])
            row["overall_src"] = src
            row["overall_mean_wt"] = round(wmean(x, wt), 3)
            row["overall_mean_unw"] = round(float(x.mean()), 3)
            row["overall_pct45_wt"] = round(wshare_45(x, wt), 1)
        # credibility 핵심3지표 + cred_mean
        cred = {}
        for ind in CRED_FACTOR_CORE3:
            x = recode_trust(df[CRED_BATTERY[ind][year]])
            cred[ind] = x
            row[f"{ind}_mean_wt"] = round(wmean(x, wt), 3)
        cred_mean = pd.concat(cred.values(), axis=1).mean(axis=1)
        row["cred_mean_wt"] = round(wmean(cred_mean, wt), 3)
        row["cred_pct45_wt"] = round(wshare_45(cred_mean.round(), wt), 1)
        rows.append(row)
    return pd.DataFrame(rows)


def section_b_step() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """B. 2019→2020 계단 진단 — 라벨 원문·응답분포·가중치 민감도."""
    labels_rows, dist_rows, notes = [], [], []
    for year in (2019, 2020):
        df, meta, enc, wt = load_year(year)
        lab = meta.column_names_to_labels
        vlab = meta.variable_value_labels
        for ind in CRED_FACTOR_CORE3 + ["cred_trustworthy", "press_free"]:
            var = CRED_BATTERY[ind][year]
            if var is None:
                continue
            labels_rows.append({
                "year": year, "indicator": ind, "var": var,
                "question_label": lab.get(var, ""),
                "value_labels": str(vlab.get(var, "")),
            })
            x = recode_trust(df[var])
            d = wdist(x, wt)
            dist_rows.append({"year": year, "indicator": ind, "var": var,
                              "mean_wt": round(wmean(x, wt), 3),
                              **{f"p{k}": round(v, 1) for k, v in d.items()}})
        # 2019 가중치 민감도: wt1(주) vs wt2(보조)
        if year == 2019 and "wt2" in df.columns:
            wt2 = _num(df["wt2"])
            for ind in CRED_FACTOR_CORE3:
                x = recode_trust(df[CRED_BATTERY[ind][2019]])
                notes.append(
                    f"2019 {ind}: wt1 가중평균={wmean(x, wt):.3f} / "
                    f"wt2 가중평균={wmean(x, wt2):.3f} / 비가중={float(x.mean()):.3f}"
                )
    return pd.DataFrame(labels_rows), pd.DataFrame(dist_rows), notes


def section_c_reproduce(levels: pd.DataFrame) -> list[str]:
    """C. 파이프라인 cred_mean 재현 대조(±0.001)."""
    msgs = []
    for year in YEARS:
        got = float(levels.loc[levels["year"] == year, "cred_mean_wt"].iloc[0])
        exp = PIPELINE_CRED_MEAN[year]
        ok = abs(got - exp) <= 0.001
        msgs.append(f"{year}: 재검증 {got:.3f} vs 파이프라인 {exp:.3f} → {'PASS' if ok else 'FAIL'}")
        assert ok, f"cred_mean 재현 불일치 {year}: {got:.3f} != {exp:.3f}"
    return msgs


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("A. 연도별 신뢰 절대수준 (원척도 5점, 연도별 공식 WT 가중)")
    print("=" * 72)
    levels = section_a_levels()
    print(levels.to_string(index=False))
    levels.to_csv(OUT_DIR / "trust_levels_by_year.csv", index=False, encoding="utf-8-sig")

    print()
    print("=" * 72)
    print("B. 2019→2020 계단 진단 (문항 라벨·응답분포·가중치 민감도)")
    print("=" * 72)
    labels, dists, notes = section_b_step()
    print("--- 문항·값 라벨 원문 ---")
    print(labels.to_string(index=False))
    print("--- 응답분포(1~5 가중 %) ---")
    print(dists.to_string(index=False))
    print("--- 2019 가중치 민감도 ---")
    for n in notes:
        print(" ", n)
    labels.to_csv(OUT_DIR / "step_2019_2020_labels.csv", index=False, encoding="utf-8-sig")
    dists.to_csv(OUT_DIR / "step_2019_2020_dists.csv", index=False, encoding="utf-8-sig")

    print()
    print("=" * 72)
    print("C. 파이프라인 cred_mean 재현 대조 (eda-overview §1-③, ±0.001)")
    print("=" * 72)
    for m in section_c_reproduce(levels):
        print(" ", m)

    print()
    print(f"[완료] CSV 산출 → {OUT_DIR}")


if __name__ == "__main__":
    main()
