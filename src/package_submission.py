"""제출 패키징 — PDF(분석·제안)와 ZIP(추가 산출물)을 분리 구성한다.

대회 제출 형식:
  * PDF: 자유 양식 15장 이내 분석 보고서 → submission/report.pdf
  * ZIP: 추가 산출물(노트북 32종·src·assets·원고·웹데모 소스·데이터 정보) → submission/kpf-submission-extra.zip

산출물 위치 규율:
  * dist/  = build_report.py의 재생성 중간 산출(html·pdf). .gitignore로 저장소에서 제외.
  * submission/ = 확정 제출본(pdf·zip). **저장소가 추적**하므로 어느 체크아웃에서 열어도 최신 산출이 보인다.
  본 스크립트가 dist/의 최신 산출을 게이트 통과 후 submission/으로 승격(복사)한다.

사용: python src/build_report.py && python src/package_submission.py
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SUBMIT = ROOT / "submission"
ZIP_PATH = SUBMIT / "kpf-submission-extra.zip"
PDF_SRC = DIST / "report.pdf"
PDF_OUT = SUBMIT / "report.pdf"
MAX_PAGES = 15

# ZIP 포함 대상 — (아카이브 경로, 원본 경로). 디렉토리는 재귀 포함.
INCLUDE: list[tuple[str, Path]] = [
    ("README-SUBMISSION.md", ROOT / "docs" / "submission-readme.md"),
    ("report.html", DIST / "report.html"),
    ("notebooks", ROOT / "notebooks"),
    ("src", ROOT / "src"),
    ("assets", ROOT / "assets"),
    ("docs/report", ROOT / "docs" / "report"),
    ("web", ROOT / "web"),
    ("data/README.md", ROOT / "data" / "README.md"),
    ("data/raw/README.md", ROOT / "data" / "raw" / "README.md"),
    ("data/raw/INVENTORY.md", ROOT / "data" / "raw" / "INVENTORY.md"),
    ("data/raw/DOWNLOAD-GUIDE.md", ROOT / "data" / "raw" / "DOWNLOAD-GUIDE.md"),
    ("requirements.txt", ROOT / "requirements.txt"),
    ("PROJECT-README.md", ROOT / "README.md"),
]

# 재현에 불필요하거나 용량만 차지하는 항목(빌드 캐시·의존성 설치본 등)
EXCLUDE_DIRS = {"node_modules", ".next", "out", "__pycache__", ".ipynb_checkpoints"}
EXCLUDE_FILES = {".gitkeep", ".DS_Store"}


def gate_pdf() -> int:
    """PDF 제출물 게이트 — 존재·쪽수(≤15)·그림 내장 확인 후 submission/으로 승격."""
    from pypdf import PdfReader

    assert PDF_SRC.exists(), "dist/report.pdf 없음 — 먼저 python src/build_report.py 실행"
    reader = PdfReader(str(PDF_SRC))
    n_pages = len(reader.pages)
    n_images = sum(len(p.images) for p in reader.pages)
    assert n_pages <= MAX_PAGES, f"쪽수 게이트 위반: {n_pages}p > {MAX_PAGES}p"
    assert n_images >= 10, f"그림 내장 수 이상: {n_images} < 10"
    SUBMIT.mkdir(exist_ok=True)
    shutil.copy2(PDF_SRC, PDF_OUT)
    print(f"[PDF] report.pdf {n_pages}p ≤ {MAX_PAGES}p · 이미지 {n_images} · "
          f"{PDF_OUT.stat().st_size/1024:.0f}KB → {PDF_OUT.relative_to(ROOT)} — PASS")
    return n_pages


def iter_files(arc_base: str, src: Path):
    if src.is_file():
        yield arc_base, src
        return
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(src)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or p.name in EXCLUDE_FILES:
            continue
        yield f"{arc_base}/{rel.as_posix()}", p


def build_zip() -> None:
    SUBMIT.mkdir(exist_ok=True)
    n = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc_base, src in INCLUDE:
            assert src.exists(), f"포함 대상 없음: {src}"
            for arc, p in iter_files(arc_base, src):
                zf.write(p, arc)
                n += 1
    mb = ZIP_PATH.stat().st_size / 1024 / 1024
    print(f"[ZIP] {ZIP_PATH.relative_to(ROOT)} — 파일 {n}개 · {mb:.1f}MB")
    # 필수 항목 봉인 — 노트북 32종 + 루트 README + 사양 json
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        nb = [x for x in names if x.startswith("notebooks/") and x.endswith(".ipynb")]
        assert len(nb) == 32, f"노트북 수 이상: {len(nb)} ≠ 32"
        for must in ["README-SUBMISSION.md", "report.html", "web/diagnosis-spec.json",
                     "docs/report/manuscript.md", "data/raw/DOWNLOAD-GUIDE.md"]:
            assert must in names, f"필수 항목 누락: {must}"
        assert not any("node_modules" in x for x in names)
    print(f"[ZIP] 게이트: 노트북 32종·필수 5항목 포함·node_modules 제외 — PASS")


if __name__ == "__main__":
    gate_pdf()
    build_zip()
    print("\n제출물 2종 준비 완료 — submission/report.pdf + submission/kpf-submission-extra.zip")
    sys.exit(0)
