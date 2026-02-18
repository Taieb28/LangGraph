# main.py
import logging
from fastapi import FastAPI, Request
from telegram import Bot, Update
from langchain_core.messages import HumanMessage, AIMessage
from agent import agent 
import os

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
        logging.info(f"Received update: {data}")
        
        update = Update.de_json(data, bot)
        
        if update.message and update.message.text:
            user_text = update.message.text
            chat_id = update.message.chat_id

            result = await agent.ainvoke({"messages": [HumanMessage(content=user_text)]})
            # إرسال الرد
            await bot.send_message(
                chat_id=chat_id,
                text=extract_ai_reply(result["messages"])
            )

        return {"ok": True}
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)  
        return {"ok": False, "error": str(e)}
    
def extract_ai_reply(messages):
    for message in reversed(messages):
        if not isinstance(message, AIMessage):
            continue 
        # معالجة النص المباشر
        if isinstance(message.content, str) and message.content.strip():
            return message.content
            
        # معالجة القائمة (Gemini Style)
        if isinstance(message.content, list):
            for part in message.content:
                if isinstance(part, dict) and part.get("type") == "text":
                    return part.get("text", "")
    return "نعتذر لم اتلقى اي رد من النموذج"