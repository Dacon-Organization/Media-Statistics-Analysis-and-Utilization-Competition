# -*- coding: utf-8 -*-
"""뉴스 소비 건강지수 — 변수 매핑·전처리 SSOT (Task 02 확정).

근거:
- EDA: notebooks/01-eda-2025.ipynb (신뢰·다양성 2코어, 검증·회피 보조)
- 방법론: docs/groundwork/03-research-index-methodology.md (Perplexity Deep Research)
- 설계: docs/design/preprocessing-design.md, data-spec.md §5

설계 원칙(경량): pandas·numpy·sklearn만. 무거운 의존성(factor_analyzer/pingouin) 미사용
  — 동등 통계를 자체 구현(Cronbach α)·sklearn(FactorAnalysis)으로 대체해 재현성 확보.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

# ── 경로 ──────────────────────────────────────────────────────────────
def find_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "data/raw/audience/2025").exists():
            return cand
    raise FileNotFoundError("data/raw/audience/2025 를 찾지 못했습니다")

# ── 특수코드 (코드북) ─────────────────────────────────────────────────
# 9997=기타, 9998=해당없음/이용안함, 9999=모름·무응답
SPECIAL = [9997, 9998, 9999]

# ── 신뢰 차원 ─────────────────────────────────────────────────────────
# 코어 = 뉴스/언론 신뢰 (Kohring & Matthes 2007 4요인 준용). 모두 5점·양성 키.
TRUST_CORE = (
    [f"Q85_{i}" for i in range(1, 6)]    # 언론 인식(공정/전문/정확/자유/영향)
    + [f"Q86_{i}" for i in range(1, 8)]  # 언론 역할 수행
    + ["Q87_1", "Q87_2"]                  # 전반/실제 신뢰
    + ["Q88_1", "Q88_2", "Q88_3"]         # 출처별 신뢰
    + [f"Q94_{i}" for i in range(1, 5)]  # 언론인 평가
    + ["Q95_5"]                           # 직업군 중 '언론인'만
)
# 통제/맥락 = 일반화 신뢰 (코어 제외 — 측정타당도 보호). Uslaner 2002.
TRUST_CONTEXT = [f"Q95_{i}" for i in (1, 2, 3, 4, 6, 7, 8, 9, 10)] + ["Q96"]
# 비판적 문제인식 = 별도 지표(신뢰 합산 금지). 냉소(역신뢰) vs 회의(건강 리터러시) 모호 → CFA 검증.
CRITICAL_PERCEPTION = [f"Q91_{i}" for i in range(1, 9)]  # 보도 문제점 심각도(높을수록 부정)

# ── 다양성 차원 ───────────────────────────────────────────────────────
# 주지표 = Richness(뉴스 매체유형 폭). 보조/진단 = 일수가중 Shannon/Pielou(균등도).
# 매체유형별 '뉴스 이용일수(평일)' — 모바일/PC 분리분은 합산(플랫폼 중복 방지).
NEWS_DAYS = {
    "종이신문": ["Q2A_1"], "뉴스잡지": ["Q9A_1"], "TV뉴스": ["Q14A_1"],
    "라디오뉴스": ["Q21A_1"], "인터넷뉴스": ["Q27A_1", "Q27A_2"], "포털뉴스": ["Q32A_1", "Q32A_2"],
    "메신저뉴스": ["Q40A_1"], "SNS뉴스": ["Q47A_1"], "동영상뉴스": ["Q54A_1"],
    "숏폼뉴스": ["Q62A_1"], "OTT뉴스": ["Q68A_1"], "AI뉴스": ["Q74A_1"],
}
# 매체 이용여부 게이트(이진) — 보조 breadth 점검용. 1=이용/2=비이용.
USE_GATE = ["Q1", "Q6", "Q8", "Q10", "Q13", "Q17", "Q20", "Q36", "Q39", "Q43",
            "Q46", "Q50", "Q53", "Q58", "Q61", "Q64", "Q67", "Q70", "Q73", "Q76", "Q78"]

# ── 보조 플래그·프록시 ────────────────────────────────────────────────
VERIFY_PROXY = ["Q93", "Q34_3", "Q56_2", "Q34_5", "Q56_4"]  # 검증습관(구조적 결측·약상관)
AVOID_VAR, AVOID_CODE = "Q84", 9998                          # 회피: Q84==9998 → 이진 플래그

# ── 인구·가중 ─────────────────────────────────────────────────────────
WEIGHT = "WT"
AGE = "DQ3"
AGE_BINS = [18, 29, 39, 49, 59, 69, 200]
AGE_LABELS = ["19-29", "30-39", "40-49", "50-59", "60-69", "70+"]
GENDER = "DQ2"                      # 1=남성, 2=여성
GENDER_LABELS = {1: "남성", 2: "여성"}
REGION = "SQ1"                      # 17개 시도 코드(표준순서)
# 17개 시도 → 6개 권역 (인구 프로파일 가독성)
REGION_BAND = {
    1: "수도권", 4: "수도권", 9: "수도권",          # 서울·인천·경기
    2: "영남", 3: "영남", 7: "영남", 15: "영남", 16: "영남",  # 부산·대구·울산·경북·경남
    5: "호남", 13: "호남", 14: "호남",              # 광주·전북·전남
    6: "충청", 8: "충청", 11: "충청", 12: "충청",   # 대전·세종·충북·충남
    10: "강원", 17: "제주",
}


def region_band(df: pd.DataFrame) -> pd.Series:
    """SQ1(17 시도) → 6 권역 라벨."""
    return df[REGION].map(REGION_BAND)


def gender_label(df: pd.DataFrame) -> pd.Series:
    return df[GENDER].map(GENDER_LABELS)


# ── 로딩 ──────────────────────────────────────────────────────────────
def load_2025(root: Path | None = None) -> pd.DataFrame:
    """2025 .sav를 parquet 캐시 경유로 로딩(없으면 생성). EUC-KR."""
    root = root or find_root()
    parquet = root / "data/interim/2025_audience.parquet"
    if parquet.exists():
        return pd.read_parquet(parquet)
    import pyreadstat
    sav = root / "data/raw/audience/2025/2025_언론수용자조사_데이터.sav"
    df, _ = pyreadstat.read_sav(str(sav), encoding="euc-kr")
    parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet)
    return df


# ── 정제 헬퍼 ─────────────────────────────────────────────────────────
def mask_special(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """특수코드(9997/9998/9999)를 NaN으로 치환한 float 프레임."""
    sub = df[cols].astype(float)
    return sub.mask(sub.isin(SPECIAL))


def cronbach_alpha(X: pd.DataFrame) -> float:
    """Cronbach's α (listwise). α = k/(k-1) · (1 - Σσ²ᵢ/σ²_total)."""
    X = X.dropna()
    k = X.shape[1]
    if k < 2 or len(X) < 2:
        return np.nan
    var_items = X.var(axis=0, ddof=1).sum()
    var_total = X.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - var_items / var_total)


def age_band(df: pd.DataFrame) -> pd.Series:
    return pd.cut(df[AGE], AGE_BINS, labels=AGE_LABELS)


def news_days_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """매체유형별 뉴스 이용일수(평일, 플랫폼 합산, 특수코드 제거·음수 0)."""
    out = pd.DataFrame(index=df.index)
    for k, cols in NEWS_DAYS.items():
        out[k] = mask_special(df, cols).sum(axis=1, min_count=1)
    return out.clip(lower=0)


def diversity_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """다양성 지표: Richness(S, 주지표) + 일수가중 Shannon H·Pielou J·ENS·HHI(보조)."""
    days = news_days_matrix(df)
    S = (days > 0).sum(axis=1)
    tot = days.sum(axis=1)
    p = days.div(tot.replace(0, np.nan), axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -(p * np.log(p)).sum(axis=1)
    J = (H / np.log(S.where(S > 1))).where(S > 1)   # Pielou 균등도(S>1)
    return pd.DataFrame({
        "richness": S,            # 폭(주지표)
        "shannon_H": H,           # 일수가중 다양성
        "pielou_J": J,            # 균등도(본 데이터 천장→변별력 낮음)
        "effective_N": np.exp(H), # 등가 매체 수
        "hhi": (p ** 2).sum(axis=1),  # 집중도(역다양성)
    })


def avoid_flag(df: pd.DataFrame) -> pd.Series:
    """회피 이진 플래그: 주 이용경로가 '이용 안함'(Q84==9998)."""
    return (df[AVOID_VAR] == AVOID_CODE).astype(int)


# ── 지수 산출 (Task 03) ───────────────────────────────────────────────
# 근거: docs/groundwork/04-research-aggregation-direction.md (Perplexity Deep Research)
#   · 집계 = 기하평균 NCHI=√(T×D) 주 + 산술 강건성 (JRC 저보완성, HDI 2010 전환)
#   · 방향성 = 단조 v1 (신뢰 역U·다양성 상한은 한계로 기록)
from sklearn.preprocessing import StandardScaler  # noqa: E402


def _scale_1_100(s: pd.Series) -> pd.Series:
    """관측 min~max를 [1,100]로 선형 환산(기하평균 0붕괴 방지)."""
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(50.0, index=s.index)
    return 1 + (s - lo) / (hi - lo) * 99


def trust_index(df: pd.DataFrame, weights: str = "equal") -> pd.Series:
    """신뢰지수 0~100. 코어 22문항 → z-표준화 → (동일가중 평균 | PCA 제1성분) → [1,100]."""
    core = mask_special(df, TRUST_CORE)
    z = pd.DataFrame(StandardScaler().fit_transform(core), index=core.index, columns=core.columns)
    if weights == "pca":
        from sklearn.decomposition import PCA
        valid = z.dropna()
        pc = PCA(n_components=1).fit(valid)
        raw = pd.Series(np.nan, index=z.index)
        raw.loc[valid.index] = pc.transform(valid)[:, 0]
        if pc.components_[0].sum() < 0:
            raw = -raw
    else:
        raw = z.mean(axis=1)
    return _scale_1_100(raw)


def diversity_index(df: pd.DataFrame) -> pd.Series:
    """다양성지수 0~100. Richness(뉴스 매체유형 폭) → [1,100]."""
    return _scale_1_100(diversity_metrics(df)["richness"].astype(float))


def nchi(trust: pd.Series, diversity: pd.Series, method: str = "geometric") -> pd.Series:
    """뉴스 소비 건강지수(NCHI). geometric=√(T·D) 주, arithmetic=(T+D)/2 강건성."""
    both = pd.DataFrame({"t": trust, "d": diversity}).dropna()
    if method == "arithmetic":
        out = both.mean(axis=1)
    else:
        out = np.sqrt(both["t"].clip(lower=1) * both["d"].clip(lower=1))
    return out.reindex(trust.index)


# 2축 페르소나 4사분면 (임계값 = 중앙값 기본)
PERSONA_LABELS = {
    (True, True): "건강한 소비자",     # 신뢰高·다양高
    (True, False): "신뢰편향형",       # 신뢰高·다양低
    (False, True): "비판적 탐색형",     # 신뢰低·다양高
    (False, False): "이중취약형",      # 신뢰低·다양低
}


def persona_quadrant(trust: pd.Series, diversity: pd.Series,
                     t_thresh: float | None = None, d_thresh: float | None = None) -> pd.Series:
    """신뢰×다양성 4사분면 페르소나 라벨. 임계값 미지정 시 각 축 중앙값."""
    t_thresh = trust.median() if t_thresh is None else t_thresh
    d_thresh = diversity.median() if d_thresh is None else d_thresh
    hi_t, hi_d = trust >= t_thresh, diversity >= d_thresh
    return pd.Series(
        [PERSONA_LABELS[(bool(t), bool(d))] if pd.notna(t) and pd.notna(d) else np.nan
         for t, d in zip(hi_t, hi_d)],
        index=trust.index,
    )


def wmean(values: pd.Series, weight: pd.Series) -> float:
    """결측 제외 가중평균."""
    v = pd.to_numeric(values, errors="coerce")
    m = v.notna() & weight.notna()
    return float(np.average(v[m], weights=weight[m])) if m.any() else np.nan


# ── K-means 검증 (Task 04) ────────────────────────────────────────────
# 하이브리드 확정: 운영·웹데모는 4사분면 규칙(persona_quadrant), K-means는
#   '데이터가 같은 4구조를 독립 재발견'했음을 보이는 타당화 근거로만 사용.
# 결정 근거: k=4(4사분면 정합), 입력=2지표(신뢰·다양성)만(검증·회피 포함 시
#   실루엣 0.35→0.25 하락·표본 30% 손실). 표준화=z(StandardScaler).
def kmeans_personas(trust: pd.Series, diversity: pd.Series, k: int = 4,
                    random_state: int = 42):
    """표준화된 [신뢰·다양성]에 K-means(k=4). (labels, centers_원척도, model) 반환.

    centers_원척도는 표준화 역변환한 (신뢰, 다양성) 군집 중심.
    """
    from sklearn.cluster import KMeans
    both = pd.DataFrame({"trust": trust, "diversity": diversity}).dropna()
    sc = StandardScaler().fit(both)
    km = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(sc.transform(both))
    labels = pd.Series(km.labels_, index=both.index, name="cluster").reindex(trust.index)
    centers = pd.DataFrame(sc.inverse_transform(km.cluster_centers_),
                           columns=["trust", "diversity"])
    return labels, centers, km


def map_cluster_to_persona(centers: pd.DataFrame,
                           t_thresh: float, d_thresh: float) -> dict[int, str]:
    """군집 중심을 임계값 기준 4사분면 페르소나명으로 매핑(K-means↔규칙 대조용)."""
    return {i: PERSONA_LABELS[(c.trust >= t_thresh, c.diversity >= d_thresh)]
            for i, c in centers.iterrows()}


def adjusted_rand(a: pd.Series, b: pd.Series) -> float:
    """두 군집해의 일치도(ARI). 규칙기반 4사분면 vs K-means 검증용."""
    from sklearn.metrics import adjusted_rand_score
    m = a.notna() & b.notna()
    return float(adjusted_rand_score(a[m].astype(str), b[m].astype(str)))
