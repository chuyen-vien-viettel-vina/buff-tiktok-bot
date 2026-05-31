import logging
import subprocess
import json
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# TOKEN CỦA BẠN - ĐÃ BỊ LỘ, CẦN REVOKE SAU KHI DÙNG
TOKEN = "8902944127:AAHgt3SzDEWpuA_-sVlV_yY1hLjjzYM52bY"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot tăng tương tác TikTok đã sẵn sàng!\n"
        "📌 Lệnh:\n"
        "/view <url_video> - Tăng lượt xem\n"
        "/like <url_video> - Tăng tim\n"
        "Ví dụ: /view https://www.tiktok.com/@user/video/123"
    )

async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Vui lòng cung cấp URL video TikTok.")
        return
    url = context.args[0]
    msg = await update.message.reply_text(f"⏳ Đang xử lý tăng view...\n{url}")

    config_path = "config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except:
        config = {}
    config['url'] = url
    config['service'] = 'views'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    try:
        result = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            await msg.edit_text(f"✅ Thành công! Đã tăng view cho {url}")
        else:
            await msg.edit_text(f"❌ Lỗi: {result.stderr}")
    except Exception as e:
        await msg.edit_text(f"❌ Lỗi: {e}")

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Vui lòng cung cấp URL video TikTok.")
        return
    url = context.args[0]
    msg = await update.message.reply_text(f"⏳ Đang xử lý tăng tim...\n{url}")

    config_path = "config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except:
        config = {}
    config['url'] = url
    config['service'] = 'hearts'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    try:
        result = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            await msg.edit_text(f"✅ Thành công! Đã tăng tim cho {url}")
        else:
            await msg.edit_text(f"❌ Lỗi: {result.stderr}")
    except Exception as e:
        await msg.edit_text(f"❌ Lỗi: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("like", like))
    print("🤖 Bot đang lắng nghe...")
    app.run_polling()

if __name__ == "__main__":
    main()
