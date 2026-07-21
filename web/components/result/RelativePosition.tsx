// 축별 상대 위치 — 기준선 대비 "N%보다 높은 위치(방향)" (v1.1 baseline lookup 소비)
import type { DiagnosisSpec, WizardResult } from "@/lib/types";
import { baselineLabel } from "@/lib/diagnosis";

interface Props {
  spec: DiagnosisSpec;
  result: WizardResult;
  color: string;
}

export default function RelativePosition({ spec, result, color }: Props) {
  const axes = [
    {
      name: "신뢰 인식",
      score: result.trustScore,
      pct: result.trustPctBelow,
      side: result.trustScore >= spec.trust.threshold_1_100 ? "상위" : "하위",
    },
    {
      name: "다양성(매체 폭)",
      score: result.diversityScore,
      pct: result.diversityPctBelow,
      side:
        result.diversityScore >= spec.diversity.threshold_1_100
          ? "상위"
          : "하위",
    },
  ];
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <p className="text-xs font-bold text-slate-500">
        기준선 대비 상대 위치{" "}
        <span className="font-normal">
          ({baselineLabel(spec)} 통합 {spec.baseline.n.toLocaleString()}명)
        </span>
      </p>
      <div className="mt-3 space-y-4">
        {axes.map(({ name, score, pct, side }) => (
          <div key={name}>
            <div className="mb-1 flex items-baseline justify-between">
              <span className="text-sm font-medium">{name}</span>
              <span className="text-xs text-slate-500">
                {side} 절반 · 기준선의 약 {pct.toFixed(0)}%보다 높은 위치(방향)
              </span>
            </div>
            <div className="relative h-2.5 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full"
                style={{ width: `${score}%`, backgroundColor: color }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
