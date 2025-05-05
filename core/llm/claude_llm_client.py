"""Claude Implementation"""

import os
import httpx
import re
import json
import time
from typing import List
from core.llm.llm_client import LLMClient
from core.llm.enums.llm_model import LLMModel
import json5

#claude-3-opus-20240229 best for chunking but costly
#claude-3-7-sonnet-20250219 claude-3-5-sonnet-20241022
# ============================
# Claude Implementation
# ============================
class ClaudeLLMClient(LLMClient):
    def __init__(self, model: LLMModel = LLMModel.CLAUDE_SONNET_5, max_tokens: int = 3000, temperature: float = 0.3):
        super().__init__(model, max_tokens, temperature)
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.api_url = os.getenv("CLAUDE_URL")
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

    def _prepare_prompt(self, batch_texts: List[str], embedded_prompt: str) -> str:
        combined = "".join([f"Chunk {i+1}:\n{chunk}\n\n" for i, chunk in enumerate(batch_texts)])
        return f"{embedded_prompt}\n\n{combined}"
    
    def call(self, prompt: str, system_prompt: str = None) -> str:
        combined_prompt = f"{system_prompt.strip()}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "model": self.model.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": combined_prompt}
            ]
        }
        response = httpx.post(self.api_url, headers=self.headers, json=payload, timeout=60)
        return response.json()["content"][0]["text"]


    def call_batch(self, batch_texts: List[str], embedded_prompt: str, system_prompt: str = None) -> List[dict]:
        prompt = self._prepare_prompt(batch_texts, embedded_prompt)
        combined_prompt = f"{system_prompt.strip()}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "model": self.model.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": combined_prompt}
            ]
        }

        response = httpx.post(self.api_url, headers=self.headers, json=payload, timeout=60)
        response.raise_for_status()
        raw_text = response.json()["content"][0]["text"]               

    
        extracted_json = ClaudeLLMClient.extract_json_array(raw_text)
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


    # def _extract_chunks_from_text(self, text: str) -> List[dict]:
    #     match = re.search(r"(\[\s*{.*?}\s*\])", text, re.DOTALL)
    #     if not match:
    #         print("❌ No JSON array found in Claude response")
    #         print("Raw:", text[:500])
    #         raise ValueError("Invalid Claude output: missing JSON array")

    #     try:
    #         return json.loads(match.group(1))
    #     except json.JSONDecodeError as e:
    #         print("❌ JSON decode failed:", e)
    #         print("Extracted:", match.group(1)[:500])
    #         raise
