// 판정 로직 — notebooks/09 §5 diagnose()의 JS 이식.
// 사양(web/diagnosis-spec.json)의 상수만 사용하며 로직을 재정의하지 않는다.
// (09 §4에서 이 상수 경로가 파이프라인 판정과 90,996행 전수 일치함이 입증됨)

import type {
  CredKey,
  DiagnosisSpec,
  DiagnosisResult,
  QuadrantKey,
} from "./types";

export const CRED_KEYS: readonly CredKey[] = [
  "cred_fair",
  "cred_professional",
  "cred_accurate",
];

/**
 * 기준선 출처 표기(예: 「언론수용자 조사」 2019–2025) — 조사명·연도를 사양에서만 읽는다.
 * 화면에 조사명·연도를 하드코딩하면 데이터와 어긋날 수 있으므로 전 표기가 이 함수를 거친다.
 */
export function baselineLabel(spec: DiagnosisSpec): string {
  const [from, to] = spec.baseline.years;
  return `「${spec.baseline.survey}」 ${from}–${to}`;
}

/**
 * cred 3문항(1~5) + 이용 매체 수(0~8) → 4사분면 페르소나 판정.
 * 임계 비교는 비반올림 값으로 수행(반올림하면 경계 응답자 판정이 뒤집힐 수 있음 — 09 §2 주석).
 */
export function diagnose(
  spec: DiagnosisSpec,
  cred: Record<CredKey, number>,
  mediaCount: number,
): DiagnosisResult {
  const t = spec.trust;
  const d = spec.diversity;

  // 신뢰: 문항별 z 표준화 → 평균 → 1~100 선형 스케일
  const zMean =
    CRED_KEYS.reduce(
      (acc, c) => acc + (cred[c] - t.item_mean[c]) / t.item_std[c],
      0,
    ) / CRED_KEYS.length;
  const trustScore = 1 + ((zMean - t.raw_min) / (t.raw_max - t.raw_min)) * 99;

  // 다양성: richness(이용 매체 수) → 1~100 선형 스케일
  const diversityScore =
    1 +
    ((mediaCount - d.richness_min) / (d.richness_max - d.richness_min)) * 99;

  const quadrantKey = ((trustScore >= t.threshold_1_100 ? "T" : "F") +
    (diversityScore >= d.threshold_1_100 ? "T" : "F")) as QuadrantKey;
  const persona = spec.quadrant_labels[quadrantKey];

  return {
    quadrantKey,
    persona,
    trustScore,
    diversityScore,
    prescription: spec.prescriptions[persona],
  };
}

/**
 * 신뢰 점수 → 기준선(90,996명)에서 내 점수 미만인 비율(%).
 * 도달 가능 점수 전량(≤125)이 spec에 열거돼 있으므로 최근접 조회만 한다(재계산 없음).
 */
export function lookupTrustPercentile(
  spec: DiagnosisSpec,
  trustScore: number,
): number {
  const { scores, pct_below } = spec.baseline.trust_percentiles;
  let best = 0;
  for (let i = 1; i < scores.length; i++) {
    if (Math.abs(scores[i] - trustScore) < Math.abs(scores[best] - trustScore))
      best = i;
  }
  return pct_below[best];
}

/** 이용 매체 수(0~8) → 기준선에서 내 매체 수 미만인 비율(%) — CDF lookup */
export function lookupDiversityPercentile(
  spec: DiagnosisSpec,
  mediaCount: number,
): number {
  const idx = spec.baseline.diversity_cdf.richness.indexOf(mediaCount);
  return spec.baseline.diversity_cdf.pct_below[idx];
}

/**
 * 임계 부근 판정 여부 — 입력 ±1(문항 1개 또는 매체 1개) 변화로
 * 유형이 바뀔 수 있는 구간인지. 밴드 상수는 notebooks/09 §9가 전수 입증.
 */
export function isNearBoundary(
  spec: DiagnosisSpec,
  trustScore: number,
  diversityScore: number,
): { trust: boolean; diversity: boolean } {
  const bb = spec.boundary_band;
  return {
    trust:
      Math.abs(trustScore - spec.trust.threshold_1_100) <=
      bb.trust_half_width_1_100,
    diversity:
      Math.abs(diversityScore - spec.diversity.threshold_1_100) <=
      bb.diversity_half_width_1_100,
  };
}
