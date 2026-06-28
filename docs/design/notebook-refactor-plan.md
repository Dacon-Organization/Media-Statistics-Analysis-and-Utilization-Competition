# 구형 노트북 전면 리팩토링 설계 노트 — "2025 단일연도 → 7개년 전체 데이터"

> 작성: 2026-06-28 (KST) · 상태: **설계 확정(다양성축 방법론은 Perplexity Deep Research 대기)**
> 목적: 횡단면 트랙 A(01~04, 특히 03 NCHI·04 페르소나)가 7개년(raw 14개년) 데이터를 보유하고도
>   **2025 한 해만 실험한** 구조라는 사용자 지적을 해소. 전체 데이터(7개년 하모나이즈 패널) 기준으로 전면 리팩토링한다.
> 연관: 마스터플랜 [`analysis-master-plan.md`](analysis-master-plan.md) §2.1(기존 노트북 재배치) · crosswalk [`variable-crosswalk.md`](variable-crosswalk.md) §3.4
>   · 신뢰축 다개년 근거 [`variable-crosswalk-trust-battery.md`](variable-crosswalk-trust-battery.md) · 방법론 브리프 [`../groundwork/06-research-diversity-harmonization-brief.md`](../groundwork/06-research-diversity-harmonization-brief.md)
> ⚠️ 분석 수치는 KPF 원자료 재검증·측정 비동등 검정 전 보고서·웹데모 직접 인용 금지(`data-spec.md §6`).

---

## 0. 문제 진단 — 무엇이 "2025만 실험한 느낌"인가

| 구형 산출 | 입력 | 한계 |
|----------|------|------|
| `notebooks/03-health-index` (NCHI) | 2025 `.sav` 단일연도 | 7개년 추세 없음 — "지수의 시간적 변화"라는 가장 강한 스토리 부재 |
| `notebooks/04-personas-kmeans` | 2025 `.sav` 단일연도 | 페르소나 구성비의 연도별 이동(예: 이중취약형 증가?) 미관측 |
| `src/news_health_features.py` | **2025 전용 하드코딩** | `load_2025()`·`TRUST_CORE`(Q85_*/Q94_*)·`NEWS_DAYS`(Q2A_1 등)·`WEIGHT="WT"`·`AGE="DQ3"` 모두 2025 변수번호. 타 연도 적용 불가 |

반면 **자산은 이미 충분**하다:
- `data/processed/audience_harmonized.parquet` — 7개년(2019~2025) 통합 패널(90,996행×32컬럼). `src/harmonize.py` 산출.
- 신뢰성(credibility) 배터리 핵심3(공정·전문·정확)은 **7개년 전부 존재**(`cred_fair`/`cred_professional`/`cred_accurate`) → 신뢰 잠재요인은 이미 MGCFA(21·22)로 다개년 검정 완료.

→ **신뢰축은 즉시 다개년 가능. 병목은 다양성축(Richness)뿐.**

---

## 1. 핵심 분기 결정 (사용자 확정, 2026-06-28)

### 1.1 다양성축 7개년 마련 → **A안: crosswalk 정공법 확장** ✅

| 후보 | 내용 | 채택 |
|------|------|:--:|
| **A** | `harmonize.py`에 7개년 **매체별 이용여부/이용일수 배터리**를 신규 매핑 → 공통 매체 고정풀로 진짜 Richness·Shannon을 7개년 산출 | **✅ 채택** |
| B | 패널의 단일 `media_main_route`(주이용경로 1개)만으로 다양성 프록시 | 기각(주 1경로는 폭/breadth이 아님) |
| C | 신뢰축만 다개년, NCHI·페르소나는 2025 유지 | 기각(다개년 NCHI 야심 포기 불가) |

> **A안의 실체**: 패널의 `media_main_route`는 crosswalk §3.4의 **단일선택 주이용경로**(Q1/Q68/Q76/Q84)다.
> 그러나 2025 Richness(`news_health_features.NEWS_DAYS`)는 **12개 매체유형별 이용일수 배터리**(Q2A_1·Q14A_1 …)에 의존한다.
> 즉 둘은 **다른 변수군**이며, A안 = 「7개년 각 연도의 매체이용 배터리를 sav-meta에서 역추적해 crosswalk에 신규 매핑」이 실작업이다.

### 1.2 첫 리팩토링 묶음 → **03-health-index 다개년** ✅
- 가치가 가장 큰 산출(NCHI 추세)부터. 단, 1.1이 A안이므로 **crosswalk 다양성 배터리 확장이 선행조건**.
- 따라서 실제 착수 순서: **① Perplexity 방법론 확정 → ② crosswalk 확장 → ③ `harmonize.py` 확장 → ④ `src/health_index_panel.py` 신설 → ⑤ `03` 다개년 노트북**.

### 1.3 Perplexity 스페이스 활용 (사용자 강조)
- 방법론 갈림길마다 Perplexity Deep Research를 써온 워크플로(groundwork 00~05)를 이번 다양성 하모나이즈에도 적용한다.
- A안에는 **진짜 방법론 갈림길**이 있다(아래 §3): 공통 매체 고정풀 정의 / 이용여부 vs 이용일수 / 측정 비동등 하 다양성 추세의 타당성 / 매체 범주 증식 보정.
- → 이번 묶음의 핵심 산출 = **[`06-research-diversity-harmonization-brief.md`](../groundwork/06-research-diversity-harmonization-brief.md)**. 결과는 groundwork에 보존 후 crosswalk·코드에 반영.

---

## 2. 모듈 아키텍처 결정 — **신규 `src/health_index_panel.py` (파라미터화 아님)**

`news_health_features.py`를 `load_year(year)`로 파라미터화하지 **않고**, 패널 입력 전용 신규 모듈을 만든다.

| 근거 | 설명 |
|------|------|
| **이력 보존** | 2025 전용 `news_health_features.py`는 횡단면 트랙 A(01~04)가 그대로 작동하도록 보존(마스터플랜 §2.1 정신). |
| **스키마 상이** | 패널은 `target_var`·`cred_*` 배터리 기반(harmonize 산출). 2025 원본은 `Q85_*` 원변수. 한 함수에 우겨넣으면 연도분기 지옥. |
| **thin 원칙** | 패널 모듈은 **수학 로직을 재구현하지 않고** `news_health_features`에서 공통 함수를 import 재사용한다(로직 SSOT 유지). |

### 2.1 공통 수학 = 재사용, 입력 어댑터 = 신규
`health_index_panel.py`가 `news_health_features`에서 그대로 import할 SSOT 함수:
- `cronbach_alpha`, `_scale_1_100`, `nchi`(기하/산술), `persona_quadrant`, `wmean`, `kmeans_personas`, `adjusted_rand`

신규로 구현할 패널 전용:
- `load_panel()` — `audience_harmonized.parquet` 로더(없으면 `harmonize.py` 안내).
- `trust_index_panel(df, year=None)` — `cred_*` 배터리(연도 가용 지표) z-표준화 평균 → [1,100]. (2025 `TRUST_CORE` 22문항이 아니라 7개년 공통 신뢰성 배터리 기반.)
- `diversity_index_panel(df, year=None)` — **A안 산출물**: 고정풀 Richness(또는 e^H). crosswalk 확장 후 확정.
- `nchi_by_year(df)` — 연도별 가중 NCHI·페르소나 구성비 산출(웹데모/보고서 추세용).

> ⚠️ 패널 신뢰지수는 2025 단일연도 `trust_index`(22문항 α=0.902)와 **구성이 다르다**(7개년 공통 3~5지표).
> 절대수준 직접 비교 금지 — 추세는 "방향성" 위주(05 §1.5 측정 비동등 원칙 준용). 노트북에서 이 차이를 명시 서술.

---

## 3. Perplexity로 해소할 미결정 목록 (→ 브리프 06의 질문)

1. **공통 매체 고정풀 정의** — crosswalk §3.4는 8매체(종이신문·TV·라디오·잡지·포털·SNS·메신저·동영상)를 잠정 제시. 7개년 모두 측정된 매체집합을 확정하고, 신설항목(숏폼·AI·뉴스레터)은 보조지표로 분리하는 기준은?
2. **이용여부(binary) vs 이용일수(count)** — Richness(폭)는 이용여부, Shannon(균등도)은 이용일수가 자연스럽다. 연도별 측정형식(여부만 있는 해 vs 일수 있는 해)이 다를 때 비교가능성을 어떻게 확보?
3. **측정 비동등 하 다양성 추세** — 매체 범주 증식(2025=17범주)에서 Richness/Shannon의 연도 비교가 타당한가? e^H(유효 종 수) 변환의 정당성·한계.
4. **단일경로(media_main_route) 보강 활용** — 패널에 이미 있는 단일 주이용경로를 다양성 보조축(예: 디지털 전환 추세)으로 동시 활용하는 게 분석타당성에 더 좋은가?

---

## 4. 작업 순서(로드맵) & 이력 보존

```
[이번 묶음] 설계 확정 + Perplexity 브리프(06)            ← 현재
   ↓ (사용자 Deep Research 실행 → 06 결과 반영)
① crosswalk 확장: 7개년 매체이용 배터리 매핑(variable-crosswalk.md §3.4 확장)
② harmonize.py 확장: 고정풀 매체이용 컬럼 + 다양성 파생 산출
③ src/health_index_panel.py 신설(공통수학 import + 패널 어댑터)
④ notebooks/03-health-index 다개년 리팩토링(NCHI 7개년 추세 + 벤치마크 스타일 + 5단계 배너)
⑤ notebooks/04-personas-kmeans 다개년(페르소나 구성비 추세)
```

### 이력 보존 원칙(마스터플랜 §2.1)
- 구형 노트북(01~04)·`news_health_features.py`는 **삭제하지 않는다**. 횡단면 트랙 A로 유지.
- 03/04 다개년 리팩토링은 **동일 파일을 in-place 개선**하되, 표지에 "v1(2025 단일) → v2(7개년)" 변경 이력을 남긴다. (번호 재매핑이 필요하면 그때 결정.)
- 모든 변경은 feature 브랜치 → PR → auto-merge(R1).

---

## 5. 완료 정의 (이번 묶음)
- [x] 다양성축 A안 채택·모듈 아키텍처 결정 문서화(본 노트).
- [x] Perplexity Deep Research 브리프(06) 작성 — 사용자 스페이스 실행 대기.
- [ ] (다음 세션) 06 결과 반영 → crosswalk 확장 → harmonize 확장 → 03 다개년.
