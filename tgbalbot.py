import re
import logging
import unicodedata
from telegram.ext import Application, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = input("Token: ").strip()
if not TOKEN:
    print("Token can not be empty")
    exit(1)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def clean_text(text):
    return ''.join(c for c in text if not unicodedata.category(c).startswith('Cf'))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    logger.info(f"Получено сообщение: {message_text[:50]}...")

    if re.match(r'(?i)^\s*.*?баланс.*?', message_text):
        await process_balance_message(update, message_text)
    elif re.match(r'(?i)^\s*.*?ура(?:а+)?\s*.*?', message_text):
        await process_lottery_message(update, message_text)
    elif message_text.lower().startswith("цена") and update.message.reply_to_message:
        await process_price_message(update, message_text)
    else:
        await update.message.reply_text("Сообщение не распознано.")


async def process_balance_message(update: Update, message_text: str):
    try:
        amounts = re.findall(r'-\s*([\d\s]+)\s*₽', message_text)
        total = sum(int(a.replace(" ", ""))
                    for a in amounts if a.replace(" ", "").isdigit())
        await update.message.reply_text(f"💰 Общая сумма: {total}₽")
    except Exception as e:
        logger.error(f"Ошибка в process_balance_message: {e}")
        await update.message.reply_text("Ошибка при обработке баланса.")


async def process_lottery_message(update: Update, message_text: str):
    try:
        # Очистка текста от скрытых символов
        cleaned_message = clean_text(message_text)

        # Ищем все имена участников (@~Имя или @⁨~Имя⁩), плюс наличие галочек
        matches = re.findall(r'(@⁨~.*?⁩|@~.+?)(?=\n|$)', cleaned_message)

        if not matches:
            await update.message.reply_text("Не удалось найти имена участников.")
            return

        # Подсчёт количества для каждого уникального участника
        name_counts = {}
        for match in matches:
            name = match.strip()
            # убираем лишние пробелы внутри
            name = re.sub(r'\s+', ' ', name)
            name_counts[name] = name_counts.get(name, 0) + 1

        # Формируем строку для подсчёта
        response = ""
        for i, (name, count) in enumerate(name_counts.items(), 1):
            response += f"[{i}] {name} - {count}\n"

        total_count = sum(name_counts.values())
        response += f"\nОбщее количество - {total_count}"

        # Теперь создаём изменённый текст розыгрыша с галочками
        modified_text = ""
        start_idx = 0
        for match in re.finditer(r'(@⁨~.*?⁩|@~.+?)(?=\n|$)', message_text, re.DOTALL):
            modified_text += message_text[start_idx:match.start()]
            name = match.group(0)

            end_idx = message_text.find('\n', match.end())
            if end_idx == -1:
                end_idx = len(message_text)

            name_segment = message_text[match.start():end_idx]
            # убираем старые галочки
            clean_name_segment = re.sub(r'✅+', '', name_segment)

            # добавляем галочку
            modified_text += clean_name_segment + "✅"
            start_idx = end_idx

        modified_text += message_text[start_idx:]

        # Отправляем исправленное сообщение с галочками
        await update.message.reply_text(modified_text)

        # Отправляем второй текст с подсчётом
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка в process_lottery_message: {e}")
        await update.message.reply_text("Ошибка при обработке розыгрыша.")


async def process_price_message(update: Update, message_text: str):
    try:
        price_match = re.search(r'цена\s*\n?\s*(\d+)',
                                message_text, re.IGNORECASE)
        if not price_match:
            await update.message.reply_text("Не удалось распознать сумму.")
            return

        price = int(price_match.group(1))
        replied_text = update.message.reply_to_message.text
        matches = re.findall(r'@~([^-\n]+?)\s*-\s*(\d+)', replied_text)

        if not matches:
            await update.message.reply_text("Не удалось распознать список с номерками.")
            return

        result = ""
        total_sum = 0
        for name, count in matches:
            count = int(count)
            total = count * price
            total_sum += total
            result += f"@~{name.strip()} — {count} × {price} = {total}₽\n"

        await update.message.reply_text(result.strip())
        await update.message.reply_text(f"💰 Общая сумма: {total_sum}₽")
    except Exception as e:
        logger.error(f"Ошибка в process_price_message: {e}")
        await update.message.reply_text("Ошибка при обработке цены.")


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Запуск бота...")
    application.run_polling()


if __name__ == "__main__":
    main()
