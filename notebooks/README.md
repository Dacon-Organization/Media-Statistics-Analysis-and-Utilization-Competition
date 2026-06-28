# notebooks/ — 분석 노트북

Jupyter 노트북. **ZIP 추가 산출물로 제출**하며, 대회 심사에서 "실제 분석 과정"을 보여주는 핵심 증거다.

## 5단계 표준 DS 파이프라인 ↔ 노트북 지도

본 프로젝트는 **데이터분석 표준 5단계**를 그대로 밟으며, 업계표준 **CRISP-DM**과 이중 라벨로 매핑한다.
각 노트북 표지의 `📍 파이프라인 위치` 배너가 자신이 어느 단계인지 가리킨다.

| 5단계 (표준 DS 흐름) | CRISP-DM | 종단 트랙(B, 7개년) | 횡단면 트랙(A, 2025) |
|------|------|------|------|
| **① 데이터 파악·문제정의** | P1·P2 | `10-data-understanding` | `01-eda-2025` |
| **② 데이터 전처리** | P3 | `11-data-prep-harmonize` | `01`(정제 일부) |
| **③ EDA·시각화** | P2 | `20-eda-overview` | `01-eda-2025` |
| **④ 피처 엔지니어링** | P3·P4 | (crosswalk·credibility 배터리) | `02-variable-mapping`·`03-health-index` |
| **⑤ 모델링·평가** | P4·P5 | `21`·`22`·`23`·`24`·`30` | `04-personas-kmeans` |

> ⚠️ **현황(2026-06-28)**: 종단 트랙(B)이 메인 라인이며 벤치마크 스타일로 정비 중이다. 횡단면 트랙(A, 01~04)은
> **2025 단일연도만 실험**한 초기 산출이라, 7개년 전체 데이터 기준으로 **전면 리팩토링 진행 중**.
> 설계 확정 = [`../docs/design/notebook-refactor-plan.md`](../docs/design/notebook-refactor-plan.md)(다양성축 A안·신규 `src/health_index_panel.py`·03 다개년 우선).
> 선행조건 = 다양성 하모나이즈 Perplexity 브리프 [`../docs/groundwork/06-research-diversity-harmonization-brief.md`](../docs/groundwork/06-research-diversity-harmonization-brief.md)(실행 대기).

## 두 트랙

### A. 2025 횡단면 트랙 (01~04) — 지수·페르소나
```
01-eda-2025.ipynb              # 2025 .sav 로딩·기초 탐색
02-variable-mapping.ipynb      # 코드북 ↔ 지수 변수 매핑
03-health-index.ipynb          # 뉴스 건강 지수(NCHI) 설계·산출
04-personas-kmeans.ipynb       # 군집 페르소나(K-means)
```

### B. 7개년 종단 트랙 (10~30) — CRISP-DM 파이프라인 입증
`src/*.py`(로직 SSOT)를 **import해 단계별 과정·중간 출력을 보여주는** 실행 노트북.
로직을 재구현하지 않고(thin), `self_validation()`·assert로 입증한다. 출처 보고서는 `docs/design/`.
```
10-data-understanding.ipynb    # P2 — 7개년 메타·인코딩3종·가중치명4종·변수명 직결불가·2022 구조·crosswalk   [✅]
11-data-prep-harmonize.ipynb   # P3 — build_year 재코딩(전/후)·7개년 결합(90,996행)·wt_year_eq·자기점검    [✅]
20-eda-overview.ipynb          # P2 — 7개년 통합 EDA 6패널(src/eda_overview.py)                          [✅]
21-mgcfa-invariance.ipynb      # P4 — MGCFA 측정 비동등(configural→metric→scalar, ΔCFI/ΔRMSEA)          [✅]
22-mgcfa-semopy-crossval.ipynb # P4 — 직접구현 ↔ semopy 교차검증(표준적재 최대차 0.0003·α)              [✅]
23-alignment-trend.ipynb       # P4 — 정렬법 잠재평균 추세(configural→정렬→비동등비율)                      [예정]
24-trend-apc.ipynb             # P4 — Mann-Kendall + APC(HAPC·IE) 세대효과 분해                          [예정]
30-evaluation.ipynb            # P5 — 증거 사다리·삼각검증 종합(src/p5_evaluation.py)                      [예정]
```

## 규칙
- 데이터는 [`../data/`](../data/)에서 로드. `.sav`는 `pyreadstat`(인코딩 fallback). `*.parquet`은 gitignore → 노트북/`src`로 재생성.
- **종단 트랙(B)은 실행 출력(표·검증 PASS·figure)을 박은 채 커밋**한다(재현성·입증 목적). 콘솔 cp949 회피: `PYTHONIOENCODING=utf-8`.
- 재실행: `PYTHONIOENCODING=utf-8 jupyter nbconvert --to notebook --execute --inplace notebooks/<파일>.ipynb`.
- 무거운 raw 캡처는 인라인 대신 `docs/design/figures/`로 분리(대용량 base64 지양).
- ⚠️ 분석 수치는 KPF 원자료 재검증(data-spec §6) 전 보고서·웹데모 직접 인용 신중.
