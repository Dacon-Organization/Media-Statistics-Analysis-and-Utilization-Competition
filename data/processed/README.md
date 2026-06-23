# data/processed/ — 분석용 정제 데이터

분석·모델링에 바로 투입하는 **최종 정제 데이터**를 둡니다. (예: 결측 처리·가중치 반영·지수 산출용 피처 테이블)

- **버전관리 제외**(`.gitignore`). `raw/`→`interim/`→`processed/` 파이프라인으로 재현합니다.
- 컬럼 정의가 바뀌면 [`../../docs/design/data-spec.md`](../../docs/design/data-spec.md)와 동기화합니다.
