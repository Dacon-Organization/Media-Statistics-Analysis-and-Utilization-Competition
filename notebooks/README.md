# notebooks/ — 분석 노트북 (32개 완전 지도)

Jupyter 노트북. **ZIP 추가 산출물로 제출**하며, 대회 심사에서 "실제 분석 과정"을 보여주는 핵심 증거다.

## 번호 대역 체계

| 대역 | 트랙 | 내용 |
|------|------|------|
| **0x (01~09)** | A 횡단 | 지수(NCHI)·페르소나 — EDA→매핑→설계→군집→평가→심층→웹데모 사양 |
| **1x (10~19)** | B 데이터 (P2·P3) | 메타 파악→하모나이즈→원자료 재검증→가중치·특수코드·crosswalk·품질 게이트 |
| **2x (20~29)** | B 모델링 (P2·P4) | EDA→MGCFA→교차검증→정렬법→MK/APC→강건성·방법론 심층 |
| **3x (30~32)** | B 평가·보고 (P5·P6) | 종합 평가→figure export→PDF 조판 |

## 5단계 표준 DS 파이프라인 ↔ 노트북 지도

본 프로젝트는 **데이터분석 표준 5단계**를 그대로 밟으며, 업계표준 **CRISP-DM**과 이중 라벨로 매핑한다.
각 노트북 표지의 `📍 파이프라인 위치` 배너가 자신이 어느 단계인지 가리킨다.

| 5단계 (표준 DS 흐름) | CRISP-DM | 종단 트랙(B, 7개년) | 횡단면 트랙(A) |
|------|------|------|------|
| **① 데이터 파악·문제정의** | P1·P2 | `10`·`12`(원자료 재검증)·`16`(2022 구조) | `01` |
| **② 데이터 전처리** | P3 | `11`·`13`(가중치)·`14`(특수코드)·`15`(crosswalk)·`19`(품질 게이트) | `01`(정제 일부)·`06`(다양성축) |
| **③ EDA·시각화** | P2 | `20`·`17`(단일문항 궤적) | `01` |
| **④ 피처 엔지니어링** | P3·P4 | `18`(신뢰도·상관구조) | `02`·`03`·`06`·`07`(신뢰축) |
| **⑤ 모델링·평가** | P4·P5 | `21`·`22`·`23`·`24`·`25`(강건성)·`26`(MK)·`27`(APC)·`28`(코호트)·`29`(삼각)·`30` | `04`·`05`(A트랙 평가)·`08`(프로파일) |
| **보고·전개** | P6 | `31`(figure export)·`32`(조판) | `09`(B2C 진단 사양 → 웹데모) |

> ✅ **현황(2026-07-12, P6-B-5 전면 정비 완료)**: 기존 13개(01~04·10·11·20~24·30·31)는 **stale 게이트 갱신·시각화 보강 리팩토링** 완료, 빈 번호 19개(05~09·12~19·25~29·32)는 **신규 작성** 완료 — 전 32종 벤치마크 5요소·thin import·실행 출력 포함(에러 0·검증 셀 전부 PASS). 다음 = P6-C 웹데모(`09`의 `web/diagnosis-spec.json` 소비).
> 원고·figure 정합의 SSOT는 [`../docs/report/p6-pdf-structure.md`](../docs/report/p6-pdf-structure.md) §3(인용 수치표)·`src/p5_evaluation.py` 인용 상수이며, 신규 노트북은 **새 결론을 만들지 않고** 기존 검증 자산을 재입증·심화한다.

## A트랙 0x — 횡단(지수·페르소나)

```
01-eda-2025.ipynb              # 7개년 통합 EDA·문제정의(순진 pool 편향 → 설계결정 매핑)          [✅ 다개년]
02-variable-mapping.ipynb      # 개념→변수 정렬(7개년 crosswalk 정합성)                           [✅ 다개년]
03-health-index.ipynb          # 뉴스 건강 지수(NCHI) 설계·산출(7개년 추세·페르소나 구성비)        [✅ 다개년]
04-personas-kmeans.ipynb       # 군집 페르소나(K-means, 단년 과적합 교정 ARI 진단)                 [✅ 다개년]
05-a-track-evaluation.ipynb    # A트랙 종합 평가 — 구성타당도·ARI 진단·종단↔횡단 외적 타당도·자격등급 [✅ 벤치마크]
06-diversity-deep-dive.ipynb   # 다양성축 심층 — fixed8/incl 설계·신설매체 기여 분해·formative 규율  [✅ 벤치마크]
07-trust-axis-deep-dive.ipynb  # 신뢰축 심층 — pooled z 합성·스케일링·연도별 α·reflective 자격      [✅ 벤치마크]
08-persona-profiles.ipynb      # 페르소나 프로파일 심층 — 4유형 × 인구·매체·회피 가중 프로파일 전수  [✅ 벤치마크]
09-b2c-diagnosis-spec.ipynb    # B2C 진단 규칙 설계 — 입력 최소문항·판정 로직·처방(웹데모 사양 SSOT) [✅ 벤치마크]
```

## B트랙 1x — 데이터 (P2·P3)

`src/*.py`(로직 SSOT)를 **import해 단계별 과정·중간 출력을 보여주는** 실행 노트북.
로직을 재구현하지 않고(thin), `self_validation()`·assert로 입증한다. 출처 보고서는 `docs/design/`.

```
10-data-understanding.ipynb    # P2 — 7개년 메타·인코딩3종·가중치명4종·변수명 직결불가·crosswalk    [✅ 벤치마크]
11-data-prep-harmonize.ipynb   # P3 — build_year 재코딩(전/후)·7개년 결합(90,996행)·자기점검        [✅ 벤치마크]
12-kpf-revalidation.ipynb      # P2·P5 — 원자료 재검증: 공식 보고서 ↔ 재계산 전 셀 대조·계단 실재    [✅ 벤치마크]
13-weighting-design.ipynb      # P3 — 가중치명 4종 통일·정규화·wt_year_eq 설계와 효과·민감도         [✅ 벤치마크]
14-special-codes.ipynb         # P3 — 특수코드·결측 의미기반 분기 단위검증·구조적 부재 vs 무응답      [✅ 벤치마크]
15-crosswalk-validation.ipynb  # P3 — presence matrix·신뢰 배터리+매체 8종 7개년 가용성 게이트       [✅ 벤치마크]
16-2022-structure.ipynb        # P2 — 2022 가구/개인 이중구조·표본 지배·cap 처리 계보               [✅ 벤치마크]
17-single-item-trend.ipynb     # P2 — 단일문항 신뢰 궤적(2020~2025)·삼각검증 B궤적 해부             [✅ 벤치마크]
18-reliability-structure.ipynb # P4 토대 — cred 배터리 연도별 α·상관행렬·단일차원성                  [✅ 벤치마크]
19-data-quality-gate.ipynb     # P3 마감 — self_validation 일괄·행수·범위·라운드트립 판정표          [✅ 벤치마크]
```

## B트랙 2x — 모델링 (P2·P4)

```
20-eda-overview.ipynb          # P2 — 7개년 통합 EDA 6패널(src/eda_overview.py)                    [✅]
21-mgcfa-invariance.ipynb      # P4 — MGCFA 측정 비동등(configural→metric→scalar, ΔCFI/ΔRMSEA)    [✅]
22-mgcfa-semopy-crossval.ipynb # P4 — 직접구현 ↔ semopy 교차검증(표준적재 최대차 0.0003·α)         [✅]
23-alignment-trend.ipynb       # P4 — 정렬법 잠재평균 추세(Δα=+0.671·비동등 2.4%≤20%→비교 정당)    [✅ 벤치마크]
24-trend-apc.ipynb             # P4 — MK(P(S>0)=1.00)+APC(기간주도 r≥+0.96·코호트 구배 -0.891)     [✅ 벤치마크]
25-robustness-synthesis.ipynb  # P4 — 강건성 종합: 가중 3변형·표본상한·3vs4지표 일괄 재실행 비교     [✅ 벤치마크]
26-mk-sen-deep-dive.ipynb      # P4 — MK/Sen 심층: n=7 순열 정확분포·부트스트랩 τ 분포 해부         [✅ 벤치마크]
27-apc-identification.ipynb    # P4 — APC 식별 문제 심층: 선형종속·간격차 설계·HAPC↔IE 삼각         [✅ 벤치마크]
28-cohort-gradient.ipynb       # P4 — 코호트 구배 심층: IE 편차 -0.891·소표본 규칙·세대교체 함의     [✅ 벤치마크]
29-triangulation-deep.ipynb    # P4·P5 — 삼각검증 심층: z-겹침·단년 저점 불일치의 정직한 처리        [✅ 벤치마크]
```

## B트랙 3x — 평가·보고 (P5·P6)

```
30-evaluation.ipynb            # P5 — 증거 사다리·삼각검증 종합(인용 상수 drift 검증·자격등급)       [✅ 벤치마크]
31-figure-export.ipynb         # P6 — 보고서 figure F3~F6·F10·F11 export 입증(thin import·SSOT assert 7종) [✅ 벤치마크]
32-report-typeset.ipynb        # P6 — 조판 입증: md→HTML(그림 승격·미주)→Chrome PDF·쪽수 게이트     [✅ 벤치마크]
```

## 규칙

- 데이터는 [`../data/`](../data/)에서 로드. `.sav`는 `pyreadstat`(인코딩 fallback). `*.parquet`은 gitignore → 노트북/`src`로 재생성.
- **종단 트랙(B)은 실행 출력(표·검증 PASS·figure)을 박은 채 커밋**한다(재현성·입증 목적). 콘솔 cp949 회피: `PYTHONIOENCODING=utf-8`.
- 재실행: `PYTHONIOENCODING=utf-8 jupyter nbconvert --to notebook --execute --inplace notebooks/<파일>.ipynb`.
- 무거운 raw 캡처는 인라인 대신 `docs/design/figures/`로 분리(대용량 base64 지양).
- ✅ **KPF 원자료 재검증 완료**([`../docs/design/kpf-revalidation.md`](../docs/design/kpf-revalidation.md), 2026-07-11 · 입증 노트북 = `12`): 신뢰 절대수준·배터리는 공식 보고서와 전 셀 일치 — 인용 자격은 [`../docs/report/p6-pdf-structure.md`](../docs/report/p6-pdf-structure.md) §3 자격등급 표를 따른다(잔여 게이트: 매체별 이용률 정의 대조·뉴스회피 출처 → 해당 수치는 미인용 방침).
