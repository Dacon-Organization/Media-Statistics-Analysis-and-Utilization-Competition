// 4사분면 판정 평면 — 사용자 위치·임계선·경계 밴드(임계 부근 반투명 스트립)를 SVG로 표시
import type { DiagnosisSpec } from "@/lib/types";

const QUADRANT_COLORS: Record<string, string> = {
  "건강한 소비자": "#2da44e",
  "비판적 탐색형": "#0969da",
  신뢰편향형: "#bf8700",
  이중취약형: "#cf222e",
};

interface Props {
  spec: DiagnosisSpec;
  trustScore: number;
  diversityScore: number;
  persona: string;
  nearBoundary: { trust: boolean; diversity: boolean };
}

export default function QuadrantChart({
  spec,
  trustScore,
  diversityScore,
  persona,
  nearBoundary,
}: Props) {
  const W = 360;
  const H = 300;
  const PAD = { l: 36, r: 12, t: 12, b: 32 };
  const x = (v: number) => PAD.l + ((v - 1) / 99) * (W - PAD.l - PAD.r);
  const y = (v: number) => H - PAD.b - ((v - 1) / 99) * (H - PAD.t - PAD.b);

  const tx = x(spec.diversity.threshold_1_100);
  const ty = y(spec.trust.threshold_1_100);
  const px = x(diversityScore);
  const py = y(trustScore);
  const color = QUADRANT_COLORS[persona] ?? "#334155";

  // 경계 밴드 폭(픽셀)
  const bandX =
    (spec.boundary_band.diversity_half_width_1_100 / 99) *
    (W - PAD.l - PAD.r);
  const bandY =
    (spec.boundary_band.trust_half_width_1_100 / 99) * (H - PAD.t - PAD.b);

  // 사분면 tint 사각형: [x0, x1, y0, y1, label]
  const tints: Array<[number, number, number, number, string]> = [
    [tx, W - PAD.r, PAD.t, ty, spec.quadrant_labels.TT],
    [PAD.l, tx, PAD.t, ty, spec.quadrant_labels.TF],
    [tx, W - PAD.r, ty, H - PAD.b, spec.quadrant_labels.FT],
    [PAD.l, tx, ty, H - PAD.b, spec.quadrant_labels.FF],
  ];

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full max-w-sm"
      role="img"
      aria-label={`판정 평면: 다양성 ${diversityScore.toFixed(1)}, 신뢰 ${trustScore.toFixed(1)} → ${persona}`}
    >
      {tints.map(([x0, x1, y0, y1, lab]) => (
        <g key={lab}>
          <rect
            x={x0}
            y={y0}
            width={x1 - x0}
            height={y1 - y0}
            fill={QUADRANT_COLORS[lab]}
            opacity={lab === persona ? 0.13 : 0.045}
          />
          <text
            x={(x0 + x1) / 2}
            y={(y0 + y1) / 2}
            textAnchor="middle"
            fontSize="10.5"
            fill={QUADRANT_COLORS[lab]}
            fontWeight={lab === persona ? 700 : 500}
            opacity={lab === persona ? 1 : 0.6}
          >
            {lab}
          </text>
        </g>
      ))}

      {/* 경계 밴드 스트립(±half_width) */}
      <rect
        x={tx - bandX}
        y={PAD.t}
        width={bandX * 2}
        height={H - PAD.t - PAD.b}
        fill="#64748b"
        opacity={0.06}
      />
      <rect
        x={PAD.l}
        y={ty - bandY}
        width={W - PAD.l - PAD.r}
        height={bandY * 2}
        fill="#64748b"
        opacity={0.06}
      />

      {/* 임계선(pooled 중앙값) */}
      <line x1={tx} y1={PAD.t} x2={tx} y2={H - PAD.b} stroke="#94a3b8" strokeDasharray="4 3" />
      <line x1={PAD.l} y1={ty} x2={W - PAD.r} y2={ty} stroke="#94a3b8" strokeDasharray="4 3" />
      <rect
        x={PAD.l}
        y={PAD.t}
        width={W - PAD.l - PAD.r}
        height={H - PAD.t - PAD.b}
        fill="none"
        stroke="#cbd5e1"
      />

      {/* 사용자 위치 — 경계 밴드 해당 시 펄스 링 */}
      {(nearBoundary.trust || nearBoundary.diversity) && (
        <circle className="pulse-ring" cx={px} cy={py} r={7} fill="none" stroke={color} strokeWidth={2} />
      )}
      <circle cx={px} cy={py} r={7} fill={color} stroke="#fff" strokeWidth={2.5} />

      <text x={(PAD.l + W - PAD.r) / 2} y={H - 8} textAnchor="middle" fontSize="10" fill="#475569">
        다양성 (이용 매체 폭) →
      </text>
      <text
        x={13}
        y={(PAD.t + H - PAD.b) / 2}
        textAnchor="middle"
        fontSize="10"
        fill="#475569"
        transform={`rotate(-90 13 ${(PAD.t + H - PAD.b) / 2})`}
      >
        신뢰 인식 →
      </text>
    </svg>
  );
}

export { QUADRANT_COLORS };
