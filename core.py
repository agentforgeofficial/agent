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

# Session memory dictionary
memory = {}

MAX_MEMORY = 5  # keep last 5 messages per user

@app.post("/message")
async def reply_message(msg: Message):
    user_id = msg.user
    user_message = msg.text.strip()

    # Get previous conversation or empty list
    conversation = memory.get(user_id, [])

    # Append current user message
    conversation.append({"role": "user", "content": user_message})

    # Trim memory to last MAX_MEMORY messages
    conversation = conversation[-MAX_MEMORY:]

    # Build messages for the API
    messages = [
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
        }
    ] + conversation

    # Get OpenAI response
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=messages,
        temperature=0.1
    )

    reply = response.choices[0].message.content.replace("\n", " ").strip()

    # Append bot reply to conversation memory
    conversation.append({"role": "assistant", "content": reply})
    conversation = conversation[-MAX_MEMORY:]  # trim again after adding reply
    memory[user_id] = conversation  # update memory

    return {"reply": reply}

@app.get("/")
async def root():
    return {"status": "AI Agent running"}
from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # you invent this

@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return "Verification failed"

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            if "message" in event and "text" in event["message"]:
                text = event["message"]["text"]

                reply_text = "Got it."  # later replaced by your AI reply

                requests.post(
                    "https://graph.facebook.com/v18.0/me/messages",
                    params={"access_token": PAGE_ACCESS_TOKEN},
                    json={
                        "recipient": {"id": sender_id},
                        "message": {"text": reply_text},
                    },
                )

    return {"status": "ok"}
