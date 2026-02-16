# main.py
from fastapi import FastAPI, Request
from telegram import Bot, Update
import os
from langchain_core.messages import HumanMessage, AIMessage
from agent import agent 

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}
    
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        # تحويل البيانات القادمة من تليجرام إلى كائن Update
        update = Update.de_json(data, bot)

        if update.message and update.message.text:
            user_text = update.message.text
            chat_id = update.message.chat_id

            # استخدام ainvoke بدلاً من invoke لأنه أفضل مع FastAPI
            result = await agent.ainvoke({"messages": [HumanMessage(content=user_text)]})
            
            reply = "نعتذر، لم أتمكن من صياغة رد حالياً." 
            
            for message in reversed(result["messages"]):
                if isinstance(message, AIMessage) and message.content:
                    reply = message.content
                    break

            # إرسال الرد
            await bot.send_message(
                chat_id=chat_id,
                text=reply
            )

        return {"ok": True}
    except Exception as e:
        print(f"Error: {e}")
        return {"ok": False, "error": str(e)}