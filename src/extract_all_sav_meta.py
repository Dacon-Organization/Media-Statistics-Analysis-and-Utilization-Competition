"""7개년(2019~2025) 언론수용자 조사 .sav 메타데이터 일괄 추출 스크립트.

목적: P2 Data Understanding의 **변수 카탈로그 + Crosswalk 후보** 근거 생성.
  - 전체 메타: data/interim/_all_sav_meta.json (gitignore, 재생성용)
  - 사람용 카탈로그: docs/design/sav-meta-catalog.md (tracked)
    · 연도별 프로파일(N·변수수·인코딩·가중치 변수)
    · 3핵심군(신뢰·매체이용/다양성·인구통계) 레이블 키워드 후보 변수
  → 이 산출물이 docs/design/variable-crosswalk.md 초안의 데이터 근거.

설계 근거: docs/groundwork/05-research-harmonization.md §1~2
  (보수적 수작업 매핑 + 자동 후보탐색 보조), analysis-master-plan.md §1.1.

실행: python src/extract_all_sav_meta.py
의존: pyreadstat (conda-forge), 파이썬 3.x.
재현성: .sav가 git에 포함되므로 본 스크립트로 산출물 전부 재생성 가능.
주의: 후보 스캔은 **스크리닝(screening)** 용도일 뿐, 최종 매핑은 코드북 대조 수작업으로 확정한다.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data/raw/audience"
META_JSON = ROOT / "data/interim/_all_sav_meta.json"
CATALOG_MD = ROOT / "docs/design/sav-meta-catalog.md"

# 연도별 .sav 경로. 2022는 분석단위=개인 → 개인용 사용(가구용은 보조).
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

# 가중치 변수명 4종(wt1/wt2·WT·HMWT) → 표준 'WT'로 통일 매핑 대상.
WEIGHT_CANDIDATES = {"wt1", "wt2", "WT", "HMWT", "wt", "hmwt"}

# 3핵심군 후보 스캔 키워드(레이블 텍스트 부분일치). screening 전용.
CONSTRUCT_KEYWORDS: dict[str, list[str]] = {
    "신뢰·언론인식": ["신뢰", "공정", "전문적", "정확", "언론활동이 자유", "오보", "낚시", "허위조작", "가짜뉴스"],
    "매체이용·다양성": ["이용 여부", "시청 여부", "청취 여부", "주 이용 경로", "이용일수", "이용 빈도", "이용한 적"],
    "인구통계": ["성별", "연령", "최종학력", "가구소득", "본인직업", "거주지역", "정치성향", "주관적 계층"],
}


def read_sav_any(path: Path) -> tuple:
    """인코딩을 순차 시도해 (df, meta, encoding)을 반환. 모두 실패 시 마지막 예외 전파."""
    last_err: Exception | None = None
    for enc in ENCODINGS:
        try:
            df, meta = pyreadstat.read_sav(str(path), encoding=enc)
            return df, meta, enc
        except Exception as e:  # noqa: BLE001 — 인코딩 오류 외 포맷 오류도 다음 인코딩으로 재시도
            last_err = e
    raise RuntimeError(f"{path.name}: 모든 인코딩 실패 → {last_err}")


def detect_weight(names: list[str]) -> list[str]:
    """가중치 후보 변수명을 데이터에 존재하는 것만 추려 반환."""
    return [n for n in names if n in WEIGHT_CANDIDATES]


def fmt_value_labels(vl: dict | None, limit: int = 6) -> str:
    """값레이블을 '1=남성; 2=여성' 형태로. 범주 과다 시 앞 limit개만."""
    if not vl:
        return ""
    parts = []
    for k, v in list(vl.items())[:limit]:
        try:
            k = int(float(k))
        except (TypeError, ValueError):
            pass
        parts.append(f"{k}={v}")
    more = "; …" if len(vl) > limit else ""
    return " || " + "; ".join(parts) + more


def scan_candidates(vars_list: list[dict]) -> dict[str, list[dict]]:
    """레이블 키워드 부분일치로 구성개념별 후보 변수를 수집한다(중복 허용 없음)."""
    out: dict[str, list[dict]] = {k: [] for k in CONSTRUCT_KEYWORDS}
    for v in vars_list:
        label = v.get("label") or ""
        for construct, kws in CONSTRUCT_KEYWORDS.items():
            if any(kw in label for kw in kws):
                out[construct].append(v)
                break  # 한 변수는 가장 먼저 매칭된 군에만 귀속
    return out


def main() -> None:
    full: dict = {"years": {}}
    for year, path in SAV_BY_YEAR.items():
        if not path.exists():
            print(f"WARN: {year} 파일 없음 → 건너뜀 ({path})")
            continue
        df, meta, enc = read_sav_any(path)
        names = list(df.columns)
        vars_list = [
            {
                "name": c,
                "label": meta.column_names_to_labels.get(c),
                "value_labels": meta.variable_value_labels.get(c),
            }
            for c in names
        ]
        full["years"][str(year)] = {
            "path": str(path.relative_to(ROOT)),
            "shape": list(df.shape),
            "encoding": enc,
            "weight_vars": detect_weight(names),
            "vars": vars_list,
        }
        print(f"OK {year}: {df.shape} enc={enc} wt={detect_weight(names)}")

    # 1) 전체 메타 JSON (재생성용, gitignore)
    META_JSON.parent.mkdir(parents=True, exist_ok=True)
    with io.open(META_JSON, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=1)

    # 2) 사람용 카탈로그 (tracked)
    L: list[str] = []
    L.append("# 7개년 .sav 메타 카탈로그 (자동 추출)")
    L.append("")
    L.append("> 생성: `src/extract_all_sav_meta.py` · **수정 금지(스크립트로 재생성)**.")
    L.append("> 용도: [`variable-crosswalk.md`](variable-crosswalk.md) 후보 매칭 근거. "
             "후보 스캔은 **스크리닝 전용** — 최종 매핑은 코드북 대조 수작업 확정.")
    L.append("> 설계 근거: [`../groundwork/05-research-harmonization.md`](../groundwork/05-research-harmonization.md) §1~2.")
    L.append("")

    # 2-1) 연도별 프로파일
    L.append("## 연도별 프로파일")
    L.append("")
    L.append("| 연도 | 표본 N | 변수 수 | 인코딩 | 가중치 변수 |")
    L.append("|:--:|:--:|:--:|:--:|:--|")
    for year in SAV_BY_YEAR:
        y = full["years"].get(str(year))
        if not y:
            L.append(f"| {year} | — | — | (없음) | — |")
            continue
        wt = ", ".join(f"`{w}`" for w in y["weight_vars"]) or "(미검출)"
        L.append(f"| {year} | {y['shape'][0]:,} | {y['shape'][1]} | {y['encoding']} | {wt} |")
    L.append("")

    # 2-2) 구성개념별 후보 변수(연도별)
    for construct in CONSTRUCT_KEYWORDS:
        L.append(f"## 후보 — {construct}")
        L.append(f"> 키워드: {', '.join(CONSTRUCT_KEYWORDS[construct])}")
        L.append("")
        for year in SAV_BY_YEAR:
            y = full["years"].get(str(year))
            if not y:
                continue
            cands = scan_candidates(y["vars"])[construct]
            L.append(f"### {year} ({len(cands)}개)")
            if not cands:
                L.append("(후보 없음)")
            else:
                for v in cands:
                    L.append(f"- `{v['name']}` :: {v['label']}{fmt_value_labels(v['value_labels'])}")
            L.append("")

    CATALOG_MD.write_text("\n".join(L), encoding="utf-8")
    n_years = len(full["years"])
    print(f"\nDONE: {META_JSON.name} ({n_years}개년), {CATALOG_MD.name}")


if __name__ == "__main__":
    main()
