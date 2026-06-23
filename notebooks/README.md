# notebooks/ — 분석 노트북

EDA·지수 설계·군집(페르소나)·코호트 분석 Jupyter 노트북. ZIP 추가 산출물로 제출.

## 권장 순서·명명
```
01-eda-2025.ipynb              # 2025 .sav 로딩·기초 탐색
02-variable-mapping.ipynb      # 코드북 ↔ 지수 변수 매핑
03-health-index.ipynb          # 뉴스 건강 지수 설계·산출
04-personas-kmeans.ipynb       # 군집 페르소나
05-cohort-trend.ipynb          # 2019~2025 추세·코호트
```
- 데이터는 [`../data/`](../data/)에서 로드. `.sav`는 `pyreadstat`/`pandas.read_spss`.
- 무거운 출력은 커밋 전 정리. 재현 가능하게 상대경로 사용.
