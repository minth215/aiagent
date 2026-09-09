"""데이터 접근 계층 (생성/조회/수정/삭제 + 검색)."""
from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import COLUMNS, DATE_FIELDS, REFRESH_ON_UPSERT, SEARCHABLE_FIELDS, Program


def _parse_value(name: str, raw):
    """폼 문자열을 모델 필드 타입에 맞게 변환."""
    if raw is None:
        return None
    raw = raw.strip() if isinstance(raw, str) else raw
    if raw == "":
        return None
    if name in DATE_FIELDS:
        # HTML date input은 YYYY-MM-DD
        return date.fromisoformat(raw)
    return raw


def form_to_kwargs(form: dict) -> dict:
    kwargs = {}
    for name, _, _ in COLUMNS:
        kwargs[name] = _parse_value(name, form.get(name))
    return kwargs


def create_program(db: Session, data: dict) -> Program:
    program = Program(**form_to_kwargs(data))
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


def get_program(db: Session, program_id: int) -> Program | None:
    return db.query(Program).filter(Program.id == program_id).first()


def _source_key(data: dict) -> str:
    path = (data.get("path") or "").rstrip("/")
    return f"{path}/{data.get('file_name') or ''}"


def upsert_programs(db: Session, programs: list[dict], replace: bool = False) -> dict:
    """추출 결과를 DB에 병합 적재.

    replace=True  : 추출기가 만든 기존 행(source_key 보유)을 모두 지우고 새로 넣는다.
    replace=False : source_key 기준으로 병합. 신규 파일은 추가하고, 기존 파일은
                    구조 필드(REFRESH_ON_UPSERT)만 갱신하며 사람이 확정한 값은 보존한다.

    반환: {added, updated, missing} — missing은 이번 스캔에 없지만 DB에 남은 소스 행 수.
    """
    if replace:
        db.query(Program).filter(Program.source_key.isnot(None)).delete(synchronize_session=False)
        db.commit()

    scanned_keys = set()
    added = updated = 0

    for data in programs:
        key = _source_key(data)
        scanned_keys.add(key)
        existing = db.query(Program).filter(Program.source_key == key).first()

        if existing is None:
            kwargs = form_to_kwargs(data)
            program = Program(source_key=key, **kwargs)
            db.add(program)
            added += 1
        else:
            # 구조 필드만 갱신, 사람이 입력한 값은 보존
            for field in REFRESH_ON_UPSERT:
                if field in data:
                    setattr(existing, field, _parse_value(field, data.get(field)))
            updated += 1

    db.commit()

    missing = (
        db.query(Program)
        .filter(Program.source_key.isnot(None))
        .filter(Program.source_key.notin_(scanned_keys) if scanned_keys else True)
        .count()
    )
    return {"added": added, "updated": updated, "missing": missing}


def clear_source_programs(db: Session) -> int:
    """추출기가 만든 행(source_key 보유)만 삭제. 수동 등록 행은 유지."""
    n = db.query(Program).filter(Program.source_key.isnot(None)).delete(synchronize_session=False)
    db.commit()
    return n


def update_program(db: Session, program_id: int, data: dict) -> Program | None:
    program = get_program(db, program_id)
    if program is None:
        return None
    for key, value in form_to_kwargs(data).items():
        setattr(program, key, value)
    db.commit()
    db.refresh(program)
    return program


def delete_program(db: Session, program_id: int) -> bool:
    program = get_program(db, program_id)
    if program is None:
        return False
    db.delete(program)
    db.commit()
    return True


def search_programs(
    db: Session,
    q: str | None = None,
    biz_category: str | None = None,
    program_type: str | None = None,
    change_type: str | None = None,
    manager: str | None = None,
) -> list[Program]:
    """자유 텍스트 검색 + 컬럼별 필터."""
    query = db.query(Program)

    if q:
        like = f"%{q}%"
        conditions = [getattr(Program, f).ilike(like) for f in SEARCHABLE_FIELDS]
        query = query.filter(or_(*conditions))

    if biz_category:
        query = query.filter(Program.biz_category == biz_category)
    if program_type:
        query = query.filter(Program.program_type == program_type)
    if change_type:
        query = query.filter(Program.change_type == change_type)
    if manager:
        query = query.filter(Program.manager == manager)

    return query.order_by(
        Program.biz_category,
        Program.program_level1,
        Program.program_level2,
        Program.program_level3,
        Program.priority,
        Program.id,
    ).all()


def distinct_values(db: Session, field: str) -> list[str]:
    """필터 드롭다운 채우기용 (해당 컬럼의 고유값)."""
    rows = db.query(getattr(Program, field)).distinct().all()
    return sorted({r[0] for r in rows if r[0]})
