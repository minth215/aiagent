"""데이터 모델 및 컬럼 정의.

COLUMNS는 화면(입력폼/목록), Excel 내보내기, 검색이 공유하는 단일 진실 원천이다.
컬럼을 추가/변경하려면 여기와 Program 모델 필드만 함께 수정하면 된다.
"""
from sqlalchemy import Column, Date, Integer, String, Text

from app.database import Base

# (필드명, 한글 라벨, 입력 타입) — 순서가 곧 Excel/목록의 컬럼 순서
COLUMNS = [
    ("biz_category", "업무분류", "text"),
    ("program_level1", "프로그램레벨1", "text"),
    ("program_level2", "프로그램레벨2", "text"),
    ("program_level3", "프로그램레벨3", "text"),
    ("program_name", "프로그램명", "text"),
    ("priority", "우선순위", "text"),
    ("program_type", "프로그램유형", "text"),
    ("impl_type", "구현유형", "text"),
    ("path", "경로", "text"),
    ("file_name", "파일명", "text"),
    ("change_type", "구분", "text"),  # 신규/수정
    ("remark", "비고", "textarea"),
    ("manager", "담당자", "text"),
    ("planned_start_date", "시작예정일자", "date"),
    ("planned_end_date", "종료예정일자", "date"),
    ("start_date", "시작일자", "date"),
    ("end_date", "종료일자", "date"),
    ("first_deploy_planned_date", "1차반영예정일자", "date"),
    ("first_deploy_done_date", "1차반영완료일자", "date"),
]

# 자유 텍스트 검색 대상 필드
SEARCHABLE_FIELDS = [
    "biz_category",
    "program_level1",
    "program_level2",
    "program_level3",
    "program_name",
    "program_type",
    "impl_type",
    "path",
    "file_name",
    "change_type",
    "remark",
    "manager",
]

DATE_FIELDS = [name for name, _, typ in COLUMNS if typ == "date"]


class Program(Base):
    """프로그램 목록의 한 행."""

    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)

    biz_category = Column(String(100), index=True)
    program_level1 = Column(String(100), index=True)
    program_level2 = Column(String(100), index=True)
    program_level3 = Column(String(100), index=True)
    program_name = Column(String(300), index=True)
    priority = Column(String(50))
    program_type = Column(String(100), index=True)
    impl_type = Column(String(100))
    path = Column(String(500))
    file_name = Column(String(300), index=True)
    change_type = Column(String(50))  # 신규 / 수정
    remark = Column(Text)
    manager = Column(String(100), index=True)

    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    first_deploy_planned_date = Column(Date)
    first_deploy_done_date = Column(Date)

    def as_dict(self):
        result = {"id": self.id}
        for name, _, typ in COLUMNS:
            value = getattr(self, name)
            if typ == "date" and value is not None:
                value = value.isoformat()
            result[name] = value
        return result
