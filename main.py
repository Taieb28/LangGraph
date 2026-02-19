# main.py
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from telegram import Bot, Update
from apify_client import ApifyClient
from langchain_core.messages import HumanMessage, AIMessage
from agent import agent 
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
CHAT_ID = os.getenv("MY_TELEGRAM_CHAT_ID")

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
#==============================================================================
@app.post("/apify-webhook")
async def handle_apify_update(request: Request, background_tasks: BackgroundTasks):
    
    data = await request.json()
    
    await bot.send_message(chat_id=CHAT_ID, text=data)
    
    
    dataset_id = data.get("datasetId")
    if dataset_id:
        background_tasks.add_task(fetch_process_and_send, dataset_id, bot, CHAT_ID)
        return {"status": "ok"}
    return {"status": "error", "message": "datasetId not found in payload"}
   
async def fetch_process_and_send(dataset_id, bot, chat_id):
    """جلب البيانات الفعلية، استخراج الأسماء، والإرسال"""
    try:
        # 1. جلب النتائج من Apify Dataset
        items = apify_client.dataset(dataset_id).list_items().items
        
        await bot.send_message(chat_id=CHAT_ID, text=items)
        if not items:
            await bot.send_message(chat_id=chat_id, text="⚠️ اكتمل البحث ولم يتم العثور على نتائج.")
            return

        message = "🆕 <b>تحديث دوري: منتجات ترند من TikTok</b>\n\n"
        # videoDescription
        # 2. معالجة أول 5 نتائج
        for item in items[:5]:
            raw_desc = item.get('text', 'لا يوجد وصف')
            url = item.get('webVideoUrl', '#')
            
            # ملاحظة: هنا يمكنك استدعاء نموذج LangGraph الخاص بك لتحليل raw_desc
            # واستخراج "اسم المنتج" بدقة بدلاً من النص الخام.
            
            product_name = clean_product_name(raw_desc) # دالة تنظيف بسيطة
            
            message += f"📦 <b>المنتج:</b> {product_name}\n"
            message += f"📝 <b>الوصف:</b> {raw_desc[:80]}...\n"
            message += f"🔗 <b>الرابط:</b> <a href=\"{url}\">اضغط هنا</a>\n"
            message += "------------------\n\n"

        # 3. الإرسال النهائي للتلجرام
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print(f"[ERROR] fetch_process_and_send: {e}")
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"❌ حدث خطأ تقني:\n<code>{str(e)}</code>",
                parse_mode="HTML"
            )
        except Exception as send_error:
            print(f"[ERROR] Failed to send error message: {send_error}")
def clean_product_name(text):
    
    # ✅ التحقق من النص قبل المعالجة
    if not text or not text.strip():
        return "غير محدد"
    words = [w for w in text.split() if not w.startswith('#')]
    return " ".join(words[:5]) if words else "غير محدد"

