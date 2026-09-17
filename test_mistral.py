import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

import os
import time
from langchain_mistralai import ChatMistralAI

print("API key exists:", bool(os.getenv("MISTRAL_API_KEY")))

model_name = os.getenv("MISTRAL_MODEL", "ministral-8b-latest")
print(f"Using model: {model_name}")

llm = ChatMistralAI(
    model=model_name,
    mistral_api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.2
)

try:
    response = llm.invoke("Say hello in one short sentence.")
    print("SUCCESS:")
    print(response.content)

except Exception as e:
    print("ERROR:")
    print(e)
