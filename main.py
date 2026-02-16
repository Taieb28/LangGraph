# main.py
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Application
import os
from agent import agent

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}
	
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)

    if update.message and update.message.text:
        user_text = update.message.text
		# result is a final state
        result = agent.invoke({"messages": [HumanMessage(content=user_text)]})
		reply = ""
		for message in reversed(result["messages"]):
			if isinstance(message, AIMessage) and message.content:
				reply = message.content
				break

        await bot.send_message(
            chat_id=update.message.chat_id,
            text=reply
        )

    return {"ok": True}
