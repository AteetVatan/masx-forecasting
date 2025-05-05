"""Cohere Implementation"""
import os
import re
import cohere
from typing import List
import json
from .enums.llm_model import LLMModel
from .llm_client import LLMClient

class CohereLLMClient(LLMClient):
    def __init__(self, model: LLMModel = LLMModel.COMMAND_R_PLUS, max_tokens: int = 3000, temperature: float = 0.3):
        super().__init__(model, max_tokens, temperature)
        self.client = cohere.Client(os.getenv("COHERE_API_KEY"))

    def call(self, prompt: str, system_prompt: str = None) -> str:
        response = self.client.chat(
            message=prompt,
            model=self.model.value,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            preamble=system_prompt or ""  # Injects the system-level intent
        )
        return response.text

    def call_batch(self, batch_texts: List[str], embedded_prompt: str, system_prompt: str = None) -> List[dict]:
        prompt = embedded_prompt + "\n\n" + "\n\n".join(batch_texts)
        raw_text = self.call(prompt, system_prompt=system_prompt)

        match = re.search(r"(\[\s*{.*?}\s*\])", raw_text, re.DOTALL)
        if not match:
            #raise ValueError("❌ Could not extract JSON chunk array from Groq response.")
            return {"type":"", "response": raw_text}
        return {"type":"json", "response": json.loads(match.group(1))}