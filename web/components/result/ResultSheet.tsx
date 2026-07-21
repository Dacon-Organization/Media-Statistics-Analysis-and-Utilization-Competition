// 검진 결과지 — F9 스크린샷 단위(#result-sheet)
import type { DiagnosisSpec, WizardResult } from "@/lib/types";
import QuadrantChart, { QUADRANT_COLORS } from "@/components/QuadrantChart";
import PersonaCard from "./PersonaCard";
import RelativePosition from "./RelativePosition";
import ProfileCard from "./ProfileCard";
import PrescriptionCard from "./PrescriptionCard";
import BoundaryNotice from "./BoundaryNotice";
import Disclaimer from "./Disclaimer";
import VisionCards from "./VisionCards";

interface Props {
  spec: DiagnosisSpec;
  result: WizardResult;
  onReset: () => void;
}

export default function ResultSheet({ spec, result, onReset }: Props) {
  const color = QUADRANT_COLORS[result.persona] ?? "#334155";
  const profile = spec.profiles[result.persona];
  return (
    <section id="result-sheet" aria-live="polite" className="space-y-4">
      <PersonaCard
        persona={result.persona}
        diagnosis={result.prescription.diagnosis}
      />

      <BoundaryNotice near={result.nearBoundary} />

      <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
        <p className="mb-2 text-xs font-bold text-slate-500">
          신뢰 × 다양성 판정 평면
        </p>
        <div className="flex justify-center">
          <QuadrantChart
            spec={spec}
            trustScore={result.trustScore}
            diversityScore={result.diversityScore}
            persona={result.persona}
            nearBoundary={result.nearBoundary}
          />
        </div>
      </div>

      <RelativePosition spec={spec} result={result} color={color} />

      {profile && (
        <ProfileCard persona={result.persona} profile={profile} />
      )}

      <PrescriptionCard
        rx={result.prescription.rx}
        evidence={result.prescription.evidence}
      />

      <Disclaimer spec={spec} />

      <VisionCards />

      <button
        type="button"
        onClick={onReset}
        className="w-full rounded-2xl border border-slate-300 bg-white py-3 text-sm font-bold text-slate-600 transition hover:bg-slate-50"
      >
        다시 진단하기
      </button>
    </section>
  );
}
