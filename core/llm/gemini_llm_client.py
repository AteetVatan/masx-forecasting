"""Gemini Implementation"""

import os
import re
import google.generativeai as genai
from typing import List
import json
import json5
from .enums.llm_model import LLMModel
from .llm_client import LLMClient

# ============================
# Gemini Implementation
# ============================  

class GeminiLLMClient(LLMClient):
    def __init__(self, model: LLMModel = LLMModel.GEMINI_PRO, max_tokens: int = 3000, temperature: float = 0.3):
        super().__init__(model, max_tokens, temperature)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_obj = genai.GenerativeModel(model.value)

    def call(self, prompt: str, system_prompt: str = None) -> str:        
        full_prompt = f"{system_prompt.strip()}\n\n{prompt}" if system_prompt else prompt
        response = self.model_obj.generate_content(full_prompt)
        return response.text

    def call_batch(self, batch_texts: List[str], embedded_prompt: str, system_prompt: str = None) -> List[dict]:
        combined_prompt = embedded_prompt + "\n\n" + "\n\n".join(batch_texts)
        raw_text = self.call(combined_prompt, system_prompt=system_prompt)

        extracted_json = GeminiLLMClient.extract_json_array(raw_text)
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
