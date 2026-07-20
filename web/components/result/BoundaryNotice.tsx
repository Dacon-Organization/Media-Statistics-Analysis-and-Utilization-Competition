// 임계 부근 판정 고지 — v1.1 boundary_band 소비
interface Props {
  near: { trust: boolean; diversity: boolean };
}

export default function BoundaryNotice({ near }: Props) {
  if (!near.trust && !near.diversity) return null;
  const axis = [near.trust && "신뢰", near.diversity && "다양성"]
    .filter(Boolean)
    .join("·");
  return (
    <div className="rounded-xl bg-amber-50 p-4 text-sm leading-relaxed text-amber-900 ring-1 ring-amber-200">
      <p className="font-bold">⚖️ 임계 부근 판정</p>
      <p className="mt-1 text-xs">
        {axis} 축의 위치가 판정 기준선(중앙값) 부근입니다 — 문항 응답이나 이용
        매체 1개 차이로 유형이 바뀔 수 있는 구간이에요. 유형 이름보다는 두 축의
        방향을 참고해 주세요.
      </p>
    </div>
  );
}
