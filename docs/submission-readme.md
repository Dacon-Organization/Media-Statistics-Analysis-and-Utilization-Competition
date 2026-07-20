# 제출물 안내 — KPF 언론 통계 분석·활용 경진대회

> 이 문서는 **ZIP(추가 산출물)의 루트 README**입니다. 제출물은 두 갈래로 구성됩니다.

## 제출물 구성

| 제출물 | 내용 | 파일 |
|--------|------|------|
| **PDF (분석·제안)** | 논문형 보고서 14장(≤15장) — 재단 제공 「언론수용자 조사」 7개년(2019~2025) 원시자료 하모나이즈·신뢰/다양성 지수·추세(정렬법·APC)·페르소나·B2G/B2C 제안. 그림 10종 전부 본 저장소 코드로 재생성 가능 | `report.pdf` (별도 첨부) |
| **ZIP (추가 산출물)** | 분석 개발 산출물 전체 — 노트북 32종(실행 출력 포함)·파이프라인 코드·보고서 그림·원고·웹데모 소스·데이터 정보 | 본 ZIP |

## ZIP 내부 구조

```
├── README-SUBMISSION.md      ← 이 문서
├── report.html               ← 보고서 자기완결 HTML판(그림 base64 내장, 오프라인 열람)
├── notebooks/                ← 분석 노트북 32종(01~32) + 전체 지도(README.md) — 실행 출력·검증 assert 포함
├── src/                      ← 파이프라인 코드 SSOT(하모나이즈→지수→추세→평가→figure→조판)
├── assets/                   ← 보고서 그림 PNG(F2~F11 등)
├── docs/report/              ← 원고(manuscript.md)·설계 SSOT(p6-pdf-structure.md)
├── web/                      ← B2C 진단 웹데모 소스(Next.js 15) — 판정 사양 web/diagnosis-spec.json v1.1 소비
├── data/                     ← 데이터 정보 문서(README·INVENTORY·DOWNLOAD-GUIDE)
└── requirements.txt
```

- **데이터 파일 미포함**: 원시자료(`.sav`/`.csv`/`.xlsx`, 약 78MB)는 KPF 공개 오픈데이터로, 용량 절약을 위해 ZIP에서 제외했습니다. 전체 데이터가 포함된 **공개 GitHub 저장소**에서 받거나(아래), `data/raw/DOWNLOAD-GUIDE.md` 절차로 KPF에서 직접 내려받을 수 있습니다.
- **GitHub(전체 재현 환경)**: <https://github.com/Dacon-Organization/Media-Statistics-Analysis-and-Utilization-Competition>
- **웹데모**: 배포 URL은 제출물에 별도 첨부. 소스는 `web/`(로컬 실행: `cd web && npm install && npm run dev`, 검증: `npm run verify`).

## 재현 절차 (보고서 PDF까지)

```bash
pip install -r requirements.txt
python src/harmonize.py           # 원시자료 → data/processed/audience_harmonized.parquet (행수 게이트 90,996)
python src/export_figures.py      # 보고서 그림 7종 재생성(assets/) — 검증은 notebooks/31
python src/build_report.py        # 원고 → HTML → PDF 조판(15p 게이트) — 검증은 notebooks/32
```

- 노트북 재실행: `PYTHONIOENCODING=utf-8 jupyter nbconvert --to notebook --execute --inplace notebooks/NN-*.ipynb`
- 각 노트북의 [입증] 검증 셀(assert)이 산출 수치를 SSOT 상수·원천 문서와 대조합니다 — 실패 시 예외로 즉시 드러납니다.

## 분석 개요 (자세한 내용은 PDF·notebooks/README.md)

- **데이터**: KPF 언론수용자 조사 2019~2025(7개년, N=90,996) — 문항 크로스워크·가중치 재설계·재검증(12·13·15) 후 하모나이즈.
- **측정**: 신뢰축(reflective, MGCFA 부분불변성 확보 후 정렬법 잠재평균)·다양성축(formative, 방향성만 해석)·NCHI 종합지수.
- **추세·세대**: 정렬법 잠재평균 추세 + MK/Sen 검정(점추정 비유의 p=0.381, 방향 일관성 P(S>0)=1.00) + APC 분해(HAPC·IE) — 상승은 기간효과, 코호트는 별개의 하방 구배.
- **활용 제안**: B2G 정책지수(NCHI)·B2C 자가진단(판정 사양 v1.1 → 웹데모) — 판정 규칙은 노트북 09가 export한 사양을 웹·그림이 소비만 함(로직 재정의 없음).
