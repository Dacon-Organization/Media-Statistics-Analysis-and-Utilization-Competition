"use client";

// 진단 위저드 상태 훅 — 상태를 이 훅 하나에 완결하고 컴포넌트는 props만 소비한다.
// 향후 풀 멀티페이지(/landing·/check·/result) 분리 시:
//   ① 이 훅을 Context Provider로 승격하거나
//   ② 결과를 URL 쿼리로 직렬화(m=8비트 비트마스크, c=문항 3자리)해 /result가 복원
// 하면 된다 — 컴포넌트 계층은 그대로 재사용 가능.

import { useCallback, useMemo, useState } from "react";
import {
  diagnose,
  isNearBoundary,
  lookupDiversityPercentile,
  lookupTrustPercentile,
} from "./diagnosis";
import type { CredKey, DiagnosisSpec, WizardResult } from "./types";

export type WizardStep = "intro" | "media" | "trust" | "result";

const STEP_ORDER: WizardStep[] = ["intro", "media", "trust", "result"];

export function useDiagnosisWizard(spec: DiagnosisSpec) {
  const [step, setStep] = useState<WizardStep>("intro");
  const [media, setMedia] = useState<Set<string>>(new Set());
  const [cred, setCred] = useState<Partial<Record<CredKey, number>>>({});
  const [result, setResult] = useState<WizardResult | null>(null);

  const credKeys = useMemo(
    () => Object.keys(spec.inputs.cred_items) as CredKey[],
    [spec],
  );
  const allCredAnswered = credKeys.every((k) => cred[k] !== undefined);

  const start = useCallback(() => setStep("media"), []);

  const toggleMedia = useCallback((key: string) => {
    setMedia((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  const setCredValue = useCallback((key: CredKey, v: number) => {
    setCred((prev) => ({ ...prev, [key]: v }));
  }, []);

  const back = useCallback(() => {
    setStep((s) => {
      const i = STEP_ORDER.indexOf(s);
      return i > 0 ? STEP_ORDER[i - 1] : s;
    });
  }, []);

  const goMedia = useCallback(() => setStep("media"), []);
  const goTrust = useCallback(() => setStep("trust"), []);

  const runDiagnosis = useCallback(() => {
    if (!allCredAnswered) return;
    const base = diagnose(spec, cred as Record<CredKey, number>, media.size);
    setResult({
      ...base,
      trustPctBelow: lookupTrustPercentile(spec, base.trustScore),
      diversityPctBelow: lookupDiversityPercentile(spec, media.size),
      nearBoundary: isNearBoundary(
        spec,
        base.trustScore,
        base.diversityScore,
      ),
      mediaCount: media.size,
    });
    setStep("result");
  }, [spec, cred, media, allCredAnswered]);

  const reset = useCallback(() => {
    setMedia(new Set());
    setCred({});
    setResult(null);
    setStep("intro");
  }, []);

  return {
    step,
    media,
    cred,
    result,
    allCredAnswered,
    actions: {
      start,
      toggleMedia,
      setCredValue,
      back,
      goMedia,
      goTrust,
      runDiagnosis,
      reset,
    },
  };
}
