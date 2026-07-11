# data/interim/revalidation/ — KPF 재검증 재생성물

`python src/kpf_revalidation.py` 실행 시 생성되는 CSV(gitignore, 로컬 재생성물).

| 파일 | 내용 |
|------|------|
| `trust_levels_by_year.csv` | 연도별 신뢰 절대수준(원척도 5점·공식 WT 가중 평균, '신뢰한다' 비율) |
| `step_2019_2020_labels.csv` | 2019·2020 언론 인식 배터리 문항/값 라벨 원문 |
| `step_2019_2020_dists.csv` | 2019·2020 문항별 1~5 가중 응답분포(%) |

판정·해석의 정본(SSOT)은 [`docs/design/kpf-revalidation.md`](../../../docs/design/kpf-revalidation.md).
공식 보고서 PDF(1차 원전)는 `data/raw/audience/<연도>/` 로컬 보관(git 미포함, `data/raw/DOWNLOAD-GUIDE.md`).
