"""SQL / MyBatis XML에서 대상 테이블과 statement를 추출."""
import re

# FROM/JOIN/INTO/UPDATE/DELETE FROM 뒤의 테이블명
_TABLE_PATTERNS = [
    re.compile(r"\bFROM\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
    re.compile(r"\bJOIN\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
    re.compile(r"\bINTO\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
    re.compile(r"\bUPDATE\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
    re.compile(r"\bCREATE\s+TABLE\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
    re.compile(r"\bALTER\s+TABLE\s+([A-Za-z_][\w$]*)", re.IGNORECASE),
]

# SQL 키워드 오탐 제거용
_STOP = {
    "SELECT", "WHERE", "SET", "VALUES", "AND", "OR", "ON", "AS", "DUAL",
    "TABLE", "FROM", "INTO", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
}
_MYBATIS_STMT = re.compile(
    r"<(select|insert|update|delete)\b[^>]*\bid\s*=\s*\"([^\"]+)\"", re.IGNORECASE
)
_MYBATIS_NS = re.compile(r"<mapper\b[^>]*\bnamespace\s*=\s*\"([^\"]+)\"", re.IGNORECASE)


def extract_tables(sql_text: str) -> list:
    found = []
    for pat in _TABLE_PATTERNS:
        for name in pat.findall(sql_text):
            up = name.upper()
            if up not in _STOP and not up.startswith("("):
                found.append(up)
    # 중복 제거(순서 유지)
    return list(dict.fromkeys(found))


def parse_mybatis(text: str) -> dict:
    ns_m = _MYBATIS_NS.search(text)
    statements = [
        {"kind": kind.lower(), "id": sid} for kind, sid in _MYBATIS_STMT.findall(text)
    ]
    # XML 태그(<update id=...> 등)를 제거해 SQL 본문에서만 테이블을 추출한다.
    # 그렇지 않으면 <update>/<delete> 태그가 UPDATE/DELETE 문으로 오인된다.
    sql_body = re.sub(r"<[^>]+>", " ", text)
    return {
        "namespace": ns_m.group(1) if ns_m else "",
        "statements": statements,
        "tables": extract_tables(sql_body),
    }
