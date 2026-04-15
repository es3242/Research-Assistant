from dotenv import load_dotenv

load_dotenv()


def build_llm(provider: str = "ollama", model: str | None = None, temperature: float = 0):
    provider = provider.lower().strip()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model or "llama3.1:8b",
            temperature=temperature,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.5-flash",
            temperature=temperature,
        )

    raise ValueError(f"Unsupported provider: {provider}")