# 반복횡단면 설문 변수 하모나이즈 및 측정 비동등 처리 모범사례
## — 한국언론진흥재단 '언론수용자 조사' 7개년(2019–2025) 적용 가이드 —

> 출처: Perplexity Deep Research (2026-06-24) — P2 Data Understanding/P3 Data Preparation의 **7개년 하모나이즈 전략** 근거 외부 조사.
> 반영: ① Crosswalk = 핵심 3군 보수적 수작업 + NLP 후보 탐색 보조 → [`docs/design/variable-crosswalk.md`](../design/variable-crosswalk.md), ② 측정 비동등 = MGCFA(연도=집단) + 정렬법(Alignment), ③ 다양성 = 고정 풀 + 유효 종 수 \(e^H\), ④ 2022 표본 급증 = 연도 더미 + 가중치 정규화 + 민감도 분석.
> 연관 설계: 마스터플랜 [`docs/design/analysis-master-plan.md`](../design/analysis-master-plan.md) §1.1·§3 · NCHI 집계 근거 [`04-research-aggregation-direction.md`](04-research-aggregation-direction.md).
> ⚠️ 인용 수치(KPF·해외 조사 보고서값 등)는 원자료 재검증 전까지 보고서·웹데모 직접 인용 금지(`data-spec.md §6`).

***

## 개요

반복횡단면(repeated cross-sectional) 설문의 다개년 통합 분석은 (1) 변수명 불연속 문제, (2) 측정 비동등(measurement non-invariance) 가능성, (3) 이질적 표본 가중치 처리 등 세 가지 구조적 난제를 동시에 해결해야 한다. 아래에서는 언론수용자 조사 7개년 데이터에 직접 적용 가능한 절차와 학술적 근거를 6개 질문별로 제시한다.

***

## 1. 문항 의미 기반 Crosswalk 구축의 표준 절차와 문서화 양식

### 1-1. 표준 절차 (5단계)

**① 개념 정의 및 목표 변수 목록 작성**
분석 목적(뉴스 매체 이용, 뉴스 신뢰, 인구통계)에 상응하는 *이론적 구성개념*을 먼저 명시한다. 구성개념 없이 변수명에서 출발하면 이후 매핑 결정의 정당성을 확보하기 어렵다. DDI(Data Documentation Initiative) 표준은 변수 수준의 메타데이터를 `concept`, `question`, `responseUnit`으로 계층 분리하여 기록하도록 권고하며, 이는 ISO/PAS 25955:2026에 통합되었다.[^1][^2]

**② 연도별 코드북 수집 및 원문항 추출**
7개년 코드북(2019–2025)을 확보하고, 각 연도의 설문지 원문과 응답 척도를 그대로 추출한다. 언론수용자 조사는 한국언론진흥재단 공공데이터포털에서 원시자료와 설문지·코드북을 제공한다. 2024년에는 언론사별 신뢰도·영향력 문항이 삭제되고 매체 유형별로 변경된 사례처럼, 문항 *폐지·신설* 이력도 별도 컬럼에 기록한다.[^3][^4]

**③ 변수 수준 Crosswalk 테이블 작성 (핵심 문서)**
Koczynska & Cohrs(2022)가 제안한 재현 가능한 워크플로에 따르면, crosswalk는 *변수 크로스워크*와 *값 크로스워크* 두 레이어로 구성한다. 아래가 권장 컬럼 구조다:[^5]

| 컬럼명 | 설명 |
|--------|------|
| `target_var` | 통합 분석용 목표 변수명 (예: `news_trust`) |
| `year` | 연도 (2019–2025) |
| `src_varname` | 원시데이터 변수명 (예: `Q15_3`) |
| `src_wording` | 원문항 전문 |
| `src_scale` | 응답 범주 수 및 척도 레이블 |
| `recode_rule` | 값 매핑 규칙 (예: `1→1, 2→2, 3→NA`) |
| `equivalence_level` | `exact` / `conceptual` / `approximate` |
| `flag_wording_change` | 워딩 변경 여부 (Boolean) |
| `flag_scale_change` | 척도 변경 여부 (Boolean) |
| `coder` | 코딩 담당자 ID |
| `review_date` | 검토 일자 |
| `note` | 불확실성·판단 근거 메모 |

`equivalence_level`은 추후 측정 비동등 검정의 사전 분류로도 활용된다. 값 크로스워크는 데이터를 long 형식으로 변환한 뒤 join으로 일괄 재코딩하는 방식이 스크립트 의존성을 낮추고 검증·재현을 용이하게 한다.[^5]

**④ 이중 검토 및 신뢰도 기록**
두 명의 코더가 독립적으로 매핑을 수행하고, 불일치 항목을 제3자가 중재한다. `equivalence_level`이 `approximate`인 변수에는 Cohen's κ 또는 퍼센트 합의를 `note`에 기록한다.

**⑤ 버전 관리**
crosswalk 파일은 Git 또는 OSF에서 버전 관리한다. 논문 제출 시 데이터 파일과 함께 공개하면 재현 가능성을 확보할 수 있다.[^5]

***

## 2. 매핑 범위 결정: 보수적 소수 지표 vs. 자동 텍스트 유사도 광범위 매칭

### 접근별 트레이드오프

| 기준 | (a) 보수적 소수 매핑 | (b) NLP 자동 매칭 후 수작업 확정 |
|------|-------------------|---------------------------------|
| **타당도** | 높음 — 의미 동일성 직접 판단 | 중간 — 모델 오류 및 피상적 텍스트 유사성 위험 |
| **재현성** | 높음 — 매핑 수 적어 문서화 용이 | 중간 — NLP 파이프라인·모델 버전에 의존 |
| **커버리지** | 낮음 — 핵심 지표만 | 높음 — 누락 후보 탐색 가능 |
| **리스크** | 정보 손실 | 위양성(false positive) 매핑 |
| **적합 상황** | 분석 목적 명확, 핵심군 3개 내외 | 탐색적 연구, 100개 이상 문항 스크리닝 |

**NLP 도구 사례:** Harmony(McElroy et al., 2020; Ryan et al., 2024)는 다국어 설문 문항의 의미 유사도를 자동 계산하며, 영·포르투갈어 GAD-7 매칭에서 AUC 100%를 달성했다. 최근 arxiv 연구(2025)에서는 IR-specialised neural model이 1946–2020년 종단 설문 문항 매칭에서 가장 높은 성능을 보였으나, 전문가 사후 검토에서 모델이 표면적 유사성에 의존하는 한계를 확인했다. 따라서 **자동 매칭은 후보 생성(screening) 도구로 한정하고, 최종 채택 여부는 반드시 수작업으로 결정**해야 한다.[^6][^7][^8]

**학계 권고:** Koczynska & Cohrs(2022)는 "매핑의 정당성은 구성개념 이론에서 나와야 하며, 텍스트 유사도는 초기 탐색에만 활용하라"고 권고한다. 언론수용자 조사처럼 Jaccard 유사도가 인접 연도 간 0.08–0.73으로 불안정한 경우, (a)와 (b)의 **혼합 전략**이 최적이다: 핵심 3개군(이용, 신뢰, 인구통계)은 보수적 수작업으로 처리하고, 탐색적 문항 보완에 한해 NLP로 후보를 추출한다.[^5]

***

## 3. 반복횡단면에서 측정 동등성 검정 방법

### 3-1. 기본 원리: 연도를 집단(group)으로 취급

패널이 아닌 반복횡단면에서는 **각 조사 연도를 MGCFA(Multi-Group CFA)의 별개 집단으로 설정**하여 측정 동등성을 검정한다. 시간에 따른 문항 파라미터 안정성 질문은 구조적으로 국가 간 비교와 동일하게 취급된다.[^9][^10][^11]

### 3-2. 순차 검정 절차

측정 동등성 검정은 세 수준을 순차적으로 적용한다:

1. **형태 동등(Configural invariance):** 인자 구조(요인 수, 문항-요인 연결)가 연도별로 동일한지 검정. 이 단계에서 실패하면 동일 구성개념을 측정하고 있지 않음을 의미하므로 분석 불가.[^12]
2. **측정치 동등(Metric invariance):** 요인 부하량(factor loadings)이 연도 간 동등한지 검정. 달성 시 구성개념 간 공분산·회귀계수 비교 가능.[^11]
3. **절편 동등(Scalar invariance):** 문항 절편(intercepts)이 연도 간 동등한지 검정. 달성 시 잠재 평균 비교 가능 — 즉, 연도별 신뢰 점수·이용 일수의 *평균 추세*를 비교하려면 이 수준이 필요하다.[^13]

**모형 적합도 기준(Chen, 2007; Rutkowski & Svetina, 2014):**

| 검정 단계 | ΔCFI 기준 | ΔRMSEA 기준 |
|-----------|-----------|-------------|
| 측정치 동등 | ≤ -0.010 | ≤ 0.015 |
| 절편 동등 | ≤ -0.010 | ≤ 0.010 |
| 대규모 집단 조정(Rutkowski & Svetina) | ≤ -0.020 (metric) | ≤ 0.030 |

[^14][^15]

### 3-3. Alignment Method (정렬법): 반복횡단면에 특히 유용

Asparouhov & Muthén(2014)의 **정렬법(Alignment Method)**은 완전한 절편 동등성을 가정하지 않고도 집단별(연도별) 잠재 평균과 분산을 추정한다. 작동 원리는 다음과 같다:[^16][^17]

1. **1단계:** Configural 모형 추정 (제약 없음)
2. **2단계:** 비동등 파라미터의 총량을 최소화하는 단순성 함수(simplicity function) 최적화 — EFA의 회전과 유사[^18]

핵심 장점은 조사 연도 수가 많을 때(7개년 이상) MGCFA의 단계적 부분 불변 탐색보다 더 단순하고 해석 가능한 해를 제공한다는 것이다. 비동등 파라미터가 전체의 20%까지 존재해도 잠재 평균 추정이 편향되지 않음이 시뮬레이션으로 확인되었다. Mplus 소프트웨어와 R 패키지 `sirt`의 `invariance.alignment()` 함수로 구현 가능하다.[^19][^20][^21]

**BAMI(Bayesian Approximate Measurement Invariance):** Muthén & Asparouhov(2012), van de Schoot et al.(2013)이 제안한 방법으로, 부하량과 절편에 작은 분산의 사전분포(small-variance prior)를 부여하여 근사 동등성을 검정한다. 비동등 크기가 작지만 엄격한 동등성이 성립하지 않을 때 유용하다.[^22][^23]

### 3-4. 부분 불변(Partial Invariance) 모형

전체 절편 동등이 실패할 경우, 최소 두 문항 이상이 동등하면 부분 절편 동등(partial scalar invariance)을 선언하고 잠재 평균 비교를 제한적으로 수행할 수 있다 (Byrne, Shavelson & Muthén, 1989; Steenkamp & Baumgartner, 1998). 단, 단계적(stepwise) 제약 해제는 선택 편향 위험이 있으므로, Asparouhov & Muthén(2014)은 정렬법을 대안으로 권장한다.[^24][^25][^13]

***

## 4. 측정 비동등 확인 시 추세 해석 원칙과 보정 수준

### 4-1. 단계적 해석 원칙

| 달성 수준 | 가능한 해석 | 불가능한 해석 |
|----------|------------|--------------|
| Configural만 | 구조 유사성 기술 | 평균, 분산, 방향성 모두 불가 |
| Metric | 요인 간 관계(회귀, 상관) 비교 | 잠재 평균 수준 비교 |
| Partial scalar (≥2 문항) | 잠재 평균 *방향성(증감 추세)* 조건부 해석 | 절대 점수 변화량 수량화 |
| Full scalar | 잠재 평균 수준·크기 완전 비교 | — |

[^12][^9][^13]

### 4-2. 보정 수준 판단

**방향성만 해석 (Direction-only interpretation):** 부분 절편 동등성만 달성된 경우 권장. 비동등 문항에서 기인하는 절편 편향이 연도별 평균 비교를 오염시킬 수 있으므로, "신뢰가 2019년 대비 2024년에 더 높다/낮다"는 진술은 가능하지만 "0.3점 증가"와 같은 수량적 변화는 과잉 해석으로 간주된다.[^26]

**정렬법 기반 조정 (Alignment-based correction):** 정렬법으로 추정한 연도별 잠재 평균은 비동등 파라미터를 명시적으로 수용하면서 산출되므로, 비동등 문항 비율이 20% 이내면 조정된 잠재 평균 비교가 정당하다. 이 경우 "alignment-adjusted latent mean"임을 분명히 기술해야 한다.[^19]

**과보정 위험:** 비동등이 20%를 초과하거나 단순성 함수 수렴이 실패하면 정렬법 자체가 편향된 결과를 낼 수 있다. 이 경우 Davidov, Muthén & Schmidt(2018)의 권고대로 **측정 비동등의 원인을 파악하여 맥락적으로 설명**하는 접근이 정량적 보정보다 우선한다.[^27][^28][^19]

**OECD(2019) 지침:** PISA, ESS 등 대규모 조사에서 cross-wave 안정성 검정에 MGCFA를 적용하되, 비동등 발견 시 해당 파라미터를 구조적 차이의 *증거*로 보고하도록 권장한다.[^10]

***

## 5. 척도 변경 및 매체 항목 변동 시 다양성 지수의 연도 간 비교가능성 확보

### 5-1. 문제 구조

Shannon 엔트로피 기반 뉴스 매체 다양성 지수는 이용 항목 수(species richness)와 각 항목의 이용 비율로 계산된다:

\[
H = -\sum_{i=1}^{k} p_i \ln p_i
\]

매체 항목이 추가·삭제되면 \(k\)가 연도별로 달라져 직접 비교가 불가능하다. 또한 응답 범주 수(척도 점수)가 변경되면 \(p_i\) 추정치 자체가 달라진다.[^29][^30]

### 5-2. 비교가능성 확보 방법

**① 공통 항목 기반 고정 풀(Fixed item pool)**
7개년에 걸쳐 *모든 연도에 등장하는* 매체 항목만 포함하는 고정 풀을 정의하고, 이를 기준으로 Shannon H를 계산한다. 추가·삭제 항목은 별도 보완 지수나 기술 통계로 제시한다. 이 방식은 비교가능성을 최우선으로 하지만 정보 손실이 있다.

**② 유효 종 수(Effective Number of Species) 변환**
Jost(2006)의 지적처럼 Shannon H 자체는 직관적 다양성 척도가 아니다. \(e^H\)로 변환한 *유효 종 수(effective number of species)*는 항목 수가 달라도 동일한 척도로 해석 가능하며, 정규화(equitability index \(H/\ln k\))보다 수학적 성질이 우수하다.[^31][^32][^30]

**③ 척도 범주 변경 대응**
응답 범주가 5점에서 10점(또는 반대)으로 변경된 경우:
- **선형 변환 재코딩:** \(\text{recoded} = \frac{(\text{original} - 1)}{(\text{max} - 1)} \times (\text{new\_max} - 1) + 1\)
- **이분화(dichotomization):** "1회 이상 이용 여부" 이진 변수로 통일하면 척도 무관하게 비교 가능하나 정보 손실 발생
- 실험 연구에 따르면 10점→5점 축소 시 평균 점수 차이는 effect size d≈0.17~0.51로 무시할 수 없으므로, 척도 변경 연도를 **구조적 단절(structural break)**로 처리하는 방식도 고려해야 한다.[^33]

**④ 매체 항목 변동 보완: 앵커링(Anchoring)**
항목 추가·삭제 전후 연도(예: 2021→2022→2023)에서 *공통 항목*을 앵커(anchor)로 삼아, 앵커 항목의 Shannon H 기여분 변화를 이용해 연도 간 표준화 계수를 산출한다. 이는 교육 측정의 수직 등화(vertical equating) 논리와 유사하다.

***

## 6. 이질적 가중치와 2022년 표본 급증 처리의 모범사례

### 6-1. 2022년 언론수용자 조사 특수성 이해

2022년 조사는 기존 5,000명 규모에서 3만 가구·58,936명으로 **약 12배 확대**되었다. 이에 대해 한국언론진흥재단은 "2022년 표본 변경으로 기존 시계열과 동등 비교는 어렵다"고 명시했다. 표본 크기가 12배 확대되면 통합 분석 시 2022년 데이터가 추세 추정을 지배하는 '표본 지배 편향'(sample dominance bias)이 발생한다.[^34][^35][^36]

### 6-2. 가중치 정규화 표준 절차

**방법 1: 연도별 기여도 균등화(Equal Year Contribution)**

각 연도의 분석가중치를 해당 연도 표본 기여분이 전체에서 1/7이 되도록 조정한다:

\[
w^*_{it} = w_{it} \times \frac{n_t}{\sum_j w_{jt}} \times \frac{1}{T}
\]

여기서 \(T=7\)은 연도 수다. IPUMS, Statistics Canada 등 주요 데이터 아카이브가 다년도 풀링 시 권장하는 방식이다.[^37][^38]

**방법 2: 표본 규모 비례 보정**

Statistics Canada(2001)는 두 방법을 제안한다: (a) 연도별 추정치를 별도 산출 후 가중 평균하는 *separate approach*, (b) 가중치 조정 후 통합 분석하는 *pooled approach*. 연도 간 특성 분포가 동일하다고 가정할 수 없으면 (a)를 먼저 시도하고, 추세 검정이 목적이면 모형에 **연도 더미(cycle effect)**를 포함시켜 표본 구조 차이를 통제한다.[^38]

**방법 3: 효과적 표본 크기(Effective Sample Size) 기반 정규화**

\[
w^{\text{norm}}_{it} = w^*_{it} \times \frac{n^{\text{eff}}_t}{n_t}
\]

where \(n^{\text{eff}}_t = \frac{(\sum w_{it})^2}{\sum w_{it}^2}\) (Kish 공식). 이 방법은 설계 가중치의 분산(deff)을 반영하므로, 2022년처럼 설계가 근본적으로 변경된 경우에도 공정한 비교가 가능하다.[^39]

### 6-3. 2022년 처리 권고

2022년은 별도 연도로 처리하되 다음 두 전략 중 하나를 선택한다:
- **민감도 분석(Sensitivity analysis):** 2022년 포함/제외 시 추세 계수 변화를 보고
- **구조적 단절 검정:** 2022년 전후를 단절 회귀(interrupted time series) 혹은 척도 변경 연도 더미로 처리하여 비교가능성을 보수적으로 평가

***

## 7. APC(연령-기간-코호트) 분석에 대한 추가 고려사항

Yang & Land(2006)의 **HAPC-GLMM(Hierarchical Age-Period-Cohort Generalized Linear Mixed Model)**은 반복횡단면 데이터에서 APC 분석에 최적화되어 있으며, GSS·KGSS 등 사회조사에 적용된 검증 사례가 있다. 핵심은 응답자(Level 1)가 연도(Period, Level 2)와 출생 코호트(Cohort, Level 2)에 *동시에 교차 분류(cross-classified)*되는 다층 모형으로 설정하는 것이다. R 패키지 `apc`가 이 분석을 지원한다.[^40][^41][^42][^43]

**주의점:** APC의 선형 식별 문제(age + cohort = period + constant)는 반복횡단면에서도 존재하며, 이를 해소하기 위해 무작위 효과를 부여하는 방식은 사전 가정에 민감하다. Yang(2010)은 "연령 구간과 기간 구간이 다를 때 식별이 부분적으로 완화된다"고 설명한다.[^42]

***

## 8. 관련 한국 반복횡단면 데이터의 선행 적용 사례

| 데이터 | 기관 | 특성 | 관련성 |
|-------|------|------|-------|
| KGSS(한국종합사회조사) | 성균관대 서베이리서치센터 | 2003–2025 누적, GSS 기반 반복핵심문항 | ESS와 MoU 체결로 국제 비교 가능[^44][^45] |
| 한국미디어패널 | KISDI | 패널(추적)+반복횡단면 혼합 구조, 가구·개인 단위 | 미디어 이용 시계열, 측정 동등성 선행 연구 존재[^46][^47] |
| 언론수용자 조사 | 한국언론진흥재단 | 1984–현재, 매년 독립표본 | 2022년 표본 급증, 신뢰 문항 변경[^4][^48] |
| ICPSR KGSS Cumulative | ICPSR | 2003–2016 누적 공개 파일 | 하모나이즈 선행 사례[^49] |

***

## 결론: 본 데이터(3핵심군·7개년·워딩변동)에 권장되는 Crosswalk 범위와 비동등 처리 수준

언론수용자 조사 7개년(2019–2025)에 대해서는 **보수적 소수 매핑 + 정렬법(Alignment Method) 기반 비동등 처리**의 조합이 가장 적합하다. 구체적으로, Crosswalk 범위는 3핵심군(①뉴스 매체 이용여부·이용일수, ②뉴스/언론 신뢰, ③인구통계)에 한정하여 수작업으로 구축하되, DDI 기반 표준 crosswalk 테이블에 원문항·척도·재코딩 규칙·워딩변동 플래그를 모두 기록하고 이중 검토로 신뢰도를 확보해야 한다. NLP 자동 매칭(Harmony 등)은 누락 변수 후보 탐색에만 보조적으로 활용하고 최종 채택은 전문가 판단으로 결정해야 한다. 측정 비동등 처리는 MGCFA로 연도를 집단으로 삼아 형태→측정치→절편 동등을 순차 검정하되, 문항 수가 적고 비동등이 예상되는 신뢰 문항군에는 정렬법으로 연도별 잠재 평균을 추정하는 방식이 타당하다. 비동등 문항이 전체의 20% 이내이면 alignment-adjusted 잠재 평균 비교가 정당하고, 이를 초과하면 방향성 해석에 그쳐야 한다. 2022년은 표본 설계 변경을 반드시 연도 더미로 통제하거나 민감도 분석으로 처리해야 하며, 가중치는 연도별 기여도를 균등화하는 정규화 공식을 적용해 표본 지배 편향을 방지해야 한다. 다양성 지수는 7개년 공통 매체 항목만 포함하는 고정 풀을 기준으로 \(e^H\) 변환값을 사용하면 척도·항목 변동에 관계없이 비교가능한 시계열을 확보할 수 있다.

***

## 참고 출처 요약

| 출처 | 연도 | 내용 | URL/기관 |
|------|------|------|---------|
| Koczynska & Cohrs, *Methods, Data, Analyses* | 2022 | Crosswalk 표준 워크플로 | SSOAR[^5] |
| Asparouhov & Muthén, *SEM* 21(4) | 2014 | Alignment Method | Mplus[^17] |
| Byrne, Shavelson & Muthén, *PSPB* | 1989 | 부분 불변 개념 | [^13] |
| Davidov, Muthén & Schmidt, *SMR* 47(4) | 2018 | 사회과학 측정 동등성 리뷰 | [^27] |
| Yang & Land, *Sociological Methodology* | 2006 | HAPC-GLMM, 반복횡단면 APC | [^40][^42] |
| Chen, *Structural Equation Modeling* | 2007 | ΔCFI·ΔRMSEA 기준 | [^15] |
| Rutkowski & Svetina | 2014 | 대집단 적합도 조정 기준 | [^14][^15] |
| Leitgöb et al., *Measurement Instruments* | 2023 | 사회과학 비동등 리뷰 | KU Leuven[^22] |
| Statistics Canada | 2001 | 풀링 가중치 조정 | [^38] |
| Jost, *Oikos* | 2006 | 유효 종 수, Shannon H 변환 | [^30] |
| 한국언론진흥재단 | 2023 | 2022년 표본 확대 설명 | [^34][^35] |
| 한국언론진흥재단 | 2025–2026 | 2024년 신뢰 문항 변경, 2025 결과 | [^3][^50] |
| KGSS, 성균관대 | 2003–2025 | 한국 반복횡단면 선행 사례 | [^45][^49] |
| 한국미디어패널, KISDI | 2011–현재 | 미디어 이용 패널+횡단면 | [^46][^47] |

---

## References

1. [ISO/PAS 25955 - Technical Interoperability with Data Documentation](https://standards.iteh.ai/catalog/standards/iso/52df4b48-7c5f-4934-8e26-ba8bfaf1f25d/iso-pas-25955-2026)
2. [DDI metadata standard | IHSN](http://www.ihsn.org/projects/DDI-standard)
3. [특정매체 1위 우려? 신뢰도 문항 뺀 '언론수용자 조사' - 한국기자협회](https://www.journalist.or.kr/news/article.html?no=57972)
4. [한국언론진흥재단_언론수용자 조사_20251231 - 공공데이터포털](https://www.data.go.kr/data/15145170/fileData.do)
5. [A reproducible workflow and toolbox for survey data harmonization (Koczynska & Cohrs, 2022)](https://www.ssoar.info/ssoar/bitstream/handle/document/93887/ssoar-methinnov-2022-1-koczynska-Combining_multiple_survey_sources_A.pdf?sequence=1)
6. [Harmony](https://research-software-directory.org/software/harmony)
7. [Measuring The Performance Of NLP Algorithms | Harmony](https://harmonydata.ac.uk/nlp-semantic-text-matching/measuring-the-performance-of-nlp-algorithms/)
8. [Are Information Retrieval Approaches Good at Harmonising Longitudinal Survey Questions in Social Science?](https://arxiv.org/html/2504.20679v1)
9. [The principles of the testing invariance measurement over time (tutorial)](https://archiv.soc.cas.cz/images/Dokumenty/vinopal_pospisilova_invariance_measurement_over_time_tutorial.pdf)
10. [Invariance analyses in large-scale studies - OECD](https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/05/invariance-analyses-in-large-scale-studies_15223d0f/254738dd-en.pdf)
11. [Using a multilevel structural equation model (Davidov et al., 2012)](https://www.ssoar.info/ssoar/bitstream/handle/document/44485/ssoar-jccp-2012-4-davidov_et_al-Using_a_multilevel_structural_equation.pdf)
12. [Measurement Invariance (MI) in CFA and Differential Item Functioning](https://www.lesahoffman.com/PSYC948/948_Lecture9_Invariance.pdf)
13. [How to Compare Means of Latent Variables across Countries (Comsa)](https://www.sav.sk/journals/uploads/05130941Comsa%20AF%20OK%20corrected%20by%20Comsa.pdf)
14. [Full Html - Educational Methods & Psychometrics (EMP)](https://emp-open.de/Full_text?article_id=96)
15. [Measurement Invariance (psycModel R)](https://search.r-project.org/CRAN/refmans/psycModel/html/measurement_invariance.html)
16. [Using Alignment optimization in establishing measurement invariance (Mplus)](https://mplus.sites.uu.nl/wp-content/uploads/sites/24/2012/07/Alignment_Mplus_meeting-Jan.pdf)
17. [Alignment - Mplus (Asparouhov & Muthén, 2014)](https://www.statmodel.com/Alignment.shtml)
18. [Measurement Invariance Testing with Alignment Method - ERIC](https://files.eric.ed.gov/fulltext/EJ1279969.pdf)
19. [Multiple Group Alignment for Exploratory and Structural Equation Models](https://www.statmodel.com/download/Alignment.pdf)
20. [What to do when scalar invariance fails (Marsh et al., 2016)](https://acuresearchbank.acu.edu.au/download/c6900e78c84526e8beb549f02c00c2ce6818795c8f177e9bf7a7cf571963a816/329451/Marsh_2016_What_to_do_when_scalar_invariance_fails.pdf)
21. [Alignment Procedure for Linking under Approximate Invariance (sirt R)](https://search.r-project.org/CRAN/refmans/sirt/html/invariance.alignment.html)
22. [Measurement invariance in the social sciences - KU Leuven (Leitgöb et al., 2023)](https://ppw.kuleuven.be/okp/_pdf/Leitgoeb2023MIITS.pdf)
23. [Measurement invariance in the social sciences (SciSpace)](https://scispace.com/pdf/measurement-invariance-in-the-social-sciences-historical-7y1bqcak.pdf)
24. [Measurement Invariance Conventions and Reporting (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5145197/pdf/nihms797990.pdf)
25. [Alignment-Within-CFA (AWC) (Marsh et al., 2016 pre-pub)](https://www.statmodel.com/download/Marsh%20et%20al%202016%20Alignment%20pre-pub%20version%2010AUG2016.pdf)
26. [Measurement Invariance: From Configural to Useful Decisions](https://fatihozkann.com/blogs_backup_20251220_160512/funded/)
27. [Measurement Invariance in Cross-National Studies (Köln)](https://kups.ub.uni-koeln.de/30191/)
28. [Measurement Invariance in Cross-National Studies (SAGE)](https://journals.sagepub.com/doi/pdf/10.1177/0049124118789708)
29. [Entropy and diversity (Jost, 2006 PDF)](https://pdodds.w3.uvm.edu/research/papers/others/2006/jost2006a.pdf)
30. [Entropy and diversity (Jost, 2006 Wiley)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.2006.0030-1299.14714.x)
31. [Shannon Diversity Index (NIST)](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/shannon.htm)
32. [Diversity index - Wikipedia](https://en.wikipedia.org/wiki/Shannon_index)
33. [The effect of decreasing response options (Landrum & Braitman, 2008)](https://static1.squarespace.com/static/5681703a9cadb6554dbf0c78/t/56f6a0d2e707eb33bf559d31/1459003605534/The+effect+of+decreasing+response+options+on+students'+evaluation+of+instruction+(Landrum+&+Braitman,+2008).pdf)
34. [한국언론진흥재단 — 2022 언론수용자 조사 표본 변경](https://kpf.or.kr/front/research/consumerDetail.do?seq=593659)
35. [한국언론진흥재단 (self detail)](https://www.kpf.or.kr/front/research/selfDetail.do?seq=593658)
36. [2022 언론수용자 조사 (인포그래픽) - Scribd](https://www.scribd.com/document/907585391/2022-%EC%96%B8%EB%A1%A0%EC%88%98%EC%9A%A9%EC%9E%90-%EC%A1%B0%EC%82%AC-%EC%9D%B8%ED%8F%AC%EA%B7%B8%EB%9E%98%ED%94%BD)
37. [Sample weighting (IPUMS forum)](https://forum.ipums.org/t/sample-weighting/2936/2)
38. [Considerations before Pooling Data (Statistics Canada, 2001)](https://www.statcan.gc.ca/en/statistical-programs/document/8011_D1_T9_V1-eng.pdf)
39. [Survey Weighting - AAPOR](https://aapor.org/wp-content/uploads/2023/01/Presentation-Slides.pdf)
40. [Age-period-cohort analysis of repeated cross-section surveys (Duke)](https://scholars.duke.edu/publication/724412)
41. [Bayesian Inference for Hierarchical APC Models (Yang & Land, 2006 Wiley)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9531.2006.00174.x)
42. [Aging, Cohorts, and Methods (Yang, 2010)](https://yangclaireyang.web.unc.edu/wp-content/uploads/sites/5145/2013/08/Yang-2010-Aging-Cohorts-and-Methods1.pdf)
43. [Package 'apc' - Age-Period-Cohort Analysis (CRAN)](https://cran.r-project.org/web/packages/apc/apc.pdf)
44. [Agreement with Korean General Social Survey (ESS)](https://www.europeansocialsurvey.org/news/article/agreement-korean-general-social-survey)
45. [성균관대학교 서베이리서치센터 (KGSS)](https://kgss.skku.edu)
46. [한국미디어패널조사 - 미디어통계포털](https://stat.kisdi.re.kr/kor/contents/ContentsList.html)
47. [미디어패널조사 - 미디어통계포털 (KISDI)](https://stat.kisdi.re.kr/kor/board/BoardList.html?board_class=BOARD30&video_div=VIDEO002&srcPageUnit=4)
48. [<2024 언론수용자 조사> 결과 발표 (KPF)](https://www.kpf.or.kr/front/board/boardContentsView.do?board_id=246&contents_id=8cfa6b1bf19b4b6ab16a7b970bb1512e)
49. [Korean General Social Survey (KGSS): Cumulative File, 2003-2016 (ICPSR)](https://www.icpsr.umich.edu/web/ICPSR/studies/37214)
50. [2025 언론수용자 조사 원본 데이터 - 한국언론진흥재단](https://kpf.or.kr/front/mediaStats/mediaStatsDetail.do?miv_pageNo=&miv_pageSize=&total_cnt=&LISTOP=&mode=W&idx=29322239)
