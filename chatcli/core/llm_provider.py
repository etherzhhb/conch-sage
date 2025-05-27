from chatcli.core.config import load_config

# Optional: langchain_ollama is required for OllamaProvider
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    OllamaLLM = None


class LLMProvider:
    def ask(self, prompt: str) -> str:
        raise NotImplementedError()

    def ask_with_context(self, context: str, prompt: str) -> str:
        return self.ask(context + "\n\n" + prompt)


class MockProvider(LLMProvider):
    def __init__(self):
        config = load_config()
        self.response = config.get("mock_response", "[MOCK] Default mock response.")

    def ask(self, prompt: str) -> str:
        return self.response

    def ask_with_context(self, context: str, prompt: str) -> str:
        return f"{self.response}\n\n[Context was]: {context} [Prompt was]: {prompt}"


class OllamaProvider(LLMProvider):
    def __init__(self, model: str):
        if OllamaLLM is None:
            raise ImportError("Please install langchain_ollama: pip install langchain_ollama")
        self.llm = OllamaLLM(model=model)

    def ask(self, prompt: str) -> str:
        return self.llm(prompt)


def get_llm() -> LLMProvider:
    config = load_config()
    provider = config.get("provider", "mock")
    print(f"using provider: {provider}")

    if provider == "ollama":
        return OllamaProvider(config.get("ollama_model", "mistral"))
    elif provider == "mock":
        return MockProvider()
    else:
        raise NotImplementedError(f"LLM provider '{provider}' is not implemented yet.")
