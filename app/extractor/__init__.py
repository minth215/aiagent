"""소스 워크스페이스 결정적 추출기.

LLM 없이 파일을 스캔하여 프로그램 목록·대상 테이블·호출관계를 뽑아낸다.
정규식 기반이라 컴파일되지 않는 레거시 코드에서도 견고하게 동작한다.
"""
from app.extractor.scan import scan_workspace  # noqa: F401
