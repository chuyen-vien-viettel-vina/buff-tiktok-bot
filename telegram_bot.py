import logging, json, requests, re, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8902944127:AAHgt3SzDEWpuA_-sVlV_yY1hLjjzYM52bY"
# --- DÁN PHPSESSID CỦA BẠN VÀO ĐÂY ---
MY_COOKIE = "GIÁ_TRỊ_CỦA_PHPSESSID_BẠN_VỪA_COPY"

class Zefoy:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.set("PHPSESSID", MY_COOKIE, domain="zefoy.com")
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
        self.base_url = 'https://zefoy.com/'

    def run_service(self, url, service_type):
        try:
            req = self.session.get(self.base_url, headers=self.headers)
            # Tìm ID dịch vụ
            services = re.findall(r'<h5 class="card-title mb-3">(.+?)</h5>\n<form action="(.+?)">', req.text)
            service_map = {'views': 'Views', 'hearts': 'Likes'}
            target_action = next((s[1] for s in services if s[0] == service_map.get(service_type)), None)
            
            if not target_action: return "❌ Bot chưa lấy được quyền truy cập. Hãy F5 trang web và copy lại PHPSESSID mới."

            # Tìm video
            video_key = req.text.split('" placeholder="Enter Video URL"')[0].split('name="')[-1]
            res = self.session.post(f"{self.base_url}{target_action}", files={video_key: (None, url)}).text
            
            if 'success' in res or '1000' in res: return "✅ Thành công!"
            return "⚠️ Đang trong thời gian chờ hoặc cần xác thực thủ công trên web."
        except Exception as e: return f"Lỗi: {e}"

z = Zefoy()
async def view(update, context):
    url = context.args[0] if context.args else ""
    res = await asyncio.get_event_loop().run_in_executor(None, z.run_service, url, 'views')
    await update.message.reply_text(res)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("view", view))
app.run_polling()
