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

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)

    if update.message and update.message.text:
        user_text = update.message.text

        result = agent.invoke({"messages": [HumanMessage(content=user_text)]})
        # result is a final state
        reply = result["messages"][-1]

        await bot.send_message(
            chat_id=update.message.chat_id,
            text=reply.content
        )

    return {"ok": True}
