# docs/design/ — 설계 문서

데이터·제품·시스템 설계 명세.

| 문서 | 내용 | 상태 |
|------|------|------|
| [`analysis-master-plan.md`](analysis-master-plan.md) | **분석 마스터플랜(CRISP-DM 6단계·7개년 확장·기법 위계)** — 분석 SSOT | ✅ 설계 확정 |
| [`data-spec.md`](data-spec.md) | KPF 데이터 카탈로그·변수 명세·재검증 체크리스트 | 진행 중 |
| [`preprocessing-design.md`](preprocessing-design.md) | 전처리·지수 설계(Task 02·03) | 진행 중 |
| [`2025-sav-variables.md`](2025-sav-variables.md) | 2025 .sav 변수 정본 추출물 | ✅ |
| **P2·P4·P5 — 7개년 추세 분석 산출** | | |
| [`eda-overview.md`](eda-overview.md) | P2 7개년 통합 EDA(신뢰성 배터리 6패널) | ✅ |
| [`variable-crosswalk-trust-battery.md`](variable-crosswalk-trust-battery.md) | 신뢰성 다지표 배터리 item-level crosswalk(MGCFA 입력) | ✅ |
| [`mgcfa-invariance-results.md`](mgcfa-invariance-results.md) | P4 MGCFA 측정 비동등 검정(metric 강지지) | ✅ |
| [`mgcfa-semopy-crossval.md`](mgcfa-semopy-crossval.md) | P4 직접구현 ↔ semopy 교차검증(적재 최대차 0.0003) | ✅ |
| [`alignment-trust-trend.md`](alignment-trust-trend.md) | P4 정렬 잠재평균 추세(2019→2025 +0.671SD) | ✅ |
| [`trend-apc-results.md`](trend-apc-results.md) | P4 추세검정(MK)+APC 세대효과 분해 | ✅ |
| [`p5-evaluation.md`](p5-evaluation.md) | **P5 통합 평가 서사(증거 사다리·삼각검증 종합)** | ✅ |
| (예정) 요구사항 정의서 | B2C/B2G 시나리오·기능 목록 | 예정 |
| (예정) 기능 명세 | 진단 플로우·지수 산출 로직 | 예정 |
| (예정) API·ERD 설계 | 풀 프로덕션 가정 아키텍처 | 예정 |

> 웹 데모는 DB 없이 브라우저 계산이 기본 → API/ERD는 "확장 시" 가정 설계로 작성.
