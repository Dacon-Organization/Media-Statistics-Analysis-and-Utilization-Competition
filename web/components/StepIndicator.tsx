// 진행 표시 — 1 매체 · 2 신뢰 · 3 결과
import type { WizardStep } from "@/lib/useDiagnosisWizard";

const STEPS: Array<{ id: WizardStep; label: string }> = [
  { id: "media", label: "매체 이용" },
  { id: "trust", label: "신뢰 인식" },
  { id: "result", label: "결과" },
];

export default function StepIndicator({ step }: { step: WizardStep }) {
  const current = STEPS.findIndex((s) => s.id === step);
  return (
    <ol className="mb-6 flex items-center justify-center gap-1">
      {STEPS.map((s, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <li key={s.id} className="flex items-center gap-1">
            {i > 0 && (
              <span
                className={`h-px w-6 sm:w-10 ${done || active ? "bg-sky-500" : "bg-slate-200"}`}
              />
            )}
            <span
              aria-current={active ? "step" : undefined}
              className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold ${
                active
                  ? "bg-sky-600 text-white"
                  : done
                    ? "bg-sky-100 text-sky-700"
                    : "bg-slate-100 text-slate-400"
              }`}
            >
              <span>{done ? "✓" : i + 1}</span>
              <span className="hidden sm:inline">{s.label}</span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
