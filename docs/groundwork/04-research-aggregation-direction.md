# 뉴스 소비 건강지수: 합성지표 설계 방법론 보고서
**한국언론진흥재단 언론수용자 조사(N=6,000) 기반 '건강지수' 설계를 위한 전문가 검토서**

> 출처: Perplexity Deep Research (2026-06-24) — Task 03 지수 집계·방향성 갈림길 해소용 외부 조사.
> 반영: 집계=기하평균 `NCHI=√(T×D)` 주 + 산술 강건성, 방향성=단조 v1(신뢰 역U는 한계명시·v2), 2축 4사분면 페르소나.
> 설계 적용본: [`docs/design/preprocessing-design.md`](../design/preprocessing-design.md) · 산출 노트북: [`notebooks/03-health-index.ipynb`](../../notebooks/03-health-index.ipynb) · SSOT: [`src/news_health_features.py`](../../src/news_health_features.py).
> ⚠️ 인용 수치(KPF·로이터 보고서값 등)는 원자료 재검증 전까지 보고서 직접 인용 금지.

***

## 개요

본 보고서는 신뢰지수(Trust, 가중평균 62.5)와 다양성지수(Diversity, 가중평균 26.4)를 단일 '뉴스 소비 건강지수(News Consumption Health Index, NCHI)'로 집계하는 방법론을 검토한다. 두 지수의 상관계수 r = 0.077은 사실상 독립이므로, 집계 방식 선택과 각 축의 방향성 정의가 지수의 타당도를 결정하는 핵심 과제다. OECD/JRC 핸드북 기준, 실제 웰빙지수 사례, 그리고 뉴스 신뢰·다양성 관련 학술 문헌을 종합하여 각 질문에 대한 비교표, 권고안, 핵심 인용을 제시한다.

***

## 질문 1: 집계 방식 선택

### 1-1. 주요 집계 방식 비교

OECD/JRC Handbook(2008)과 JRC-COIN Step 6 가이드라인은 집계 방식 선택의 핵심 기준으로 **보완성(compensability)** — 한 축의 강점이 다른 축의 결핍을 대체할 수 있는가 — 을 제시한다.[^1][^2]

| 집계 방식 | 수식(두 하위지수 T, D) | 보완성 | r≈0 일 때 영향 | 장점 | 단점 | 웰빙지수 적용 사례 |
|---|---|---|---|---|---|---|
| **산술평균** | \(\frac{T+D}{2}\) | 완전 보완 | 두 변수가 독립이어도 평균 정보손실 없음 | 단순·직관적 커뮤니케이션 | T=100, D=0이어도 점수 50점 → 결핍 은폐 | OECD BLI(차원 내), ONS Health Index[^3] |
| **기하평균** | \(\sqrt{T \times D}\) | 부분 보완 | 한 축이 극단적으로 낮으면 페널티 자동 부과 | 불균형 프로파일 페널티, 이론적 정당성 명확 | 한 축이 0이면 지수 붕괴(보정 필요) | UN HDI 2010~ 전환[^4][^5] |
| **거리기반(이상점)** | \(1 - \frac{1}{2}\sqrt{(1-T)^2+(1-D)^2}\) (0~1 정규화) | 비보완 가능 | 두 축 동시 이상점에서의 거리를 균등 반영, r과 무관 | 이상점 개념의 이론적 명확성, 비대칭 페널티 설정 가능 | 2개 지수에서 기하평균과 결과 유사, 이상점 선택 임의성 | MRP-WSCI(이탈리아 지역 QoL)[^6] |
| **MPI/AMPI (Mazziotta-Pareto Index)** | \(\overline{X} \cdot (1 - cv \cdot S)\) (cv: 변동계수, S: ±1 부호) | 비보완 | 두 지수가 매우 이질적(신뢰 62.5 vs 다양성 26.4)이면 페널티 극대화 | 불균형에 직접 페널티, ISTAT 공식 채택 | 정규화 범위 의존성, 해석 복잡 | ISTAT 이탈리아 BES 웰빙지수[^7] |

### 1-2. 보완성 관점

산술평균은 "완전하고 불변적인 대체가능성(perfect and constant substitutability)"을 전제하며, 이는 신뢰가 낮아도 다양성이 높으면 보상받는 구조를 만든다. 반면 기하평균은 한 지수가 낮을수록 그 비율만큼 페널티가 커지는 **부분 보완성**을 보장하며, UNDP가 2010년 HDI를 산술평균에서 기하평균으로 전환한 것은 "한 차원의 낮은 성취를 다른 차원의 높은 성취로 선형 보상받는 구조"를 제거하기 위해서였다. 대안적 집계로 Generalized Mean-Min 방법이 제안되어 있으며, 이는 불균형 프로파일에 대한 가산 페널티를 부과함으로써 기하평균보다 보완성을 더욱 억제한다.[^4][^5][^8][^1]

### 1-3. r ≈ 0.08 조건에서의 집계 방식 선택

두 하위지수가 거의 무상관일 때, 각 집계 방식의 동작 방식은 달라진다. JRC-COIN 가이드는 "집계에 앞서 충분히 양호한 상관 구조(good enough correlation structure)가 필요하다"고 명시하며, r이 낮은 경우 집계 전에 각 차원이 독립적 구성개념임을 이론적으로 확인할 것을 권고한다. r ≈ 0.077은 두 지수가 **서로를 측정하지 않는다**는 것을 의미하므로, 하나의 숫자로 합산하는 것의 이론적 정당성에 도전한다. 그러나 각 차원이 이론적으로 '건강한 소비'의 독립된 축을 대표한다면 합산은 여전히 가능하며, 이 경우 두 축 모두 충족해야 진정한 '건강'을 달성한다는 관점에서 **비보완적 방식(기하평균 또는 MPI)이 더 적합**하다.[^1]

낮은 상관일 때 주의사항: 산술평균은 현재 신뢰가 높고(62.5) 다양성이 낮은(26.4) 한국 상황에서, 신뢰 강점이 다양성 결핍을 가리는 현상을 유발한다. 기하평균을 쓰면 \(\sqrt{62.5 \times 26.4} \approx 40.6\)으로, 산술평균 \((62.5+26.4)/2 = 44.5\)보다 4점 낮게 계산되어 불균형을 반영한다.

### 1-4. OECD BLI·UN HDI·ONS 건강지수 집계 비교

| 지수 | 운영기관 | 집계 방식 | 보완성 정책 | 두 축 무상관 시 처리 |
|---|---|---|---|---|
| OECD Better Life Index(BLI) | OECD | 차원 내 산술평균; 차원 간 사용자 가중 산술평균 | 완전 보완(사용자가 임의 조합) | 11차원이 각자 독립 — 단일 지수 강제 않음[^9][^10] |
| UN Human Development Index(HDI) | UNDP | 2010~ 기하평균 \((H \times E \times I)^{1/3}\) | 부분 보완 (저조한 차원 페널티) | 세 차원 독립 설계 유지[^4][^11] |
| ONS Health Index(England) | ONS/UK | 도메인 내·간 모두 산술평균, FA 가중 | 완전 보완 | 58개 지표가 다차원, 도메인 구분 후 단계적 집계[^12][^3] |
| OSIS Media Literacy Index | Open Society Institute | z-점수 후 가중 산술합산 | 완전 보완 | 교육·자유도·신뢰 등 이질적 지표를 차등가중 집계[^13][^14] |
| ISTAT BES (이탈리아 웰빙) | ISTAT | AMPI(Mazziotta-Pareto, 비선형) | 비보완 (불균형 페널티) | 불균형 프로파일 직접 패널티[^7] |

### 1-5. 권고안 (질문 1)

> **기하평균을 기본 집계식으로 채택하되, 0값 처리를 위해 하한을 1점으로 설정하고 두 지수를 100점 만점으로 정규화한 상태에서 \( NCHI = \sqrt{T_{norm} \times D_{norm}} \)을 사용한다.**

이유: (1) 신뢰(62.5)와 다양성(26.4)의 현저한 불균형을 가시화하고, (2) UNDP HDI 전환과 같은 이론적 정당성(부분 비보완성)을 확보하며, (3) 연령 등에 따른 다양성 급감을 산술평균보다 민감하게 포착할 수 있기 때문이다. 단, 신뢰 축에 역U자 변환(아래 질문 2 참조)을 적용한 후 기하평균을 계산해야 한다. 보고의 투명성을 위해 단일 NCHI 점수와 함께 신뢰·다양성 2축 산점도(페르소나 사분면)를 항상 병행 제시할 것을 권고한다.[^5][^4]

**핵심 인용 (질문 1)**
1. JRC-COIN Step 6 (Caperna 외, 2023): 기하평균은 "불균형 성과가 항상 페널티를 받는 첫 번째 덜-보완적 선택지"[^2][^1]
2. UNDP (2010): 기하평균은 "균등성 공리(uniformity axiom)를 만족하여 불균형 개발을 패널티화"[^5]
3. Mazziotta & Pareto (2016): MPI는 "평균 수준 측정치 + 불균형량 패널티로 구성되어 비보완성 전제"[^15]
4. OECD/JRC Handbook (2008): "집계 전 상관구조 적합성 확인 필요; 낮은 상관은 이론적 재검토를 요구"[^16][^17]
5. Unipd 연구 (2025): 기하평균과 산술평균이 실제 HDI 점수에서 유사한 경우 많아, 불균형이 극단적일 때 차이가 유의미[^8]

***

## 질문 2: 각 축의 방향성과 최적구간

### 2-1. 신뢰 축: 단조 증가인가, 역U자인가?

'높을수록 건강'이라는 단순 단조 관계는 미디어 신뢰 연구에서 도전받는다. Tsfati & Barnoy (2025)는 신뢰를 **냉소(cynicism) — 회의(skepticism) — 자동신뢰(automatic trust)** 의 연속체로 개념화하며, 냉소와 자동신뢰는 모두 **당파적 추론**에 기반하지만, 회의주의자만이 정치 이념과 독립적으로 미디어를 평가한다고 보고한다. 즉 양 극단이 모두 인식적으로 불건강하다.[^18]

Cappella(2002)는 "언론에 대한 불신이 허위 정보를 믿게 만들 수 있지만, 어느 순간 건전한 불신은 냉소·비방으로 바뀐다"고 경고하며, Pew Research(2020)도 미국 성인 63%가 "회의주의는 건강하지만 맹목적 불신은 해롭다"는 입장임을 보고한다. Kohring & Matthes(2007)는 4차원 신뢰척도(주제 선택성, 사실 선택성, 묘사 정확성, 저널리스트 판단)를 개발하였는데, 이 다차원성 자체가 신뢰가 단일 연속체가 아님을 시사한다.[^19][^20][^21][^22][^23]

**역U자 변환 방안**: 신뢰 원점수를 \(T_{raw}\)라 할 때, '보정된 신뢰(calibrated trust)' 영역 \([T_{low}, T_{high}]\)를 전문가 합의로 사전 설정하고 변환식을 적용한다:

\[
T_{adj} = 100 \cdot \exp\left(-\frac{(T_{raw} - T_{opt})^2}{2\sigma^2}\right)
\]

여기서 \(T_{opt}\)는 최적 신뢰 수준(예: 원점수 기준 50~65점 구간의 중앙), \(\sigma\)는 허용 범위이다. 그러나 역U자 처리는 최적점 설정의 자의성 문제를 수반하므로, 이 보고서는 **일차적으로 단조 처리를 유지하되**, 신뢰의 '질'을 보완하는 별도 척도(예: 뉴스 리터러시, 비판적 평가 행동)를 하위지수에 포함시키는 방식으로 역U자 효과를 간접 반영할 것을 제안한다.[^24][^23]

한국 맥락: 디지털 뉴스 리포트 2025에서 한국 뉴스 신뢰도는 31%(48개국 중 37위)로 전체 신뢰 평균(40%)보다 낮으며, "뉴스 전반" 신뢰(31%)와 "자신이 이용하는 뉴스" 신뢰(39%) 간 8%p 격차는 선택적 신뢰 구조를 시사한다. 이는 냉소적 공중이 한편 자신이 이미 신뢰하는 소스에는 자동신뢰 패턴을 보인다는 Tsfati (2025)의 발견과 일치한다.[^25][^26][^27][^18]

### 2-2. 다양성 축: 단조 증가인가, 최적구간인가?

다양성이 높을수록 건강하다는 직관은 정보 과잉(information overload) 문헌에서 수정된다. Oxford 정보 과잉 연구(Klerings 외, 2015 인용)는 정보량에 따른 의사결정 품질이 "스위트 스팟(sweet spot)" 이후 하락하며, **과도한 새로운 정보는 불안·과부하**, 지나친 중복은 **지루함**을 야기한다고 분석한다. Park(2019) 역시 지각된 뉴스 과잉이 뉴스 회피와 선택적 노출을 매개한다고 보고한다.[^28][^29]

다양성 관련 두 가지 규범적 입장의 긴장:
- **민주적 다원주의 입장**: 다양한 출처 이용은 에코챔버·필터버블을 방지하고 사회적으로 건강한 정보식단을 보장한다[^30]
- **뉴스 다이어트 질 입장**: 양보다 질이 중요하며, UOC 연구(2024)는 유럽 5개국 포커스그룹에서 "건강한 미디어 다이어트는 양적 다양성보다 **질 높은 정보원**과 **균형 잡힌 소비**"라고 정의된다고 보고한다[^31]

한국 언론수용자 조사에서 다양성지수(Richness)가 연령 높을수록 급감하는 패턴은 KISDI(2023) 연구결과와 일치하는데, 60대 이상은 미디어 리터러시와 비판적 이해 역량이 가장 낮고, 유튜브 단일 채널 집중도가 높다. 이는 다양성 하락이 단순 정보량 감소가 아니라 **알고리즘 의존 심화**와 결부된다.[^32][^33][^34]

결론적으로 다양성 축은 **하한(너무 낮으면 불건강)은 명확하나, 상한(너무 많으면 불건강)의 경험적 근거는 개인 차원에서 약하다**. 따라서 현재 한국 상황(평균 26.4로 낮은 수준)에서는 **단조 증가** 처리가 타당하다. 다만 최대 소비자(상위 5% 이상)에 대해서는 별도 분석으로 과잉 소비 위험을 모니터링할 것을 권고한다.

### 2-3. 각 축의 방향성 처리 결정표

| 축 | 이론적 방향 | 학술 합의 수준 | 권고 처리 | 보완 조치 |
|---|---|---|---|---|
| **신뢰** | 역U자형(냉소↓, 맹신도↓, 보정신뢰↑) | 중간 (냉소vs.신뢰 논쟁 진행 중) | 단조 처리(1차)로 진행 + 리터러시 교차 지표로 보완 | 비판적 평가 행동 부가 지표 권고[^18][^23] |
| **다양성** | 단조 증가형(낮을수록 건강 위협) | 높음 (과잉 임계점의 개인차 인정) | 단조 증가 처리 | 상위 분포 이상점 모니터링 권고[^28][^31] |

**핵심 인용 (질문 2)**
1. Tsfati & Barnoy (2025, *Communication Research*): "냉소자와 자동신뢰자는 모두 당파적 추론에 기반 — 회의주의자만이 이념에서 독립적"[^18][^25]
2. Li (2025, *New Media & Society*): "모든 회의주의가 '건강한' 회의주의는 아님 — 정확성 동기vs.정체성 동기 회의주의 구별 필요"[^23]
3. Pew Research (2020): "미국 성인 63%가 회의주의는 건강하지만 과도한 불신은 유해하다고 인식"[^22][^19]
4. Oxford 정보과잉 연구(Klerings 외 인용, 2015): "정보량과 의사결정 품질 관계에 '스위트 스팟' 존재 — 이후 과부하"[^28]
5. UOC 연구 (2024): "건강한 미디어 다이어트는 양적 다양성보다 양질의 정보원과 균형 소비로 정의"[^31]

***

## 질문 3: 선행 유사 사례

### 3-1. 국내 사례

| 지수명 | 운영기관 | 발표 연도 | 구성 지표 | 집계 방식 | 건강 방향 정의 | 시행 여부 |
|---|---|---|---|---|---|---|
| **미디어 리터러시 지수 (방통위)** | 방송통신위원회 × 미디어미래연구소 | 2020 | 비판 역량, 이용 역량, 생산·표현 역량, 사회적 소통, 자기보호, 태도 (6개 역량) | 가중 산술평균 (역량별 점수 합산) | 전 역량 '높을수록 건강' 단조 | ✅ 시행 중 (2020~)[^35][^36] |
| **미디어 리터러시 지수 (KISDI)** | 정보통신정책연구원 | 2023~ | 비판적 이해 역량 중심, 5개 행동지표 (1~5점) | 평균 집계 | 높을수록 건강, 연령·학력 변인 교차 | ✅ 시행 중[^37][^34] |
| **대학내일20대연구소 미디어 리터러시 지수** | 민간 | 2018 | 뉴스 접근, 이해, 창작, 공유 4개 영역 | 산술평균, 100점 환산 | 전 영역 높을수록 건강, 종합 평균 60.2점 | ✅ 1회 조사(비공식)[^38] |
| **OSIS 미디어 리터러시 인덱스 (한국 포함)** | Open Society Institute-Sofia | 2017~, 한국 2022~ 포함 | 미디어 자유도(40%), PISA 리터러시(40%), 대인신뢰(10%), e참여(5%) 기타(5%) | z-점수 후 가중 산술합산, 0~100 변환 | 높을수록 가짜뉴스 저항성 높음 | ✅ 시행 중 (47개국)[^13][^14] |

**한국 현황 주목점**: 현재 한국에 '뉴스 소비 건강지수' 또는 '뉴스 다이어트 지수'를 신뢰×다양성 2축으로 명시적으로 설계한 **공식 사례는 확인되지 않는다**. 위 사례들은 미디어 리터러시(생산·비판 역량 중심)를 측정하며, 수용자의 '소비 패턴 건강성' 측정과는 구성 개념이 다르다. 본 설계는 이 공백을 채우는 최초 지수가 될 가능성이 있다.

### 3-2. 해외 사례 — '미디어/정보 다이어트 건강성' 유사 지수

| 지수명 | 국가/기관 | 구성 | 집계식 | 건강 방향 | 시행 여부 |
|---|---|---|---|---|---|
| **OSIS Media Literacy Index** | 불가리아/유럽 | 미디어 자유, 교육, 대인신뢰, 참여 | 가중 산술평균, z-점수 | 높을수록 건강 | ✅ 시행 중[^13] |
| **ONS Health Index (England)** | UK 통계청 | 58개 지표, 17 하위도메인, 3 도메인 | 지표→도메인: FA 가중 산술평균; 도메인 간: 등가중 산술평균 | 높을수록 건강(부정 지표 반전) | ✅ 시행 중[^12][^3] |
| **Diet Quality Index-International (DQI-I)** | Kim 외(2003) | 다양성, 적절성, 절제, 균형 4개 구성 요소 | 영역별 점수 합산, 0~100 총점 | 높을수록 건강; 절제 영역은 역코딩 | ✅ 학술 활용 중[^39][^40] |
| **DI 식이다양성지수** | FAO | 식품군 다양성 | 단순 카운팅 | 높을수록 건강 | ✅ 국제 활용[^41] |

**뉴스 소비에 특화된 '건강지수' 직접 선례**: 학술 문헌 검토 결과, 신뢰×다양성 두 축을 명시적으로 합성한 '뉴스 소비 건강지수' 공개 사례는 **확인되지 않는다**. 가장 근접한 사례는 식이다양성 지수(DQI-I)의 '다양성+절제+균형' 구조로, 이를 뉴스 소비에 유추 적용하면 다양성 외에 '절제(과잉 방지)'와 '균형(좌우 정치균형)' 하위지수를 추가할 이론적 여지가 있다.[^39]

**핵심 인용 (질문 3)**
1. 방송통신위원회×미디어미래연구소 (2020): 6개 역량 기반 미디어 리터러시 지수, 가중 산술평균 집계 — 국내 현행 유일 공식 지수[^35][^36]
2. OSIS (2022~): 47개국 대상, 교육·미디어 자유·신뢰·참여를 가중 산술집계 — 한국 포함[^13][^14]
3. ONS Health Index (2022): JRC-COIN 방법론 준수, 단계적 산술집계 + 요인분석 가중 — '건강' 합성지수 설계의 표준 참고[^12][^42]
4. Kim 외 (2003, DQI-I): 다양성+적절성+절제+균형 4개 구성요소, 합산 방식 — 식이다양성 지수를 뉴스 소비에 유추한 이론적 틀[^39]
5. UOC 연구 (2024): 유럽 5개국 포커스그룹, "건강한 미디어 다이어트=양질의 정보원+균형된 소비"로 귀납 도출[^31]

***

## 종합 설계 권고

### 단일 NCHI 집계식

\[
NCHI = \sqrt{T_{norm} \times D_{norm}}
\]

여기서 \(T_{norm}\), \(D_{norm}\)은 각각 신뢰지수·다양성지수를 \([1, 100]\) 구간에 정규화한 값이다. 현재 값(신뢰 62.5, 다양성 26.4)을 대입하면: \(NCHI \approx \sqrt{62.5 \times 26.4} \approx 40.6\)점으로 산술평균(44.5)보다 낮아 불균형이 반영된다.

### 2축 페르소나 유형화

| | 다양성 高 (D > 50) | 다양성 低 (D ≤ 50) |
|---|---|---|
| **신뢰 高 (T > 50)** | 🟢 **건강한 소비자** (Informed Citizen) | 🟡 **신뢰편향형** (Trusting but Narrow) |
| **신뢰 低 (T ≤ 50)** | 🟠 **비판적 탐색형** (Critical Explorer) | 🔴 **이중취약형** (Disengaged/At Risk) |

임계값은 각 지수 분포의 중앙값 또는 정책적 기준점(예: 평균)으로 설정하며, 연령·성별 교차 분석을 권고한다.

### 민감도 분석 의무화

OECD/JRC Handbook은 집계 방식, 가중값, 정규화 방식의 선택에 따른 결과 변동 폭을 보고하는 **민감도·강건성 분석**을 의무화한다. 기하평균과 산술평균 결과를 병기하여, 방법론 선택의 투명성을 확보할 것을 권고한다.[^17][^16]

***

## 출처 목록

| # | 출처 | URL | 발행연도 |
|---|---|---|---|
| 1 | JRC-COIN Step 6 Aggregation (Caperna 외) | https://knowledge4policy.ec.europa.eu | 2023 |
| 2 | OECD/JRC Handbook on Constructing Composite Indicators | https://www.oecd.org | 2008 |
| 3 | Tsfati & Barnoy, *Communication Research* — Media Cynicism, Skepticism, Automatic Trust | https://journals.sagepub.com | 2025 |
| 4 | UNDP Human Development Report / HDI 기하평균 전환 | https://www.scielo.org.mx; http://www.roiw.org | 2010/2019 |
| 5 | Mazziotta & Pareto — MPI 비보완 합성지수 | http://complexity.stat.unipd.it | 2013/2016 |
| 6 | OECD Better Life Index 방법론 | https://www.oecd.org | 2024 |
| 7 | ONS Health Index — Methods (UK) | https://www.ons.gov.uk | 2022 |
| 8 | OSIS Media Literacy Index (47개국) | https://osis.bg | 2022/2025 |
| 9 | 방통위 미디어 리터러시 지수 개발 | https://accesson.kr/trans | 2024 |
| 10 | Li, *New Media & Society* — Healthy vs. Identity-motivated skepticism | https://journals.sagepub.com | 2025 |
| 11 | Pew Research — Skepticism of News Media | https://www.pewresearch.org | 2020 |
| 12 | Oxford 정보과잉 연구 — Sweet spot | https://academic.oup.com | 2016 |
| 13 | UOC 연구 — Healthy Media Diet (5개국) | https://www.uoc.edu | 2024 |
| 14 | Kim 외, DQI-I (Diet Quality Index-International) | https://inddex.nutrition.tufts.edu | 2003 |
| 15 | KISDI 미디어 리터러시 역량 분석 | https://m.kisdi.re.kr | 2025 |
| 16 | KPF 디지털 뉴스 리포트 2025 한국 | https://www.kpf.or.kr | 2025 |
| 17 | KPF 언론수용자 조사 공공데이터 | https://www.data.go.kr | 2026 |
| 18 | Kohring & Matthes, *Communication Research* — Trust in News Media Scale | https://journals.sagepub.com | 2007 |

---

## References

1. [PowerPoint Presentation](https://knowledge4policy.ec.europa.eu/sites/default/files/COIN_2023_Step%206.%20Aggregation.pdf)

2. [[PDF] Step 6 Aggregation - Knowledge for policy](https://knowledge4policy.ec.europa.eu/sites/default/files/COIN_Step_06_Aggregation_Caperna_va.pdf)

3. [arXiv:2210.05154v1 [stat.AP] 11 Oct 2022](https://arxiv.org/pdf/2210.05154.pdf)

4. [An oddity in the Human Development Index](https://www.scielo.org.mx/scielo.php?script=sci_arttext&pid=S0185-16672024000100055)

5. [WP-2013-020](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=3694b5471c763096b4a73d6231d9651c89423f93)

6. [Document downloaded from: This paper must be ... - RiuNet](https://riunet.upv.es/server/api/core/bitstreams/5dc8ee6d-89de-40f5-8a5d-4526dbb67f0f/content)

7. [[PDF] MEASURING LOCAL WELL-BEING: A COMPARISON AMONG ...](https://www.sieds.it/listing/RePEc/journl/2016LXX_N4_RIEDS_91-102_Chelli_Ciommi_Emili_Gigliarano_Taralli.pdf)

8. [An Alternative Aggregation Function for the UNDP Human ... - Unipd](https://www.research.unipd.it/handle/11577/3548662?mode=complete)

9. [«YOUR» BETTER LIFE INDEX: Involving people and learning what matters most to them](https://unece.org/fileadmin/DAM/pau/age/Active_Ageing_Index/Second_int_seminar_on_AAI/presentations/03_OECD_BLI_Mark_KEESE.pdf)

10. [Slide 1](https://unece.org/fileadmin/DAM/stats/documents/ece/ces/ge.42/2015/Seminar/Session_II__OECD_-_The_OECD_Better_Life_Index.pdf)

11. [An Axiomatic Foundation of the Multiplicative Human ...](http://www.roiw.org/2019/n4/roiw12370.pdf)

12. [Methods used to develop the Health Index for England](https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/healthandwellbeing/methodologies/methodsusedtodevelopthehealthindexforengland2015to2018) - The methods and processes used to develop the experimental Health Index for England.

13. [Media Literacy Index | OSIS.BG](https://osis.bg/?p=4491&lang=en) - The index converts the data into standardized scores from 0 to 100 (lowest to highest) and ranks the...

14. [Media Literacy Index 2022](https://www.osce.org/files/f/documents/0/4/534146.pdf)

15. [On a Generalized Non-Compensatory Composite Index for ...](http://complexity.stat.unipd.it/system/files/21_MazziottaPareto_Final.pdf)

16. [[PDF] On the Methodological Framework of Composite Indices: A Review ...](https://pure.port.ac.uk/ws/files/8559735/On_the_methodological_framework_of_composite_indices.pdf)

17. [JRC Statistical Audit of the SDG Index and Dashboards](https://publications.jrc.ec.europa.eu/repository/bitstream/JRC118407/coin_tool_user_guide_2019.pdf)

18. [Media Cynicism, Media Skepticism and Automatic Media Trust: Explicating Their Connection with News Processing and Exposure - Yariv Tsfati, Aviv Barnoy, 2025](https://journals.sagepub.com/doi/full/10.1177/00936502251327717?mi=ehikzz) - In an era of increasing attention to media trust, some have argued that differentiating between medi...

19. [FOR RELEASE AUGUST 31, 2020 Americans See Skepticism of News Media as Healthy, Say Public Trust in the Institution Can Improve  72% of U.S. adults say news organizations doan insufficient jobtelling their audiences where their money comes from](https://www.pewresearch.org/wp-content/uploads/sites/20/2020/08/PJ_2020.08.31_Trust-In-News-Media_FINAL1.pdf)

20. [Trust in News Media | Semantic Scholar](https://www.semanticscholar.org/paper/Trust-in-News-Media-Kohring-Matthes/453767d37914a7115f999274a594bdcbabdadc16) - This model is the first validated scale of trust in news media in communication research and confirm...

21. [Trust in News Media - Matthias Kohring, Jörg Matthes, 2007](https://journals.sagepub.com/doi/10.1177/0093650206298071) - The dimensions that individuals apply in evaluating the trustworthiness or credibility of news media...

22. [Americans See Skepticism of News Media as Healthy, Say Public ...](https://www.pewresearch.org/journalism/2020/08/31/americans-see-skepticism-of-news-media-as-healthy-say-public-trust-in-the-institution-can-improve/) - 72% of U.S. adults say news organizations do an insufficient job telling their audiences where their...

23. [Not all skepticism is “healthy” skepticism: Theorizing accuracy- and identity-motivated skepticism toward social media misinformation - Jianing Li, 2025](https://journals.sagepub.com/doi/10.1177/14614448231179941?icid=int.sj-full-text.similar-articles.2) - Fostering skepticism has been seen as key to addressing misinformation on social media. This article...

24. [Study finds people more cynical toward news more likely to believe ...](https://news.ku.edu/news/article/study-finds-people-more-cynical-toward-news-more-likely-to-believe-misinformation-ARTICLE-F26T9T-ARTICLE-F26T9T-ARTICLE-F26T9T) - Study gauges levels of news skepticism, cynicism and media literacy and how they relate to believing...

25. [Media Cynicism, Media Skepticism and Automatic Media Trust](https://journals.sagepub.com/doi/10.1177/00936502251327717) - Some have argued that differentiating between media cynicism and media skepticism (as both attitudin...

26. [디지털 뉴스 리포트 2025 - 국가전략포털 - 국회도서관](https://nsp.nanet.go.kr/plan/subject/detail.do?nationalPlanControlNo=PLAN0000053402) - 국회도서관 국가전략정보서비스. 주요국·주제별 국가전략, 국가전략 최신동향, 인포그래픽, 세미나 정보 제공

27. [한국언론진흥재단](https://www.kpf.or.kr/front/research/selfDetail.do?seq=600108&link_g_homepage=F) - 2025년 국내 언론 지형에서 가장 눈에 띄는 트렌드는 전 연령대에서 나타나는 뉴스 이용률 하락세다. ... 특히 국내 뉴스 시장에서 핵심 역할을 해 온 포털 ...

28. [Information Overload: An Introduction | Oxford](https://academic.oup.com/edited-volume/62239/chapter/550732496?guestAccessKey=)

29. [Does Too Much News on Social Media Discourage News Seeking? Mediating Role of News Efficacy Between Perceived News Overload and News Avoidance on Social Media - Chang Sup Park, 2019](https://journals.sagepub.com/doi/full/10.1177/2056305119872956) - Drawing upon Bandura’s self-efficacy theory, this study conceptualizes “social media news efficacy” ...

30. [The Unified Framework of Media Diversity](https://pure.uva.nl/ws/files/50211514/The_Unified_Framework_of_Media_Diversity_A_Systematic_Literature_Review.pdf)

31. [What does a healthy media diet look like?](https://www.uoc.edu/en/news/2024/what-does-a-healthy-media-diet-look-like) - A study involving the UOC has analysed news consumption habits in five European countries

32. ["Attracted to Fake News"...Critical Media Literacy Declines ...](https://cm.asiae.co.kr/en/article/2023121019193203575) - The so-called 'media literacy' ability to critically understand media was found to decline gradually...

33. [[보고서 <디지털 뉴스 리포트 2025 한국>] 포털 뉴스 떠난 독자들 ...](https://blog.naver.com/PostView.naver?blogId=kpfjra_&logNo=224064425548&categoryNo=6&parentCategoryNo=6&from=thumbnailList) - 로이터저널리즘연구소는 매년 <디지털 뉴스 리포트>를 통해 한국을 비롯한 세계의 디지털 뉴스 이용 ...

34. ["미디어 리터러시 가장 뛰어난 세대는 30대…70대 이상 최저" | 연합뉴스](https://www.yna.co.kr/view/AKR20231208140900017) - 연령별 미디어 리터러시는 30대와 20대의 뒤를 이어 40대(3.10), 50대(3.00), 60대(2.68) 순으로 조사됐다. 고 교수는 "이들 사이에 통계적으로 유의미한 ...

35. [https://doi.org/10.23086/trans.2024.17.01](https://accesson.kr/trans/assets/pdf/46795/ART003115711.pdf)

36. [디지털미디어 리터러시 교육 종합계획 발표 - 대한민국 정책브리핑](https://www.korea.kr/briefing/policyBriefingView.do?newsId=156408154) - 나아가, 미디어 리터러시 수준을 측정할 수 있는 지수를 개발하고, 미디어교육 관련 조사와 통계를 통해 전 국민의 미디어 리터러시 증진을 위한 ...

37. [KISDI STAT Report(상세) - 정기간행물 - KISDI 발간물 - 정보통신정책연구원](https://m.kisdi.re.kr/report/view.do?key=m2101113025790&masterId=4333447&arrMasterId=4333447&artId=1167236) - KISDI 정보통신정책연구원 정보통신 전문연구기관 글로벌 방송 통신정책연구기관 국책연구기관 통신산업 통신환경 개선 정보통신 정책 수립

38. [대학내일20대연구소, ‘국내 연령대별 미디어 소비 및 페이크 뉴스 경험·인식 실태 조사’ 보고서 발표 - 뉴스와이어](https://www.newswire.co.kr/newsRead.php?no=864944) - 대학내일20대연구소가 ‘국내 연령대별 미디어 소비 및 페이크 뉴스 경험·인식 실태 조사’ 보고서를 26일 발표했다. 이번 설문조사는 전국 19~59세 남녀 1200명을 대상으로 진...

39. [Diet Quality Index - International (DQI-I) | INDDEX Project](https://inddex.nutrition.tufts.edu/data4diets/indicator/diet-quality-index-international-dqi-i)

40. [Cross-comparison of diet quality indices for predicting chronic disease risk: findings from the Observation of Cardiovascular Risk Factors in Luxembourg (ORISCAV-LUX) study | British Journal of Nutrition | Cambridge Core](https://www.cambridge.org/core/journals/british-journal-of-nutrition/article/crosscomparison-of-diet-quality-indices-for-predicting-chronic-disease-risk-findings-from-the-observation-of-cardiovascular-risk-factors-in-luxembourg-oriscavlux-study/DAF317528529D4ECE7948CDC8FF2221D) - Cross-comparison of diet quality indices for predicting chronic disease risk: findings from the Obse...

41. [Review of Diet Quality Indices that can be Applied to the ... - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11133024/) - The aim was to identify indices of diet quality and health that could be applied to the environmenta...

42. [Introducing the Health Index and its usage](https://rss.org.uk/news-publication/news-publications/2023/section-group-reports/introducing-the-health-index-and-its-usage/)

