import telebot
import json
import os
import re
import time

# ВСТАВЬ СЮДА СВОЙ НОВЫЙ ТОКЕН (старый обязательно отозви в BotFather!)
TOKEN = "8660904490:AAEGfU2Uu884fSA4NKGUSbpuHLtYDC3DLK4"
bot = telebot.TeleBot(TOKEN)

STATS_FILE = "digl_stats.json"

# Переменная для хранения времени (анти-спам)
cooldowns = {}
COOLDOWN_TIME = 3600  # 3600 секунд = 1 час

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

# Функция проверки наличия слова "дигл" в сообщении
def has_digl(text):
    # Ищет именно отдельное слово "дигл". 
    # \b означает границу слова. "диглдигл" не посчитается, "диглер" не посчитается.
    if re.search(r'\bдигл\b', text.lower()):
        return True
    return False

@bot.message_handler(commands=['top'])
def show_top(message):
    chat_id = str(message.chat.id)
    if chat_id not in stats or not stats[chat_id]:
        bot.reply_to(message, "Статистики пока нет. Напишите 'дигл'!")
        return

    sorted_users = sorted(stats[chat_id].items(), key=lambda item: item[1]['count'], reverse=True)
    
    text = "🏆 <b>Топ игроков по слову 'Дигл':</b>\n\n"
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        text += f"{i}. {data['name']} — {data['count']} шт. (Шанс: {data['count'] * 0.1:.1f}%)\n"
    
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text:
        return

    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # Проверяем, есть ли слово "дигл" в сообщении
    if has_digl(message.text):
        current_time = time.time()
        
        # --- СИСТЕМА АНТИ-СПАМА (1 раз в час) ---
        if chat_id not in cooldowns:
            cooldowns[chat_id] = {}
            
        if user_id in cooldowns[chat_id]:
            last_time = cooldowns[chat_id][user_id]
            time_passed = current_time - last_time
            
            if time_passed < COOLDOWN_TIME:
                # Если прошел меньше 1 часа, бот просто игнорирует сообщение.
                # (Если хочешь, чтобы бот писал "подожди час", убери решетки # со следующих 2 строк)
                # remaining = int((COOLDOWN_TIME - time_passed) / 60)
                # bot.reply_to(message, f"⏳ Антиспам! Ты сможешь написать 'дигл' только через {remaining} мин.")
                return 
                
        # Если час прошел (или пишет первый раз), обновляем время
        cooldowns[chat_id][user_id] = current_time
        # -----------------------------------------
        
        # Добавляем ровно +1 за сообщение
        if chat_id not in stats:
            stats[chat_id] = {}
            
        if user_id not in stats[chat_id]:
            stats[chat_id][user_id] = {"name": user_name, "count": 0}
            
        stats[chat_id][user_id]["name"] = user_name
        stats[chat_id][user_id]["count"] += 1  # Прибавляем всегда 1, сколько бы раз слово ни было в сообщении
        save_stats(stats)
        
        total_count = stats[chat_id][user_id]["count"]
        win_chance = total_count * 0.1
        
        bot.reply_to(message, f"🎯 {user_name} сказал(а) 'дигл'!\nВсего слов: {total_count}\n🎰 Шанс выигрыша: {win_chance:.1f}%")

if __name__ == "__main__":
    print("Бот запущен и готов считать слова...")
    bot.infinity_polling()
