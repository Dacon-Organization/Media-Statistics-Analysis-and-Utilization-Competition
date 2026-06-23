# data/raw/ — 원천 데이터 (read-only)

KPF에서 내려받은 **원본 데이터**. 가공하지 않고 보존합니다(분석은 사본으로).

## 구성
| 경로 | 내용 |
|------|------|
| [`audience/`](audience/) | 언론수용자 조사 연도별(2019~2025) 데이터·문서 |
| [`manual/`](manual/) | 언론 통계 원시자료 분석 매뉴얼(코드북 성격) |

## 포함/제외 (오픈데이터 정책)
- **포함**: 분석 입력 `.sav`/`.csv`/`.xlsx`
- **제외**: PDF(보고서·통계표·코드북·매뉴얼) — 대용량(일부 100MB↑)이라 git 미포함. → [`DOWNLOAD-GUIDE.md`](DOWNLOAD-GUIDE.md)

## 문서
- 확보 현황: [`INVENTORY.md`](INVENTORY.md)
- 다운로드 가이드: [`DOWNLOAD-GUIDE.md`](DOWNLOAD-GUIDE.md)
- 데이터 명세: [`../../docs/design/data-spec.md`](../../docs/design/data-spec.md)
