"""SQLite 데이터베이스 설정.

폐쇄망 친화적으로 외부 DB 서버 없이 단일 파일(app.db)로 동작한다.
나중에 PostgreSQL 등으로 옮기려면 DATABASE_URL 환경변수만 바꾸면 된다.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

# check_same_thread는 SQLite에서만 필요
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 의존성 주입용 DB 세션."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """테이블 생성 + 경량 마이그레이션. 앱 시작 시 1회 호출."""
    import app.models  # noqa: F401  (모델 등록을 위해 import)

    Base.metadata.create_all(bind=engine)
    _ensure_columns()


def _ensure_columns():
    """기존 SQLite DB에 신규 컬럼이 없으면 추가 (간단 마이그레이션).

    정식 마이그레이션 도구(alembic) 없이 PoC 수준에서 스키마 진화를 지원한다.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "programs" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("programs")}
    if "source_key" not in existing:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE programs ADD COLUMN source_key VARCHAR(800)"))
            conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_programs_source_key "
                "ON programs (source_key)"
            ))
