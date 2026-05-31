import logging
import json
import requests
import re
import time
import base64
import random
import os
from string import ascii_letters, digits
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# LƯU Ý: TOKEN NÀY CẦN ĐƯỢC GIỮ BẢO MẬT
TOKEN = "8902944127:AAHgt3SzDEWpuA_-sVlV_yY1hLjjzYM52bY"

logging.basicConfig(level=logging.INFO)

# --- CLASS ZEFOY GỘP ---
class Zefoy:
    def __init__(self):
        self.base_url = 'https://zefoy.com/'
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
        self.session = requests.Session()
        self.video_key = None
        self.services_ids = {}

    def get_captcha(self):
        request = self.session.get(self.base_url, headers=self.headers)
        if 'Enter Video URL' in request.text: 
            self.video_key = request.text.split('" placeholder="Enter Video URL"')[0].split('name="')[-1]
            return True
        return False

    def get_status_services(self):
        request = self.session.get(self.base_url, headers=self.headers).text
        for x in re.findall(r'<h5 class="card-title mb-3">.+</h5>\n<form action=".+">', request): 
            self.services_ids[x.split('title mb-3">')[1].split('<')[0].strip()] = x.split('<form action="')[1].split('">')[0].strip()

    def run_service(self, url, service_name):
        # Mapping tên lệnh sang tên dịch vụ trên Zefoy
        service_map = {'views': 'Views', 'hearts': 'Likes'} 
        target_service = service_map.get(service_name, 'Views')
        
        self.get_captcha()
        self.get_status_services()
        
        if target_service not in self.services_ids:
            return f"Lỗi: Không tìm thấy dịch vụ {target_service}"

        # Tìm video
        request = self.session.post(f'{self.base_url}{self.services_ids[target_service]}', 
                                    headers={'user-agent':self.headers['user-agent'], 'origin':'https://zefoy.com'}, 
                                    files={self.video_key: (None, url)})
        
        video_info = base64.b64decode(requests.utils.unquote(request.text.encode()[::-1])).decode()
        
        if 'onsubmit="showHideElements' in video_info:
            v_info = [video_info.split('" name="')[1].split('"')[0], video_info.split('value="')[1].split('"')[0]]
            # Gửi yêu cầu buff
            payload = {v_info[0]: (None, v_info[1])}
            resp = self.session.post(f'{self.base_url}{self.services_ids[target_service]}', headers={'user-agent':self.headers['user-agent']}, files=payload)
            return "✅ Yêu cầu đã được gửi thành công!"
        return "❌ Không thể tìm thấy video hoặc dịch vụ đang bảo trì."

# --- LOGIC BOT TELEGRAM ---
z = Zefoy()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot đã sẵn sàng! Dùng /view <url> hoặc /like <url>")

async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service_type):
    if not context.args:
        await update.message.reply_text("❌ Vui lòng cung cấp URL.")
        return
    url = context.args[0]
    msg = await update.message.reply_text("⏳ Đang xử lý...")
    
    # Chạy đồng bộ trong thread để không làm treo bot
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, z.run_service, url, service_type)
    await msg.edit_text(result)

async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_service(update, context, 'views')

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_service(update, context, 'hearts')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("like", like))
    app.run_polling()

if __name__ == "__main__":
    main()
