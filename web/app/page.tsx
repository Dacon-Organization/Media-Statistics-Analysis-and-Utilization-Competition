"use client";

// 뉴스 건강검진 — 스텝 위저드 조립 전용.
// 판정 로직·상수는 web/diagnosis-spec.json(SSOT, notebooks/09 export v1.1)을 소비만 한다.

import specJson from "@/diagnosis-spec.json";
import type { DiagnosisSpec } from "@/lib/types";
import { useDiagnosisWizard } from "@/lib/useDiagnosisWizard";
import Hero from "@/components/Hero";
import StepIndicator from "@/components/StepIndicator";
import WizardShell from "@/components/WizardShell";
import StepMedia from "@/components/StepMedia";
import StepTrust from "@/components/StepTrust";
import ResultSheet from "@/components/result/ResultSheet";

const spec = specJson as unknown as DiagnosisSpec;

export default function Home() {
  const { step, media, cred, result, allCredAnswered, actions } =
    useDiagnosisWizard(spec);

  return (
    <main className="mx-auto max-w-xl px-4 py-8 sm:py-12">
      {step !== "intro" && <StepIndicator step={step} />}

      <WizardShell step={step}>
        {step === "intro" && (
          <Hero baselineN={spec.baseline.n} onStart={actions.start} />
        )}
        {step === "media" && (
          <StepMedia
            spec={spec}
            media={media}
            onToggle={actions.toggleMedia}
            onNext={actions.goTrust}
            onBack={actions.reset}
          />
        )}
        {step === "trust" && (
          <StepTrust
            spec={spec}
            cred={cred}
            allAnswered={allCredAnswered}
            onSet={actions.setCredValue}
            onSubmit={actions.runDiagnosis}
            onBack={actions.goMedia}
          />
        )}
        {step === "result" && result && (
          <ResultSheet spec={spec} result={result} onReset={actions.reset} />
        )}
      </WizardShell>

      <footer className="mt-10 text-center text-[11px] text-slate-400">
        KPF 언론 통계 분석·활용 경진대회 데모 · 한국언론진흥재단 「미디어
        다양성 조사」 기반
      </footer>
    </main>
  );
}
