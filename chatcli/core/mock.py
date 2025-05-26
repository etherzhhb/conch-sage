def mock_llm_response(prompt: str) -> str:
    return f"[MOCK LLM RESPONSE]\nPrompt received:\n{prompt[:300]}..."
