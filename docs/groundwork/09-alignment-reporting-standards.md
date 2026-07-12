# 제3장 연구방법: 연도 간 측정 비동등성과 Alignment Optimization

이 문안은 반복횡단면 설문에서 연도를 집단으로 설정하고, 동일 구성개념의 연도별 잠재평균을 비교하기 위한 방법론 절로 구성하였다. 실제 alignment 출력이 확보되지 않은 상태에서 결과를 임의로 생성하지 않았으며, 그림 3-2는 실제 결과가 아닌 히트맵 표시 규칙을 설명하는 설계도이다.

## 3.1 분석 목적과 기본 원칙

본 연구는 조사연도에 따라 문항의 표현, 응답범주 및 응답행태가 달라질 수 있다는 점을 고려하여 연도 간 측정동일성을 검토하였다. 관측점수 평균의 단순 비교는 동일한 잠재특성을 가진 응답자에게 각 문항이 연도별로 동일하게 작동한다는 가정을 필요로 하므로, 연도를 집단으로 설정한 다집단 확인적 요인분석을 우선 실시하였다.

완전한 scalar invariance가 성립하지 않는 경우에는 alignment optimization을 적용하였다. Alignment는 configural model에서 추정된 집단별 loading과 intercept 또는 threshold를 출발점으로 삼아 집단별 요인평균과 요인분산을 재조정하고, 전체 측정 비동등성을 최소화하는 해를 탐색한다. 이 과정은 소수의 큰 비동등성과 다수의 근사적으로 동일한 측정모수를 갖는 단순구조를 찾도록 설계되었다 ([Asparouhov & Muthén, 2014](https://www.tandfonline.com/doi/abs/10.1080/10705511.2014.919210)).

## 3.2 분석 단위와 사전 정합화

분석단위는 각 조사연도의 개인 응답이며, 조사연도를 alignment의 집단변수로 사용하였다. 동일 구성개념에 포함되는 문항은 연도별 코드북, 질문문, 응답범주와 결측값 정의를 대조하여 정합화하였다. 질문문 또는 응답척도의 실질적 의미가 달라 동일 문항으로 간주하기 어려운 경우에는 강제로 연결하지 않고 구조적 결측으로 처리하였다.

문항 정합화 이후 각 연도에서 동일한 요인 수와 동일한 문항-요인 대응관계를 갖는 CFA 모형을 지정한다. Alignment는 적절한 configural model을 전제로 하므로, 특정 연도에서 요인구조가 현저히 다르거나 국소 부적합이 큰 경우 해당 연도를 자동으로 잠재평균 비교에 포함하지 않는다 ([Muthén & Asparouhov, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4162377/)).

### 표 3-1. 연도 간 문항 정합화 및 분석 포함 기준

| 점검 영역 | 포함 기준 | 제외·별도 처리 기준 | 기록 항목 |
|---|---|---|---|
| 구성개념 | 동일한 이론적 정의 | 개념 정의 또는 측정대상이 변경됨 | 구성개념명, 조작적 정의 |
| 질문문 | 의미가 동일하거나 표현만 경미하게 변경됨 | 핵심 대상·기간·행동의 의미가 변경됨 | 연도별 원문, 변경 사유 |
| 응답범주 | 동일하거나 일대일 재코딩 가능 | 범주 통합으로 정보 복원이 불가능 | 원척도, 공통척도, 재코딩식 |
| 결측값 | 무응답·비해당을 구분 가능 | 비해당과 무응답을 분리할 수 없음 | 원코드, 변환코드 |
| 요인구조 | 동일한 요인 수와 문항 배치 | 문항의 요인 귀속이 실질적으로 변경됨 | CFA 모형식, 제외 근거 |
| 조사 미실시 | 해당 없음 | 구조적 결측으로 표시 | NA 사유, 영향받는 연도 |

## 3.3 추정 절차

분석은 다음 순서로 수행하였다. 먼저 각 연도에 동일한 요인구조를 지정한 configural model을 적합하고 CFI, TLI, RMSEA, SRMR과 국소 적합도를 검토하였다. 다음으로 configural model의 적합성이 수용 가능한 경우 alignment optimization을 실시하여 연도별 요인평균, 요인분산, loading 및 intercept 또는 threshold를 추정하였다.

Alignment 해의 평가는 단순히 모형이 수렴했는지에 그치지 않고, loading과 intercept 또는 threshold에서 비동등으로 판정된 문항×연도 조합의 비율, 모수별 \(R^2\), 비동등성 효과크기, 비동등성이 특정 문항에 집중되는지 여부를 함께 사용하였다. Alignment의 적합도는 configural model과 동일하므로, alignment 이후 별도의 전역 적합도 개선을 근거로 결과를 채택하지 않았다.

![Alignment 기반 연도별 잠재평균 비교 판정 흐름](https://d2z0o16i8xm8ak.cloudfront.net/71d3934c-0f0e-4522-b2a0-1034f4972bee/d14aba0e-cc1d-4958-b297-48f24a2e7fde/alignment-decision-flow.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9kMnowbzE2aTh4bThhay5jbG91ZGZyb250Lm5ldC83MWQzOTM0Yy0wZjBlLTQ1MjItYjJhMC0xMDM0ZjQ5NzJiZWUvZDE0YWJhMGUtY2MxZC00OTU4LWIyOTctNDhmMjRhMmU3ZmRlL2FsaWdubWVudC1kZWNpc2lvbi1mbG93LnBuZz8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzg0NDI1MDE5fX19XX0_&Signature=BLHFxfdT13qWgEIniybDbRssWV1RgH9Z9hUcQU0kuY1zb4HJ-WhgS1tw~LmGbDyLdAMawQ7dgrdXmJufP8WO-aqToAJmgcAAQBRdvZJQ~NbR2HBnm1lSKEaWpkc6Z4hGI5IAR0MLOYGllQvWMc3KaRnld0U9qRM4QAXa-Mr6UX-CVrfBP2pfa-A4xPLmQHg2BfV98iQX4gvKLDSRV3ArpRj2WgpQggwuQSpi9zeYQaqDO4w4jBKIob1Wej2zw3H4-saN51GDI~5UATEa3LJZEtzFyMqeSGOiLqjJ9-vIGtwpUBzcUgzM1r51t7zA0uMyt5Ci5JWWNVklUT-VqKxang__&Key-Pair-Id=K1BF7XGXAIMYNX)

**그림 3-1. Alignment 기반 연도별 잠재평균 비교 판정 흐름.** Loading과 intercept 또는 threshold의 비동등 비율을 각각 산출하고, 전체 결합 비율도 보조적으로 보고한다. 25%는 절대적인 통계적 임계값이 아니라 경험적 준거이므로 경계 또는 초과 조건에서는 Monte Carlo 검증과 민감도 분석을 추가한다.

## 3.4 비동등 비율과 판정 기준

Loading의 비동등 비율은 비동등으로 판정된 loading의 문항×연도 조합 수를 추정 가능한 전체 loading 조합 수로 나누어 계산하였다. Intercept 또는 threshold도 같은 방식으로 별도 계산하였다. 조사되지 않은 문항과 구조적 결측은 분모에서 제외하되, 제외된 문항과 연도는 표 3-1 및 그림 3-2에서 NA로 명시하였다.

\[
\text{Loading 비동등 비율}
=
\frac{\text{비동등 loading 문항×연도 조합 수}}
{\text{추정 가능한 전체 loading 문항×연도 조합 수}}
\times 100
\]

\[
\text{Intercept 비동등 비율}
=
\frac{\text{비동등 intercept 문항×연도 조합 수}}
{\text{추정 가능한 전체 intercept 문항×연도 조합 수}}
\times 100
\]

Muthén과 Asparouhov는 60개 집단, 집단당 1,000명 조건에서 최대 20%의 비동등 측정모수를 포함한 모형에서 만족스러운 결과를 확인했으며, 약 25%를 신뢰 가능한 alignment 결과를 위한 경험적 상한으로 제안하였다. 저자들은 이를 “rough rule of thumb”으로 표현하고 25%를 넘는 경우 실제 분석 조건을 반영한 Monte Carlo 검증을 권고하였다 ([Muthén & Asparouhov, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4162377/)).

Flake와 McCoach는 4범주 다범주 문항, 3·9·15개 집단, 집단당 500명 조건에서 비동등 비율 0·14·28·43%를 검토하였다. 작은 또는 중간 수준의 비동등성에서는 대체로 양호한 모수 회복을 보였지만 극단적 조건에서는 성능이 저하되고, 비동등성 검정은 보수적이며 심하게 편포된 문항에서 검정력이 낮았다 ([Flake & McCoach, 2018](https://www.tandfonline.com/doi/full/10.1080/10705511.2017.1374187); [Wen & Hu, 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9263979/)). 따라서 본 연구에서는 25% 이하 여부만으로 잠재평균 비교를 자동 승인하지 않고 표 3-2의 다중 기준을 적용하였다.

### 표 3-2. Alignment 결과의 단계별 판정 기준

| 조건 | 기본 판정 | 필수 추가 점검 | 잠재평균 해석 범위 |
|---|---|---|---|
| Loading과 intercept/threshold가 모두 20% 이하 | 비교적 안정 | 효과크기, \(R^2\), 비동등 집중도 | 조건을 명시하고 비교 |
| 어느 한 비율이 20% 초과∼25% 이하 | 경계 | Monte Carlo, 민감도 분석 | 검증 통과 시 조건부 비교 |
| 어느 한 비율이 25% 초과 | 불확실 | Monte Carlo 필수, 문항 제거·재정의 모형 비교 | 안정성 확인 전 비교 보류 |
| 여러 문항에 유사한 크기의 비동등성이 광범위하게 분포 | Alignment 가정 위반 가능 | 다른 부분불변·정규화 방법 비교 | 제한적 해석 |
| 비동등성이 소수 문항·연도에 집중 | 국소 비동등 | 해당 셀의 질문문·척도 변경 확인 | 민감도 결과가 일치하면 비교 |
| 문항 삭제 또는 척도 변경으로 연결 불가능 | 구조적 단절 | 해당 연도를 별도 분석 | 직접 평균비교 제외 |

최근 적용 연구는 loading과 intercept를 별도로 계산하여 각 유형이 25% 미만인지 평가하였다. 예를 들어 Cintron 등은 16개 집단과 8개 문항에서 intercept 5%, loading 24%를 보고하고 두 유형을 별도로 판정하였다 ([Cintron et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10339173/)). 반면 원 연구의 실증 예시는 threshold 33%와 loading 11%를 평균한 전체 22%도 함께 제시했으므로, 본 연구에서는 유형별 비율을 주 판정 기준으로 사용하고 전체 결합 비율을 보조지표로 보고한다 ([Muthén & Asparouhov, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4162377/)).

## 3.5 비동등성 히트맵

연도별 비동등성의 위치와 집중도를 확인하기 위해 문항을 행, 조사연도를 열로 하는 히트맵을 작성한다. 회색은 불변, 청록색과 문자 L은 loading 비동등, 주황색과 문자 I는 intercept 또는 threshold 비동등, 적색과 문자 L+I는 두 모수의 동시 비동등을 나타낸다. 조사되지 않았거나 문항 변경으로 연결할 수 없는 셀은 점선 테두리와 NA로 표시하여 통계적 비동등성과 구조적 결측을 구분한다.

![연도×문항 측정 비동등성 히트맵 설계도](https://d2z0o16i8xm8ak.cloudfront.net/71d3934c-0f0e-4522-b2a0-1034f4972bee/3fc935b9-6968-466d-9d7e-09c70f70386b/alignment-heatmap-blueprint.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9kMnowbzE2aTh4bThhay5jbG91ZGZyb250Lm5ldC83MWQzOTM0Yy0wZjBlLTQ1MjItYjJhMC0xMDM0ZjQ5NzJiZWUvM2ZjOTM1YjktNjk2OC00NjZkLTlkN2UtMDljNzBmNzAzODZiL2FsaWdubWVudC1oZWF0bWFwLWJsdWVwcmludC5wbmc~KiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4NDQyNTAxOX19fV19&Signature=L7BxR58uV6X1pCFzwrxzeYhN5V4A5FAoQioz-zLr6ETvmAr41KMwrKH9JvCjNtHEsf0m3nOYyh4JZdGtw8OPFfRxSa6I0BOTx1qNqcMw5BA5nILPdiG-HImqngtI2dylsBpldpAhUOJkxc9z41pfCywMZYnLa3gS2NQr52-xY4GXzNy04FTxWuJtP1NZQaSyUtiE5LnvY43kwV7ff~WwSQZvHxk7nG~FDEktCgapaQ5QfUwSJFTv2kSRREkS-Ki6z1EmiKiGxf3cugJBNJ1oxJVQNH1qiGEa1XpkzW-IzI~j4h2-LksrWsGye~zGnwa~OfG4w1SXrVNNEOjUhEM-KQ__&Key-Pair-Id=K1BF7XGXAIMYNX)

**그림 3-2. 연도×문항 측정 비동등성 히트맵 설계도.** 그림의 셀은 판독 규칙을 설명하기 위한 예시이며 실제 분석 결과가 아니다. 최종 제출본에서는 동일한 범례를 유지하고 alignment 출력에서 판정된 실제 문항×연도 조합으로 셀을 대체한다.

히트맵은 색상만으로 정보를 전달하지 않도록 모든 비동등 셀에 L, I 또는 L+I 기호를 함께 표시한다. 특정 연도에 비동등 셀이 집중되면 해당 연도의 질문문, 응답척도, 조사모드 및 표본구성 변화를 재확인하고, 특정 문항에 집중되면 문항 제거 또는 재정의 모형을 민감도 분석으로 추가한다.

## 3.6 Monte Carlo 검증

비동등 비율이 20%를 초과하거나 요인평균의 순위가 핵심 결론에 직접 영향을 미치는 경우에는 실제 alignment 추정치를 모집단 값으로 사용하여 Monte Carlo 모의실험을 수행하도록 설계하였다. 각 반복표본에서 동일한 alignment model을 재추정하고, 생성된 연도별 요인평균과 추정된 요인평균 사이의 상관, 편향, 평균제곱근오차와 순위 변동을 평가한다.

원 연구는 생성된 요인평균과 추정 요인평균 간 상관이 적어도 .98일 때 집단별 요인평균 순위를 신뢰할 수 있는 것으로 판단하였다 ([Muthén & Asparouhov, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4162377/)). 본 연구도 상관 \(r \ge .98\)을 기본 기준으로 사용하되, 인접 연도 간 순위 역전과 실질적 효과크기 변화가 반복적으로 발생하는 경우에는 평균순위 비교를 제한하였다.

### 표 3-3. Monte Carlo 검증 보고 항목

| 보고 항목 | 산출 방식 | 판정 목적 |
|---|---|---|
| 반복횟수 | 사용한 Monte Carlo 반복표본 수 | 추정 안정성 확인 |
| 수렴률 | 수렴한 반복 수 / 전체 반복 수 | 모형 식별·수렴 문제 확인 |
| 요인평균 상관 | 생성값과 추정값의 연도별 상관 | 연도 순위 회복 여부 |
| 평균 편향 | 추정값과 생성값 차이의 평균 | 체계적 과대·과소 추정 확인 |
| RMSE | 추정오차 제곱평균의 제곱근 | 전체 추정오차 평가 |
| 순위 일치율 | 기준 순위와 동일한 반복의 비율 | 핵심 연도 순위의 안정성 |
| 95% 구간 포함률 | 생성값을 포함한 신뢰구간 비율 | 불확실성 추정의 적절성 |

## 3.7 강건성 및 민감도 분석

Alignment 결과의 강건성을 확인하기 위해 최소한 다음 분석을 병행한다.

- 비동등성이 집중된 문항을 포함한 모형과 제외한 모형의 연도별 요인평균 순위를 비교하였다.
- Loading 및 intercept/threshold 비동등 비율을 각각 적용한 판정과 전체 결합 비율을 적용한 판정을 비교하였다.
- 관측점수 평균과 alignment 잠재평균의 연도별 변화 방향을 비교하되, 두 결과가 불일치하면 관측점수 결과를 측정비동등성에 민감한 결과로 해석하였다.
- 특정 연도의 문항 삭제 또는 척도 변경이 확인되면 해당 연도를 포함한 모형과 제외한 모형을 비교하였다.
- 비동등 모수의 통계적 유의성뿐 아니라 원척도 단위와 표준화 단위의 효과크기를 함께 확인하였다.

Alignment는 문항 수준의 DIF 원인을 확정하는 방법이 아니라 잠재평균과 분산의 비교 가능성을 평가·보정하는 최적화 방법이다. 개별 문항의 차별기능 자체가 연구대상인 경우에는 별도의 DIF 분석을 병행하는 것이 적절하다 ([Cintron et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10339173/)).

## 3.8 결과 보고 규칙

최종 결과에서는 configural model 적합도, alignment 식별방식, 추정량, 전체 및 유형별 비동등 비율, 모수별 \(R^2\), 비동등 히트맵, Monte Carlo 검증 결과를 함께 보고한다. “측정동일성이 확보되었다”는 이분법적 표현 대신, 어느 문항과 연도에서 어떤 유형의 비동등성이 발견되었고 그것이 잠재평균 순위에 어느 정도 영향을 주었는지를 기술한다.

### 표 3-4. 최종 보고에 포함할 Alignment 정보

| 구분 | 필수 보고 내용 |
|---|---|
| 자료 구조 | 조사연도, 분석대상 수, 연도별 표본크기, 문항 수 |
| 문항 정합화 | 공통문항 기준, 재코딩, 구조적 결측, 제외 사유 |
| Configural model | 요인구조, 추정량, CFI, TLI, RMSEA, SRMR |
| Alignment 설정 | FIXED/FREE, 기준집단, 소프트웨어와 버전 |
| 비동등 비율 | Loading, intercept/threshold, 전체 결합 비율 |
| 국소 진단 | 비동등 문항×연도, \(R^2\), 효과크기, simplicity function 기여도 |
| 시각화 | 그림 3-2 형식의 실제 결과 히트맵 |
| Monte Carlo | 반복횟수, 수렴률, 요인평균 상관, 편향, RMSE, 순위 안정성 |
| 민감도 분석 | 문항·연도 제외 결과, 관측점수와 잠재평균 비교 |
| 해석 제한 | 비교 제외 연도, 방향성만 해석한 결과, 확인되지 않은 원인 |

## 3.9 방법론 선택의 요약

본 연구는 완전한 scalar invariance의 기계적 충족 여부보다 측정 비동등성을 고려한 연도별 잠재평균 비교의 안정성을 평가하는 데 목적을 둔다. 이에 따라 25% 기준은 단독 합격선이 아닌 선별적 경고기준으로 사용하고, 20%를 초과하는 경계 조건에서는 실제 자료 구조를 반영한 Monte Carlo 검증을 실시하도록 분석 절차를 설계하였다. 비동등성이 광범위하거나 구조적 문항 단절이 확인된 경우에는 해당 연도의 직접 평균비교를 포기하고 변화의 방향 또는 비교 가능한 연도 구간만 제한적으로 해석한다.

## 출처 URL 및 발행연도

| 출처 | 발행연도 | URL |
|---|---:|---|
| Asparouhov & Muthén, *Multiple-Group Factor Analysis Alignment* | 2014 | https://doi.org/10.1080/10705511.2014.919210 |
| Muthén & Asparouhov, *IRT Studies of Many Groups: The Alignment Method* | 2014 | https://doi.org/10.3389/fpsyg.2014.00978 |
| Flake & McCoach, *An Investigation of the Alignment Method With Polytomous Indicators* | 2018 | https://doi.org/10.1080/10705511.2017.1374187 |
| Pokropek, Davidov, & Schmidt, *A Monte Carlo Simulation Study* | 2019 | https://doi.org/10.1080/10705511.2018.1561293 |
| Wen & Hu, *Investigating the Applicability of Alignment* | 2022 | https://doi.org/10.3389/fpsyg.2022.845721 |
| Cintron, Matthay, & McCoach, *Testing for Intersectional Measurement Invariance* | 2023 | https://doi.org/10.1111/1475-6773.14189 |
| Cao, *How Much Is Too Much?* | 2026 | https://doi.org/10.1080/10705511.2026.2654815 |

주: Cao(2026)의 서지정보와 온라인 게재 사실은 확인되지만, 공개된 메타데이터만으로 연구의 구체적 시뮬레이션 결론과 25% 기준에 대한 최종 권고는 확인되지 않았다.
