"""Ollama LLM client wrapper with streaming support."""

import json
from typing import AsyncGenerator

import httpx

from app.core.config import settings


class LLMService:
    """HTTP client for Ollama API with streaming support."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.sql_model = getattr(settings, "SQL_MODEL", "sqlcoder")
        self.answer_model = getattr(settings, "ANSWER_MODEL", "llama3.1:8b")
        self.api_key = getattr(settings, "LLM_API_KEY", None)
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    def _is_openai_format(self):
        return bool(self.api_key)

    async def generate(
        self, prompt: str, model: str | None = None, system: str = ""
    ) -> str:
        """Generate a complete response (non-streaming)."""
        model = model or self.answer_model
        headers = {}
        
        if self._is_openai_format():
            url = f"{self.base_url}/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ] if system else [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "stream": False
            }
        else:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 1024},
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if self._is_openai_format():
                return data["choices"][0]["message"]["content"]
            return data.get("response", "")

    async def generate_stream(
        self, prompt: str, model: str | None = None, system: str = ""
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from the LLM one at a time."""
        model = model or self.answer_model
        headers = {}

        if self._is_openai_format():
            url = f"{self.base_url}/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ] if system else [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "stream": True
            }
        else:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": True,
                "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 1024},
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                        
                    if self._is_openai_format():
                        if line == "data: [DONE]":
                            break
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                token = data["choices"][0]["delta"].get("content", "")
                                if token:
                                    yield token
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                    else:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    async def generate_sql(self, prompt: str) -> str:
        """Generate SQL using SQLCoder model."""
        return await self.generate(prompt, model=self.sql_model)

    async def generate_answer(
        self, prompt: str, system: str = ""
    ) -> str:
        """Generate natural language answer using Llama 3.1."""
        return await self.generate(prompt, model=self.answer_model, system=system)

    async def stream_answer(
        self, prompt: str, system: str = ""
    ) -> AsyncGenerator[str, None]:
        """Stream natural language answer tokens."""
        async for token in self.generate_stream(
            prompt, model=self.answer_model, system=system
        ):
            yield token

    async def check_health(self) -> bool:
        """Check if Ollama is running and models are available."""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# Singleton instance
llm_service = LLMService()
