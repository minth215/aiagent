"""로컬 실행기 (Windows/macOS/Linux 공통).

    # 그냥 웹앱만 실행
    python run.py

    # svn update 후: 워크스페이스 재추출 → DB 병합 → 웹앱 실행 (원클릭 최신화)
    python run.py --workspace C:\\eclipse-workspace\\myproject --base-package com.acme

옵션:
    --workspace PATH   추출할 소스 경로 (지정 시 실행 전 추출·병합 수행)
    --base-package PKG 회사 패키지 prefix (업무분류 추정 정확도 향상)
    --replace          추출기가 만든 기존 행을 모두 지우고 재구성 (사람 편집 삭제)
    --port PORT        웹 포트 (기본 8000)
    --no-browser       브라우저 자동 실행 안 함
"""
import argparse
import threading
import webbrowser


def _refresh(workspace: str, base_package: str | None, replace: bool):
    from app.extractor import scan_workspace
    from app.crud import upsert_programs
    from app.database import SessionLocal, init_db

    print(f"[추출] {workspace} 스캔 중…")
    result = scan_workspace(workspace, base_package=base_package)
    s = result["summary"]
    print(f"[추출] 파일 {s['file_count']}건 · 테이블 {len(s['tables'])}종 · "
          f"업무분류 {list(s['clusters'].keys())}")

    init_db()
    db = SessionLocal()
    try:
        rows = [{k: v for k, v in p.items() if not k.startswith("_")}
                for p in result["programs"]]
        stats = upsert_programs(db, rows, replace=replace)
    finally:
        db.close()
    print(f"[적재] 신규 {stats['added']}건 / 갱신 {stats['updated']}건"
          + (f" / 스캔에 없는 잔여 {stats['missing']}건" if stats["missing"] else ""))


def main():
    ap = argparse.ArgumentParser(description="프로그램 목록/업무흐름도 관리 — 로컬 실행기")
    ap.add_argument("--workspace", help="추출할 소스 경로")
    ap.add_argument("--base-package", help="회사 패키지 prefix (예: com.acme)")
    ap.add_argument("--replace", action="store_true", help="기존 추출 행 재구성")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    if args.workspace:
        _refresh(args.workspace, args.base_package, args.replace)

    url = f"http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}"
    print(f"\n웹앱 실행: {url}  (종료: Ctrl+C)")
    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    import uvicorn
    uvicorn.run("app.main:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
