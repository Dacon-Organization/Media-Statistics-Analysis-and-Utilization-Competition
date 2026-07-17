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
| 27 | **IE(내재적 추정량) 원 서지** | Yang, Fu & Land 2004/2008 (IE 제안 논문) | ⚠️ manuscript에 Yang & Land 2006(HAPC)만 — IE 별도 서지 미기재 | **선택 조사 ①** |
| 13 | 설계효과 Kish 근사(deff=1+CV²) | Kish 1965/1992 | ⚠️ 관례 산식 — 서지 미기재(노트북 서술용, 보고서 미인용) | **선택 조사 ②** |
| 05 | K-means 타당화·ARI 해석 기준(0.5 '강한 일치') | Steinley 2004 등 ARI 벤치마크 문헌 | ⚠️ 관례 임계 — 서지 미기재(보고서 미인용, 노트북 진단용) | **선택 조사 ③** |
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
