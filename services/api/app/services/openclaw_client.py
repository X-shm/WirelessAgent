"""OpenClaw Agent client — OpenAI-compatible API wrapper with SSE streaming."""
import asyncio
import json
import httpx
from app.config import settings


class OpenClawClient:
    """Async client for OpenClaw's OpenAI-compatible chat API."""

    def __init__(self):
        self.base_url = settings.openclaw_base_url.rstrip("/")
        self.api_key = settings.openclaw_api_key
        self.model = settings.openclaw_model
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_messages(self, history: list[dict], system_prompt: str | None = None) -> list[dict]:
        """Build the messages payload from conversation history."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        return messages

    async def chat(self, messages: list[dict], system_prompt: str | None = None, user_id: str | None = None, model: str | None = None, api_base_url: str | None = None, api_key: str | None = None, tools: list[dict] | None = None, tool_choice: str | dict | None = None, **kwargs) -> dict:
        """Send a non-streaming chat completion request."""
        base_url = (api_base_url or self.base_url).rstrip("/")
        request_key = api_key or self.api_key
        request_headers = {"Authorization": f"Bearer {request_key}", "Content-Type": "application/json"}
        payload = {
            "model": model or self.model,
            "messages": self._build_messages(messages, system_prompt),
            "stream": False,
            **kwargs,
        }
        if user_id:
            payload["user"] = user_id
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", headers=request_headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(self, messages: list[dict], system_prompt: str | None = None, user_id: str | None = None, model: str | None = None, api_base_url: str | None = None, api_key: str | None = None, tools: list[dict] | None = None, tool_choice: str | dict | None = None, **kwargs):
        """Stream chat completion via an optional OpenAI-compatible override. Yields each token delta string."""
        base_url = (api_base_url or self.base_url).rstrip("/")
        request_key = api_key or self.api_key
        request_headers = {"Authorization": f"Bearer {request_key}", "Content-Type": "application/json"}
        payload = {
            "model": model or self.model,
            "messages": self._build_messages(messages, system_prompt),
            "stream": True,
            **kwargs,
        }
        if user_id:
            payload["user"] = user_id
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        max_attempts = 2
        for attempt in range(max_attempts):
            yielded = False
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream("POST", f"{base_url}/chat/completions", headers=request_headers, json=payload) as resp:
                        resp.raise_for_status()
                        async for line in resp.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yielded = True
                                        yield content
                                except json.JSONDecodeError:
                                    continue
                return
            except Exception:
                if yielded or attempt >= max_attempts - 1:
                    raise
                await asyncio.sleep(0.5)


# Singleton
openclaw = OpenClawClient()
