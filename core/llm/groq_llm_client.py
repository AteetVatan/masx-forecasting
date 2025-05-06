"""Groq (Mistral) Implementation"""

import os
import re
import httpx
import json
from typing import List
from .enums.llm_model import LLMModel
from .llm_client import LLMClient
import json5

# ============================
# Groq Implementation
# ============================


class GroqLLMClient(LLMClient):
    def __init__(
        self,
        model: LLMModel = LLMModel.MIXTRAL,
        max_tokens: int = 3000,
        temperature: float = 0.3,
    ):
        super().__init__(model, max_tokens, temperature)
        self.api_key = os.getenv("GROQ_API_KEY")

    def call(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        # Insert system prompt if available
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = httpx.post(
            url=os.getenv("GROQ_URL"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model.value,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
        )
        return response.json()["choices"][0]["message"]["content"]

    def call_batch(
        self, batch_texts: List[str], embedded_prompt: str, system_prompt: str = None
    ) -> List[dict]:
        prompt = embedded_prompt + "\n\n" + "\n\n".join(batch_texts)
        raw_text = self.call(prompt, system_prompt=system_prompt)

        extracted_json = GroqLLMClient.extract_json_array(raw_text)
        if not extracted_json:
            return {"type": "text", "response": raw_text}  # fallback

        return {"type": "json", "response": extracted_json}

    @staticmethod
    def extract_json_array(text: str):
        try:
            # First try to extract strict JSON array
            match = re.search(r"(\[\s*{.*?}\s*\])", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Try extracting code block version (```json ... ```)
            match = re.search(r"```json(.*?)```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

        # Try using json5 as fallback (accepts trailing commas, etc.)
        try:
            return json5.loads(text)
        except Exception:
            return None
