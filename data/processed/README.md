# data/processed/ — 분석용 정제 데이터

분석·모델링에 바로 투입하는 **최종 정제 데이터**를 둡니다. (예: 결측 처리·가중치 반영·지수 산출용 피처 테이블)

- **버전관리 제외**(`.gitignore`). `raw/`→`interim/`→`processed/` 파이프라인으로 재현합니다.
- 컬럼 정의가 바뀌면 [`../../docs/design/data-spec.md`](../../docs/design/data-spec.md)와 동기화합니다.

---

## `audience_harmonized.parquet` — 7개년 하모나이즈 패널 (P3)

생성: `python src/harmonize.py` · 명세(SSOT): [`../../docs/design/variable-crosswalk.md`](../../docs/design/variable-crosswalk.md) v0.2 §3.
반복횡단면(repeated cross-section) long-format. **총 90,996행 = 7개년 응답 스택**(2019~2025).
동반 산출: `_presence_matrix.csv`(연도×target 유효응답 수, gitignore).

### 컬럼 스키마

| 컬럼 | 의미 | 비고 |
|------|------|------|
| `year` | 조사연도(2019~2025) | |
| `resp_id` | 응답자 ID(`{year}_{행번호}`) | 연도 내 고유 |
| `wt` | 표준화 설계가중치 | wt1(2019)·WT·HMWT(2023)→통일 |
| `wt_within` | 연도 내 평균=1 정규화 가중치 | 상대가중 보존, 스케일 제거 |
| `wt_year_eq` | **연도기여 균등화** 가중치 | 각 연도 합=N/7 → 2022 표본지배 제거(05 §6) |
| `sex` | 성별(1=남,2=여) | |
| `age` | 만나이(연속) | |
| `birth_cohort` | 출생 코호트(=year−age) | APC 분석 키 |
| `edu` | 학력 4단계(1=중졸이하…4=대학원) | 2019~2021 5→4단계 재코딩 |
| `income_band9` | 가구소득 9밴드(1~9) | 2022는 600만+(band7) 분해불가→NA |
| `income_band7` | 가구소득 7밴드(7개년 공통) | 9밴드 {7,8,9}→7 통합, 2022 native |
| `job` | 직업(명목 1~13, 13=기타) | 9997=기타→13. 2019 equiv=conceptual |
| `region` | 시도(명목 1~17) | 2019 행정코드→순차 리맵 |
| `trust_news_overall` | 뉴스 전반신뢰 5점 | **2019 부재(NA)** |
| `trust_news_used` | 실제이용 뉴스신뢰 5점 | **2019·2020 부재(NA)** |
| `trust_society` | 사회 전반신뢰 5점 | **2019 부재(NA)** |
| `media_main_route` | 뉴스 주이용경로(디코드 한글 라벨) | 비이용→NA. 고정풀·e^H는 P4 |
| `media_main_route_code` | 주이용경로 원본 코드 | 연도별 코드체계 상이 |
| `yr_2019`…`yr_2025` | 연도 더미(0/1) | 추세회귀 통제용 |
| `is_2022` | 2022 식별 플래그 | 민감도분석·구조단절 통제 |

> ⚠️ 신뢰 시계열은 **2020~2025만 유효**(2019 구조적 단절, crosswalk §5-1).
> ⚠️ 측정 비동등 검정(P4 MGCFA·정렬법) 전 추세 수치 보고서/웹데모 직접 인용 금지.
