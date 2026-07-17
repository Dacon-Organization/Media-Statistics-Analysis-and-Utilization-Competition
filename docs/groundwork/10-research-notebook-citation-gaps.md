# 10 · Perplexity 추가 조사 필요성 판정 — 노트북 32종 방법론 인용 전수 점검 (P6-B-5)

> **작성**: 2026-07-12 · **목적**: 전면 정비된 노트북 01~32의 방법론 서술이 외부 서지를 필요로 하는 지점을 전수 점검하고, 추가 조사가 필요한 항목만 Perplexity 브리프로 남긴다.
> **결과 요약**: 보고서(manuscript) 인용 요구는 기존 조사(groundwork 07~09)로 **전부 충족**. 노트북 자체는 서지 인용이 필수가 아니나, **선택 실행 시 설득력이 오르는 3건**을 브리프로 정리(아래 §2). 실행하지 않아도 제출 요건에 결손 없음.

---

## 1. 판정표 — 방법론 서술 × 서지 현황

| 노트북 | 방법론 서술 | 필요 서지 | 현황 | 판정 |
|--------|------------|----------|------|:---:|
| 21~23·25 | 정렬법·비동등 25% 준거 | Asparouhov & Muthén 2014 · Muthén & Asparouhov 2014 · Flake & McCoach 2018 | ✅ 확보(manuscript 참고문헌 + groundwork 09) | 불요 |
| 12 | house effect(실사기관 변경) | Smith 1978 · Schnell & Klingwort 2024 | ✅ 확보(groundwork 07, A안 채택) | 불요 |
| 12·23 | 코로나기 신뢰 상승 국제 동시성 | Reuters DNR 2020-21 · Knudsen et al. 2023 | ✅ 확보(groundwork 08) | 불요 |
| 24·26 | MK/Sen 표준 | Mann 1945 · Sen 1968 | ✅ 확보(manuscript 참고문헌) | 불요 |
| 24·27·28 | HAPC | Yang & Land 2006 | ✅ 확보(manuscript 참고문헌) | 불요 |
| 27 | **IE(내재적 추정량) 원 서지** | Yang, Fu & Land 2004/2008 (IE 제안 논문) | ✅ 확보(§4-① — 2004/2008/2011 + Luo 2013 논쟁) | **해소(①)** |
| 13 | 설계효과 Kish 근사(deff=1+CV²) | Kish 1965/1992 | ✅ 확보(§4-② — 직접 출처는 **Kish 1987**로 정정) | **해소(②)** |
| 05 | K-means 타당화·ARI 해석 기준(0.5 '강한 일치') | Steinley 2004 등 ARI 벤치마크 문헌 | ✅ 확보(§4-③ — '0.5 강한 일치' 근거 부재, Steinley 구간으로 교체) | **해소(③)** |
| 06 | Richness=Hill₀·formative 지수 규율 | Hill numbers·formative index 문헌 | ✅ 확보(groundwork 06 §결과 에이전트 리서치) | 불요 |
| 18 | Cronbach α 관례 0.70 | Nunnally 1978 | △ 통용 관례 — 필요 시 ②와 함께 | (②에 포함) |

**판정 원칙**: 보고서(PDF) 본문에 인용되는 방법론은 서지 필수(→ 전부 확보됨). 노트북 내부 서술만의 관례 산식·임계는 서지가 있으면 좋으나 결손 아님.

---

## 2. 선택 실행 브리프 (Perplexity 프롬프트 — 사용자 실행용)

각 프롬프트는 독립 실행 가능. 결과는 본 문서 아래에 §결과로 붙이고, 서지는 manuscript 참고문헌 또는 해당 노트북 표지에만 반영(수치 게이트와 무관).

### ① IE(Intrinsic Estimator) 원 서지
> "APC(Age-Period-Cohort) 분석의 Intrinsic Estimator를 제안·정식화한 원 논문들의 정확한 서지를 정리해줘: Yang, Fu, Land 계열(2004 Sociological Methodology, 2008 AJS 등)과 IE의 영공간(null space) 제약 해석, 그리고 IE 비판(Luo 2013 Demography 'Assessing Validity and Application Scope of the Intrinsic Estimator')과 응답 논문까지. 각 논문의 정확한 제목·저널·권호·DOI를 인용 형식으로."

### ② 설계효과·신뢰도 관례 서지
> "설문 가중치 설계효과의 Kish 근사 deff = 1 + CV²(가중치 변동계수) 공식의 원 출처(Kish 1965 Survey Sampling 또는 1992 논문)와, Cronbach α ≥ 0.70 관례의 원 출처(Nunnally 1978 Psychometric Theory) 및 이 임계에 대한 현대적 비판(예: Lance et al. 2006)의 정확한 서지를 정리해줘."

### ③ ARI 일치 수준 해석 기준
> "군집 일치도 Adjusted Rand Index(ARI)의 해석 기준(예: 0.5 이상 '강한 일치' 등)을 제시하거나 검증한 방법론 문헌을 찾아줘 — Steinley 2004 (Psychological Methods, 'Properties of the Hubert-Arabie adjusted Rand index')를 포함해, ARI 값 구간별 해석 가이드가 있는 문헌의 정확한 서지를."

---

## 3. 처리 방침

- ①~③은 **보고서 결론·수치에 영향 없음** — 미실행 시에도 제출 결손 없음(관례 산식은 노트북에 '관례'로 명시돼 있음).
- 실행하게 되면: §결과 추가 → manuscript 참고문헌(방법론 절)에 서지만 추가 → `30` §6 drift 파싱 6종 문서는 무변경 원칙 유지.

---

## 4. 조사 결과 (2026-07-17 실행 — Perplexity, 사용자 제공)

①~③ 전부 실행 완료. 아래 서지는 DOI까지 교차확인된 것만 수록하고, 확인 실패 항목은 "확인 안 됨"으로 명시한다. 반영 범위: manuscript 참고문헌(① IE만 — 보고서 본문이 IE를 인용하므로) + 노트북 04·05·13·18·27 서술(P6-B-6).

### 4-① IE(Intrinsic Estimator) — 원 서지·영공간 제약 논쟁

**핵심 교훈**: IE는 APC 식별문제를 "해결"하는 것이 아니라, 설계행렬 영공간(null space) 방향의 계수 성분을 0으로 두는 **특정 제약을 채택하는 추정량**이다(b·b₀=0). 이 제약은 범주 수·코딩 설계에 의존하며 데이터만으로 타당성을 검증할 수 없다 — 노트북 27의 기존 서술("검증 불가한 기하학적 가정")과 정합.

| 서지 | DOI |
|------|-----|
| Yang, Y., Fu, W. J., & Land, K. C. (2004). A methodological comparison of age-period-cohort models: The intrinsic estimator and conventional generalized linear models. *Sociological Methodology*, 34(1), 75–110. | 10.1111/j.0081-1750.2004.00148.x |
| Yang, Y., Schulhofer-Wohl, S., Fu, W. J., & Land, K. C. (2008). The intrinsic estimator for age-period-cohort analysis: What it is and how to use it. *American Journal of Sociology*, 113(6), 1697–1736. | 10.1086/587154 |
| Fu, W. J., Land, K. C., & Yang, Y. (2011). On the intrinsic estimator and constrained estimators in age-period-cohort models. *Sociological Methods & Research*, 40(3), 453–466. | 10.1177/0049124111415355 |
| Luo, L. (2013). Assessing validity and application scope of the intrinsic estimator approach to the age-period-cohort problem. *Demography*, 50(6), 1945–1967. **[비판]** IE는 b 전체가 아닌 영공간 수직 투영 b₁을 추정 — 실제 계수가 제약을 만족할 때만 불편 | 10.1007/s13524-013-0243-z |
| Yang, Y. C., & Land, K. C. (2013). Misunderstandings, mischaracterizations, and the problematic choice of a specific instance in which the IE should never be applied. *Demography*, 50(6), 1969–1971. **[응답]** IE는 만능 해법이 아니며 축소모형 적합도 검토 선행 필요 | 10.1007/s13524-013-0254-9 |
| Luo, L. (2013). Paradigm shift in age-period-cohort analysis: A response to Yang and Land, O'Brien, Held and Riebler, and Fienberg. *Demography*, 50(6), 1985–1988. **[재응답]** | 10.1007/s13524-013-0263-8 |

**확인 안 됨**: Fu(2000) 선행 제안의 정확한 서지 · 같은 호 O'Brien / Held & Riebler / Fienberg 코멘터리 3편의 제목·페이지·DOI(인용하려면 *Demography* 50(6) 목차에서 재대조 필요) — 본 프로젝트는 이들을 인용하지 않는다.

### 4-② Kish 설계효과 · Cronbach α 관례

**정정**: `deff = 1 + CV²(w)`의 직접 출처는 Kish 1965/1992가 **아니라 Kish (1987)**. 1965는 DEFF 개념의 원전, 1992는 후속 재표현. 또한 이 공식은 **가중치 불균등 성분만의 근사**로, 층화·집락 효과를 포함하지 않으며 가중치-분석변수 독립 등의 가정 아래 성립.

| 서지 | 역할 |
|------|------|
| Kish, L. (1965). *Survey Sampling*. New York: Wiley. | design effect(DEFF) 개념 원전 |
| Kish, L. (1987). Weighting in Deft². *The Survey Statistician*, June, 26–30. | **deff_w = 1+CV²(w) 공식의 직접 출처** |
| Kish, L. (1992). Weighting for unequal Pᵢ. *Journal of Official Statistics*, 8(2), 183–200. | 후속 재표현 |
| Gabler, S., Häder, S., & Lahiri, P. (1999). A model-based justification of Kish's formula for design effects for weighting and clustering. *Survey Methodology*, 25(1), 105–106. | 모형 기반 검증(특정 조건에서 보수적) |
| Nunnally, J. C. (1978). *Psychometric Theory* (2nd ed.). McGraw-Hill. | α .70은 **초기 연구 단계** 권고(기초연구 .80, 적용 검사 .90+) — 보편 합격선 아님 |
| Lance, C. E., Butts, M. M., & Michels, L. C. (2006). The sources of four commonly reported cutoff criteria: What did they really say? *Organizational Research Methods*, 9(2), 202–220. DOI 10.1177/1094428105284919 | 절단값의 탈맥락 인용("methodological urban legends") 비판 |

### 4-③ ARI 해석 기준 — "0.5 = 강한 일치"는 근거 부재

**정정**: "ARI ≥ 0.5 = 강한 일치" 같은 보편 합의 기준은 **확인되지 않음**. 표준 실무 가이드는 Steinley(2004)에 귀속되는 군집 복원도 구간: **< 0.65 poor / 0.65–0.80 moderate / 0.80–0.90 good / ≥ 0.90 excellent**. 본 프로젝트 실측 pooled ARI 0.195는 어느 기준으로도 poor → **노트북 04·05의 결론("규칙 기반 유지, K-means는 진단용") 불변**, 판정 문구의 임계만 서지 있는 기준으로 교체. ARI 이론 하한은 -0.5 고정이 아니므로 음수는 "우연보다 낮은 일치"로만 해석.

| 서지 | DOI |
|------|-----|
| Hubert, L., & Arabie, P. (1985). Comparing partitions. *Journal of Classification*, 2, 193–218. | 10.1007/BF01908075 |
| Steinley, D. (2004). Properties of the Hubert-Arabie adjusted Rand index. *Psychological Methods*, 9(3), 386–396. | 10.1037/1082-989X.9.3.386 |
| Steinley, D., Brusco, M. J., & Hubert, L. (2016). The variance of the adjusted Rand index. *Psychological Methods*, 21(2), 261–272. | — |
| Warrens, M. J., & van der Hoef, H. (2022). Understanding the adjusted Rand index and other partition comparison indices based on counting object pairs. *Journal of Classification*. | 10.1007/s00357-022-09413-z — 군집 크기 불균형 시 ARI가 큰 군집에 좌우됨(단독 근거 사용 금지의 근거) |

### 4-④ 반영 내역 (P6-B-6)

- manuscript 참고문헌: ① IE 3건 + Luo/Yang & Land 2013 추가(본문 §3·§7.3 IE 언급과 연결). ②③은 보고서 미인용 원칙 유지 — 노트북 전용.
- 노트북: `27`(IE 서지·영공간 가정), `13`(Kish 1987 정정), `05`(ARI 판정 Steinley 구간 교체), `04`·`18`(정합화).
