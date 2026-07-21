"""샘플 데이터 입력 스크립트 (데모/테스트용).

    python seed_sample.py

실행하면 app.db에 예시 프로그램 몇 건을 넣는다.
"""
from datetime import date

from app.database import SessionLocal, init_db
from app.models import Program

SAMPLES = [
    # (업무분류, 레벨1, 레벨2, 레벨3, 프로그램명, 우선순위, 유형, 구현유형, 경로, 파일명, 구분, 담당자)
    ("정산관리", "신청", "정산신청", "", "정산신청 화면", "1", "JSP", "화면", "/web/settle", "settleApply.jsp", "신규", "김철수"),
    ("정산관리", "신청", "정산신청", "", "정산신청 컨트롤러", "1", "Controller", "Java", "/src/settle", "SettleController.java", "신규", "김철수"),
    ("정산관리", "신청", "정산신청", "", "정산신청 서비스", "1", "Service", "Java", "/src/settle", "SettleService.java", "신규", "김철수"),
    ("정산관리", "신청", "정산신청", "", "정산 매퍼", "1", "Mapper", "MyBatis", "/src/settle", "SettleMapper.xml", "신규", "김철수"),
    ("정산관리", "승인", "정산승인", "", "정산승인 화면", "2", "JSP", "화면", "/web/settle", "settleApprove.jsp", "수정", "이영희"),
    ("정산관리", "승인", "정산승인", "", "정산승인 서비스", "2", "Service", "Java", "/src/settle", "ApproveService.java", "수정", "이영희"),
    ("정산관리", "정산", "정산배치", "", "월정산 배치", "3", "Batch", "Shell", "/batch", "monthly_settle.sh", "신규", "박민수"),
    ("정산관리", "정산", "정산배치", "", "정산 테이블", "3", "Table", "DDL", "/db", "TB_SETTLE.sql", "신규", "박민수"),
    ("회원관리", "가입", "회원가입", "", "회원가입 화면", "1", "JSP", "화면", "/web/member", "join.jsp", "신규", "최지훈"),
    ("회원관리", "가입", "회원가입", "", "회원가입 컨트롤러", "1", "Controller", "Java", "/src/member", "MemberController.java", "신규", "최지훈"),
    ("회원관리", "조회", "회원조회", "", "회원조회 서비스", "2", "Service", "Java", "/src/member", "MemberSearchService.java", "수정", "최지훈"),
]


def main():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Program).count() > 0:
            print("이미 데이터가 있습니다. 건너뜁니다.")
            return
        for s in SAMPLES:
            db.add(
                Program(
                    biz_category=s[0], program_level1=s[1], program_level2=s[2], program_level3=s[3],
                    program_name=s[4], priority=s[5], program_type=s[6], impl_type=s[7],
                    path=s[8], file_name=s[9], change_type=s[10], manager=s[11],
                    planned_start_date=date(2026, 8, 1), planned_end_date=date(2026, 8, 31),
                )
            )
        db.commit()
        print(f"{len(SAMPLES)}건 입력 완료.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
