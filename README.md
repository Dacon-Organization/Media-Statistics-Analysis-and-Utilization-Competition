# 언론 통계 분석·활용 경진대회 — 프로젝트

> 한국언론진흥재단 주최 · 데이콘 운영 · 2026
> **핵심 산출물: 자유 양식 PDF 보고서(15장 이내, 논문 형식) + 추가 산출물 ZIP**

재단이 공개한 언론 통계 자료를 분석해 **사회적·산업적 시사점**을 도출하고,
**현실 적용 가능한 정책·서비스 아이디어**를 제안하는 대회입니다.

---

## 1. 대회 개요

| 항목 | 내용 |
|------|------|
| 주최/주관 | 한국언론진흥재단 |
| 운영 | 데이콘 |
| 주제 | 언론 통계 자료를 이용한 시사점 및 아이디어 제안 |
| 데이터 | [KPF 언론 통계 자료](https://www.kpf.or.kr/front/mediaStats/mediaStatsListPage.do) (메인 필수) + 공개 외부자료(보조) |
| 산출물 | PDF(분석·제안, 15장 이내, 필수) + ZIP(추가 산출물, 선택) |
| 상금 | 총 200만원 (최우수 100 / 우수 2팀 각 50) + 이사장상 |

### 일정 (KST)
| 단계 | 기간 |
|------|------|
| 접수·제출 | 2026-06-22 10:00 ~ **2026-07-23 10:00** |
| 산출물 검증 | 07-23 ~ 07-30 |
| 1차 투표 평가 | 08-03 ~ 08-12 |
| 2차 내부 평가(상위 15팀) | 08-13 ~ 08-21 |
| 최종 발표 | 08-24 |

### 평가 구조
- **1차 대중 투표** → 상위 15팀 (제출자 60% + 참가자 20% + 대중 20%)
- **2차 내부 정성 평가** (수상 3팀 결정)

| 2차 평가 항목 | 배점 |
|---------------|------|
| 데이터 활용 적절성 | 25 |
| 분석의 타당성 | 25 |
| 시사점·아이디어 구체성 | 25 |
| 실현 가능성·활용성 | 25 |

> ⚠️ **규정상 제외/무효 사유**: 데이터 근거 없는 제안, **타 기관·기업이 이미 시행 중이거나 기본구상이 유사한 제안**, 타인 권리 침해, 단순 민원성 제안. → *차별화 방어가 곧 생존 조건.*

---

## 2. 프로젝트 방향 (확정)

분석 척추(spine)와 산출 제품을 다음과 같이 확정했습니다. (근거: [`docs/groundwork/01-strategy-synthesis.md`](docs/groundwork/01-strategy-synthesis.md))

### 분석 앵글: **A + B 결합**
- **A. 뉴스 건강 지수(News Health Index) 설계** — 언론수용자 조사 원시자료로 국민 뉴스 소비의 "건강성"(다양성·신뢰·검증습관·회피도)을 합성지수로 설계·산출. *리서치가 명시한 "미디어 리터러시 표준 측정도구 부재" GAP을 정면으로 메움.*
- **B. 뉴스 소비 페르소나 세분화** — K-means 등 군집분석으로 정밀 페르소나(예: "숏폼 의존·저신뢰형", "유튜브 과몰입 5060형") 도출 → 집단별 맞춤 처방.

### 산출 제품: **"뉴스 건강검진" (가칭 / working title)**
양면(兩面) 스토리로 구성:
- **B2C 시민 서비스** — 개인이 몇 문항 답하면 ① 내 뉴스 건강점수 ② 페르소나 ③ 맞춤 처방 제공 (미디어 리터러시 실천 도구)
- **B2G 정책 도구** — KPF가 매년 산출하는 *국민 뉴스 건강 지수* 모니터링 대시보드 (측정도구 GAP 해소)

### 산출물 전략 (Tier 2)
| 산출물 | 형식 | 비고 |
|--------|------|------|
| 논문형 PDF 보고서 | PDF 15장 이내 | **핵심 채점 대상** |
| 분석 코드·노트북 | Jupyter/Python | ZIP 첨부 |
| 실동작 웹 데모 | Next.js (Vercel 배포) | 진단 플로우 1개 집중 → 대중투표·실현가능성 증명 |
| 설계 문서 | 요구사항/기능/API/ERD | 풀 프로덕션 비전(가정) |

> 웹은 **DB·백엔드 없이 분석에서 추출한 계수를 브라우저에서 계산**하는 정적 데모를 기본으로 하여 안정 배포. API/ERD는 "확장 시 이렇게" 설계 문서로 정당화.

---

## 3. 분석 스택

실무 표준 Python 데이터 분석 스택:
- **데이터 처리**: pandas, numpy
- **통계·모델링**: scipy, statsmodels, scikit-learn (군집/회귀)
- **시각화**: matplotlib, seaborn, plotly
- **노트북**: Jupyter
- **웹 데모(별도)**: Next.js 15 + TypeScript + Tailwind + shadcn/ui

---

## 4. 폴더 구조

```
Media-Statistics-Analysis-and-Utilization-Competition/
├── README.md                ← 이 파일
├── requirements.txt         ← Python 분석 의존성
├── docs/
│   ├── groundwork/         ← 사전 시장조사·전략 종합 (완료)
│   ├── design/             ← 요구사항·기능·API·ERD 명세 (예정)
│   ├── report/             ← 논문형 PDF 보고서 원고 (예정)
│   └── specs/              ← brainstorming/plan 산출 spec (예정)
├── data/
│   ├── raw/                ← KPF 원시자료 (대용량은 gitignore)
│   ├── interim/            ← 중간 가공
│   └── processed/          ← 분석용 정제 데이터
├── notebooks/              ← EDA·지수설계·클러스터링 분석 (예정)
├── src/                    ← 재사용 분석 파이프라인 모듈 (예정)
├── web/                    ← Next.js "뉴스 건강검진" 데모 (예정)
└── assets/                 ← 차트·이미지 산출물
```

---

## 5. 진행 현황

- [x] 사전 시장조사 (KPF 데이터·정책·경쟁서비스·방법론) → [`docs/groundwork/00-market-research.md`](docs/groundwork/00-market-research.md)
- [x] 전략 종합 — 앵글(A+B)·차별화·산출물 확정 → [`docs/groundwork/01-strategy-synthesis.md`](docs/groundwork/01-strategy-synthesis.md)
- [x] 폴더 구조 정립 + 루트 README 등록
- [ ] 심화 설계 (요구사항·기능·API·ERD 명세)
- [x] KPF 데이터 명세 — 자료 카탈로그·시계열 분절점·다운로드 가이드 정립 → [`docs/design/data-spec.md`](docs/design/data-spec.md), [`data/raw/DOWNLOAD-GUIDE.md`](data/raw/DOWNLOAD-GUIDE.md)
- [x] KPF 원시자료 확보·정돈 — 언론수용자 조사 7개년(2019~2025) + 매뉴얼 → [`data/raw/INVENTORY.md`](data/raw/INVENTORY.md)
- [ ] 변수 명세 확정(코드북 정독) + 시장조사 인용 수치 재검증
- [ ] 분석 (지수 설계 → 페르소나 군집 → 코호트)
- [ ] 웹 데모 구현
- [ ] 논문형 PDF 보고서 작성

> 작업 진척 시각화: [`dev/dashboard/index.html`](../dev/dashboard/index.html) (R2)
