"""7개년(2019~2025) 언론수용자 조사 하모나이즈 데이터셋 빌드 (P3 Data Preparation).

목적: `docs/design/variable-crosswalk.md` **v0.2** §3 재코딩 규칙을 **코드(SSOT)** 로 구현해,
  반복횡단면(repeated cross-section) 통합분석(EDA·MGCFA·모델링)의 입력 패널을 산출한다.

핵심 처리(crosswalk v0.2 + groundwork/05-research-harmonization.md 근거):
  1. 7개년 .sav 로더 — 인코딩 fallback(euc-kr↔utf-8) + 가중치 변수명(wt1/WT/HMWT) → 표준 `WT` 통일.
  2. target_var 생성 — 핵심 3군(매체이용·신뢰·인구) crosswalk §3 매핑대로:
     trust_news_overall/_used/_society, media_main_route, sex, age, edu(5→4단계),
     income(밴드 통일), job, region(2019 코드 리맵).
  3. 특수코드 결측 — **변수별** 처리(income 10=소득없음→NA, route 비이용→NA, trust 1~5 외→NA).
     ⚠️ job 9997=기타는 '결측'이 아닌 실범주 → 기타(13)로 통일(블랭킷 NA 금지).
  4. 연도 더미 + 2022 표본지배 보정 — 연도기여 균등화 가중치(05 §6 방법1).
  5. 산출 — data/processed/audience_harmonized.parquet + 연도×target 존재행렬 요약.

설계 근거: docs/design/variable-crosswalk.md §3·§5, analysis-master-plan.md §3(P3),
  docs/groundwork/05-research-harmonization.md §6(가중치 정규화).

실행: python src/harmonize.py
의존: pyreadstat, pandas, numpy, pyarrow.
재현성: .sav가 git에 포함되므로 본 스크립트로 산출물 전부 재생성 가능(processed/는 gitignore).

⚠️ 2019 신뢰 3종은 '부재'(NA) 처리 → 신뢰 시계열은 2020~2025만 유효(crosswalk §5-1).
⚠️ 분석 수치는 KPF 원자료 재검증·측정 비동등 검정 전 보고서/웹데모 직접 인용 금지.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data/raw/audience"
OUT_PARQUET = ROOT / "data/processed/audience_harmonized.parquet"
OUT_PRESENCE = ROOT / "data/processed/_presence_matrix.csv"

YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
T = len(YEARS)  # 연도 수(가중치 균등화 분모)

# 연도별 .sav 경로. 2022는 분석단위=개인 → 개인용 사용.
SAV_BY_YEAR: dict[int, Path] = {
    2019: AUD / "2019/2019_언론수용자조사_데이터.sav",
    2020: AUD / "2020/2020_언론수용자조사_데이터.sav",
    2021: AUD / "2021/2021_언론수용자조사_데이터.sav",
    2022: AUD / "2022/2022_언론수용자조사_개인용_데이터.sav",
    2023: AUD / "2023/2023_언론수용자조사_데이터.sav",
    2024: AUD / "2024/2024_언론수용자조사_데이터.sav",
    2025: AUD / "2025/2025_언론수용자조사_데이터.sav",
}

# 인코딩 혼재(euc-kr: 19·20·23·24·25 / utf-8: 21·22) → 순차 시도.
ENCODINGS = ["euc-kr", "utf-8"]

# 가중치 변수명 통일: 연도별 1순위 변수(2019는 wt1 사용, wt2는 보조).
WEIGHT_BY_YEAR: dict[int, str] = {
    2019: "wt1", 2020: "WT", 2021: "WT", 2022: "WT",
    2023: "HMWT", 2024: "WT", 2025: "WT",
}

# crosswalk v0.2 §3: target_var → 연도별 src_varname (None=부재).
SRC: dict[str, dict[int, str | None]] = {
    "trust_news_overall": {2019: None, 2020: "Q79_10", 2021: "Q81_10", 2022: "Q72_10",
                           2023: "Q79_1", 2024: "Q79_1", 2025: "Q87_1"},
    "trust_news_used": {2019: None, 2020: None, 2021: "Q82", 2022: "Q73",
                        2023: "Q79_2", 2024: "Q79_2", 2025: "Q87_2"},
    "trust_society": {2019: None, 2020: "BQ8", 2021: "Q91", 2022: "Q82",
                      2023: "Q91", 2024: "Q88", 2025: "Q96"},
    "media_main_route": {2019: "Q1", 2020: "Q1", 2021: "Q1", 2022: "Q68",
                         2023: "Q76", 2024: "Q76", 2025: "Q84"},
    "sex": {2019: "SQ3", 2020: "SQ3", 2021: "SQ3", 2022: "DQ2",
            2023: "DQ2", 2024: "DQ2", 2025: "DQ2"},
    "age": {2019: "SQ4", 2020: "SQ4", 2021: "SQ4", 2022: "DQ3",
            2023: "DQ3", 2024: "DQ3", 2025: "DQ3"},
    "edu": {2019: "DQ3", 2020: "BQ3", 2021: "BQ3", 2022: "BQ1",
            2023: "BQ3", 2024: "BQ3", 2025: "BQ3"},
    "income": {2019: "DQ5", 2020: "BQ5", 2021: "BQ5", 2022: "BA25",
               2023: "BQ5", 2024: "BQ5", 2025: "BQ5"},
    "job": {2019: "DQ4", 2020: "BQ4", 2021: "BQ4", 2022: "BQ2",
            2023: "BQ4", 2024: "BQ4", 2025: "BQ4"},
    "region": {2019: "SQ1", 2020: "SQ1", 2021: "SQ1", 2022: "SQ1",
               2023: "SQ1", 2024: "SQ1", 2025: "SQ1"},
}

# edu: 2019~2021은 5단계(초등이하/중/고/대/대학원) → 4단계로 재코딩(crosswalk §3.6).
EDU_5CAT_YEARS = {2019, 2020, 2021}
EDU_RECODE_5TO4 = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}  # {초등,중}→중졸이하, 고→2, 대→3, 대학원→4

# income: 10밴드 연도(2019~2021)는 10=소득없음→NA. 2022는 7밴드(BA25), 그 외 9밴드.
INCOME_10BAND_YEARS = {2019, 2020, 2021}  # 1~9 유효 + 10=소득없음
INCOME_2022_7BAND = 2022                  # BA25 1~7 (7=600만+)
# 9밴드 → 7밴드 통일(2022 포함 7개년 비교): {7,8,9}→7.
INCOME_9TO7 = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 7, 9: 7}

# region: 2019 SQ1은 행정코드 → 1~17 순차 리맵(crosswalk §3.6). 2020~2025는 그대로.
REGION_2019_REMAP = {
    11: 1, 21: 2, 22: 3, 23: 4, 24: 5, 25: 6, 26: 7, 29: 8,
    31: 9, 32: 10, 33: 11, 34: 12, 35: 13, 36: 14, 37: 15, 38: 16, 39: 17,
}

# media_main_route: 연도별 '비이용/비해당' 코드 → NA(crosswalk §3.4 비교풀 대상 외).
ROUTE_NONUSE: dict[int, set[int]] = {
    2019: {9998}, 2020: {12}, 2021: {12}, 2022: {9998},
    2023: {13, 9998}, 2024: {13, 9998}, 2025: {9998},
}

# job: 9997=기타(실범주) → 13(기타)로 통일. 결측으로 처리하지 않음.
JOB_OTHER_CODE = 13

# 언론 신뢰성(credibility) 다지표 배터리 — MGCFA·정렬법 입력(variable-crosswalk-trust-battery.md).
# 문항: "우리나라 언론은 ~하다" 5점 동의척도(1~5). 문항 prefix는 연도마다 리셋.
# 핵심 3지표{공정·전문·정확}은 7개년 전부 존재 → 잠재 신뢰성 요인을 2019~2025로 검정 가능.
CRED_BATTERY: dict[str, dict[int, str | None]] = {
    # 형용사            2019      2020      2021      2022      2023      2024      2025
    "cred_fair":         {2019: "Q77_1", 2020: "Q78_1", 2021: "Q78_1", 2022: "Q69_1",
                          2023: "Q77_1", 2024: "Q77_1", 2025: "Q85_1"},  # 공정하다(7개년)
    "cred_professional": {2019: "Q77_2", 2020: "Q78_2", 2021: "Q78_2", 2022: "Q69_2",
                          2023: "Q77_2", 2024: "Q77_2", 2025: "Q85_2"},  # 전문적이다(7개년)
    "cred_accurate":     {2019: "Q77_3", 2020: "Q78_3", 2021: "Q78_3", 2022: "Q69_3",
                          2023: "Q77_3", 2024: "Q77_3", 2025: "Q85_3"},  # 정확하다(7개년)
    "cred_trustworthy":  {2019: "Q77_4", 2020: "Q78_4", 2021: "Q78_4", 2022: "Q69_4",
                          2023: None, 2024: None, 2025: None},           # 신뢰할수있다(2019~2022)
    "press_free":        {2019: "Q77_5", 2020: "Q78_5", 2021: "Q78_5", 2022: "Q69_5",
                          2023: "Q77_4", 2024: "Q77_4", 2025: "Q85_4"},  # 언론자유(별개 구성개념)
    "media_influence":   {2019: None, 2020: None, 2021: "Q78_6", 2022: "Q69_6",
                          2023: "Q77_5", 2024: "Q77_5", 2025: "Q85_5"},  # 영향력(2021~2025)
}
# credibility 요인 지표(배제: press_free=별개차원, media_influence=valence불일치).
CRED_FACTOR_CORE3 = ["cred_fair", "cred_professional", "cred_accurate"]   # 주 모형(2019~2025)
CRED_FACTOR_PLUS4 = CRED_FACTOR_CORE3 + ["cred_trustworthy"]              # 민감도(2019~2022)


def read_sav_any(path: Path) -> tuple[pd.DataFrame, object, str]:
    """인코딩을 순차 시도해 (df, meta, encoding)을 반환(extract_all_sav_meta.py와 동일 패턴)."""
    last_err: Exception | None = None
    for enc in ENCODINGS:
        try:
            df, meta = pyreadstat.read_sav(str(path), encoding=enc)
            return df, meta, enc
        except Exception as e:  # noqa: BLE001 — 인코딩/포맷 오류는 다음 인코딩으로 재시도
            last_err = e
    raise RuntimeError(f"{path.name}: 모든 인코딩 실패 → {last_err}")


def _num(series: pd.Series) -> pd.Series:
    """문자/혼합형도 숫자로 강제(비숫자→NaN)."""
    return pd.to_numeric(series, errors="coerce")


def recode_trust(s: pd.Series) -> pd.Series:
    """신뢰 5점 리커트: 1~5만 유효, 그 외(무응답·특수코드)→NA."""
    x = _num(s)
    return x.where(x.isin([1, 2, 3, 4, 5]))


def recode_sex(s: pd.Series) -> pd.Series:
    x = _num(s)
    return x.where(x.isin([1, 2]))


def recode_age(s: pd.Series) -> pd.Series:
    """연속 연령: 비현실 값(<=0, >=120: 999 등 특수코드)→NA."""
    x = _num(s)
    return x.where((x > 0) & (x < 120))


def recode_edu(s: pd.Series, year: int) -> pd.Series:
    """최종학력 → 목표 4단계(중졸이하/고졸/대재이상/대학원)."""
    x = _num(s)
    if year in EDU_5CAT_YEARS:
        return x.map(EDU_RECODE_5TO4)  # 5단계→4단계, 범위 외는 NaN
    return x.where(x.isin([1, 2, 3, 4]))  # 이미 4단계


def recode_income(s: pd.Series, year: int) -> tuple[pd.Series, pd.Series]:
    """가구소득 → (income_band9, income_band7).

    - income_band9: 100만 단위 9밴드(1~9). 2019~2021의 10=소득없음→NA.
        2022(BA25 7밴드)는 1~6만 9밴드에 배치, 7(600만+)은 9밴드로 분해 불가→NA.
    - income_band7: 7개년 공통 비교용. 9밴드의 {7,8,9}를 600만+(7)로 통합, 2022는 원래 7밴드.
    """
    x = _num(s)
    if year == INCOME_2022_7BAND:
        b7 = x.where(x.isin([1, 2, 3, 4, 5, 6, 7]))
        b9 = x.where(x.isin([1, 2, 3, 4, 5, 6]))  # 7(600만+)은 9밴드 분해 불가
        return b9, b7
    # 9밴드 체계(2019~2021은 10=소득없음 존재)
    b9 = x.where(x.isin([1, 2, 3, 4, 5, 6, 7, 8, 9]))  # 10 및 그 외 → NA
    b7 = b9.map(INCOME_9TO7)
    return b9, b7


def recode_job(s: pd.Series) -> pd.Series:
    """직업(명목): 9997=기타→13 통일. 1~13만 유효(세부 21·22 등 잔여코드→NA).

    ⚠️ 직업 코드체계는 2019(DQ4)와 2020+(BQ4)가 세부 분류가 달라 equiv=conceptual(2019).
    추세·세그먼트 사용 시 광역 그룹 재집계 권장(crosswalk §3.6).
    """
    x = _num(s).replace({9997: JOB_OTHER_CODE})
    return x.where(x.between(1, 13))


def recode_region(s: pd.Series, year: int) -> pd.Series:
    """거주지역(시도, 1~17). 2019만 행정코드→순차 리맵."""
    x = _num(s)
    if year == 2019:
        return x.map(REGION_2019_REMAP)
    return x.where(x.between(1, 17))


def recode_route(s: pd.Series, year: int, value_labels: dict | None) -> tuple[pd.Series, pd.Series]:
    """뉴스 주 이용경로 → (코드, 디코드 라벨). 비이용/비해당 코드→NA.

    범주 체계가 연도별로 증식(2025=17범주)하므로 P3에서는 **무손실 보존**(코드+라벨)하고,
    7개년 비교 가능한 고정 풀 + 유효종수 e^H 변환은 P4 다양성지수에서 수행(crosswalk §3.4).
    """
    x = _num(s)
    nonuse = ROUTE_NONUSE.get(year, set())
    code = x.where(~x.isin(list(nonuse)))
    # 값레이블 디코드(인코딩은 read_sav에서 처리되어 라벨은 정상 한글). 키는 float일 수 있어 정규화.
    lab_map: dict[int, str] = {}
    if value_labels:
        for k, v in value_labels.items():
            try:
                lab_map[int(float(k))] = str(v)
            except (TypeError, ValueError):
                continue
    label = code.map(lab_map)
    return code, label


def build_year(year: int) -> pd.DataFrame:
    """단일 연도 .sav를 읽어 target_var DataFrame(표준 스키마)으로 변환."""
    path = SAV_BY_YEAR[year]
    df, meta, enc = read_sav_any(path)
    n = len(df)
    vmap = SRC

    def col(target: str) -> pd.Series:
        """해당 연도의 src_varname 컬럼을 가져오되, 부재(None/누락) 시 전부 NA."""
        src = vmap[target][year]
        if src is None or src not in df.columns:
            return pd.Series([np.nan] * n, index=df.index)
        return df[src]

    out = pd.DataFrame(index=df.index)
    out["year"] = year
    out["resp_id"] = [f"{year}_{i}" for i in range(n)]

    # 가중치: 표준 WT 통일(없으면 1.0).
    wname = WEIGHT_BY_YEAR[year]
    out["wt"] = _num(df[wname]) if wname in df.columns else 1.0

    # 인구통계
    out["sex"] = recode_sex(col("sex"))
    out["age"] = recode_age(col("age"))
    out["edu"] = recode_edu(col("edu"), year)
    b9, b7 = recode_income(col("income"), year)
    out["income_band9"] = b9
    out["income_band7"] = b7
    out["job"] = recode_job(col("job"))
    out["region"] = recode_region(col("region"), year)

    # 신뢰 3종(2019 전부 NA, 2020 trust_news_used도 NA)
    out["trust_news_overall"] = recode_trust(col("trust_news_overall"))
    out["trust_news_used"] = recode_trust(col("trust_news_used"))
    out["trust_society"] = recode_trust(col("trust_society"))

    # 언론 신뢰성(credibility) 다지표 배터리 — MGCFA 입력(5점, 1~5만 유효).
    # 핵심 3지표{공정·전문·정확}은 7개년 전부, 신뢰=2019~2022, 영향력=2021~2025만 존재.
    for ind, ymap in CRED_BATTERY.items():
        src = ymap[year]
        s = df[src] if (src and src in df.columns) else pd.Series([np.nan] * n, index=df.index)
        out[ind] = recode_trust(s)

    # 매체 주이용경로(코드+라벨)
    rsrc = vmap["media_main_route"][year]
    rvl = meta.variable_value_labels.get(rsrc) if rsrc else None
    rcode, rlabel = recode_route(col("media_main_route"), year, rvl)
    out["media_main_route_code"] = rcode
    out["media_main_route"] = rlabel

    # 파생: 출생 코호트(조사연도 - 만나이)
    out["birth_cohort"] = (year - out["age"]).round()

    print(f"OK {year}: N={n:,} enc={enc} wt={wname}"
          f" | trust_overall_valid={out['trust_news_overall'].notna().sum():,}"
          f" income9_valid={out['income_band9'].notna().sum():,}")
    return out


def add_weight_normalization(panel: pd.DataFrame) -> pd.DataFrame:
    """가중치 정규화 2종 추가(05 §6, 2022 표본지배 보정).

    - wt_within: 연도 내 평균=1 정규화(상대가중 보존, 스케일 제거). w*(n_t/Σw_t).
    - wt_year_eq: **연도기여 균등화** — 각 연도가 전체에서 1/T씩 기여하도록.
        Σ_i wt_year_eq(연도 t) = N_total/T (상수) → 2022 N=58,936 지배 제거.
        wt_year_eq = (w_it / Σ_i w_it) × (N_total / T).
    """
    n_total = len(panel)
    panel = panel.copy()
    panel["wt"] = panel["wt"].fillna(1.0)
    grp = panel.groupby("year")["wt"]
    sum_w = grp.transform("sum")
    cnt = grp.transform("count")
    panel["wt_within"] = panel["wt"] * cnt / sum_w
    panel["wt_year_eq"] = (panel["wt"] / sum_w) * (n_total / T)
    return panel


def add_year_dummies(panel: pd.DataFrame) -> pd.DataFrame:
    """연도 더미(yr_2019..yr_2025) + 2022 식별 플래그(추세회귀 통제용, 05 §6)."""
    panel = panel.copy()
    for y in YEARS:
        panel[f"yr_{y}"] = (panel["year"] == y).astype("int8")
    panel["is_2022"] = (panel["year"] == 2022).astype("int8")
    return panel


def presence_matrix(panel: pd.DataFrame) -> pd.DataFrame:
    """연도×target 유효(non-NA)응답 수 행렬."""
    targets = [
        "sex", "age", "edu", "income_band9", "income_band7", "job", "region",
        "trust_news_overall", "trust_news_used", "trust_society",
        "media_main_route_code",
        "cred_fair", "cred_professional", "cred_accurate",
        "cred_trustworthy", "press_free", "media_influence",
    ]
    rows = []
    for y in YEARS:
        sub = panel[panel["year"] == y]
        row = {"year": y, "N": len(sub)}
        for t in targets:
            row[t] = int(sub[t].notna().sum())
        rows.append(row)
    return pd.DataFrame(rows).set_index("year")


def main() -> None:
    frames = [build_year(y) for y in YEARS]
    panel = pd.concat(frames, ignore_index=True)
    panel = add_weight_normalization(panel)
    panel = add_year_dummies(panel)

    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(OUT_PARQUET, index=False)

    pm = presence_matrix(panel)
    pm.to_csv(OUT_PRESENCE, encoding="utf-8-sig")

    # ── 콘솔 요약 ─────────────────────────────────────────────
    print("\n" + "=" * 64)
    print(f"하모나이즈 패널 산출 완료: {OUT_PARQUET.relative_to(ROOT)}")
    print(f"  총 행수: {len(panel):,}  컬럼수: {panel.shape[1]}")
    print(f"  연도별 N: " + ", ".join(f"{y}={int((panel['year']==y).sum()):,}" for y in YEARS))

    print("\n[연도×target 존재행렬 — 유효(non-NA) 응답 수]")
    print(pm.to_string())

    print("\n[가중치 정규화 검증 — 연도별 합계]")
    chk = panel.groupby("year")[["wt", "wt_within", "wt_year_eq"]].sum().round(1)
    print(chk.to_string())
    print(f"  → wt_year_eq 연도합 목표(N/T={len(panel)/T:,.1f})로 균등 = 2022 지배 제거 확인")

    print("\n[핵심 범주 분포 검증]")
    for col_name in ["edu", "income_band7", "region", "sex"]:
        vc = panel[col_name].value_counts(dropna=False).sort_index()
        print(f"  {col_name}: {dict(vc)}")

    print("\n[신뢰 시계열 유효성 — 2019 부재 확인]")
    for tcol in ["trust_news_overall", "trust_news_used", "trust_society"]:
        by = panel.groupby("year")[tcol].apply(lambda s: int(s.notna().sum()))
        print(f"  {tcol}: " + ", ".join(f"{y}={by[y]:,}" for y in YEARS))

    print("\n[credibility 배터리 가용성 — 핵심3지표는 7개년 전부 존재 확인]")
    for ind in CRED_BATTERY:
        by = panel.groupby("year")[ind].apply(lambda s: int(s.notna().sum()))
        mark = "(핵심)" if ind in CRED_FACTOR_CORE3 else ""
        print(f"  {ind:18s}{mark:5s}: " + ", ".join(f"{y}={by[y]:,}" for y in YEARS))
    cov = panel[CRED_FACTOR_CORE3].notna().all(axis=1).groupby(panel["year"]).sum()
    print("  → 핵심3지표 동시 응답(완전케이스): "
          + ", ".join(f"{y}={int(cov[y]):,}" for y in YEARS))

    print("=" * 64)


if __name__ == "__main__":
    main()
