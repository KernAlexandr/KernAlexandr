import aiosqlite
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import json

# Пути к файлам
# Зададим имя базы данных
DB_NAME = 'bot\quiz_bot.db'

# Путь к файлу с вопросами
DICT_DATA = 'bot\quiz_questions.json'
#DICT_DATA = 'C:\Users\PC\Desktop\Python\bot\quiz_questions.json'   


# Загрузка файла с вопросами 
with open(DICT_DATA, 'r', encoding='UTF-8') as file:
    quiz_data = json.load(file)['quiz_data']

# Создаем базу данных состоящую из 2х столбцов (user_id, question_index)
async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, user_score INTEGER)''')
        # Сохраняем изменения
        await db.commit()

# Получение текущего значения `question_index` в базе данных для заданного пользователя.
async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

# Получение текущего значения `user_score` в базе данных для заданного пользователя.
async def get_user_score(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT user_score FROM users WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
            
# Обновляем значение 'question_index' по мере прохождения квиза пользователем
async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()

# Обновляем значение 'user_score' по мере прохождения квиза пользователем
async def update_user_score(user_id, score):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO users (user_id, user_score) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET user_score = excluded.user_score', (user_id, score))
        # Сохраняем изменения
        await db.commit()

# Из сообщения узнаем пользователя, сбрасываем счетчик вопросов в 0, и запрашиваем асинхронно следующий вопрос для отправки пользователю в чат.
async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    # сбрасываем значение текущего счета пользователя квиза в 0
    new_score = 0
    await update_quiz_index(user_id, current_question_index)
    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)
    # Добавляем запись о счете
    await update_user_score(user_id, new_score)

#
async def get_question(message, user_id):
    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

def generate_options_keyboard(answer_options, right_answer):
  # Создаем сборщика клавиатур типа Inline
    builder = InlineKeyboardBuilder()

    # В цикле создаем 4 Inline кнопки, а точнее Callback-кнопки
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            # Текст на кнопках соответствует вариантам ответов
            text=option,
            # Присваиваем данные для колбэк запроса.
            # Если ответ верный сформируется колбэк-запрос с данными 'right_answer'
            # Если ответ неверный сформируется колбэк-запрос с данными 'wrong_answer'
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    # Выводим по одной кнопке в столбик
    builder.adjust(1)
    return builder.as_markup()    
