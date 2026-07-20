"""논문형 PDF 조판 — manuscript.md → HTML(논문형 CSS) → headless Chrome PDF (P6-B-3).

파이프라인(`docs/report/p6-pdf-structure.md` §6 B-3 확정안):
  1. `docs/report/manuscript.md`를 Python-Markdown(extra: tables·footnotes)으로 HTML 변환.
  2. 원고의 그림 캡션 단락("**그림 N (Fx).** … 경로.png")을 <figure> 블록으로 승격 —
     PNG는 base64로 HTML에 내장(자기완결 문서, 경로 의존 제거).
  3. 논문형 CSS(A4·바탕 세리프 본문·표/그림 break-inside 회피)를 입혀 `dist/report.html` 저장.
  4. headless Chrome `--print-to-pdf`로 `dist/report.pdf` 생성.
  5. pypdf로 쪽수 게이트(15p 이내) 검증 — 초과 시 종료코드 1.

수치 규율: 이 스크립트는 원고 내용을 생성·수정하지 않는다(조판 전용). 원고 수치의
  유일한 복사원은 p6-pdf-structure §3 표(§5 게이트)이며 본 스크립트 밖에서 관리된다.

실행: python src/build_report.py   (산출: dist/report.html · dist/report.pdf)
의존: markdown, pypdf(기설치) + 로컬 Chrome. 신규 파이썬 의존 없음.
"""
from __future__ import annotations

import base64
import re
import subprocess
import sys
from pathlib import Path

import markdown
from pypdf import PdfReader

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "docs" / "report" / "manuscript.md"
DIST = ROOT / "dist"
MAX_PAGES = 15  # 대회 규정: 자유 양식 PDF 15장 이내

CHROME_CANDIDATES = [
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
]

# 논문형 CSS — A4 단단(單段), 본문 세리프(바탕), 표·그림 쪽 분리 회피
CSS = """
@page { size: A4; margin: 21mm 19mm 23mm 19mm; }
html { -webkit-print-color-adjust: exact; }
body {
  font-family: 'Batang', '바탕', 'Noto Serif KR', serif;
  font-size: 10.2pt; line-height: 1.62; color: #1a1a1a;
  text-align: justify; word-break: keep-all; margin: 0;
}
h1, h2, h3, h4 { font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; line-height: 1.35; }
h1 { font-size: 15.5pt; text-align: center; margin: 0 0 4mm; }
h2 { font-size: 12pt; margin: 7mm 0 2.5mm; border-bottom: 1.2px solid #444; padding-bottom: 1mm;
     break-after: avoid; }
h3 { font-size: 10.8pt; margin: 4.5mm 0 1.8mm; break-after: avoid; }
p { margin: 0 0 2.2mm; }
blockquote { margin: 2mm 0 3mm; padding: 1.5mm 4mm; border-left: 2.5px solid #999;
             color: #444; font-size: 9.2pt; }
blockquote p { margin: 0.6mm 0; }
table { border-collapse: collapse; width: 100%; font-size: 8.6pt; margin: 2.5mm 0 3.5mm;
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; break-inside: avoid; }
th, td { border: 0.6px solid #888; padding: 1mm 1.8mm; vertical-align: top; text-align: left; }
th { background: #efefef; }
code { font-family: 'Consolas', monospace; font-size: 0.92em; background: #f3f3f3;
       padding: 0 0.35em; border-radius: 2px; }
pre { background: #f5f5f5; border: 0.6px solid #ccc; padding: 2mm 3mm; font-size: 8.6pt;
      break-inside: avoid; }
pre code { background: none; padding: 0; }
figure.fig { margin: 3.5mm 0 4mm; text-align: center; break-inside: avoid; }
figure.fig img { max-width: 100%; max-height: 95mm; }
figure.fig figcaption { font-size: 8.8pt; color: #333; text-align: justify; margin-top: 1.5mm;
                        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }
.footnote { font-size: 8.8pt; color: #333; }
.footnote hr { border: none; border-top: 1px solid #888; margin: 6mm 0 2mm; }
.footnote ol { padding-left: 5mm; }
.footnote li p { margin: 0 0 1.5mm; }
sup { line-height: 0; }
hr { border: none; border-top: 0.8px solid #bbb; margin: 5mm 0; }
a { color: inherit; text-decoration: none; }
strong { font-family: inherit; }
"""

# 주의: 캡션 매칭은 반드시 한 단락(</p> 이전) 안으로 한정한다 — 탐욕 매칭이 단락 경계를
# 넘으면 png 없는 표 캡션이 다음 그림 경로까지 삼켜 표·본문이 figcaption에 들어간다.
FIG_CAPTION_RE = re.compile(
    r"<p>(<strong>(?:그림|표)\s*\d+[^<]*</strong>(?:(?!</p>).)*?)"
    r"<code>([^<]+?\.png)</code>((?:(?!</p>).)*?)</p>",
    re.DOTALL,
)


def _find_chrome() -> Path:
    for p in CHROME_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit("Chrome을 찾을 수 없습니다 — CHROME_CANDIDATES 확인")


def _b64_img(rel_path: str) -> str:
    """레포 루트 기준 상대경로 PNG → data URI(base64). 없으면 실패(조판 중단)."""
    f = ROOT / rel_path.strip()
    if not f.exists():
        raise SystemExit(f"그림 파일 없음: {rel_path} — export 먼저 실행(src/export_figures.py 등)")
    return "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()


def _promote_figures(html: str) -> tuple[str, list[str]]:
    """그림 캡션 단락(경로 code 포함)을 <figure>(이미지 내장)로 승격."""
    used: list[str] = []

    def repl(m: re.Match) -> str:
        cap_head, path, cap_tail = m.group(1), m.group(2), m.group(3)
        used.append(path)
        caption = (cap_head + cap_tail).strip().rstrip(".") + "."
        return (f'<figure class="fig"><img src="{_b64_img(path)}" alt="{path}">'
                f"<figcaption>{caption}</figcaption></figure>")

    return FIG_CAPTION_RE.sub(repl, html), used


def _relocate_footnotes(html: str) -> str:
    """각주 블록(기본: 문서 맨 끝)을 '미주' 제목과 함께 참고문헌 앞으로 이동."""
    m = re.search(r'<div class="footnote">.*?</div>\s*$', html, re.DOTALL)
    ref = re.search(r"<h2>참고문헌</h2>", html)
    if not (m and ref):
        return html
    block = '<h2>미주</h2><div class="footnote">' + m.group(0).split(">", 1)[1]
    html = html[: m.start()] + html[m.end():]
    return html.replace("<h2>참고문헌</h2>", block + "<h2>참고문헌</h2>", 1)


def build_html() -> Path:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["extra", "sane_lists"])
    body, figs = _promote_figures(body)
    body = _relocate_footnotes(body)
    print(f"그림 승격 {len(figs)}건: {[Path(p).name for p in figs]}")

    DIST.mkdir(exist_ok=True)
    out = DIST / "report.html"
    out.write_text(
        "<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'>"
        f"<title>KPF 언론통계 경진대회 — 논문형 보고서</title><style>{CSS}</style></head>"
        f"<body>{body}</body></html>",
        encoding="utf-8",
    )
    print(f"HTML 저장: {out.relative_to(ROOT)} ({out.stat().st_size/1024:.0f} KB)")
    return out


def print_pdf(html: Path) -> Path:
    pdf = DIST / "report.pdf"
    cmd = [str(_find_chrome()), "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf}", html.resolve().as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not pdf.exists():
        raise SystemExit(f"PDF 생성 실패: {r.stderr[-500:]}")
    print(f"PDF 저장: {pdf.relative_to(ROOT)} ({pdf.stat().st_size/1024:.0f} KB)")
    return pdf


def gate_pages(pdf: Path) -> int:
    n = len(PdfReader(str(pdf)).pages)
    verdict = "PASS" if n <= MAX_PAGES else "FAIL"
    print(f"쪽수 게이트: {n}p / 상한 {MAX_PAGES}p → {verdict}")
    if n > MAX_PAGES:
        raise SystemExit(1)
    return n


def main() -> None:
    html = build_html()
    pdf = print_pdf(html)
    gate_pages(pdf)
    print("완료 — 조판 파이프라인(md → HTML → Chrome PDF) 종료")


if __name__ == "__main__":
    main()
