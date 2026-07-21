// 방법론 공개 페이지 — 판정 규칙 전문·채택 근거·자격 규율 (정적 서버 컴포넌트)
import type { Metadata } from "next";
import Link from "next/link";
import specJson from "@/diagnosis-spec.json";
import type { DiagnosisSpec } from "@/lib/types";
import { baselineLabel } from "@/lib/diagnosis";

const spec = specJson as unknown as DiagnosisSpec;

export const metadata: Metadata = {
  title: "방법론 — 뉴스 건강검진",
  description:
    "뉴스 건강검진의 판정 규칙 전문, 규칙 기반 4사분면 채택 근거, 기준선과 자격 규율을 공개합니다.",
};

function Section({
  no,
  title,
  children,
}: {
  no: number;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-6">
      <h2 className="text-base font-bold">
        <span className="mr-2 text-sky-600">{no}.</span>
        {title}
      </h2>
      <div className="mt-3 space-y-3 text-sm leading-relaxed text-slate-700">
        {children}
      </div>
    </section>
  );
}

export default function MethodPage() {
  const t = spec.trust;
  const d = spec.diversity;
  const bb = spec.boundary_band;
  return (
    <main className="mx-auto max-w-xl px-4 py-8 sm:py-12">
      <header className="mb-6">
        <Link href="/" className="text-xs font-medium text-sky-700 underline">
          ← 진단으로 돌아가기
        </Link>
        <h1 className="mt-3 text-2xl font-bold">
          방법론 — 판정 기준의 전부를 공개합니다
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          이 데모의 판정은 공개 사양(diagnosis-spec {spec.version})의 상수만으로
          이뤄지며, 분석 파이프라인과의 판정 일치가{" "}
          {spec.baseline.n.toLocaleString()}행 전수 대조로 검증돼 있습니다.
        </p>
      </header>

      <div className="space-y-4">
        <Section no={1} title="판정 규칙 전문">
          <p>
            입력은 11문항 — 언론 인식 3문항(공정·전문·정확, 1~5점)과 8개 매체
            이용 여부 — 뿐입니다. 점수화는:
          </p>
          <ul className="list-disc space-y-1 pl-5 text-[13px]">
            <li>
              <b>신뢰</b>: 각 문항을 기준선의 문항별 평균·표준편차로 표준화(z) →
              3문항 평균 → 1~100 선형 환산
            </li>
            <li>
              <b>다양성</b>: 이용 매체 수(0~8)를 1~100 선형 환산
            </li>
            <li>
              <b>판정</b>: 각 축을 기준선의 중앙값 임계(신뢰{" "}
              {t.threshold_1_100.toFixed(2)} · 다양성{" "}
              {d.threshold_1_100.toFixed(2)})와 비교해 4사분면 유형 결정
            </li>
          </ul>
          <p className="text-[13px] text-slate-500">
            데모(JavaScript)의 판정이 분석 파이프라인(Python)과 동일함은
            가상 사용자·경계 케이스 자동 검증(<code>npm run verify</code>)과
            기준선 전수 재판정(notebooks/09 §4)으로 입증돼 있습니다.
          </p>
        </Section>

        <Section no={2} title="왜 '중앙값 4사분면' 규칙인가">
          <p>
            비지도 군집(K-means)은 이 데이터에서 4사분면 구조를 안정적으로
            재발견하지 못했습니다(pooled ARI 0.244, 연도별 0.128~0.406 —
            통용 기준 0.65에 크게 미달). 다양성 축이 0~8의 이산 값에 치우쳐
            있어, 군집은 분산이 큰 신뢰 축만 가르는 경향이 있습니다.
          </p>
          <p>
            따라서 이 진단은 &lsquo;데이터가 자연히 4개 집단으로 나뉜다&rsquo;는
            주장이 아니라, <b>투명하고 재현 가능한 규칙 기반 구획</b>(두 축 ×
            중앙값 임계)을 채택합니다 — 같은 입력이면 언제나 같은 판정이 나오고,
            기준이 전부 공개됩니다(notebooks/04 Decision Box).
          </p>
        </Section>

        <Section no={3} title="기준선과 '상대 위치'의 의미">
          <p>
            기준선은 한국언론진흥재단 {baselineLabel(spec)} 통합{" "}
            {spec.baseline.n.toLocaleString()}명입니다(연도 균등 가중). 결과
            화면의 위치 표현은 이 기준선 대비 <b>상대 위치(방향)</b>이며, 점수의
            절대값은 지수 설계(매체 목록·환산 방식)에 의존하므로 개인에 대한
            절대 평가로 읽지 않습니다.
          </p>
        </Section>

        <Section no={4} title="임계 민감도와 경계 밴드">
          <p>
            유형 구성은 임계 선택에 민감합니다 — 임계를 중앙값에서 평균으로
            바꾸면 유형별 구성이 크게 달라집니다(notebooks/04 §6, 방향).
            그래서 판정이 임계 부근(신뢰 ±{bb.trust_half_width_1_100.toFixed(1)}
            점 · 다양성 ±{bb.diversity_half_width_1_100.toFixed(1)}점 — 문항
            또는 매체 1개 차이가 만드는 최대 변화)이면 &lsquo;임계 부근
            판정&rsquo;임을 함께 고지합니다. 이 밴드가 판정이 뒤집힐 수 있는
            모든 입력을 덮는다는 것은 1,125개 입력 전수 검사로
            확인했습니다(notebooks/09 §9).
          </p>
        </Section>

        <Section no={5} title="자격 규율 — 말하지 않는 것">
          <ul className="list-disc space-y-1 pl-5 text-[13px]">
            <li>다양성·종합지수의 절대값 비교(지수 설계 의존 — 방향만)</li>
            <li>유형 구성비 절대 %의 헤드라인화(임계 선택에 민감)</li>
            <li>인과 주장(이 설계는 표적 식별이지 원인 규명이 아님)</li>
            <li>&lsquo;데이터가 자연히 4개 군집&rsquo;이라는 서술</li>
            <li>출처가 확인되지 않은 외부 수치의 인용</li>
          </ul>
        </Section>

        <Section no={6} title="사양 공개">
          <p>
            판정에 쓰이는 모든 상수(문항별 표준화 파라미터, 환산 범위, 임계,
            분위수 테이블, 경계 밴드, 유형 프로파일 문구)는{" "}
            <code>diagnosis-spec.json</code>({spec.version})에 담겨 있고, 이
            사양은 분석 노트북(notebooks/09)이 직접 export하며 웹은 이를
            소비만 합니다. 유형 프로파일 문구는 검증 assert를 통과한 방향
            서술만 포함하도록 기계적으로 봉인돼 있습니다.
          </p>
        </Section>
      </div>

      <footer className="mt-10 text-center text-[11px] text-slate-400">
        KPF 언론 통계 분석·활용 경진대회 데모 · 한국언론진흥재단{" "}
        {baselineLabel(spec)} 기반
      </footer>
    </main>
  );
}
