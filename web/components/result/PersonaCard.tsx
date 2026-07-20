// 유형 카드 — 진단 결과 헤드라인
import { QUADRANT_COLORS } from "@/components/QuadrantChart";

interface Props {
  persona: string;
  diagnosis: string;
}

const PERSONA_EMOJI: Record<string, string> = {
  "건강한 소비자": "🟢",
  "비판적 탐색형": "🔵",
  신뢰편향형: "🟡",
  이중취약형: "🔴",
};

export default function PersonaCard({ persona, diagnosis }: Props) {
  const color = QUADRANT_COLORS[persona] ?? "#334155";
  return (
    <div
      className="rounded-2xl p-6 text-center text-white shadow-md"
      style={{ backgroundColor: color }}
    >
      <p className="text-xs font-semibold tracking-[0.2em] opacity-80">
        나의 뉴스 소비 유형
      </p>
      <p className="mt-2 text-3xl font-bold">
        {PERSONA_EMOJI[persona]} {persona}
      </p>
      <p className="mt-2 text-sm opacity-90">{diagnosis}</p>
    </div>
  );
}
