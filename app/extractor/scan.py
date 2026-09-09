"""워크스페이스 스캔 오케스트레이션.

파일 순회 → 분류 → 메타 추출 → 업무분류/계층 추정 → 호출관계 그래프 →
프로그램 목록 엔트리 생성. 결과는 순수 dict/JSON 직렬화 가능 구조.
"""
import os
from datetime import datetime, timezone

from app.extractor.classify import classify
from app.extractor.javameta import parse_java
from app.extractor.sqlmeta import extract_tables, parse_mybatis

SCAN_EXTS = (".java", ".jsp", ".jspf", ".xml", ".sql", ".sh", ".bat", ".ksh")
SKIP_DIRS = {
    "target", "build", "out", "bin", "dist", ".git", ".svn", ".hg",
    "node_modules", ".settings", ".idea", ".metadata", "META-INF",
}
# 패키지에서 업무명이 아닌 '역할' 세그먼트
ROLE_SEGMENTS = {
    "web", "controller", "ctrl", "service", "svc", "impl", "mapper", "dao",
    "vo", "dto", "domain", "model", "entity", "common", "comm", "cmm",
    "util", "utils", "config", "job", "batch", "api", "biz", "persistence",
    "repository", "repo",
}
MAX_BYTES = 2_000_000


def _read_text(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read(MAX_BYTES)
    for enc in ("utf-8", "cp949", "euc-kr", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _common_package_prefix(packages: list) -> list:
    """모든 패키지에 공통인 선행 세그먼트(회사/조직 prefix 추정)."""
    seg_lists = [p.split(".") for p in packages if p]
    if not seg_lists:
        return []
    prefix = []
    for parts in zip(*seg_lists):
        if len(set(parts)) == 1:
            prefix.append(parts[0])
        else:
            break
    # 마지막 도메인 세그먼트까지 먹지 않도록 최대 3개까지만 prefix로 인정
    return prefix[:3]


def _domain_segments(package: str, base_prefix: list) -> list:
    segs = package.split(".") if package else []
    if base_prefix and segs[: len(base_prefix)] == base_prefix:
        segs = segs[len(base_prefix):]
    return [s for s in segs if s.lower() not in ROLE_SEGMENTS]


def _path_domain(rel_path: str, base_prefix: list) -> list:
    parts = rel_path.replace("\\", "/").split("/")[:-1]
    skip = {"webapp", "web", "src", "main", "java", "resources", "sql",
            "batch", "scripts", "WEB-INF", "views", "jsp", "pages"}
    # 순서: ①구조 디렉터리 제거 → ②base 패키지 prefix 제거 → ③역할 세그먼트 제거
    parts = [p for p in parts if p and p not in skip]
    if base_prefix and parts[: len(base_prefix)] == base_prefix:
        parts = parts[len(base_prefix):]
    return [p for p in parts if p.lower() not in ROLE_SEGMENTS]


def scan_workspace(root: str, base_package: str | None = None) -> dict:
    root = os.path.abspath(root)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(SCAN_EXTS):
                files.append(os.path.join(dirpath, fn))
    files.sort()

    # 1차 패스: 파일별 원시 메타 수집
    raw = []
    for full in files:
        rel = os.path.relpath(full, root).replace("\\", "/")
        try:
            text = _read_text(full)
        except OSError:
            continue
        cls = classify(rel, text)
        entry = {"rel": rel, "full": full, "text_len": len(text), **cls}

        if cls["impl_type"] == "Java" or rel.lower().endswith(".java"):
            entry["java"] = parse_java(text)
        if cls["program_type"] == "Mapper" and rel.lower().endswith(".xml"):
            entry["mybatis"] = parse_mybatis(text)
        if rel.lower().endswith(".sql"):
            entry["tables"] = extract_tables(text)
        raw.append(entry)

    # base package prefix 추정
    packages = [e["java"]["package"] for e in raw if e.get("java")]
    base_prefix = base_package.split(".") if base_package else _common_package_prefix(packages)

    # 인덱스: 클래스명 → rel, 매퍼 namespace → rel
    class_index = {}
    ns_index = {}
    for e in raw:
        if e.get("java") and e["java"]["class"]:
            class_index.setdefault(e["java"]["class"], e["rel"])
        if e.get("mybatis") and e["mybatis"]["namespace"]:
            ns_index[e["mybatis"]["namespace"]] = e["rel"]

    # 컨트롤러 URL prefix 인덱스 (JSP 연결용)
    controller_urls = []
    for e in raw:
        if e["program_type"] == "Controller" and e.get("java"):
            for u in e["java"]["url_mappings"]:
                controller_urls.append((u, e["rel"]))

    edges = []

    # 2차 패스: 프로그램 엔트리 + 호출관계
    programs = []
    for e in raw:
        rel = e["rel"]
        fname = rel.split("/")[-1]
        java = e.get("java")
        mb = e.get("mybatis")

        # 업무분류/레벨 추정
        if java and java["package"]:
            dom = _domain_segments(java["package"], base_prefix)
        else:
            dom = _path_domain(rel, base_prefix)
        biz = dom[0] if dom else ""
        level1 = dom[1] if len(dom) > 1 else ""
        level2 = dom[2] if len(dom) > 2 else ""

        # 프로그램명(제안): 클래스명 또는 파일명
        if java and java["class"]:
            pname = java["class"]
        else:
            pname = fname.rsplit(".", 1)[0]

        # 대상 테이블
        tables = []
        if mb:
            tables = mb["tables"]
        elif e.get("tables"):
            tables = e["tables"]

        # 비고(제안): 주석 요약 + 테이블/URL 힌트
        remark_parts = []
        if java and java["doc_summary"]:
            remark_parts.append(java["doc_summary"])
        if tables:
            remark_parts.append("[테이블] " + ", ".join(tables))
        if java and java["url_mappings"]:
            remark_parts.append("[URL] " + ", ".join(java["url_mappings"]))
        remark = " / ".join(remark_parts)

        programs.append({
            # ── 산출물 컬럼(제안값) ──
            "biz_category": biz,
            "program_level1": level1,
            "program_level2": level2,
            "program_level3": "",
            "program_name": pname,
            "priority": "",
            "program_type": e["program_type"],
            "impl_type": e["impl_type"],
            "path": "/" + "/".join(rel.split("/")[:-1]),
            "file_name": fname,
            "change_type": "",
            "remark": remark,
            "manager": "",
            # ── 분석 지원 메타(LLM/흐름도용, 산출물 컬럼 아님) ──
            "_layer": e["layer"],
            "_class": java["class"] if java else "",
            "_package": java["package"] if java else "",
            "_methods": java["methods"] if java else (
                [s["id"] for s in mb["statements"]] if mb else []),
            "_url_mappings": java["url_mappings"] if java else [],
            "_tables": tables,
            "_doc": java["doc_summary"] if java else "",
        })

        # 호출관계 edge: 자바 타입 참조
        if java:
            for ref in java["type_refs"]:
                target = class_index.get(ref)
                if target and target != rel:
                    edges.append({"from": rel, "to": target, "kind": "calls"})
            # 매퍼 인터페이스 → MyBatis XML
            fqcn = f"{java['package']}.{java['class']}" if java["package"] else java["class"]
            if fqcn in ns_index and ns_index[fqcn] != rel:
                edges.append({"from": rel, "to": ns_index[fqcn], "kind": "maps"})

        # JSP → Controller (form action / href URL 매칭)
        if e["program_type"] == "JSP":
            text_lower = None
            for url, cfile in controller_urls:
                if not url:
                    continue
                # 간단 매칭: URL 문자열이 JSP 본문에 등장하면 연결로 간주
                if text_lower is None:
                    text_lower = _read_text(e["full"])
                if url in text_lower:
                    edges.append({"from": rel, "to": cfile, "kind": "requests"})

    # 업무분류 미상 파일(배치/SQL 등)은 파일명에 등장하는 알려진 업무분류로 보완
    known_biz = {p["biz_category"] for p in programs if p["biz_category"]}
    for p in programs:
        if p["biz_category"]:
            continue
        hay = (p["file_name"] + " " + p["program_name"]).lower()
        for kb in sorted(known_biz, key=len, reverse=True):
            if kb.lower() in hay:
                p["biz_category"] = kb
                p["remark"] = (p["remark"] + " " if p["remark"] else "") + "[업무분류 추정: 파일명 기준]"
                break

    # edge 중복 제거 (순서 유지)
    seen = set()
    deduped = []
    for e in edges:
        key = (e["from"], e["to"], e["kind"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)
    edges = deduped

    # 클러스터: 업무분류 기준 그룹
    clusters = {}
    for p in programs:
        clusters.setdefault(p["biz_category"] or "(미분류)", []).append(p["file_name"])

    # 요약
    by_type = {}
    all_tables = set()
    for p in programs:
        by_type[p["program_type"]] = by_type.get(p["program_type"], 0) + 1
        all_tables.update(p["_tables"])

    return {
        "root": root,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_package": ".".join(base_prefix),
        "summary": {
            "file_count": len(programs),
            "by_type": by_type,
            "tables": sorted(all_tables),
            "clusters": {k: len(v) for k, v in clusters.items()},
        },
        "programs": programs,
        "edges": edges,
    }
