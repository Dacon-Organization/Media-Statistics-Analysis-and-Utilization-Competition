// 내 유형의 검증 프로파일 — v1.1 profiles.facts 소비(방향 문구만, 근거 배지 포함)
import EvidenceBadge from "@/components/EvidenceBadge";
import type { PersonaProfile } from "@/lib/types";

interface Props {
  persona: string;
  profile: PersonaProfile;
}

export default function ProfileCard({ persona, profile }: Props) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <p className="text-xs font-bold text-slate-500">
        &lsquo;{persona}&rsquo; 유형은 어떤 사람들인가요?
      </p>
      <ul className="mt-3 space-y-3">
        {profile.facts.map((f) => (
          <li key={f.text} className="text-sm leading-relaxed">
            <span className="mr-1.5 text-slate-400">·</span>
            {f.text}
            <span className="ml-1.5 inline-block align-middle">
              <EvidenceBadge evidence={f.evidence} />
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
