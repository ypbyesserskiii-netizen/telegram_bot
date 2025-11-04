import os
import tempfile
import shutil
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from spleeter.separator import Separator
from pydub import AudioSegment

# === ВСТАВЬ СВОЙ ТОКЕН СЮДА ===
TOKEN = "8404399161:AAF23OSsuelzXPqY2DGHskOkqeWzn8bnyfE"

# Модель, которая разделяет аудио на 2 дорожки: вокал и минус
separator = Separator('spleeter:2stems')

def start(update, context):
    update.message.reply_text("Привет! Пришли мне песню (mp3, wav, m4a и т.д.), и я разделю её на вокал и минус 🎧")

def handle_audio(update, context):
    msg = update.message

    # получаем файл
    if msg.audio:
        file = msg.audio.get_file()
        filename = msg.audio.file_name or "audio.mp3"
    elif msg.voice:
        file = msg.voice.get_file()
        filename = "voice.ogg"
    elif msg.document:
        file = msg.document.get_file()
        filename = msg.document.file_name or "file.mp3"
    else:
        msg.reply_text("Пожалуйста, отправь мне аудиофайл 🎵")
        return

    msg.reply_text("Обрабатываю аудио... Это займёт немного времени ⏳")

    # создаём временную папку
    workdir = tempfile.mkdtemp()
    input_path = os.path.join(workdir, filename)
    file.download(input_path)

    # конвертируем в wav (если нужно)
    wav_path = os.path.join(workdir, "input.wav")
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(wav_path, format="wav")
    except Exception:
        msg.reply_text("Ошибка при конвертации файла 😢")
        shutil.rmtree(workdir)
        return

    # разделяем вокал/минус
    try:
        separator.separate_to_file(wav_path, workdir)
    except Exception:
        msg.reply_text("Ошибка при разделении файла 😢")
        shutil.rmtree(workdir)
        return

    # ищем готовые файлы
    result_dir = os.path.join(workdir, "input")
    vocals = os.path.join(result_dir, "vocals.wav")
    instrumental = os.path.join(result_dir, "accompaniment.wav")

    # отправляем пользователю
    if os.path.exists(vocals):
        msg.reply_text("🎤 Капелла (вокал):")
        msg.reply_document(open(vocals, "rb"))
    if os.path.exists(instrumental):
        msg.reply_text("🎵 Минус (инструментал):")
        msg.reply_document(open(instrumental, "rb"))

    msg.reply_text("Готово ✅")

    # удаляем временные файлы
    shutil.rmtree(workdir)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.audio | Filters.voice | Filters.document.audio, handle_audio))

    updater.start_polling()
    print("Бот запущен. Нажми Ctrl+C чтобы остановить.")
    updater.idle()

if __name__ == "__main__":
    main()
