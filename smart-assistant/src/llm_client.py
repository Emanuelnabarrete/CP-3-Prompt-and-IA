import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "gpt-oss:120b")


class LLMClient:

    def chat(self, prompt: str, system: str = "", temperature: float = 0.3,
             max_tokens: int = 512, history: list = None) -> dict:

        url = f"{OLLAMA_HOST}/api/chat"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        start_time = time.time()

        try:
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            answer = data["message"]["content"].strip()
        except Exception as error:
            answer = f"ERROR: {error}"

        end_time = time.time()

        return {
            "answer": answer,
            "time_ms": round((end_time - start_time) * 1000, 2)
        }
