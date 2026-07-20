// web/diagnosis-spec.json 의 타입 정의 — 사양(SSOT)은 notebooks/09가 export, 여기서는 소비만 한다.
// v1.1: baseline(분위수/CDF)·boundary_band(경계 밴드)·profiles(유형 카드) 추가.

export type CredKey = "cred_fair" | "cred_professional" | "cred_accurate";

export type QuadrantKey = "TT" | "TF" | "FT" | "FF";

/** 신뢰 점수 분위수 lookup — cred3 완답 도달 가능 점수 전량(≤125) */
export interface TrustPercentiles {
  scores: number[];
  pct_below: number[];
  pct_at_or_below: number[];
}

/** 다양성(0~8 이산) 누적분포 lookup */
export interface DiversityCdf {
  richness: number[];
  pct_below: number[];
  pct_at_or_below: number[];
}

export interface Baseline {
  n: number;
  note: string;
  trust_percentiles: TrustPercentiles;
  diversity_cdf: DiversityCdf;
}

/** 임계 부근 판정 고지 밴드 — 입력 ±1 변화가 만드는 최대 점수 변화 */
export interface BoundaryBand {
  trust_half_width_1_100: number;
  diversity_half_width_1_100: number;
  rule: string;
}

export interface ProfileFact {
  text: string;
  /** 검증 근거 노트북 참조(예: "notebooks/08 §6(a)") */
  evidence: string;
}

export interface PersonaProfile {
  facts: ProfileFact[];
}

export interface DiagnosisSpec {
  version: string;
  inputs: {
    cred_items: Record<CredKey, { label: string; scale: [number, number] }>;
    media_items: Record<string, string>;
  };
  trust: {
    item_mean: Record<CredKey, number>;
    item_std: Record<CredKey, number>;
    raw_min: number;
    raw_max: number;
    threshold_1_100: number;
  };
  diversity: {
    richness_min: number;
    richness_max: number;
    threshold_1_100: number;
  };
  quadrant_labels: Record<QuadrantKey, string>;
  prescriptions: Record<
    string,
    { diagnosis: string; rx: string; evidence: string }
  >;
  baseline: Baseline;
  boundary_band: BoundaryBand;
  profiles: Record<string, PersonaProfile>;
}

export interface DiagnosisResult {
  /** 4사분면 키: 신뢰(T/F) + 다양성(T/F) */
  quadrantKey: QuadrantKey;
  /** 페르소나 라벨(예: 건강한 소비자) */
  persona: string;
  /** 신뢰 점수(1~100, 임계 비교는 비반올림 값) */
  trustScore: number;
  /** 다양성 점수(1~100) */
  diversityScore: number;
  prescription: { diagnosis: string; rx: string; evidence: string };
}

/** 결과 화면용 — 판정 + 상대 위치 + 경계 밴드 여부 */
export interface WizardResult extends DiagnosisResult {
  /** 기준선에서 내 신뢰 점수 미만인 비율(%) — "N%보다 높은 위치(방향)" */
  trustPctBelow: number;
  /** 기준선에서 내 매체 수 미만인 비율(%) */
  diversityPctBelow: number;
  nearBoundary: { trust: boolean; diversity: boolean };
  mediaCount: number;
}
