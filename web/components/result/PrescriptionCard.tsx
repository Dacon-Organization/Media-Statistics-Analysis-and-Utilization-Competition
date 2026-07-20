// 맞춤 처방 — spec prescriptions 소비 + 근거 배지
import EvidenceBadge from "@/components/EvidenceBadge";

interface Props {
  rx: string;
  evidence: string;
}

export default function PrescriptionCard({ rx, evidence }: Props) {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-sky-50 to-slate-50 p-5 ring-1 ring-sky-100">
      <p className="text-xs font-bold text-sky-700">💊 맞춤 처방</p>
      <p className="mt-2 text-sm font-medium leading-relaxed text-slate-800">
        {rx}
      </p>
      <div className="mt-2">
        <EvidenceBadge evidence={`notebooks/${evidence}`} />
      </div>
    </div>
  );
}
