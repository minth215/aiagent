"""워크스페이스 추출 CLI.

    # 스캔만 (JSON 출력)
    python extract_workspace.py sample_workspace -o extract.json

    # 스캔 후 DB에 적재 (웹앱에서 바로 검토)
    python extract_workspace.py sample_workspace --import

    # 회사 패키지 prefix 지정 (업무분류 추정 정확도 향상)
    python extract_workspace.py /path/to/workspace --base-package com.acme
"""
import argparse
import json
import sys

from app.extractor import scan_workspace


def _print_summary(result: dict):
    s = result["summary"]
    print(f"\n스캔 루트 : {result['root']}")
    print(f"base 패키지: {result['base_package'] or '(자동추정 실패/없음)'}")
    print(f"파일 수   : {s['file_count']}")
    print("유형별    :", ", ".join(f"{k} {v}" for k, v in sorted(s["by_type"].items())))
    print("업무분류  :", ", ".join(f"{k}({v})" for k, v in s["clusters"].items()))
    print(f"테이블({len(s['tables'])}): {', '.join(s['tables'])}")
    print(f"호출관계 edge 수: {len(result['edges'])}")


def _import_to_db(result: dict, replace: bool) -> dict:
    from app.crud import upsert_programs
    from app.database import SessionLocal, init_db

    init_db()
    db = SessionLocal()
    try:
        # '_' 로 시작하는 분석 메타는 제외하고 컬럼만 적재
        rows = [{k: v for k, v in p.items() if not k.startswith("_")}
                for p in result["programs"]]
        return upsert_programs(db, rows, replace=replace)
    finally:
        db.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eclipse 워크스페이스 소스 추출기")
    ap.add_argument("root", help="스캔할 워크스페이스/프로젝트 경로")
    ap.add_argument("-o", "--out", help="결과 JSON 저장 경로")
    ap.add_argument("--base-package", help="회사 패키지 prefix (예: com.acme)")
    ap.add_argument("--import", dest="do_import", action="store_true",
                    help="스캔 결과를 DB에 병합 적재 (사람이 입력한 값은 보존)")
    ap.add_argument("--replace", action="store_true",
                    help="추출기가 만든 기존 행을 모두 지우고 새로 적재 (사람 편집 내용도 삭제)")
    args = ap.parse_args(argv)

    result = scan_workspace(args.root, base_package=args.base_package)
    _print_summary(result)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nJSON 저장: {args.out}")

    if args.do_import or args.replace:
        stats = _import_to_db(result, replace=args.replace)
        print(f"\nDB 적재 완료: 신규 {stats['added']}건 / 갱신 {stats['updated']}건"
              f" (웹앱 목록에서 확인)")
        if stats["missing"]:
            print(f"  ※ 이번 스캔에 없지만 DB에 남은 소스 행: {stats['missing']}건 "
                  f"(삭제된 파일일 수 있음 — 확인 후 웹에서 삭제하거나 --replace로 재구성)")

    if not args.out and not args.do_import and not args.replace:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main()
