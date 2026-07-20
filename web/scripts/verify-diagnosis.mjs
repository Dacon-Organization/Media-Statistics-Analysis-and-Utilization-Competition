// 판정 로직 검증 — notebooks/09의 파이썬 기준값과 JS 이식(lib/diagnosis.ts)의 결과를 대조한다.
// 실행: npm run verify  (Node 24의 type stripping으로 .ts를 직접 import)
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import assert from "node:assert/strict";
import {
  diagnose,
  isNearBoundary,
  lookupDiversityPercentile,
  lookupTrustPercentile,
} from "../lib/diagnosis.ts";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const spec = JSON.parse(
  readFileSync(join(root, "diagnosis-spec.json"), "utf-8"),
);

// ── 1. 판정 대조: notebooks/09 §5 demo_users를 spec 상수로 재계산한 파이썬 값 ──
const cases = [
  {
    name: "TV만 보는 고신뢰 응답자",
    cred: { cred_fair: 4, cred_professional: 4, cred_accurate: 4 },
    mediaCount: 1,
    expected: { persona: "신뢰편향형", T: 75.25, D: 13.375 },
  },
  {
    name: "다채널 저신뢰 탐색가",
    cred: { cred_fair: 2, cred_professional: 3, cred_accurate: 2 },
    mediaCount: 6,
    expected: { persona: "비판적 탐색형", T: 33.912025409389585, D: 75.25 },
  },
  {
    name: "평균적 이용자",
    cred: { cred_fair: 3, cred_professional: 3, cred_accurate: 3 },
    mediaCount: 3,
    expected: { persona: "비판적 탐색형", T: 50.5, D: 38.125 },
  },
];

for (const c of cases) {
  const r = diagnose(spec, c.cred, c.mediaCount);
  assert.equal(r.persona, c.expected.persona, `${c.name}: 페르소나 불일치`);
  assert.ok(
    Math.abs(r.trustScore - c.expected.T) < 1e-9,
    `${c.name}: 신뢰 점수 불일치 (${r.trustScore} vs ${c.expected.T})`,
  );
  assert.ok(
    Math.abs(r.diversityScore - c.expected.D) < 1e-9,
    `${c.name}: 다양성 점수 불일치 (${r.diversityScore} vs ${c.expected.D})`,
  );
  console.log(
    `PASS ${c.name}: [${r.persona}] 신뢰 ${r.trustScore.toFixed(1)} · 다양성 ${r.diversityScore.toFixed(1)}`,
  );
}

// ── 2. 경계 동작: 임계 정확히 같으면 상위(T) — 파이썬 `>=`와 동일 ──
{
  const r = diagnose(
    spec,
    { cred_fair: 5, cred_professional: 5, cred_accurate: 5 },
    2,
  );
  assert.equal(
    r.diversityScore >= spec.diversity.threshold_1_100,
    true,
    "경계(=임계) mediaCount=2는 상위로 판정되어야 함",
  );
  console.log(
    `PASS 경계 검증: mediaCount=2 → 다양성 ${r.diversityScore} (임계 ${spec.diversity.threshold_1_100}) → 상위`,
  );
}

// ── 3. v1.1 스키마 존재 검사 ──
assert.ok(spec.baseline && spec.boundary_band && spec.profiles, "v1.1 키 누락");
for (const lab of Object.values(spec.quadrant_labels)) {
  assert.ok(
    Array.isArray(spec.profiles[lab]?.facts) &&
      spec.profiles[lab].facts.length > 0,
    `profiles[${lab}] facts 비어 있음`,
  );
}
console.log("PASS v1.1 스키마: baseline·boundary_band·profiles(4유형 facts)");

// ── 4. 분위수 테이블 무결성 ──
{
  const tp = spec.baseline.trust_percentiles;
  const dc = spec.baseline.diversity_cdf;
  assert.ok(tp.scores.length <= 125 && tp.scores.length > 0);
  for (let i = 1; i < tp.scores.length; i++)
    assert.ok(tp.scores[i] > tp.scores[i - 1], "scores 정렬 위반");
  for (const seq of [
    tp.pct_below,
    tp.pct_at_or_below,
    dc.pct_below,
    dc.pct_at_or_below,
  ]) {
    for (let i = 0; i < seq.length; i++) {
      assert.ok(seq[i] >= 0 && seq[i] <= 100, "pct 범위 위반");
      if (i > 0) assert.ok(seq[i] >= seq[i - 1] - 1e-12, "pct 단조 위반");
    }
  }
  assert.ok(Math.abs(dc.pct_at_or_below[8] - 100) < 1e-9, "CDF 끝값 ≠ 100");
  console.log(
    `PASS 분위수 테이블 무결성: 신뢰 ${tp.scores.length}개 · 다양성 CDF 9값`,
  );
}

// ── 5. 분위수 lookup 대조 — notebooks/09 §7 출력의 파이썬 기준값 ──
// (노트북 재실행 후 §7 print 값으로 채워짐; 비어 있으면 실패해 동기화 누락을 잡는다)
const PCT_REF = [
  {
    name: "TV만 보는 고신뢰 응답자",
    cred: { cred_fair: 4, cred_professional: 4, cred_accurate: 4 },
    mediaCount: 1,
    trustPctBelow: 82.12778583674007,
    diversityPctBelow: 3.8639061057628905,
  },
  {
    name: "다채널 저신뢰 탐색가",
    cred: { cred_fair: 2, cred_professional: 3, cred_accurate: 2 },
    mediaCount: 6,
    trustPctBelow: 17.482087124708777,
    diversityPctBelow: 99.16699635148798,
  },
  {
    name: "평균적 이용자",
    cred: { cred_fair: 3, cred_professional: 3, cred_accurate: 3 },
    mediaCount: 3,
    trustPctBelow: 33.90918282122291,
    diversityPctBelow: 69.27227570442656,
  },
];
assert.equal(
  PCT_REF.length,
  3,
  "PCT_REF 미기입 — notebooks/09 §7 출력값으로 채워야 함",
);
for (const c of PCT_REF) {
  const r = diagnose(spec, c.cred, c.mediaCount);
  const tPct = lookupTrustPercentile(spec, r.trustScore);
  const dPct = lookupDiversityPercentile(spec, c.mediaCount);
  assert.ok(
    Math.abs(tPct - c.trustPctBelow) < 1e-9,
    `${c.name}: 신뢰 분위수 불일치 (${tPct} vs ${c.trustPctBelow})`,
  );
  assert.ok(
    Math.abs(dPct - c.diversityPctBelow) < 1e-9,
    `${c.name}: 다양성 분위수 불일치 (${dPct} vs ${c.diversityPctBelow})`,
  );
  console.log(
    `PASS 분위수 ${c.name}: 신뢰 pct_below ${tPct.toFixed(2)} · 다양성 pct_below ${dPct.toFixed(2)}`,
  );
}

// ── 6. 경계 밴드 판정 ──
{
  // mediaCount=2 → 다양성 = 임계와 정확히 일치 → near.diversity true
  const r2 = diagnose(
    spec,
    { cred_fair: 5, cred_professional: 5, cred_accurate: 5 },
    2,
  );
  const n2 = isNearBoundary(spec, r2.trustScore, r2.diversityScore);
  assert.equal(n2.diversity, true, "mediaCount=2는 다양성 경계 밴드 내여야 함");
  // mediaCount=6 → 다양성 75.25, 임계 25.75에서 멀리 → false
  const r6 = diagnose(
    spec,
    { cred_fair: 1, cred_professional: 1, cred_accurate: 1 },
    6,
  );
  const n6 = isNearBoundary(spec, r6.trustScore, r6.diversityScore);
  assert.equal(n6.diversity, false, "mediaCount=6는 다양성 밴드 밖이어야 함");
  // 신뢰: (3,3,3) → 50.5, 임계 58.66과의 거리 8.16 < 밴드 반경이면 true — 스펙 값으로 판정만 확인
  const r3 = diagnose(
    spec,
    { cred_fair: 3, cred_professional: 3, cred_accurate: 3 },
    0,
  );
  const n3 = isNearBoundary(spec, r3.trustScore, r3.diversityScore);
  const dist = Math.abs(r3.trustScore - spec.trust.threshold_1_100);
  assert.equal(
    n3.trust,
    dist <= spec.boundary_band.trust_half_width_1_100,
    "신뢰 밴드 판정 불일치",
  );
  // 극단 입력(1,1,1)은 임계에서 멀어 false
  const r1 = diagnose(
    spec,
    { cred_fair: 1, cred_professional: 1, cred_accurate: 1 },
    0,
  );
  const n1 = isNearBoundary(spec, r1.trustScore, r1.diversityScore);
  assert.equal(n1.trust, false, "극단 저신뢰는 신뢰 밴드 밖이어야 함");
  console.log(
    `PASS 경계 밴드: 다양성 임계=true/원거리=false · 신뢰 (3,3,3)→${n3.trust} · 극단→false`,
  );
}

console.log("\n검증 전부 PASS — JS 판정·lookup ≡ notebooks/09 파이썬 기준");
