import telebot
import os
from lessons_data import LESSONS, LEVELS, user_progress

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def get_user_level(user_id):
    """Получить уровень пользователя"""
    if user_id not in user_progress:
        user_progress[user_id] = {"level": "beginner", "current_lesson": 0}
    return user_progress[user_id]["level"]

def set_user_level(user_id, level):
    """Установить уровень пользователя"""
    if user_id not in user_progress:
        user_progress[user_id] = {"level": level, "current_lesson": 0}
    else:
        user_progress[user_id]["level"] = level
        user_progress[user_id]["current_lesson"] = 0

def get_current_lesson(user_id):
    """Получить номер текущего урока"""
    if user_id not in user_progress:
        user_progress[user_id] = {"level": "beginner", "current_lesson": 0}
    return user_progress[user_id]["current_lesson"]

def set_current_lesson(user_id, lesson_num):
    """Установить номер текущего урока"""
    user_progress[user_id]["current_lesson"] = lesson_num

def get_lesson_by_id(level, lesson_id):
    """Получить урок по уровню и ID"""
    lessons = LESSONS.get(level, [])
    for lesson in lessons:
        if lesson["id"] == lesson_id:
            return lesson
    return None

def get_next_lesson_id(level, current_id):
    """Получить ID следующего урока"""
    lessons = LESSONS.get(level, [])
    for i, lesson in enumerate(lessons):
        if lesson["id"] == current_id and i + 1 < len(lessons):
            return lessons[i + 1]["id"]
    return None

def get_prev_lesson_id(level, current_id):
    """Получить ID предыдущего урока"""
    lessons = LESSONS.get(level, [])
    for i, lesson in enumerate(lessons):
        if lesson["id"] == current_id and i - 1 >= 0:
            return lessons[i - 1]["id"]
    return None

# ========== КОМАНДЫ БОТА ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_level = get_user_level(user_id)
    level_name = LEVELS[user_level]["name"]
    
    welcome_text = (
        f"🐍 *Добро пожаловать в Школу Python!*\n\n"
        f"Твой текущий уровень: {level_name}\n\n"
        f"📖 *Что я умею:*\n"
        f"/theory — показать теорию по текущему уроку\n"
        f"/practice — дать практическое задание\n"
        f"/solve — показать решение с объяснением\n"
        f"/next — следующий урок\n"
        f"/prev — предыдущий урок\n"
        f"/level — сменить уровень\n"
        f"/progress — твой прогресс\n\n"
        f"👉 Начни с /theory"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['level'])
def change_level(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for level_key, level_info in LEVELS.items():
        markup.add(telebot.types.InlineKeyboardButton(
            text=level_info["name"], 
            callback_data=f"set_level_{level_key}"
        ))
    bot.reply_to(message, "🎯 *Выбери свой уровень:*", 
                 parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_level_"))
def set_level_callback(call):
    user_id = call.from_user.id
    new_level = call.data.replace("set_level_", "")
    
    set_user_level(user_id, new_level)
    level_name = LEVELS[new_level]["name"]
    
    bot.edit_message_text(
        f"✅ Уровень изменён на {level_name}\n\n"
        f"Теперь начни изучение с /theory",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['theory'])
def show_theory(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    lesson_id = get_current_lesson(user_id)
    
    if lesson_id == 0:
        first_lesson = LESSONS[level][0]
        lesson_id = first_lesson["id"]
        set_current_lesson(user_id, lesson_id)
    
    lesson = get_lesson_by_id(level, lesson_id)
    if lesson:
        text = f"📖 *Урок {lesson_id}: {lesson['title']}*\n\n{lesson['theory']}"
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Урок не найден. Попробуй /level чтобы выбрать уровень.")

@bot.message_handler(commands=['practice'])
def show_practice(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    lesson_id = get_current_lesson(user_id)
    
    if lesson_id == 0:
        first_lesson = LESSONS[level][0]
        lesson_id = first_lesson["id"]
        set_current_lesson(user_id, lesson_id)
    
    lesson = get_lesson_by_id(level, lesson_id)
    if lesson:
        text = f"💪 *Практика к уроку {lesson_id}: {lesson['title']}*\n\n{lesson['practice']}\n\n" \
               "Когда решишь, напиши /solve чтобы увидеть решение и объяснение."
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Практика не найдена.")

@bot.message_handler(commands=['solve'])
def show_solution(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    lesson_id = get_current_lesson(user_id)
    
    if lesson_id == 0:
        first_lesson = LESSONS[level][0]
        lesson_id = first_lesson["id"]
        set_current_lesson(user_id, lesson_id)
    
    lesson = get_lesson_by_id(level, lesson_id)
    if lesson:
        bot.reply_to(message, lesson['solution'], parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Решение не найдено.")

@bot.message_handler(commands=['next'])
def next_lesson(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    current_id = get_current_lesson(user_id)
    
    if current_id == 0:
        lessons = LESSONS[level]
        if lessons:
            next_id = lessons[0]["id"]
            set_current_lesson(user_id, next_id)
            lesson = get_lesson_by_id(level, next_id)
            bot.reply_to(message, f"📖 *Урок {next_id}: {lesson['title']}*\n\n"
                         f"Напиши /theory чтобы начать!", parse_mode='Markdown')
        return
    
    next_id = get_next_lesson_id(level, current_id)
    if next_id:
        set_current_lesson(user_id, next_id)
        lesson = get_lesson_by_id(level, next_id)
        bot.reply_to(message, f"➡️ *Переход к уроку {next_id}: {lesson['title']}*\n\n"
                     f"Напиши /theory чтобы начать!", parse_mode='Markdown')
    else:
        total_lessons = len(LESSONS[level])
        bot.reply_to(message, f"🏆 *Поздравляю!* Ты прошёл все {total_lessons} уроков уровня {LEVELS[level]['name']}!\n\n"
                     f"Попробуй сменить уровень командой /level", parse_mode='Markdown')

@bot.message_handler(commands=['prev'])
def prev_lesson(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    current_id = get_current_lesson(user_id)
    
    prev_id = get_prev_lesson_id(level, current_id)
    if prev_id:
        set_current_lesson(user_id, prev_id)
        lesson = get_lesson_by_id(level, prev_id)
        bot.reply_to(message, f"⬅️ *Возврат к уроку {prev_id}: {lesson['title']}*\n\n"
                     f"Напиши /theory чтобы повторить!", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Это первый урок. Назад нельзя.")

@bot.message_handler(commands=['progress'])
def show_progress(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    current_id = get_current_lesson(user_id)
    lessons = LESSONS[level]
    total = len(lessons)
    
    if current_id == 0:
        current_index = 0
    else:
        current_index = next((i for i, l in enumerate(lessons) if l["id"] == current_id), 0)
    
    progress_bar = "🟩" * current_index + "⬜" * (total - current_index)
    if current_index == 0:
        progress_bar = "⬜" * total
    
    text = (
        f"📊 *Твой прогресс*\n\n"
        f"Уровень: {LEVELS[level]['name']}\n"
        f"Пройдено уроков: {current_index} из {total}\n\n"
        f"{progress_bar}\n\n"
        f"Текущий урок: {current_id if current_id > 0 else 'не начат'}"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "📖 *Справка по командам*\n\n"
        "/start — начать обучение\n"
        "/theory — показать теорию текущего урока\n"
        "/practice — показать практическое задание\n"
        "/solve — показать решение с объяснением\n"
        "/next — следующий урок\n"
        "/prev — предыдущий урок\n"
        "/level — сменить уровень (новичок/средний/профи)\n"
        "/progress — показать прогресс обучения\n"
        "/help — эта справка"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработка ответов на практические задания"""
    user_id = message.from_user.id
    level = get_user_level(user_id)
    lesson_id = get_current_lesson(user_id)
    
    if lesson_id == 0:
        bot.reply_to(message, "Начни с /theory чтобы выбрать урок.")
        return
    
    lesson = get_lesson_by_id(level, lesson_id)
    if lesson:
        check_keywords = lesson.get("check", "").lower().split()
        user_text = message.text.lower()
        
        # Простая проверка: ищем ключевые слова в ответе пользователя
        found = all(keyword in user_text for keyword in check_keywords) if check_keywords else False
        
        if found or len(user_text) > 20:  # Если длинный ответ, считаем что старался
            bot.reply_to(message, 
                        "✅ *Отличная работа!*\n\n"
                        "Твоё решение выглядит правильным!\n"
                        "Напиши /solve чтобы сравнить с эталонным решением и прочитать объяснение.\n\n"
                        "Готов к следующему уроку? Напиши /next",
                        parse_mode='Markdown')
        else:
            bot.reply_to(message,
                        "💡 *Попробуй ещё раз!*\n\n"
                        "Внимательно перечитай условие задания.\n"
                        "Если нужна помощь — напиши /solve и посмотри правильное решение с объяснением.",
                        parse_mode='Markdown')

print("🐍 Бот-учитель Python запущен и работает!")
bot.infinity_polling()
