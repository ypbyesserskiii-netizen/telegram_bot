import os
import subprocess
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

TOKEN = "8404399161:AAF23OSsuelzXPqY2DGHskOkqeWzn8bnyfE"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🎶 Привет! Пришли мне песню, и я разделю её на вокал и минус с помощью AI Demucs 🎤🎵")

def handle_audio(update: Update, context: CallbackContext):
    audio_file = update.message.audio or update.message.voice or update.message.document
    if not audio_file:
        update.message.reply_text("⚠️ Пришли аудиофайл (mp3, wav и т.д.)")
        return

    file = audio_file.get_file()
    file_path = os.path.join(DOWNLOAD_DIR, "input.mp3")
    file.download(file_path)

    update.message.reply_text("⏳ Обрабатываю песню с помощью Demucs, подожди немного...")

    try:
        subprocess.run(["demucs", file_path], check=True)

        demucs_dir = os.path.expanduser("~/Downloads/demucs")
        latest = sorted(os.listdir(demucs_dir))[-1]
        track_dir = os.path.join(demucs_dir, latest, "htdemucs")

        vocals = os.path.join(track_dir, "vocals.wav")
        accompaniment = os.path.join(track_dir, "no_vocals.wav")

        update.message.reply_audio(open(accompaniment, "rb"), caption="🎵 Минус")
        update.message.reply_audio(open(vocals, "rb"), caption="🎤 Вокал")

    except Exception as e:
        update.message.reply_text(f"❌ Ошибка при обработке: {e}")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.audio | Filters.document, handle_audio))
    updater.start_polling()
    print("✅ Бот запущен. Нажми Ctrl+C чтобы остановить.")
    updater.idle()

if __name__ == "__main__":
    main()

