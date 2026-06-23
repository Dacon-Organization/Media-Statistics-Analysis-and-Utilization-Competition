# data/ — 데이터 디렉토리

KPF 언론 통계 원시자료와 그 가공물을 보관합니다.

## 구조
| 폴더 | 용도 | git 포함 |
|------|------|:--:|
| [`raw/`](raw/) | 원천 데이터(다운로드 원본). 손대지 않음(read-only) | 데이터 ✅ / PDF ❌ |
| `interim/` | 중간 가공(병합·정제 진행분). 재현 가능 | ❌(gitignore) |
| `processed/` | 분석·모델 입력용 최종 정제본 | ❌(gitignore) |

## 데이터 공개·버전관리 정책

- KPF 언론 통계는 **공개 오픈데이터**(누구나 내려받아 분석·활용 가능)이므로, **분석 입력 데이터(`.sav`/`.csv`/`.xlsx`)는 본 저장소에 포함**해 재현성을 확보합니다.
- 단, **PDF 문서(보고서·통계표·코드북·분석매뉴얼)는 총 ~570MB이고 일부 파일(2021·2022 통계표)이 GitHub 100MB 한도를 초과**하여 저장소에서 제외합니다.
  - 받는 방법: [`raw/DOWNLOAD-GUIDE.md`](raw/DOWNLOAD-GUIDE.md)
- 출처: [한국언론진흥재단 언론 통계](https://www.kpf.or.kr/front/mediaStats/mediaStatsListPage.do). 다운로드 시 **연구활용 동의** 절차가 있으므로, 재배포·인용 시 출처를 명시하고 KPF 이용조건을 준수합니다.
- `interim/`·`processed/`는 `raw/`로부터 코드로 재생성되므로 버전관리하지 않습니다(노트북·`src/` 파이프라인으로 재현).

## 관련 문서
- 데이터 명세·카탈로그: [`../docs/design/data-spec.md`](../docs/design/data-spec.md)
- 확보 현황 인벤토리: [`raw/INVENTORY.md`](raw/INVENTORY.md)
