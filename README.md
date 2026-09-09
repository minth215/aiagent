# 프로그램 목록 / 업무흐름도 관리 (폐쇄망 대응 PoC)

Eclipse/SVN 소스 개발 업무를 정리하기 위한 도구입니다.
**개발자 PC 한 대에서 완결**되도록 설계되어, 별도 서버 없이 로컬에서 실행합니다.
소스를 스캔해 프로그램 목록을 자동 생성하고, 웹 화면으로 **검토·수정·검색**한 뒤
버튼 한 번으로 **프로그램 목록(Excel)** 과 **업무흐름도(PPT)** 산출물을 만듭니다.

일상 사용 흐름:

```
svn update  →  python run.py --workspace <경로>  →  브라우저에서 검토·수정  →  Excel/PPT 내보내기
   (최신화)        (추출 → DB 병합 → 웹앱 실행)          (localhost)              (산출물)
```

재추출해도 **사람이 확정한 값(업무분류·업무명·담당자 등)은 보존**되고 구조 정보만 갱신되므로,
`svn update` 후 몇 번이고 안전하게 다시 돌릴 수 있습니다.

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
# 1) 의존성 설치 (최초 1회)
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      # Windows
# ./.venv/bin/pip install -r requirements.txt        # macOS/Linux

# 2) 최신화 + 실행 (평소 사용) — 추출→DB병합→브라우저 자동 실행
python run.py --workspace C:\eclipse-workspace\myproject --base-package com.acme

# 웹앱만 실행 (추출 없이)
python run.py

# 샘플로 먼저 체험해보기
python run.py --workspace sample_workspace --base-package com.acme
```

> Windows PC 기준으로 `python run.py` 하나면 됩니다. `.sh`/`uvicorn` 직접 실행도 가능하지만
> `run.py`가 크로스플랫폼이라 가장 간단합니다.

## 터미널 없이 브라우저로만 접속하기

이 도구는 소스가 있는 PC에서 로컬로 동작하므로 외부 인터넷 도메인에는 올리지 않습니다.
대신 아래 방법으로 "터미널에 명령을 치지 않고 브라우저 주소만으로 들어가는" 경험을 만들 수 있습니다.
세 가지는 함께 쓸 수 있습니다.

### 바탕화면 아이콘으로 실행 (권장 · CMD 창 없음)

**Windows**
1. `install-desktop-icon.bat` 을 **한 번** 더블클릭
   → 가상환경·의존성 설치 후 바탕화면에 **`프로그램목록관리`** 아이콘을 만듭니다.
2. 이후로는 그 **바탕화면 아이콘만 더블클릭** → CMD 창 없이 웹앱이 뜨고 브라우저가 열립니다.

- 아이콘은 내부적으로 `start-hidden.vbs`(콘솔 숨김)를 실행합니다.
- 이미 실행 중일 때 다시 더블클릭하면 새 서버를 띄우지 않고 **브라우저만** 엽니다.

**macOS/Linux**: `start.command` 더블클릭 (최초 1회 `chmod +x start.command`).
Dock/바탕화면에 별칭(alias)을 만들어 두면 동일하게 아이콘 실행이 됩니다.

> 최초 설치에는 인터넷이 필요합니다. 폐쇄망이면 `wheels/` 폴더에 미리 받은 whl을 넣어두면
> 자동으로 오프라인 설치합니다(위 "폐쇄망 오프라인 설치" 참고).

### 팀 배포 (각자 PC)

팀원 각자 자기 PC에서 독립적으로 사용합니다(로그인 불필요, 데이터도 각 PC 내부에만 존재).

1. 이 폴더를 각자 PC에 복사(또는 `git clone`) — 소스가 있는 PC에 두면 됩니다.
2. `install-desktop-icon.bat` 한 번 실행.
3. 바탕화면 아이콘 더블클릭 → "소스 추출" 메뉴에서 본인 SVN 워크스페이스 경로 입력 → 사용.

### (선택) 항상 켜두기 / 예쁜 주소

- **로그인 시 자동 실행**: `Win+R` → `shell:startup` → 그 폴더에 `start-hidden.vbs` 바로가기 넣기.
- **로컬 도메인**: hosts 파일에 `127.0.0.1  progtool.local` 추가 후 `http://progtool.local:8000` 접속
  (포트 없이 쓰려면 `run.py --port 80`, 관리자 권한 필요). 외부 인터넷 도메인이 아니라
  각 PC 내부에서만 유효한 이름입니다.

브라우저에서 `http://<서버IP>:8000` 접속.

## 화면 구성

- `/` — 목록·통합검색·필터, Excel/PPT 내보내기 버튼
- `/scan` — **소스 추출·최신화** (워크스페이스 경로 입력 → 추출 → DB 병합, CLI 없이 브라우저에서)
- `/new` — 신규 등록 폼
- `/edit/{id}` — 수정
- `/export/excel`, `/export/pptx` — 현재 검색결과 반영 산출물 다운로드
- `/api/programs` — 검색/조회 JSON API (외부 연동·자동화용)

> **전 과정 GUI**: 웹앱을 한 번 띄운 뒤(`python run.py`)에는 추출·검토·수정·검색·산출물까지
> 모두 브라우저에서 수행할 수 있습니다. `svn update` 후 "소스 추출" 메뉴에서 경로를 입력하고
> "추출 실행"만 누르면 됩니다(명령줄 재실행 불필요).

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

## 로컬 배포 (개발자 PC 1대 완결)

서버가 필요 없습니다. 각 개발자가 자기 PC에서 SVN 최신 소스를 기준으로 추출·검토·산출물화까지
모두 수행합니다. 데이터(`app.db`)와 산출물도 그 PC 안에만 존재합니다.

- **실행 대상**: 개발자 각자의 PC (소스가 있는 곳)
- **소스 기준**: `svn update`로 받은 로컬 워크스페이스 경로
- **DB**: 로컬 SQLite 파일 1개(`app.db`) — PC별 독립. 필요 시 팀 공유는 파일 복사로 충분
- **웹앱**: `localhost`에서만 뜸 (`--host 127.0.0.1` 기본) — 외부 노출 없음

### 폐쇄망 오프라인 설치

인터넷이 없는 PC에서는 외부망에서 wheel을 미리 받아 반입 후 설치합니다.

```bash
# (외부망) 다운로드
pip download -r requirements.txt -d wheels/
# (사내 PC) 오프라인 설치
pip install --no-index --find-links=wheels/ -r requirements.txt
```

### (선택) 팀 공유 서버로 확대

회사 승인을 받아 공유 서버에 올릴 경우, `DATABASE_URL`을 PostgreSQL로 바꾸고
`--host 0.0.0.0`으로 실행하면 그대로 다인 사용이 가능합니다(코드 변경 불필요).
그 경우 "개발자 PC 분석 → 서버 적재"를 위한 업로드 API를 추가하면 됩니다.

## 소스 워크스페이스 자동 추출기 (`extract_workspace.py`)

Eclipse 워크스페이스/프로젝트 소스를 **스캔하여 프로그램 목록을 자동 생성**합니다.
정규식 기반이라 컴파일되지 않는 레거시 코드에서도 견고하게 동작하며, **LLM이 필요 없습니다.**

```bash
# 스캔만 (JSON 출력)
./.venv/bin/python extract_workspace.py sample_workspace -o extract.json

# 스캔 후 DB에 적재 → 웹앱 목록에서 바로 검토
./.venv/bin/python extract_workspace.py sample_workspace --import

# 회사 패키지 prefix 지정 시 업무분류 추정 정확도 향상
./.venv/bin/python extract_workspace.py /path/to/workspace --base-package com.acme
```

추출 항목:

| 구분 | 방식 | 예시 |
|------|------|------|
| 프로그램유형 | 확장자 + 애노테이션(@Controller/@Service/@Mapper) + 파일명 규칙 | JSP, Controller, Service, Mapper, Batch, SQL/DDL |
| 대상 테이블 | SQL/MyBatis의 FROM·JOIN·INTO·UPDATE 파싱 | TB_SETTLE, TB_MEMBER |
| 업무분류(제안) | 패키지/디렉터리 구조에서 추정 | settle, member |
| 호출관계 | 타입참조(Controller→Service→Mapper), 매퍼 namespace, JSP↔Controller URL | 8 edges |
| 업무 힌트 | 클래스 상단 Javadoc 첫 문장 | "정산 신청·승인 처리 로직 구현" |

> 업무분류·업무명 등 **의미적 값은 "제안값"** 입니다. 다음 단계(Claude Code 분석 또는 사람 검토)에서 확정합니다.

## 심화 아키텍처 (3계층)

```
① 결정적 추출  (extract_workspace.py)   ← LLM 아님. 정확·빠름
     파일분류 · 테이블 · 호출관계 · 구조
        │  JSON
        ▼
② 의미 분석    (Claude Code 스킬 — 예정)  ← Haiku 4.5
     ①의 사실을 근거로 업무명·업무설명·처리흐름 초안 작성 (환각 억제)
        │  DB 적재
        ▼
③ 검토·확정·산출물  (본 웹앱)
     사람이 검토·수정 → Excel(프로그램목록) · PPT(업무흐름도) 생성
```

**핵심**: LLM에 코드를 통째로 넣지 않는다. ①이 정확한 사실을 뽑고, ②(Haiku)는 "무슨 업무인지"
의미 레이어만 담당하며, ③에서 사람이 확정한다. → Haiku 4.5로도 실무 품질 확보.

## 향후 로드맵

- [x] ① 결정적 추출기 (파일분류·테이블·호출관계)
- [x] 재추출 안전 병합(upsert) — svn update 후 재실행해도 사람 편집 보존
- [x] 크로스플랫폼 로컬 실행기 `run.py` (추출→병합→실행 원클릭)
- [x] 웹 GUI 추출 화면 `/scan` — 브라우저에서 경로 입력만으로 추출·최신화
- [ ] ② Claude Code 스킬 `/analyze-workspace` — 추출 결과를 근거로 업무 분석 초안 생성
- [ ] SVN 연동 `구분(신규/수정)` 자동 표기 (`svn status` 기반)
- [ ] Excel 일괄 업로드(기존 관리 엑셀 가져오기)
