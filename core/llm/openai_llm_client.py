from openai import OpenAI
import os
from typing import List
import json
import re
from .enums.llm_model import LLMModel


class OpenAILLMClient:
    def __init__(
        self,
        model: LLMModel = LLMModel.GPT_4,
        max_tokens: int = 3000,
        temperature: float = 0.3,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def call(self, prompt: str, system_prompt: str = None) -> str:
        system_prompt = system_prompt or "You are a helpful assistant."
        response = self.client.chat.completions.create(
            model=self.model.value,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

    def call_batch(
        self, batch_texts: List[str], embedded_prompt: str, system_prompt: str = None
    ) -> List[dict]:
        prompt = embedded_prompt + "\n\n" + "\n\n".join(batch_texts)
        raw_text = self.call(prompt, system_prompt)
        match = re.search(r"(\[\s*{.*?}\s*\])", raw_text, re.DOTALL)
        if not match:
            # raise ValueError("❌ Could not extract JSON chunk array from Groq response.")
            return {"type": "", "response": raw_text}
        return {"type": "json", "response": json.loads(match.group(1))}
