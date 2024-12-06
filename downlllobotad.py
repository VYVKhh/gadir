import os
import logging
import time
import threading
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# تثبيت المكتبات المطلوبة إذا لم تكن مثبتة مسبقًا
os.system('pip install python-telegram-bot')
os.system('pip install yt-dlp')
os.system('pip install requests')
os.system('pip install beautifulsoup4')
os.system('pip install lxml')

# استيراد مكتبات بعد تثبيتها
import yt_dlp

# تفعيل السجل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# تخزين الرابط المستخدم لتنزيل الفيديو
download_url = ""
stop_countdown = False  # متغير للتحكم في إيقاف العداد التنازلي

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("YouTube🌚", callback_data='youtube')],
        [InlineKeyboardButton("TIKTOK😎", callback_data='tiktok')],
        [InlineKeyboardButton("Instagram🤖", callback_data='instagram')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('اختر المنصة التي تريد التحميل منها:', reply_markup=reply_markup)

def youtube_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("رجوع", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="أرسل لي رابط فيديو يوتيوب وسأقوم بتحميله لك.", reply_markup=reply_markup)

def tiktok_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("رجوع", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="أرسل لي رابط فيديو تيك توك وسأقوم بتحميله لك.", reply_markup=reply_markup)

def instagram_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("رجوع", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="أرسل لي رابط فيديو إنستغرام وسأقوم بتحميله لك.", reply_markup=reply_markup)

def download_video(url: str, update: Update, context: CallbackContext, chat_id: int, message_id: int) -> io.BytesIO:
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'retries': 5,
        'timeout': 20,
    }
    buffer = io.BytesIO()
    global stop_countdown
    stop_countdown = False
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict)
            countdown_thread = threading.Thread(target=countdown, args=(chat_id, context.bot, message_id))
            countdown_thread.start()
            with open(video_file, 'rb') as f:
                buffer = io.BytesIO(f.read())
            buffer.seek(0)
            stop_countdown = True
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        stop_countdown = True
        return None
    return buffer

def countdown(chat_id, bot, message_id):
    global stop_countdown
    steps = 10
    for i in range(steps):
        if stop_countdown:
            break
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"[🟩{'🟩' * i}] {((i + 1) / steps) * 100:.0f}%")
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
        time.sleep(1)

def handle_message(update: Update, context: CallbackContext) -> None:
    global download_url, stop_countdown
    stop_countdown = False
    download_url = update.message.text
    chat_id = update.effective_chat.id

    if not download_url.startswith("http"):
        update.message.reply_text("يرجى إدخال رابط صالح يبدأ ب http أو https.")
        return

    message = update.message.reply_text("[🟩] 0%")
    message_id = message.message_id

    try:
        video_buffer = download_video(download_url, update, context, chat_id, message_id)

        if video_buffer:
            # حذف رسالة العداد التنازلي
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            # إرسال الفيديو مع التسمية التوضيحية
            context.bot.send_video(chat_id=update.effective_chat.id, video=video_buffer, filename="video.mp4", supports_streaming=True, caption="𝐃𝐄𝐕𝐄𝑳𝐎𝐏𝐄𝐑 : @VYV_K")
        else:
            stop_countdown = True
            raise Exception("Failed to download video.")
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        stop_countdown = True
        keyboard = [
            [InlineKeyboardButton("إعادة المحاولة", callback_data='retry')],
            [InlineKeyboardButton("خروج", callback_data='exit')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('حدث خطأ أثناء تنزيل الفيديو. يرجى اختيار إحدى الخيارات التالية:', reply_markup=reply_markup)

def retry(update: Update, context: CallbackContext) -> None:
    global download_url, stop_countdown
    stop_countdown = False
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    try:
        video_buffer = download_video(download_url, update, context, chat_id, message_id)

        if video_buffer:
            # حذف رسالة العداد التنازلي
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            # إرسال الفيديو مع التسمية التوضيحية
            context.bot.send_video(chat_id=chat_id, video=video_buffer, filename="video.mp4", supports_streaming=True, caption="𝐃𝐄𝐕𝐄𝑳𝐎𝐏𝐄𝐑 : @VYV_K")
        else:
            stop_countdown = True
            raise Exception("Failed to download video.")
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        stop_countdown = True
        context.bot.send_message(chat_id=chat_id, text='حدث خطأ أثناء تنزيل الفيديو. يرجى التأكد من صحة الرابط.')

def exit(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    start(query, context)

def back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    start(query, context)

def main() -> None:
    bot_token = '7376905431:AAGuKezo_TZr7UwJvhNzNSDtu46rnSzfXF8'
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(youtube_handler, pattern='youtube'))
    dispatcher.add_handler(CallbackQueryHandler(tiktok_handler, pattern='tiktok'))
    dispatcher.add_handler(CallbackQueryHandler(instagram_handler, pattern='instagram'))
    dispatcher.add_handler(CallbackQueryHandler(retry, pattern='retry'))
    dispatcher.add_handler(CallbackQueryHandler(exit, pattern='exit'))
    dispatcher.add_handler(CallbackQueryHandler(back, pattern='back'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()