// 인트로 히어로 — 검진 시작 CTA + 방법론 링크
import Link from "next/link";

interface Props {
  baselineN: number;
  onStart: () => void;
}

export default function Hero({ baselineN, onStart }: Props) {
  return (
    <section className="text-center">
      <p className="mb-2 text-xs font-semibold tracking-[0.25em] text-sky-700">
        NEWS HEALTH CHECK
      </p>
      <h1 className="text-3xl font-bold leading-tight sm:text-4xl">
        내 뉴스 소비,
        <br />
        건강할까요?
      </h1>
      <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-slate-600">
        매체 이용 폭(다양성)과 언론 신뢰 인식 — 두 축으로 나의 뉴스 소비
        유형을 진단하고 맞춤 처방을 받아보세요.
      </p>

      <div className="mx-auto mt-6 grid max-w-md grid-cols-3 gap-2 text-center">
        {[
          { v: "11문항", k: "1분 자가진단" },
          { v: `${baselineN.toLocaleString()}명`, k: "통합 기준선" },
          { v: "2016–2025", k: "미디어 다양성 조사" },
        ].map(({ v, k }) => (
          <div
            key={k}
            className="rounded-xl bg-white px-2 py-3 shadow-sm ring-1 ring-slate-200"
          >
            <p className="text-sm font-bold text-slate-800">{v}</p>
            <p className="mt-0.5 text-[10px] text-slate-500">{k}</p>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={onStart}
        className="mt-8 w-full max-w-md rounded-2xl bg-sky-600 py-4 text-base font-bold text-white shadow-md shadow-sky-600/20 transition hover:bg-sky-700"
      >
        검진 시작하기
      </button>
      <p className="mt-3 text-xs text-slate-500">
        판정 기준이 궁금하다면{" "}
        <Link href="/method" className="font-medium text-sky-700 underline">
          방법론 공개 페이지
        </Link>
      </p>
    </section>
  );
}
