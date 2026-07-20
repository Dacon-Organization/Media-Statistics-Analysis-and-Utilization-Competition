import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "뉴스 건강검진 — 나의 뉴스 소비 유형 진단",
  description:
    "매체 이용 폭과 언론 신뢰 인식 11문항으로 나의 뉴스 소비 유형(4사분면 페르소나)을 진단하고 맞춤 처방을 받아보세요. KPF 미디어 다양성 조사 2016–2025 통합 기준선 기반.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
