"""Java 소스에서 메타정보를 정규식으로 추출.

완전한 파서가 아니라 필요한 신호(패키지/클래스/애노테이션/URL매핑/메서드/참조타입)만
견고하게 뽑는다. 컴파일 불가능한 레거시 코드에서도 동작하는 것이 목표다.
"""
import re

_PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)
_CLASS = re.compile(r"\b(?:class|interface|enum)\s+([A-Z]\w*)")
_REQ_MAPPING = re.compile(r'@(?:Request|Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"')
_METHOD = re.compile(
    r"\bpublic\s+(?:static\s+)?(?:final\s+)?[\w<>\[\],.\s]+?\s+([a-z]\w*)\s*\([^)]*\)\s*(?:throws[\w,\s]+)?\{"
)
_IFACE_METHOD = re.compile(r"\b[\w<>\[\],.\s]+?\s+([a-z]\w*)\s*\([^)]*\)\s*;")
_TYPE_REF = re.compile(r"\b([A-Z][A-Za-z0-9]+(?:Service|Mapper|DAO|Dao|Repository))\b")


def _block_comment_summary(text: str, class_pos: int) -> str:
    """클래스 선언 직전의 블록주석 첫 문장을 업무 힌트로 추출."""
    head = text[:class_pos]
    comments = re.findall(r"/\*\*?(.*?)\*/", head, re.DOTALL)
    if not comments:
        return ""
    last = comments[-1]
    lines = [re.sub(r"^\s*\*?\s?", "", ln).strip() for ln in last.splitlines()]
    body = " ".join(ln for ln in lines if ln and not ln.startswith("@"))
    if not body:
        return ""
    # 첫 문장(마침표/。기준)
    m = re.split(r"(?<=[.。])\s", body, maxsplit=1)
    return m[0].strip()[:200]


def parse_java(text: str) -> dict:
    pkg_m = _PACKAGE.search(text)
    package = pkg_m.group(1) if pkg_m else ""

    cls_m = _CLASS.search(text)
    class_name = cls_m.group(1) if cls_m else ""
    class_pos = cls_m.start() if cls_m else 0

    is_interface = bool(re.search(r"\binterface\s+" + re.escape(class_name), text)) if class_name else False

    urls = _REQ_MAPPING.findall(text)

    if is_interface:
        methods = _IFACE_METHOD.findall(text)
    else:
        methods = _METHOD.findall(text)
    # 흔한 오탐 제거
    methods = [m for m in dict.fromkeys(methods) if m not in ("if", "for", "while", "switch", "catch", "new")]

    refs = sorted(set(_TYPE_REF.findall(text)))
    if class_name in refs:
        refs.remove(class_name)

    return {
        "package": package,
        "class": class_name,
        "is_interface": is_interface,
        "url_mappings": urls,
        "methods": methods[:40],
        "type_refs": refs,
        "doc_summary": _block_comment_summary(text, class_pos),
    }
