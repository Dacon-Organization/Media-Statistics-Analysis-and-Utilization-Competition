// Step 2 — 언론 신뢰 인식(cred3, 리커트 5점)
import type { CredKey, DiagnosisSpec } from "@/lib/types";
import { CRED_KEYS } from "@/lib/diagnosis";

const LIKERT_LABELS = ["전혀 아니다", "아니다", "보통", "그렇다", "매우 그렇다"];

interface Props {
  spec: DiagnosisSpec;
  cred: Partial<Record<CredKey, number>>;
  allAnswered: boolean;
  onSet: (key: CredKey, v: number) => void;
  onSubmit: () => void;
  onBack: () => void;
}

export default function StepTrust({
  spec,
  cred,
  allAnswered,
  onSet,
  onSubmit,
  onBack,
}: Props) {
  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-6">
      <h2 className="text-lg font-bold">언론에 대한 생각을 알려주세요</h2>
      <p className="mt-1 text-xs text-slate-500">
        세 문항의 응답이 &lsquo;신뢰&rsquo; 축이 됩니다 (1~5점)
      </p>
      <div className="mt-4 space-y-5">
        {CRED_KEYS.map((key) => (
          <div key={key}>
            <p className="mb-2 text-sm font-medium">
              {spec.inputs.cred_items[key].label}
            </p>
            <div className="grid grid-cols-5 gap-1.5">
              {LIKERT_LABELS.map((label, i) => {
                const v = i + 1;
                const on = cred[key] === v;
                return (
                  <button
                    key={v}
                    type="button"
                    onClick={() => onSet(key, v)}
                    aria-pressed={on}
                    className={`rounded-lg border px-1 py-2 text-center transition ${
                      on
                        ? "border-sky-600 bg-sky-600 text-white"
                        : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
                    }`}
                  >
                    <span className="block text-sm font-bold">{v}</span>
                    <span className="block text-[10px] leading-tight">
                      {label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 flex items-center justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 hover:bg-slate-100"
        >
          ← 이전
        </button>
        <button
          type="button"
          onClick={onSubmit}
          disabled={!allAnswered}
          className="flex-1 rounded-xl bg-sky-600 py-3 text-sm font-bold text-white transition enabled:hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {allAnswered ? "진단 결과 보기" : "3개 문항에 모두 응답해 주세요"}
        </button>
      </div>
    </section>
  );
}
