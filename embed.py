"""Embedding provider abstraction — OpenAI with Ollama fallback."""

import os
import json
import urllib.request
import urllib.error
from typing import Optional


def _openai_embed(texts: list[str], api_key: str, model: str = "text-embedding-3-small") -> list[list[float]]:
    """Get embeddings from OpenAI API."""
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps({"input": texts, "model": model}).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return [item["embedding"] for item in data["data"]]


def _ollama_embed(texts: list[str], base_url: str, model: str = "nomic-embed-text") -> list[list[float]]:
    """Get embeddings from Ollama API."""
    req = urllib.request.Request(
        f"{base_url}/api/embed",
        data=json.dumps({"model": model, "input": texts}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "neo4j-recall/1.0"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["embeddings"]


def embed(texts: list[str], provider: Optional[str] = None) -> list[list[float]]:
    """Embed texts using configured provider, with automatic fallback.

    Priority: explicit provider arg > EMBEDDING_PROVIDER env > openai > ollama
    """
    provider = provider or os.getenv("EMBEDDING_PROVIDER", "openai")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        try:
            return _openai_embed(texts, api_key, model)
        except urllib.error.URLError:
            # Fallback to ollama
            print("[recall] OpenAI unreachable, falling back to Ollama")
            return _ollama_fallback(texts)

    elif provider == "ollama":
        return _ollama_fallback(texts)

    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


def _ollama_fallback(texts: list[str]) -> list[list[float]]:
    base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.aga.my")
    model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    return _ollama_embed(texts, base_url, model)


def dimensions(provider: Optional[str] = None) -> int:
    """Return embedding dimensions for the active provider."""
    provider = provider or os.getenv("EMBEDDING_PROVIDER", "openai")
    if provider == "openai":
        return 1536
    return 768  # nomic-embed-text default


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    vecs = embed(["test memory about Malaysian politics"])
    print(f"Provider: {os.getenv('EMBEDDING_PROVIDER', 'openai')}")
    print(f"Dimensions: {len(vecs[0])}")
    print(f"First 5 values: {vecs[0][:5]}")
