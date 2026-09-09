"""파일을 프로그램유형/구현유형/계층으로 분류한다.

program_type 값은 PPT 호출흐름(app/exporters/pptx.py의 LAYERS) 키워드와 맞춰
분류 결과가 그대로 흐름도 계층에 매핑되도록 한다.
"""
import re

# 계층(layer): 호출 흐름 순서와 클러스터 구조에 사용
LAYER_ORDER = ["화면", "Controller", "Service", "DAO", "Mapper", "Batch", "DB", "기타"]


def classify(rel_path: str, text: str) -> dict:
    """(program_type, impl_type, layer) 반환."""
    lower = rel_path.lower()
    fname = rel_path.replace("\\", "/").split("/")[-1]
    base = fname.rsplit(".", 1)[0]

    # 확장자 우선 규칙
    if lower.endswith(".jsp") or lower.endswith(".jspf"):
        return {"program_type": "JSP", "impl_type": "화면(JSP)", "layer": "화면"}
    if lower.endswith((".sh", ".bat", ".ksh")):
        return {"program_type": "Batch", "impl_type": "Shell", "layer": "Batch"}
    if lower.endswith(".sql"):
        return {"program_type": "SQL/DDL", "impl_type": "SQL", "layer": "DB"}
    if lower.endswith(".xml"):
        if "<mapper" in text and "namespace" in text:
            return {"program_type": "Mapper", "impl_type": "MyBatis", "layer": "Mapper"}
        return {"program_type": "XML", "impl_type": "XML", "layer": "기타"}

    if lower.endswith(".java"):
        return _classify_java(base, text)

    return {"program_type": "기타", "impl_type": "", "layer": "기타"}


def _classify_java(base: str, text: str) -> dict:
    has = lambda ann: re.search(r"@" + ann + r"\b", text) is not None  # noqa: E731

    if has("RestController") or has("Controller"):
        return {"program_type": "Controller", "impl_type": "Java", "layer": "Controller"}
    if has("Service"):
        return {"program_type": "Service", "impl_type": "Java", "layer": "Service"}
    if has("Repository"):
        return {"program_type": "DAO", "impl_type": "Java", "layer": "DAO"}
    if has("Mapper") or (re.search(r"\binterface\b", text) and base.endswith("Mapper")):
        return {"program_type": "Mapper", "impl_type": "Java", "layer": "Mapper"}

    # 애노테이션이 없을 때 파일명 규칙으로 보완 (레거시/비-Spring)
    name_rules = [
        ("Controller", "Controller", "화면", "Controller"),
        ("Service", "Service", "Service", "Service"),
        ("ServiceImpl", "Service", "Service", "Service"),
        ("DAO", "DAO", "DAO", "DAO"),
        ("Dao", "DAO", "DAO", "DAO"),
        ("Mapper", "Mapper", "Mapper", "Mapper"),
        ("VO", "VO/DTO", "Java", "기타"),
        ("DTO", "VO/DTO", "Java", "기타"),
        ("Dto", "VO/DTO", "Java", "기타"),
        ("Job", "Batch", "Java", "Batch"),
        ("Batch", "Batch", "Java", "Batch"),
        ("Config", "Config", "Java", "기타"),
        ("Util", "Util", "Java", "기타"),
        ("Utils", "Util", "Java", "기타"),
    ]
    for suffix, ptype, impl, layer in name_rules:
        if base.endswith(suffix):
            return {"program_type": ptype, "impl_type": impl, "layer": layer}

    return {"program_type": "Java", "impl_type": "Java", "layer": "기타"}
