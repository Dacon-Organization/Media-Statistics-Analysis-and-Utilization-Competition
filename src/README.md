# src/ — 분석 파이프라인 모듈

노트북에서 재사용하는 **함수·파이프라인 코드**. (로딩·전처리·지수 산출·군집)

## 구성(예정)
```
src/
├── data_loading.py     # 연도별 .sav/.csv/.xlsx 로더(포맷 분기·레이블)
├── preprocess.py       # 결측·가중치·변수 하모나이즈
├── health_index.py     # 지수 구성식(정규화·가중·합성)
└── personas.py         # 군집(K-means 등)
```
- 명명: 함수 `camelCase`/`snake_case`, 상수 `UPPER_SNAKE_CASE`. 복잡한 로직엔 한국어 주석.
- 의존성은 루트 [`../requirements.txt`](../requirements.txt).
