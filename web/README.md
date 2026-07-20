# web/ — "뉴스 건강검진" 웹 데모

Next.js 15 기반 실동작 데모. **진단 플로우 1개에 집중**(대중투표·실현가능성 증명용).

## 원칙
- **DB·백엔드 없이** 사양 상수를 **브라우저에서 계산** → 정적 배포(`output: "export"`).
- 판정 사양 SSOT = [`diagnosis-spec.json`](diagnosis-spec.json) **v1.1** (notebooks/09가 export) — 웹은 **소비만**, 로직 재정의 금지.
- 히어로 기능(진단→페르소나→처방)만 구현. 계정·연도추적·B2G 대시보드는 결과 화면의 "다음 버전" 카드로 비전 제시.
- 스택: Next.js 15(App Router) + TypeScript(strict) + Tailwind 4. Mobile First.

## 실행
```
npm install && npm run dev      # 개발 (http://localhost:3000)
npm run build                   # 정적 빌드 → out/ (/, /method)
npm run verify                  # 판정·분위수·경계밴드 검증 (notebooks/09 파이썬 기준값 대조)
```

## 구조 (스텝 위저드 + 결과지 + /method)
- [`app/page.tsx`](app/page.tsx) — 조립 전용: Hero → StepIndicator/WizardShell(전환 애니메이션) → ResultSheet
- [`app/method/page.tsx`](app/method/page.tsx) — 방법론 전문 공개(판정 규칙·K-means 기각 근거·자격 규율·사양 공개)
- [`lib/diagnosis.ts`](lib/diagnosis.ts) — `diagnose`(09 §5 이식) + v1.1 lookup 3종(`lookupTrustPercentile`·`lookupDiversityPercentile`·`isNearBoundary`) — 전부 spec 조회만
- [`lib/useDiagnosisWizard.ts`](lib/useDiagnosisWizard.ts) — 위저드 상태 훅(향후 멀티페이지 분리 대비 완결 설계)
- `components/` — Hero·StepIndicator·WizardShell·StepMedia·StepTrust·EvidenceBadge·QuadrantChart(사분면 tint + 경계 밴드 스트립 + 펄스 링)
- `components/result/` — ResultSheet(`#result-sheet` = F9 캡처 단위): PersonaCard·RelativePosition(상대 위치)·ProfileCard(검증 facts)·PrescriptionCard·BoundaryNotice·Disclaimer·VisionCards
- [`scripts/verify-diagnosis.mjs`](scripts/verify-diagnosis.mjs) — 판정 3케이스 + 분위수 lookup 대조 + 테이블 무결성 + 경계 밴드 케이스

## spec v1.1 (notebooks/09 §7~§10)
| 키 | 내용 | 입증 |
|----|------|------|
| `baseline` | 신뢰 도달가능 점수(≤125) 분위수 + 다양성 CDF(0~8) | 09 §10(e) 단조·중앙값 정합 |
| `profiles` | 유형별 방향 facts(절대 수치 regex 봉인) | 09 §8 = 08 §6 재검증 후 조립 |
| `boundary_band` | 임계 부근 판정 고지 반경(±1 섭동 최대 변화) | 09 §9 — 1,125 입력 전수 brute-force |

v1.0 판정 상수는 불변(09 §10(g)) → 90,996행 전수 일치(09 §4)는 그대로 유효.

## 검증 결과 (2026-07-17, 판정 대조)
| 케이스 | 입력 | 판정 | 신뢰 | 다양성 |
|--------|------|------|------|--------|
| TV만 보는 고신뢰 | cred(4,4,4) · 1매체 | 신뢰편향형 | 75.3 | 13.4 |
| 다채널 저신뢰 탐색가 | cred(2,3,2) · 6매체 | 비판적 탐색형 | 33.9 | 75.3 |
| 평균적 이용자 | cred(3,3,3) · 3매체 | 비판적 탐색형 | 50.5 | 38.1 |

JS 판정 ≡ notebooks/09 파이썬 기준(오차 < 1e-9) — `npm run verify` 전부 PASS.
