"""FastAPI 애플리케이션 진입점.

화면(웹 입력/검색/조회) + 산출물 내보내기(Excel/PPT) + 간단한 JSON API 제공.
"""
import os
import urllib.parse
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db, init_db
from app.exporters.excel import build_program_list
from app.exporters.pptx import build_flow_diagram
from app.extractor import scan_workspace
from app.models import COLUMNS

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="프로그램 목록/업무흐름도 관리")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def _startup():
    init_db()


def _filters(db: Session) -> dict:
    return {
        "biz_categories": crud.distinct_values(db, "biz_category"),
        "program_types": crud.distinct_values(db, "program_type"),
        "change_types": crud.distinct_values(db, "change_type"),
        "managers": crud.distinct_values(db, "manager"),
    }


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    q: str | None = None,
    biz_category: str | None = None,
    program_type: str | None = None,
    change_type: str | None = None,
    manager: str | None = None,
    db: Session = Depends(get_db),
):
    programs = crud.search_programs(
        db,
        q=q,
        biz_category=biz_category,
        program_type=program_type,
        change_type=change_type,
        manager=manager,
    )
    current = {
        "q": q or "",
        "biz_category": biz_category or "",
        "program_type": program_type or "",
        "change_type": change_type or "",
        "manager": manager or "",
    }
    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "programs": programs,
            "columns": COLUMNS,
            "filters": _filters(db),
            "current": current,
            "query_string": urllib.parse.urlencode({k: v for k, v in current.items() if v}),
        },
    )


@app.get("/scan", response_class=HTMLResponse)
def scan_form(request: Request):
    return templates.TemplateResponse(
        "scan.html",
        {"request": request, "result": None, "stats": None, "error": None,
         "workspace": "", "base_package": "", "mode": "merge"},
    )


@app.post("/scan", response_class=HTMLResponse)
async def scan_run(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    workspace = (form.get("workspace") or "").strip()
    base_package = (form.get("base_package") or "").strip() or None
    mode = form.get("mode") or "merge"

    ctx = {"request": request, "result": None, "stats": None, "error": None,
           "workspace": workspace, "base_package": base_package or "", "mode": mode}

    if not workspace:
        ctx["error"] = "워크스페이스 경로를 입력하세요."
    elif not os.path.isdir(workspace):
        ctx["error"] = f"경로를 찾을 수 없거나 폴더가 아닙니다: {workspace}"
    else:
        try:
            result = scan_workspace(workspace, base_package=base_package)
            rows = [{k: v for k, v in p.items() if not k.startswith("_")}
                    for p in result["programs"]]
            stats = crud.upsert_programs(db, rows, replace=(mode == "replace"))
            ctx["result"] = result["summary"]
            ctx["stats"] = stats
        except Exception as exc:  # noqa: BLE001 - 사용자에게 원인 표시
            ctx["error"] = f"추출 중 오류: {exc}"

    return templates.TemplateResponse("scan.html", ctx)


@app.get("/new", response_class=HTMLResponse)
def new_form(request: Request):
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "columns": COLUMNS, "program": None, "action": "/new", "title": "신규 등록"},
    )


@app.post("/new")
async def create(request: Request, db: Session = Depends(get_db)):
    form = dict(await request.form())
    crud.create_program(db, form)
    return RedirectResponse(url="/", status_code=303)


@app.get("/edit/{program_id}", response_class=HTMLResponse)
def edit_form(program_id: int, request: Request, db: Session = Depends(get_db)):
    program = crud.get_program(db, program_id)
    if program is None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "columns": COLUMNS,
            "program": program.as_dict(),
            "action": f"/edit/{program_id}",
            "title": f"수정 (#{program_id})",
        },
    )


@app.post("/edit/{program_id}")
async def update(program_id: int, request: Request, db: Session = Depends(get_db)):
    form = dict(await request.form())
    crud.update_program(db, program_id, form)
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{program_id}")
def delete(program_id: int, db: Session = Depends(get_db)):
    crud.delete_program(db, program_id)
    return RedirectResponse(url="/", status_code=303)


def _current_filter_args(q, biz_category, program_type, change_type, manager):
    return dict(
        q=q,
        biz_category=biz_category,
        program_type=program_type,
        change_type=change_type,
        manager=manager,
    )


@app.get("/export/excel")
def export_excel(
    q: str | None = None,
    biz_category: str | None = None,
    program_type: str | None = None,
    change_type: str | None = None,
    manager: str | None = None,
    db: Session = Depends(get_db),
):
    programs = crud.search_programs(db, **_current_filter_args(q, biz_category, program_type, change_type, manager))
    content = build_program_list(programs)
    filename = urllib.parse.quote("프로그램목록.xlsx")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@app.get("/export/pptx")
def export_pptx(
    q: str | None = None,
    biz_category: str | None = None,
    program_type: str | None = None,
    change_type: str | None = None,
    manager: str | None = None,
    db: Session = Depends(get_db),
):
    programs = crud.search_programs(db, **_current_filter_args(q, biz_category, program_type, change_type, manager))
    content = build_flow_diagram(programs)
    filename = urllib.parse.quote("업무흐름도.pptx")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@app.get("/api/programs")
def api_programs(
    q: str | None = None,
    biz_category: str | None = None,
    program_type: str | None = None,
    change_type: str | None = None,
    manager: str | None = None,
    db: Session = Depends(get_db),
):
    """검색/조회용 JSON API (외부 연동·자동화용)."""
    programs = crud.search_programs(db, **_current_filter_args(q, biz_category, program_type, change_type, manager))
    return {"count": len(programs), "items": [p.as_dict() for p in programs]}
