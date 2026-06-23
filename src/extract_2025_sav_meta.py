"""2025 언론수용자 조사 .sav 메타데이터 추출 스크립트.

목적: `.sav` 원시자료에서 변수명·레이블·값레이블을 추출해
  - 전체 메타: data/interim/_2025_sav_meta.json (gitignore, 재생성용)
  - 핵심 변수 사람용 추출물: docs/design/2025-sav-variables.md (tracked, data-spec §5 근거)
를 생성한다.

실행: python src/extract_2025_sav_meta.py
의존: pyreadstat (conda-forge), 파이썬 3.x. 파일 인코딩 EUC-KR.
재현성: .sav가 git에 포함되므로 본 스크립트로 산출물 전부 재생성 가능.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
SAV = ROOT / "data/raw/audience/2025/2025_언론수용자조사_데이터.sav"
META_JSON = ROOT / "data/interim/_2025_sav_meta.json"
KEYVARS_MD = ROOT / "docs/design/2025-sav-variables.md"


def fmt_value_labels(vl: dict | None) -> str:
    """값레이블을 '1=남성; 2=여성' 형태 문자열로 정규화한다."""
    if not vl:
        return ""
    parts = []
    for k, v in vl.items():
        try:
            k = int(float(k))
        except (TypeError, ValueError):
            pass
        parts.append(f"{k}={v}")
    return " || " + "; ".join(parts)


def main() -> None:
    # 인코딩 자동 인식이 실패할 수 있어 euc-kr 명시
    df, meta = pyreadstat.read_sav(str(SAV), encoding="euc-kr")
    names = list(df.columns)

    # 1) 전체 메타 JSON (재생성용, gitignore)
    full = {
        "shape": list(df.shape),
        "file_encoding": meta.file_encoding,
        "vars": [
            {
                "name": c,
                "label": meta.column_names_to_labels.get(c),
                "value_labels": meta.variable_value_labels.get(c),
            }
            for c in names
        ],
    }
    META_JSON.parent.mkdir(parents=True, exist_ok=True)
    with io.open(META_JSON, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=1)

    # 2) 핵심 변수 사람용 추출물 (tracked)
    vars_by_name = {v["name"]: v for v in full["vars"]}

    def show(name: str) -> str:
        v = vars_by_name[name]
        return f"- `{name}` :: {v['label']}{fmt_value_labels(v['value_labels'])}"

    L: list[str] = []
    L.append("# 2025 언론수용자 조사 .sav 핵심 변수 (자동 추출)")
    L.append("")
    L.append(f"> 생성: `src/extract_2025_sav_meta.py` · 원본 `{SAV.name}` · "
             f"{full['shape'][0]}행 × {full['shape'][1]}변수 · 인코딩 {meta.file_encoding}")
    L.append("> data-spec.md §5의 근거 추출물. **수정 금지(스크립트로 재생성)**.")
    L.append("")

    def section(title: str, pred) -> None:
        L.append(f"## {title}")
        hits = [show(n) for n in names if pred(vars_by_name[n])]
        L.extend(hits or ["(없음)"])
        L.append("")

    section('[검색] "회피" 포함 변수', lambda v: v["label"] and "회피" in v["label"])
    section('[검색] "검증/팩트/확인" 포함 변수',
            lambda v: v["label"] and any(k in v["label"] for k in ["검증", "팩트", "확인"]))
    section("인구통계 (SQ/DQ/BQ/WT)",
            lambda v: v["name"] in ("ID", "SQ1", "DQ2", "DQ3", "WT") or v["name"].startswith("BQ"))
    section("다양성 — 주 이용경로·매체 게이트 (Q84 + 이용여부)",
            lambda v: v["name"] == "Q84"
            or (v["label"] and any(g in v["label"] for g in ["이용 여부", "시청 여부", "청취 여부"])))
    section("신뢰/인식 차원 (Q85~Q97)",
            lambda v: any(v["name"].startswith(p) for p in
                          ["Q85", "Q86", "Q87", "Q88", "Q91", "Q92", "Q93", "Q94", "Q95", "Q96", "Q97"]))
    section("검증습관 proxy (Q34/Q35/Q42/Q49/Q56/Q57)",
            lambda v: any(v["name"].startswith(p) for p in
                          ["Q34", "Q35", "Q42", "Q49", "Q56", "Q57"]))

    KEYVARS_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"OK: {META_JSON.name} ({full['shape']}), {KEYVARS_MD.name}")


if __name__ == "__main__":
    main()
