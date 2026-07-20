// 스텝 컨테이너 — key={step} 리마운트로 전환 애니메이션 재생(prefers-reduced-motion 존중)
import type { ReactNode } from "react";
import type { WizardStep } from "@/lib/useDiagnosisWizard";

interface Props {
  step: WizardStep;
  children: ReactNode;
}

export default function WizardShell({ step, children }: Props) {
  return (
    <div key={step} className="animate-step-in">
      {children}
    </div>
  );
}
