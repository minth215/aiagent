# 프로그램 목록 / 업무흐름도 관리 (폐쇄망 대응 PoC)

Eclipse 소스 개발 업무를 정리하기 위한 웹 애플리케이션입니다.
사람이 웹으로 프로그램 정보를 입력하면 **DB에 저장·검색·조회**되고,
버튼 한 번으로 **프로그램 목록(Excel)** 과 **업무흐름도(PPT)** 산출물을 내려받을 수 있습니다.

## 특징

- **폐쇄망 친화적** — 외부 인터넷/클라우드 LLM 불필요, 오프라인에서 완전 동작
- **DB 저장** — 입력 데이터가 쌓이며 검색·필터·수정·삭제 가능 (일회성 아님)
- **프론트엔드 빌드 도구 없음** — 서버 렌더링 HTML + 최소 CSS만 사용 (npm/CDN 반입 불필요)
- **산출물 자동 생성**
  - 프로그램 목록 → Excel (`openpyxl`)
  - 업무흐름도 → PPT (`python-pptx`) : **업무 프로세스 흐름 + 호출 흐름** 2종
- **LLM은 선택** — 향후 사내 GPU 서버가 준비되면 업무설명 자동 확장 등에 붙일 수 있는 여지만 남겨둠

## 기술 스택

| 구성 | 선택 | 이유 |
|------|------|------|
| 웹 프레임워크 | FastAPI + Uvicorn | 경량, JSON API 겸용 |
| 화면 | Jinja2 서버 렌더링 | 빌드 도구 불필요 (폐쇄망) |
| DB | SQLite (기본) | 파일 하나, DB 서버 설치 불필요. `DATABASE_URL`로 PostgreSQL 교체 가능 |
| Excel | openpyxl | |
| PPT | python-pptx | |

## 실행 방법

```bash
# 1) 의존성 설치 (폐쇄망에서는 사전에 wheel 반입 후 오프라인 설치)
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

# 2) (선택) 샘플 데이터 넣기
./.venv/bin/python seed_sample.py

# 3) 서버 실행
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
#   또는  ./run.sh
```

브라우저에서 `http://<서버IP>:8000` 접속.

## 화면 구성

- `/` — 목록·통합검색·필터, Excel/PPT 내보내기 버튼
- `/new` — 신규 등록 폼
- `/edit/{id}` — 수정
- `/export/excel`, `/export/pptx` — 현재 검색결과 반영 산출물 다운로드
- `/api/programs` — 검색/조회 JSON API (외부 연동·자동화용)

## 컬럼

업무분류 / 프로그램레벨1 / 프로그램레벨2 / 프로그램레벨3 / 프로그램명 / 우선순위 /
프로그램유형 / 구현유형 / 경로 / 파일명 / 구분(신규·수정) / 비고 / 담당자 /
시작예정일자 / 종료예정일자 / 시작일자 / 종료일자 / 1차반영예정일자 / 1차반영완료일자

컬럼을 바꾸려면 `app/models.py`의 `COLUMNS`와 `Program` 모델만 함께 수정하면
화면·Excel·검색에 일괄 반영됩니다.

## 업무흐름도(PPT) 생성 규칙

- **업무 프로세스 흐름** : `업무분류`별 슬라이드에 `프로그램레벨1`을 우선순위 순으로 나열 (예: 신청 → 승인 → 정산)
- **호출 흐름** : `프로그램유형`을 키워드로 계층 매핑 (화면 → Controller → Service → Mapper → DB)
  - 매핑 키워드는 `app/exporters/pptx.py`의 `LAYERS`에서 조정

## 폐쇄망 반입 메모

인터넷이 없는 환경에서는 외부망 PC에서 wheel을 미리 받아 반입 후 설치합니다.

```bash
# (외부망) 다운로드
pip download -r requirements.txt -d wheels/
# (폐쇄망) 오프라인 설치
pip install --no-index --find-links=wheels/ -r requirements.txt
```

## 향후 확장 여지

- 소스 경로에서 파일 메타/테이블명(SQL의 FROM·JOIN) 자동 추출 → 입력 반자동화
- 사내 GPU LLM 연동 시 업무설명 자동 생성·요약
- 인증/권한(로그인), 첨부파일, 이력 관리
