// "다음 버전" 비전 카드 3종 — 원고 7.1절(B2G)·web/README 비전 항목의 정적 제시
const VISIONS = [
  {
    icon: "👤",
    title: "계정·기록 저장",
    desc: "진단 결과를 저장하고 습관 변화에 따라 다시 진단 — 나의 처방 이행을 추적",
  },
  {
    icon: "📈",
    title: "연도별 위치 추적",
    desc: "해마다 갱신되는 기준선 위에서 내 위치의 이동을 확인 — 같은 잣대의 종단 추적",
  },
  {
    icon: "🏛️",
    title: "B2G 정책 대시보드",
    desc: "유형 구성의 변화를 지역·연령대별로 모니터링 — 다양성 노출 개입의 타깃 추적(보고서 7.1절)",
  },
];

export default function VisionCards() {
  return (
    <div>
      <p className="mb-2 text-xs font-bold text-slate-500">
        🚀 다음 버전에서 만나요
      </p>
      <div className="grid gap-2 sm:grid-cols-3">
        {VISIONS.map((v) => (
          <div
            key={v.title}
            className="rounded-xl border border-dashed border-slate-300 bg-slate-50/60 p-3.5"
          >
            <p className="text-sm font-bold text-slate-700">
              {v.icon} {v.title}
              <span className="ml-1.5 rounded bg-slate-200 px-1.5 py-0.5 text-[9px] font-semibold text-slate-500 align-middle">
                예정
              </span>
            </p>
            <p className="mt-1 text-[11px] leading-relaxed text-slate-500">
              {v.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
