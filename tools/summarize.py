def cheap_summarize(text: str, max_len: int = 120) -> str:
    """LLM을 안 쓰는 가짜 요약기(드라이런 전용). 임포트해도 아무 동작 안 함."""
    s = " ".join(text.split())
    return (s[:max_len] + "…") if len(s) > max_len else s