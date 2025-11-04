import os
import subprocess
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

BOT_TOKEN = "8404399161:AAF23OSsuelzXPqY2DGHskOkqeWzn8bnyfE"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🎵 Привет! Отправь мне mp3 файл — я разделю его на вокал и минус 🎤")

def handle_audio(update: Update, context: CallbackContext):
    file = update.message.audio or update.message.voice or update.message.document
    if not file:
        update.message.reply_text("Отправь аудиофайл (mp3)")
        return

    update.message.reply_text("🔄 Обрабатываю... это может занять минуту")

    # Скачиваем файл
    file_path = file.get_file().download(custom_path="input.mp3")

    # Запускаем команду Docker через subprocess и захватываем вывод
    process = subprocess.Popen([
        "docker", "run", "--rm",  # --rm удаляет контейнер после выполнения
        "-v", f"{os.getcwd()}:/data",  # Монтируем текущую директорию в контейнер
        "researchdeezer/spleeter",  # Имя Docker образа
        "separate", "-p", "spleeter:2stems",  # Разделение на вокал и минус
        "-o", "/data", "/data/input.mp3"  # Выходной каталог и входной файл
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Захватываем вывод и ошибки

    # Чтение стандартного вывода и ошибок
    stdout, stderr = process.communicate()

    # Печатаем вывод и ошибки в терминал для отладки
    print(stdout.decode())  # Это показывает, что вывел Docker в stdout
    print(stderr.decode())  # Это покажет возможные ошибки

    # Проверим, созданы ли файлы
    if os.path.exists("accompaniment.wav") and os.path.exists("vocals.wav"):
        update.message.reply_audio(open("accompaniment.wav", "rb"), caption="🎵 Минус")
        update.message.reply_audio(open("vocals.wav", "rb"), caption="🎤 Вокал")
    else:
        update.message.reply_text("❌ Ошибка при обработке файла. Попробуй еще раз.")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.audio | Filters.document, handle_audio))

    updater.start_polling()
    print("✅ Бот запущен. Нажми Ctrl+C чтобы остановить.")
    updater.idle()

if __name__ == "__main__":
    main()
