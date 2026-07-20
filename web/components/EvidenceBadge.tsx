// 검증 근거 배지 — 문구가 어느 노트북 검증 셀에 얹혔는지 표시
export default function EvidenceBadge({ evidence }: { evidence: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700 ring-1 ring-emerald-200">
      <svg viewBox="0 0 12 12" className="h-2.5 w-2.5" fill="currentColor" aria-hidden>
        <path d="M4.8 8.4 2.4 6l-.85.85L4.8 10.1l6-6-.85-.85z" />
      </svg>
      {evidence} 검증
    </span>
  );
}
