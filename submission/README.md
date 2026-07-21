# submission/ — KPF 언론 통계 경진대회 확정 제출본

이 폴더는 **저장소가 추적하는 최종 제출 산출물**입니다. `dist/`(재생성 임시물, `.gitignore` 제외)와 달리, 어느 체크아웃에서 열어도 최신 확정본이 보이도록 여기에 승격해 둡니다.

| 파일 | 제출 항목 | 내용 |
|------|-----------|------|
| `report.pdf` | **PDF (분석·제안)** | 논문형 보고서 14장(≤15장). 재단 제공 「언론수용자 조사」 7개년(2019~2025) 원시자료 분석 결과 포함. 그림 10종 내장 |
| `kpf-submission-extra.zip` | **ZIP (추가 산출물)** | 분석 개발 산출물 — 노트북 32종(실행 출력 포함)·파이프라인 코드·보고서 그림·원고·웹데모 소스·데이터 정보 문서 |

## 웹데모(배포)

- **B2C 자가진단 「뉴스 건강검진」**: <https://media-statistics-analysis-and-utili.vercel.app>
- 판정 규칙은 노트북 09가 export한 `web/diagnosis-spec.json` v1.1을 **소비만** 하며 웹에서 임계값을 재정의하지 않습니다(`npm run verify` 10항목 PASS로 파이프라인 판정과 일치 검증).

## 재생성 방법

```bash
python src/build_report.py       # 원고 → HTML → PDF 조판(dist/, 15장 게이트)
python src/package_submission.py # dist/ 산출을 게이트 통과 후 이 폴더로 승격 + ZIP 구성
```

- `package_submission.py`는 PDF 게이트(쪽수 ≤15·그림 ≥10)와 ZIP 게이트(노트북 32종·필수 항목 포함·`node_modules` 제외)를 assert로 검증한 뒤에만 산출물을 갱신합니다.
- ZIP 루트의 상세 안내는 `docs/submission-readme.md`(= ZIP 내 `README-SUBMISSION.md`)를 참조하세요.
