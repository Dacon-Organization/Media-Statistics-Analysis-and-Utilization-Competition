// Step 1 — 매체 이용 폭(8종 선택)
import type { DiagnosisSpec } from "@/lib/types";

interface Props {
  spec: DiagnosisSpec;
  media: Set<string>;
  onToggle: (key: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function StepMedia({
  spec,
  media,
  onToggle,
  onNext,
  onBack,
}: Props) {
  const keys = Object.keys(spec.inputs.media_items);
  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-6">
      <h2 className="text-lg font-bold">
        지난 1주일, 뉴스를 접한 매체를
        <br className="sm:hidden" /> 모두 선택하세요
      </h2>
      <p className="mt-1 text-xs text-slate-500">
        이용 매체의 폭이 &lsquo;다양성&rsquo; 축이 됩니다 (0~8개 · 없으면 그대로
        다음)
      </p>
      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {keys.map((key) => {
          const on = media.has(key);
          return (
            <button
              key={key}
              type="button"
              onClick={() => onToggle(key)}
              aria-pressed={on}
              className={`rounded-xl border px-2 py-3 text-sm font-medium transition ${
                on
                  ? "border-sky-600 bg-sky-50 text-sky-800"
                  : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
              }`}
            >
              {spec.inputs.media_items[key]}
            </button>
          );
        })}
      </div>
      <div className="mt-5 flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 hover:bg-slate-100"
        >
          ← 처음으로
        </button>
        <p className="text-xs font-medium text-slate-500">선택 {media.size} / 8</p>
        <button
          type="button"
          onClick={onNext}
          className="rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-bold text-white transition hover:bg-sky-700"
        >
          다음 →
        </button>
      </div>
    </section>
  );
}
