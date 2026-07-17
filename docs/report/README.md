# docs/report/ — 논문형 보고서 원고

대회 **핵심 채점 대상**인 자유 양식 PDF 보고서(15장 이내, 논문 형식)의 원고·자료를 둡니다.

## 설계 SSOT

장 구성·figure 선정·인용 수치표(자격등급)는 **[p6-pdf-structure.md](p6-pdf-structure.md)** 가 정본입니다.

## 원고

- **[manuscript.md](manuscript.md)** — 본문 원고 v0.1 (P6-B-2, 2026-07-12 · P6-B-6 서지 보강 2026-07-17: IE 원전·Luo 논쟁 반영). 7장 구성·figure F1~F9(F9는 웹데모 후 placeholder 교체)·각주 4종+house effect(A안)+코로나 국제동시성. 수치는 p6-pdf-structure §3 표에서만 복사(§5 게이트 준수, 수동 대조 완료).
- 조판(P6-B-3, 2026-07-12 완료): `python src/build_report.py` — md → HTML(논문형 CSS, 그림 base64 내장·각주는 '미주'로 참고문헌 앞 배치) → headless Chrome PDF → `dist/report.pdf`. 쪽수 게이트(15p 이내) 자동 검증 — 현재 **12p PASS**. figure export 과정 입증은 [`notebooks/31-figure-export.ipynb`](../../notebooks/31-figure-export.ipynb).

## 노트북 ↔ 원고 ↔ PDF 동기화 루프 (상시 절차, P6-B-6 확립)

노트북을 수정할 때마다 아래 순서로 원고와 PDF를 동기화한다. 수치가 바뀌는 수정과 서술만 바뀌는 수정의 경로가 다르다.

1. **노트북 수정** — 코드 셀이 바뀌면 `jupyter nbconvert --to notebook --execute --inplace notebooks/NN-*.ipynb`로 재실행해 [입증] assert 전부 PASS 확인. 마크다운만 바뀌면 재실행 불요.
2. **수치 변경 여부 판정** —
   - 수치·상수 불변(서술·서지만): 3으로 직행.
   - 수치가 바뀌면: 해당 SSOT(`src/p5_evaluation.py` 상수·design 문서)를 먼저 갱신하고 `30-evaluation.ipynb` §6 drift 게이트 재실행 PASS → [p6-pdf-structure.md](p6-pdf-structure.md) §3 인용 수치표 갱신 → 그 다음에만 원고 반영(§5 게이트).
3. **원고 갱신** — [manuscript.md](manuscript.md)에 반영. 새 수치는 반드시 p6-pdf-structure §3 표에서만 복사.
4. **PDF 재빌드** — `python src/build_report.py` 실행. 15p 게이트 자동 검증(초과 시 exit 1 — 감축 우선순위: 3장 디테일 → 부록 → 5장).
5. **기록** — 대시보드 로그(`dev/dashboard/`)와 관련 README 갱신 후 커밋.

## 구성(예정, 15장)
배경·문제정의(측정도구 부재 GAP) → 데이터·방법론(원시자료+코호트/군집) → 분석결과(지수·추세·페르소나) → 제안(B2G 정책지수/B2C 진단) → 기대효과·실현가능성(데모 스크린샷).

- 본문 수치는 **KPF 원자료 재검증 완료분만** 인용.
- 차트·이미지는 [`../../assets/`](../../assets/)에서 가져옵니다.
