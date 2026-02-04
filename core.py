from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class Message(BaseModel):
    user: str
    text: str

@app.post("/message")
async def reply_message(msg: Message):
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a WhatsApp store assistant. "
                    "Reply in 1–2 short sentences. "
                    "No emojis. "
                    "No examples or menus. "
                    "Answer only what is asked. "
                    "If info is missing, ask one short question. "
                    "Never use line breaks."
                )
            },
            {
                "role": "user",
                "content": msg.text
            }
        ],
        temperature=0.1
    )

    reply = response.choices[0].message.content.replace("\n", " ").strip()
    return {"reply": reply}

@app.get("/")
async def root():
    return {"status": "AI Agent running"}
print(os.getenv("OPENROUTER_API_KEY") is not None)
