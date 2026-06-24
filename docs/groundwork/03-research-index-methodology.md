# 뉴스 소비 건강지수 설계를 위한 계량방법론 검토: 다양성 측정과 신뢰 구성

> 출처: Perplexity Deep Research (2026-06-24) — Task 02 변수매핑 전 방법론 갈림길 해소용 외부 조사.
> 반영: 다양성=Richness 주지표(+일수가중 Shannon/Pielou 보조·진단), 신뢰=뉴스/언론 신뢰만 코어(Q95 직업군·Q96 사회신뢰 제외), Q91 문제점인식=신뢰 합산 금지·별도 지표(냉소 vs 회의 CFA 검증).
> 설계 적용본: [`docs/design/preprocessing-design.md`](../design/preprocessing-design.md) · 검증 노트북: [`notebooks/02-variable-mapping.ipynb`](../../notebooks/02-variable-mapping.ipynb).
> ⚠️ 인용 수치(KPF 보고서값 등)는 원자료 재검증 전까지 보고서 직접 인용 금지.

**대상 데이터**: 한국언론진흥재단 언론수용자 조사 (N=6,000, 5점 척도·매체 이용여부·이용일수)[^1]
**합성지표 차원**: 뉴스 매체 레퍼토리 다양성 + 뉴스 신뢰  
**분석 준거**: OECD/JRC 합성지표 핸드북, 미디어 레퍼토리·뉴스 다이어트 선행연구[^2]

***

## 질문 1: 뉴스 매체 레퍼토리 다양성 측정

### 1-1. 핵심 지표 비교: Shannon H, Normalized H (Pielou J), Simpson D, HHI

미디어 레퍼토리 다양성 연구에서 가장 널리 쓰이는 지표는 Shannon 엔트로피(H), 그 정규화 형태인 Pielou 균등도(J), Simpson 다양성 지수(D), 그리고 집중도 역지표 Herfindahl-Hirschman Index(HHI)이다. 이용 빈도(일수) 데이터가 있을 때는 이를 가중치로 활용해 **richness**(이용 매체 수)와 **evenness**(매체 간 이용 균등도)를 구분하는 것이 학술 표준이다.[^3][^4]

#### 산식 비교표

| 지표 | 산식 | 값 범위 | 측정 대상 | 이진 데이터 시 문제 |
|------|------|---------|-----------|-------------------|
| **Richness (S)** | \(S = \sum_{i=1}^{k} \mathbf{1}[d_i > 0]\) | 0 ~ k (매체 수) | 이용 매체 종류 수(breadth) | 없음 (그 자체가 count) |
| **Shannon H** | \(H = -\sum_{i=1}^{S} p_i \ln p_i\) (p_i = 매체 i 이용일수 비율) | 0 ~ ln(S) | richness + evenness | **이진 시 H = ln(S) 로 count의 단조변환** [^5] |
| **Pielou J (정규화 H)** | \(J = H / H_{\max} = H / \ln(S)\) | 0 ~ 1 | evenness만 (richness 독립) | 이진 시 J ≡ 1 (항상 최대) |
| **Simpson D** | \(D = 1 - \sum p_i^2\) (또는 \(D = Prob(i \neq j)\)) | 0 ~ 1 | richness + evenness, 직관적 해석 | 이진 시 S가 다르면 변별 가능[^4][^6] |
| **HHI (집중도)** | \(HHI = \sum p_i^2 \times 10000\) | 0 ~ 10000 | 집중도 (D의 역수 개념) | 이진 균등 배분 시 HHI = 10000/S |
| **Effective N (ENS)** | \(ENS = e^H\) (Hill q=1) | 1 ~ S | "등가 매체 수" 단위, 해석 용이[^7] | 이진 시 ENS = S (richness와 동일) |

*p_i: 매체 i 이용일수 / 전체 이용일수 합계*

#### 선행연구 적용 사례

- **Fletcher, Kalogeropoulos & Nielsen(2023)**: 영국 뉴스 레퍼토리 패널 연구에서 Simpson D와 Shannon H를 동시 보고. D는 직관적 해석(임의 두 기사가 서로 다른 매체일 확률)이 가능하고, H는 이용 빈도가 낮은 소수 매체에 더 민감하여 이용 빈도 분포가 다양할 때 유리하다고 결론.[^4][^6]
- **Boydstun et al.(2014) / Jonkman et al.(2018)**: 의제 다양성 연구에서 Shannon H가 HHI보다 극단값(dominance 0) 영향을 덜 받아 통계적 검정력 우위라고 보고.[^8][^3]
- **한국 여론집중도조사위원회**: 5대 매체(종이신문·TV·라디오·인터넷뉴스·SNS) 이용 점유율 기준 HHI 산출. 2024년 매체합산 HHI=644.[^9][^10]
- **KISDI 미디어 다양성 지표(2014)**: 공급측 다양성은 HHI, 이용측 다양성은 이용여부·이용시간·가중이용시간 4가지 기준 병행 산출을 권고.[^11][^12]
- **뉴스 다이어트/허위정보 연구(Cinelli et al.)**: Twitter 뉴스 이용에서 Random Entropy(log₂N = Richness의 log), Uncorrelated Entropy(Shannon H), Actual Entropy(Lempel-Ziv) 세 층위를 구분 적용.[^5]

***

### 1-2. 이진(binary) 이용여부만 있을 때 Shannon 엔트로피가 count의 단조변환이 되는 문제

**문제의 본질**: 이진 데이터(이용=1, 비이용=0)만으로 Shannon H를 계산하면 모든 이용 매체가 동일 가중치(1/S)를 받게 되어 H = ln(S)가 된다. 따라서 H는 S의 단조증가 함수, 즉 매체 종류 수(Richness)를 log 변환한 것과 동일하다. Pielou J 역시 이진 데이터에서는 항상 J = H/ln(S) = 1이 되어 evenness 정보를 전혀 담지 못한다.[^13][^5]

**회피 전략 (우선순위 순)**:

1. **이용일수 데이터 활용 (권장)**: 언론수용자 조사의 "최근 1주일 이용일수" 변수를 p_i로 사용. p_i = (매체 i 이용일수) / (전체 이용일수 합). 이 경우 동일 매체 수를 이용해도 특정 매체 집중 여부에 따라 H, J, D가 달라진다. 이 방식이 미디어 레퍼토리 연구의 표준이다.[^14][^4]

2. **Richness(S)와 Evenness(J)를 분리 보고**: 이진 데이터만 가용한 경우 S를 breadth 지표로, 이용일수 기반 J를 evenness 지표로 분리하여 2차원 레퍼토리 프로파일을 구성한다. 이 방식은 각 차원의 이론적 해석이 명확하다.[^4]

3. **Simpson D 우선 사용**: 이진 데이터에서도 S가 2 이상이면 D = (S-1)/S · Σ(1/S²... 정확히는 1 - S·(1/S)²= 1-1/S)로 S와 단조관계이나, 이용일수 빈도 데이터가 있으면 Simpson D는 richness와 evenness를 동시에 포착하면서도 HHI보다 극단값에 덜 민감하다.[^6][^3]

4. **이진 데이터를 완전히 포기하지 않는 실용적 접근**: Richness(S)를 로 Min-Max 정규화한 뒤, 이용일수 기반 Pielou J와 함께 합산 또는 기하평균으로 결합하여 "다양성 복합점수"를 구성. 이때 두 지표의 가중치는 이론적 근거(breadth vs. evenness 상대적 중요도)에 따라 결정.[^15][^2]

***

### 1-3. OECD/JRC 합성지수 맥락에서 다양성 하위지표 정규화·해석 권고

OECD/JRC 합성지표 핸드북은 하위지표를 공통 척도로 변환하여 "사과-오렌지 비교" 문제를 해소할 것을 핵심 원칙으로 제시한다. 다양성 하위지표에 적용 시 다음 절차를 따른다.[^16][^2]

**정규화 방법 비교**:

| 방법 | 산식 | 권고 상황 | 주의사항 |
|------|------|----------|----------|
| **Min-Max** | \(I_q = (x_q - x_{\min}) / (x_{\max} - x_{\min})\) | Shannon H, Simpson D, Richness | 극단값이 benchmark 기능. 이론적 최소·최대값이 알려진 경우(예: H_max=ln(k)) 활용[^2][^17] |
| **표준화 (Z-score)** | \(I_q = (x_q - \bar{x}) / \sigma_x\) | HHI, 분포가 정규에 가까울 때 | 음수 값 발생. 합산 전 선형 이동 필요[^18] |
| **이론적 상한 정규화** | \(I_q = H / \ln(k)\) (k = 총 매체 수) | Shannon H를 Pielou J로 변환 | k 선택이 결과에 민감. 조사에 포함된 매체 총수를 k로 권장 |

**실천 권고**:
- Pielou J (= H/ln(k))는 이미 로 정규화된 evenness 지표이므로 추가 변환 불필요.[^15]
- HHI는 집중도(높을수록 다양성 낮음) 방향이 역방향이므로 합성 전 반전: I_diversity = 1 - (HHI/10000).
- 왜도가 심한 경우 로그변환 후 Min-Max 적용.[^18]
- JRC는 산술 평균보다 **기하 평균 집계**를 권고하는 경우가 많음 — 기하 평균은 지표 간 보완 관계를 최소화하여 하위지표 결핍이 총점에 더 잘 반영됨.[^17]

***

### 질문 1 권고안

> **이용일수 데이터가 있을 때**: 이용일수를 p_i로 사용한 **Shannon H와 Pielou J(정규화 H)를 쌍으로 보고**한다. H는 richness+evenness 통합, J는 evenness 분리. 여기에 Richness(S, 이용 매체 종류 수)를 breadth 지표로 별도 수록. HHI는 공급측(여론집중도 조사)과의 정합성 확보 목적으로 보조 지표로 활용한다. OECD/JRC 권고대로 Min-Max 또는 이론적 상한(ln k) 기준으로  정규화한 뒤 arithmetic 또는 geometric 평균으로 집계한다.[^15]
> **이진 데이터만 있을 때**: Shannon H를 사용하지 말고 Richness(S)를 그대로 breadth 지표로 사용한다. 다양성 하위지표를 단일 값으로 제시해야 하는 경우, S를 [0, S_max]로 Min-Max 정규화한 것 외 추가 evenness 지표를 포함하지 않는다(이진 데이터에서 evenness 정보는 측정 불가).

***

### 핵심 인용 (질문 1)

1. **Fletcher, Kalogeropoulos & Nielsen (2023)** — *New Media & Society* — 영국 뉴스 레퍼토리 추적 패널 연구에서 Simpson D와 Shannon H 동시 적용, 이용 빈도 비율 p_i 산정 방식 상세 기술.[^6][^4]
2. **Boydstun et al. (2014) / Jonkman et al. (2018)** — *Policy Studies Journal* / *Journalism* — 의제 다양성 측정에서 Shannon H가 HHI보다 통계적으로 우월함을 시뮬레이션과 실제 데이터로 검증.[^3][^8]
3. **KISDI (2014) "미디어 다양성 지표 개발 연구"** — 한국 맥락에서 이용여부·이용시간·가중이용시간·매체특성 반영 4가지 기준 병행 산출, HHI 기반 집중도 측정.[^19][^12]
4. **OECD/JRC (2008) Handbook on Constructing Composite Indicators** — Min-Max, 표준화, 기하 집계 등 정규화·집계 방법론 표준.[^16][^2]
5. **Cinelli et al. (2020/2025 review)** — Twitter COVID-19 데이터에서 Random Entropy(log₂S), Uncorrelated Entropy(Shannon H), Actual Entropy(Lempel-Ziv) 3층위 구분 적용.[^5]

***

## 질문 2: 신뢰 구성 — 사회신뢰 분리와 비판적 인식의 위치

### 2-1. 일반화된 사회신뢰 vs. 뉴스·언론 신뢰: 반드시 분리해야 하는가?

학술적 합의는 **분리를 권장**한다. Uslaner(2002)는 일반화된 사회신뢰(generalized social trust, "대부분의 사람을 믿을 수 있다")는 사회화를 통해 형성된 안정적 성향으로 특정 제도·인물에 대한 신뢰와 개념적으로 다르다고 이론화했다. 이를 세 유형으로 구분하면:[^20][^21]

| 신뢰 유형 | 개념 | 대표 측정 문항 | 측정 도구 |
|-----------|------|--------------|----------|
| **일반화 사회신뢰** | 낯선 타인 전반에 대한 신뢰 (bridging social capital) | "대부분의 사람은 믿을 수 있다" | WVS, OECD BLI, Uslaner Scale[^20][^22] |
| **뉴스·언론 신뢰** | 저널리즘의 기능 수행에 대한 기대 충족 | 선택성·정확성·전문성·공정성 | Kohring & Matthes(2007) 4요인 척도[^23][^24] |
| **정치적 제도 신뢰** | 정부·의회·사법부 등 공적 기관 신뢰 | "정부를 신뢰한다" | 별도 측정 권고 |

Hanitzsch et al.(2019)와 Jackob(2010)은 언론 신뢰를 일반 사회신뢰와 혼용하면 두 구성물 간 교란효과(confounding)가 발생한다고 경고한다. 한국 맥락에서도 한국언론진흥재단 언론수용자 조사는 뉴스 신뢰를 "이 뉴스 및 시사 정보 전반"에 대한 5점 척도로 별도 측정해왔으며, 이는 사회신뢰 문항과 구분된 것이다.[^25][^26][^27][^1]

**Kohring & Matthes(2007) 4요인 뉴스 신뢰 척도**: 커뮤니케이션 연구 최초의 검증된 다차원 척도로, (1) 주제 선택의 선택성 신뢰, (2) 사실 선택의 선택성 신뢰, (3) 묘사의 정확성 신뢰, (4) 저널리스틱 평가 신뢰의 4요인 위계 모형이다. 이 척도는 신뢰를 단순한 "믿음"이 아니라 저널리즘의 기능적 수행에 대한 기대로 이론화한다.[^23][^28][^29]

***

### 2-2. 비판적 인식(오보·편파 인식)은 낮은 신뢰인가, 건강한 리터러시인가?

이 질문에 대한 학술적 합의는 **회의주의(skepticism), 냉소주의(cynicism), 불신(distrust/low trust)을 개념적으로 명확히 구분**해야 한다는 것이다.[^30][^31]

#### 세 개념 비교

| 개념 | 정의 | 미디어 리터러시 관계 | 허위정보 취약성 |
|------|------|---------------------|----------------|
| **건강한 회의주의 (Healthy Skepticism)** | 증거 기반의 비판적 평가, 출처·맥락 고려 | 긍정적 지표 — 뉴스 리터러시 높을수록 회의주의↑[^32][^31] | 상관 없음 (유의미 관계 없음)[^31] |
| **냉소주의 (Cynicism)** | 미디어 전반에 대한 체계적 불신, "언론은 거짓말한다" | 리터러시 높아도 냉소↑ 가능 (역설적 결과)[^30] | **정(+)의 관계 — 허위정보 믿을 확률↑**[^30][^31] |
| **낮은 신뢰 (Low Trust)** | 특정 뉴스미디어의 신뢰도 평가 낮음 | 별도 차원 | 높은 신뢰도 일부 연구서 허위정보 취약성↑[^30] |

**핵심 발견**: Wilner et al.(2024/2025)의 N=1,003 온라인 서베이 연구에서 뉴스 지식(news knowledge)이 높을수록 회의주의는 높고 냉소주의는 낮았으며, 냉소주의만이 허위정보 믿음과 유의한 정(+)의 관계를 보였다. 회의주의는 허위정보 믿음과 유의한 관계가 없었다. 이는 회의주의를 낮은 신뢰의 동의어로 처리하면 안 된다는 강력한 근거이다.[^31][^30]

**뉴스 리터러시 척도의 처리 방식**:

- **5Cs 척도 (Tully, Maksl, Ashley, Vraga & Craft, 2021/2022)**: Context·Creation·Content·Circulation·Consumption 5개 영역에 걸친 지식과 기술을 측정. 신뢰를 직접 측정하지 않고, 비판적 이해력(content 영역의 출처 평가, 증거 신뢰성 판단)을 리터러시의 긍정 차원으로 위치시킨다.[^33][^34][^35]
- **NML 척도 (Chen et al., 2011 기반)**: Functional Consuming(FC), Critical Consuming(CC), Functional Prosuming(FP), Critical Prosuming(CP) 4요인. CC의 분석·종합·평가 능력이 미디어 비판적 인식을 **긍정적 역량**으로 포함.[^36][^37]
- **NMLS (Maksl et al., 2015)**: 뉴스 미디어 리터러시를 Potter(2004) 모형에서 도출. 고(高)리터러시 집단이 저(低)리터러시 집단보다 뉴스 회의주의 점수가 유의하게 높음(F(1,432)=7.41, p<.01).[^32]
- **Li(2025)**: "모든 회의주의가 건강한 것은 아니다"(not all skepticism is "healthy" skepticism) — 정확성 동기 회의주의(accuracy-motivated skepticism)는 허위정보 저항에 효과적이지만, 정체성 동기 회의주의(identity-motivated skepticism)는 당파적 허위정보 수용에 오히려 기여할 수 있음.[^38]

***

### 2-3. '뉴스 소비 건강지수' 신뢰 차원 구성 적용

**분리 원칙**: 언론수용자 조사의 5점 척도 신뢰 문항(뉴스 전반 신뢰, 이용 뉴스 신뢰)은 **뉴스·언론 신뢰**로 분류하고, 별도 사회신뢰 문항이 없으면 일반화 사회신뢰를 지수에 포함하지 않는다. 두 개념의 혼용은 측정 타당도를 훼손한다.[^26][^25]

**비판적 인식의 위치 결정**:

- "오보·편파 인식" 문항이 "언론은 거짓말을 한다(냉소적 불신)"에 가까우면 → **신뢰 차원의 역방향 지표**(낮은 신뢰)로 처리.  
- "뉴스 소비 시 출처·편향을 따져본다(증거 기반 비판)" 형태면 → **미디어 리터러시의 긍정 지표**(건강한 회의주의)로 별도 차원 또는 신뢰 차원 내 조절 변수로 배치.  
- 2022 언론수용자 조사의 "언론 가장 큰 문제점" 문항(편파 보도 22.1%, 허위정보 19.9%)은 인식적 비판 수준을 측정하므로 건강지수 내 **비판적 리터러시 지표**로 활용 가능하나 신뢰 하위지표로 역코딩해 합산하면 냉소주의를 리터러시로 오분류할 위험이 있다.[^39]

***

### 질문 2 권고안

> 신뢰 차원은 **뉴스·언론 신뢰**만을 측정하며, 일반화된 사회신뢰는 별도 통제변수로 분리한다(Kohring & Matthes, 2007 4요인 모형 준용). "오보·편파 인식"은 **냉소주의인지 회의주의인지에 따라** 처리 방향이 반대이다: ① 문항이 체계적 불신·음모적 회의(냉소)에 가까우면 신뢰의 역지표; ② 문항이 증거 기반 비판·출처 평가(건강한 회의주의)에 가까우면 미디어 리터러시 긍정 지표로 분리. 언론수용자 조사 기존 문항은 양자가 혼재되어 있으므로 항목별 내용 검토 후 귀속 차원을 결정해야 하며, 구분이 모호한 경우 CFA(확인적 요인분석)로 두 요인 적합도를 비교 검증할 것을 권장한다.

***

### 핵심 인용 (질문 2)

1. **Kohring & Matthes (2007)** — *Communication Research* — 뉴스 신뢰 4요인 위계 척도 개발·검증. 커뮤니케이션 연구 최초 표준화 척도.[^24][^28][^23]
2. **Wilner, Ashley & Craft (2024/2025)** — *Mass Communication and Society* — 회의주의·냉소주의·신뢰를 분리 측정, N=1,003. 냉소주의만 허위정보 믿음과 유의한 정의 관계.[^30][^31]
3. **Tully, Maksl, Ashley, Vraga & Craft (2021/2022)** — *Journalism* — 5Cs 뉴스 리터러시 개념화. 비판적 인식을 긍정적 리터러시 역량으로 위치시킴.[^34][^35][^33]
4. **Li, Jianing (2025)** — *New Media & Society* — "모든 회의주의가 건강한 것은 아니다": 정확성 동기 회의주의 vs. 정체성 동기 회의주의 구분.[^38]
5. **한국언론진흥재단 언론수용자 조사 (2022·2024·2025)** — TV 신뢰도 최고(3.90점/5점), 뉴스 전반 신뢰도 상승세(2025년 49% 신뢰). 매체별·언론 전반 신뢰를 5점 척도로 구분 측정.[^40][^39][^1]

***

## 부록: 출처 정리

| 출처 | 유형 | 발행 연도 | URL / 출처 |
|------|------|----------|------------|
| Fletcher, Kalogeropoulos & Nielsen, "More diverse, more politically varied" | 학술논문 | 2023 | *New Media & Society* [^4][^6] |
| Boydstun et al., "The Importance of Attention Diversity" | 학술논문 | 2014 | *Policy Studies Journal* [^3] |
| Jonkman et al., "More or less diverse" | 학술논문 | 2018 | *Journalism* [^8] |
| Kohring & Matthes, "Trust in News Media" | 학술논문 | 2007 | *Communication Research* [^23][^24] |
| Tully et al., "Defining and Conceptualizing News Literacy" | 학술논문 | 2021/2022 | *Journalism* [^33] |
| Wilner et al., "Defining and Validating News Skepticism" | 학술논문 | 2024/2025 | *Mass Communication and Society* [^31] |
| Li, "Not all skepticism is 'healthy' skepticism" | 학술논문 | 2025 | *New Media & Society* [^38] |
| OECD/JRC, *Handbook on Constructing Composite Indicators* | 정책보고서 | 2008 | OECD [^2][^16] |
| KISDI, 미디어 다양성 지표 개발 연구 | 정책연구 | 2014 | KISDI [^19][^12] |
| 한국 여론집중도조사위원회 2022-2024 | 정책보고서 | 2025 | 문화체육관광부 [^9][^10] |
| 한국언론진흥재단, 언론수용자 조사 (2022·2024·2025) | 조사보고서 | 2022–2026 | KPF [^40][^39][^1] |
| Uslaner, *The Moral Foundations of Trust* | 학술단행본 | 2002 | Cambridge [^20][^21] |
| Cinelli et al. (COVID Infodemic Platform review) | 학술논문 | 2025 | arXiv/peer-review [^5] |

---

## References

1. [[데이터로 보는 언론] 40년 뉴스 신뢰도의 기록, 무엇이 달라졌나](https://blog.naver.com/kpfjra_/224242361994) - 신문 독자를 대상으로 출발한 언론수용자 조사는 현재 만 19세 이상 전국 국민 6,000명을 대상으로 미디어 전반의 이용 행태와 인식을 파악하는 조사로 ...

2. [Please cite this paper as:](https://edisciplinas.usp.br/pluginfile.php/8545891/mod_folder/content/0/texto20_Handbook_composite_indicators.pdf?forcedownload=1)

3. [The Importance of Attention Diversity and How to Measure It](https://onlinelibrary.wiley.com/doi/abs/10.1111/psj.12055) - Studies of political attention often focus on attention to a single issue, such as front‐page covera...

4. [[PDF] How social media, search engines and aggregators shape news ...](https://ora.ox.ac.uk/objects/uuid:08329efd-fd35-4fe9-974a-991091cf987a/files/r5t34sk456)

5. [[Literature Review] Decoding the News Media Diet of Disinformation Spreaders](https://www.themoonlight.io/en/review/decoding-the-news-media-diet-of-disinformation-spreaders) - This paper explores the consumption of news media on social media, especially how users who spread d...

6. [More diverse, more politically varied: How social media, search engines and aggregators shape news repertoires in the United Kingdom - Richard Fletcher, Antonis Kalogeropoulos, Rasmus Kleis Nielsen, 2023](https://journals.sagepub.com/doi/10.1177/14614448211027393) - There is still much to learn about how the rise of new, ‘distributed’, forms of news access through ...

7. [Diversity index - Wikipedia](https://en.wikipedia.org/wiki/Shannon_index)

8. [More or less diverse: An assessment of the effect of attention to media salient company types on media agenda diversity in Dutch newspaper coverage between 2007 and 2013 - Jeroen GF Jonkman, Damian Trilling, Piet Verhoeven, Rens Vliegenthart, 2018](https://journals.sagepub.com/doi/10.1177/1464884916680371?icid=int.sj-abstract.citing-articles.57) - This study on news coverage of highly visible company types in a Dutch daily quality newspaper (NRC ...

9. [여론집중도 조사… 종편군 비중 확대, 뉴스통신·보도채널군 감소](https://www.kapnews.kr/news/view.php?idx=2847&mcode=m66ak8d&page=6) - 문화체육관광부 소속 제5기 여론집중도조사위원회(위원장 윤석민)는 8월 29일 ‘2022~2024 여론집중도 조사’ 결과를 발표하며, 종편군의 영향력이 확대되는 한편 전체 매체 합산...

10. [제5기 여론집중도조사위원회, '2022~2024 여론집중도 조사' 발표](https://www.thepress1.com/bbs/board.php?bo_table=news&wr_id=4591) - -종편군 점유율 상승·뉴스통신‧보도전문채널군 하락…매체 영향력 지형 변화 확인

11. [[보고서]미디어다양성 지표의 시범적용 분석 - KiSTi](https://scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn=TRKO201600012011) - 4. 연구 내용 및 결과◦ 미디어 범위*(플랫폼, 채널, 프로그램), 접근방식(공급, 이용), 다양성 영역(구조, 내용)을 조합, 아래의 그림과 같이 총 20개의 지표 도출 ...

12. [보도자료(상세) - KISDI 정보센터 - 정보통신정책연구원](https://www.kisdi.re.kr/bbs/view.do?bbsSn=100663&key=m2101113055776) - KISDI 정보통신정책연구원 정보통신 전문연구기관 글로벌 방송 통신정책연구기관 국책연구기관 통신산업 통신환경 개선 정보통신 정책 수립

13. [[PDF] Entropy and diversity](https://pdodds.w3.uvm.edu/research/papers/others/2006/jost2006a.pdf) - The most common diversity measure, the Shannon!/Wiener index, is an entropy, giving the uncertainty ...

14. [Media Repertoire and Multiplatform Media Use: Media Consumption Diversity in a Digital Age [Slides]](https://scholarworks.bgsu.edu/cgi/viewcontent.cgi?article=1024&context=smc_pub)

15. [[PDF] Journal for Current Sign](https://currentsignreview.com/index.php/JCS/article/download/210/170/333)

16. [[PDF] Handbook on Constructing Composite Indicators | OECD](https://www.oecd.org/content/dam/oecd/en/publications/reports/2008/08/handbook-on-constructing-composite-indicators-methodology-and-user-guide_g1gh9301/9789264043466-en.pdf) - The OECD is a unique forum where the governments of 30 democracies work together to address the econ...

17. [Microsoft Word - Deliverable3_RES_EXC_Experts.doc](https://publications.jrc.ec.europa.eu/repository/bitstream/JRC72592/reqno_jrc72592_deliverable3_res_exc.pdf%5B1%5D.pdf)

18. [[PDF] Composite Indicators of Country Performance: A Critical Assessment](https://www.oecd.org/content/dam/oecd/en/publications/reports/2003/11/composite-indicators-of-country-performance_g17a155e/405566708255.pdf) - The OECD Composite of Leading Indicators, which ... with four different normalization methods and fo...

19. [KCC-2014-20(최종).hwp](https://www.kisdi.re.kr/report/fileView.do?key=m2101113024770&arrMasterId=3934580&id=520383)

20. [[PDF] Varieties of Trust* Eric M. Uslaner Department of Government and ...](http://gvptsites.umd.edu/uslaner/uslanereps.pdf) - Generalized trust is the perception that most people are part of your moral community. Its foundatio...

21. [The Oxford Handbook of ...](https://academic.oup.com/edited-volume/34638/chapter/295110765) - AbstractIn this introductory chapter, I survey approaches to the study of social and political trust...

22. [[DOC] To Trust or not to Trust - Department of Government and Politics](http://gvptsites.umd.edu/uslaner/israeltrustterrorrevisediv.doc)

23. [Trust in News Media - Semantic Scholar](https://www.semanticscholar.org/paper/Trust-in-News-Media-Kohring-Matthes/453767d37914a7115f999274a594bdcbabdadc16) - This model is the first validated scale of trust in news media in communication research and confirm...

24. [Trust in News Media - Matthias Kohring, Jörg Matthes, 2007](https://journals.sagepub.com/doi/10.1177/0093650206298071) - The purpose of this article is to present the development and validation of a multidimensional scale...

25. [Effects of Editorial Media Bias Perception and Media Trust ...](http://www.homerogdz.com/documents/Ardevol-Abreu%20&%20Gil%20de%20Zuniga%20(2016)%20Journalism%20&%20Mass%20Communication%20Quarterly.pdf)

26. [Individual and Contextual Correlates of Trust in Media Across 44 ...](https://www.academia.edu/11973490/Individual_and_Contextual_Correlates_of_Trust_in_Media_Across_44_Countries) - Media research demonstrates that audience trust in the news media is a highly consequential factor, ...

27. [한국언론진흥재단](https://kpf.or.kr/front/research/consumerDetail.do?seq=591716) - <2020 언론수용자 조사> 결과, 신문·방송과 같은 전통 미디어의 신뢰도가 3.54점으로 가장 높고(TV는 3.71점, 종이신문은 3.37점이었다), 유튜브 등 온라인 동영상 플...

28. [Studies in Communication Sciences 18.2 (2018), pp. 231–245](https://www.hope.uzh.ch/scoms/article/download/j.scoms.2018.02.003/1043/1775)

29. [[PDF] Journalism, trust, and credibility van Dalen, Arjen](https://findresearcher.sdu.dk/ws/portalfiles/portal/155570015/Journalism_trust_and_credibility.pdf) - Kohring and Matthes (2007) used factor analysis to validate a theory-driven media trust scale, which...

30. [Study finds people more cynical toward news more likely to believe ...](https://news.ku.edu/news/article/study-finds-people-more-cynical-toward-news-more-likely-to-believe-misinformation-ARTICLE-F26T9T-ARTICLE-F26T9T-ARTICLE-F26T9T) - Wilner's research examines media literacy, how it is developed and how it intersects with individual...

31. [Defining and Validating News Skepticism: Distinctions from News Trust and Cynicism, and Links to News Literacy and Misinformation Belief](https://www.tandfonline.com/doi/full/10.1080/15205436.2025.2534983) - This study explores the role of news skepticism in countering misinformation beliefs and skepticism’...

32. [[PDF] Measuring News Media Literacy - ERIC](https://files.eric.ed.gov/fulltext/EJ1059962.pdf) - This study measured levels of news media literacy among 500 teenagers using a new scale measure base...

33. [Defining and conceptualizing news literacy - Melissa Tully, Adam Maksl, Seth Ashley, Emily K Vraga, Stephanie Craft, 2022](https://journals.sagepub.com/doi/abs/10.1177/14648849211005888) - Interest in news literacy inside and outside the academy has grown alongside related concerns about ...

34. [News Literacy 101: A Guide on How NOT to Get Fooled](https://sites.create.ou.edu/ciarawolfe/2025/10/02/news-literacy-101-a-guide-on-how-not-to-get-fooled/)

35. [Teaching Information Literacy in a GenAI World: A 5Cs Framework ...](https://digitalcommons.georgiasouthern.edu/gaintlit/2025/2025/29/) - The 5Cs of news literacy (context, creation, content, circulation, and consumption), as outlined in ...

36. [Establishing the norm of new media literacy ...](https://www.sciencedirect.com/science/article/abs/pii/S0360131518300988)

37. [Understanding the role of new media literacy in the diffusion of unverified information during the COVID-19 pandemic - Eun Hee Lee, Taejun (David) Lee, Byung-Kwan Lee, 2024](https://journals.sagepub.com/doi/10.1177/14614448221130955?icid=int.sj-full-text.similar-articles.6) - New media literacy (NML) is an emerging construct of great value in a digital age in which informati...

38. [Not all skepticism is “healthy” skepticism: Theorizing accuracy- and identity-motivated skepticism toward social media misinformation - Jianing Li, 2025](https://journals.sagepub.com/doi/10.1177/14614448231179941?icid=int.sj-full-text.similar-articles.2) - Fostering skepticism has been seen as key to addressing misinformation on social media. This article...

39. ["20대 인터넷, 70대 TV로 뉴스 본다"…신뢰도는 전통매체 높아](https://www.yna.co.kr/view/AKR20221230086700005) - 30일 한국언론진흥재단이 발표한 '2022 언론수용자 조사' 결과에 따르면 20대의 92.3%는 인터넷, 70대 이상의 90.8%는 텔레비전으로 뉴스를 접하는 것으로 ...

40. [<2024 언론수용자 조사> 결과 발표 - 한국언론진흥재단](https://www.kpf.or.kr/front/board/boardContentsView.do?board_id=246&contents_id=8cfa6b1bf19b4b6ab16a7b970bb1512e) - 반면,'뉴스 및 시사정보 전반'에 대한 신뢰도는 2023년 3.27점(5점 척도 평균점)에서 3.36점, '실제 이용하는 뉴스 및 시사정보'의 신뢰도는 3.28점 ...

