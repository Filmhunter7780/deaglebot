import telebot
import json
import os
import re

# СЮДА НУЖНО БУДЕТ ВСТАВИТЬ ТВОЙ ТОКЕН
TOKEN = "8660904490:AAEGfU2Uu884fSA4NKGUSbpuHLtYDC3DLK4"
bot = telebot.TeleBot(TOKEN)

# Файл для сохранения статистики, чтобы при перезапуске бота данные не терялись
STATS_FILE = "digl_stats.json"

# Загрузка статистики
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Сохранение статистики
def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

stats = load_stats()

# Функция для подсчета слова "дигл" в сообщении (игнорируем регистр)
def count_digl(text):
    # Ищет слово "дигл" как отдельное слово (чтобы не считать "диглер")
    matches = re.findall(r'\bдигл\b', text.lower())
    return len(matches)

@bot.message_handler(commands=['top'])
def show_top(message):
    chat_id = str(message.chat.id)
    if chat_id not in stats or not stats[chat_id]:
        bot.reply_to(message, "Статистики пока нет. Напишите 'дигл'!")
        return

    # Сортируем пользователей по количеству слов
    sorted_users = sorted(stats[chat_id].items(), key=lambda item: item[1]['count'], reverse=True)
    
    text = "🏆 <b>Топ игроков по слову 'Дигл':</b>\n\n"
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        text += f"{i}. {data['name']} — {data['count']} шт. (Шанс: {data['count'] * 0.1:.1f}%)\n"
    
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Игнорируем сообщения без текста
    if not message.text:
        return

    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # Считаем сколько раз было слово "дигл" в этом сообщении
    count = count_digl(message.text)
    
    if count > 0:
        # Если чата еще нет в базе, добавляем
        if chat_id not in stats:
            stats[chat_id] = {}
            
        # Если пользователя еще нет в базе чата, добавляем
        if user_id not in stats[chat_id]:
            stats[chat_id][user_id] = {"name": user_name, "count": 0}
            
        # Обновляем имя (на случай если человек сменил имя)
        stats[chat_id][user_id]["name"] = user_name
        
        # Прибавляем количество найденных слов
        stats[chat_id][user_id]["count"] += count
        save_stats(stats) # Сохраняем в файл
        
        total_count = stats[chat_id][user_id]["count"]
        win_chance = total_count * 0.1 # 1 слово = 0.1%
        
        # Отправляем ответ
        bot.reply_to(message, f"🎯 {user_name} сказал(а) 'дигл'!\nВсего слов: {total_count}\n🎰 Шанс выигрыша: {win_chance:.1f}%")

if __name__ == "__main__":
    print("Бот запущен и готов считать слова...")
    # Запускаем бота, чтобы он работал постоянно
    bot.infinity_polling()
