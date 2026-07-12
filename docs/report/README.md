# docs/report/ — 논문형 보고서 원고

대회 **핵심 채점 대상**인 자유 양식 PDF 보고서(15장 이내, 논문 형식)의 원고·자료를 둡니다.

## 설계 SSOT

장 구성·figure 선정·인용 수치표(자격등급)는 **[p6-pdf-structure.md](p6-pdf-structure.md)** 가 정본입니다.

## 원고

- **[manuscript.md](manuscript.md)** — 본문 원고 v0.1 (P6-B-2, 2026-07-12). 7장 구성·figure F1~F9(F9는 웹데모 후 placeholder 교체)·각주 4종+house effect(A안)+코로나 국제동시성. 수치는 p6-pdf-structure §3 표에서만 복사(§5 게이트 준수, 수동 대조 완료).
- 조판(md → HTML → headless Chrome PDF, `dist/report.pdf`)은 P6-B-3에서 진행.

## 구성(예정, 15장)
배경·문제정의(측정도구 부재 GAP) → 데이터·방법론(원시자료+코호트/군집) → 분석결과(지수·추세·페르소나) → 제안(B2G 정책지수/B2C 진단) → 기대효과·실현가능성(데모 스크린샷).

- 본문 수치는 **KPF 원자료 재검증 완료분만** 인용.
- 차트·이미지는 [`../../assets/`](../../assets/)에서 가져옵니다.
