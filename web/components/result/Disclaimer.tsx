// 자격규율 고지 — 절대 평가 아님·상대 위치/방향, spec 버전 병기
import Link from "next/link";

export default function Disclaimer({ version }: { version: string }) {
  return (
    <p className="text-[11px] leading-relaxed text-slate-400">
      * 점수와 위치는 한국언론진흥재단 「미디어 다양성 조사」 2016–2025 통합
      기준선 대비 <b>상대 위치(상·하위 절반의 방향)</b>이며, 개인에 대한 절대적
      평가가 아닙니다. 유형은 통계적 구획이며 인과를 뜻하지 않습니다. 판정
      기준은 공개 사양(diagnosis-spec {version})을 따르고, 산출 과정은{" "}
      <Link href="/method" className="underline">
        방법론 페이지
      </Link>
      에 공개돼 있습니다.
    </p>
  );
}
