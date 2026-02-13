from __future__ import annotations
from typing import Dict, Any, List
import json
import requests

class LLMBase:
    def chat_json(self, system: str, user: str, schema_hint: str) -> Dict[str, Any]:
        raise NotImplementedError
    def chat_text(self, system: str, user: str) -> str:
        raise NotImplementedError

class OllamaLLM(LLMBase):
    def __init__(self, base_url: str, model: str, timeout_sec: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_sec = timeout_sec

    def _chat(self, messages: List[Dict[str,str]], format_json: bool) -> str:
        url = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {"model": self.model, "messages": messages, "stream": False}
        if format_json:
            payload["format"] = "json"
        r = requests.post(url, json=payload, timeout=self.timeout_sec)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")

    def chat_json(self, system: str, user: str, schema_hint: str) -> Dict[str, Any]:
        content = self._chat(
            [{"role":"system","content": system + "\n\nJSON SCHEMA HINT:\n" + schema_hint},
             {"role":"user","content": user}],
            format_json=True,
        )
        content = content.strip().strip("```").strip()
        return json.loads(content)

    def chat_text(self, system: str, user: str) -> str:
        return self._chat([{"role":"system","content": system}, {"role":"user","content": user}], format_json=False)

class OpenAILLM(LLMBase):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        self.model = model

    def chat_text(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

    def chat_json(self, system: str, user: str, schema_hint: str) -> Dict[str, Any]:
        prompt = user + "\n\n반드시 JSON만 출력하세요. 다른 텍스트/코드블록 금지."
        text = self.chat_text(system + "\n\nJSON SCHEMA HINT:\n" + schema_hint, prompt)
        text = text.strip().strip("```").strip()
        return json.loads(text)
