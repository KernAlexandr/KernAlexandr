from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import  Dispatcher, types, F      
from functions import *

# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем кнопку в сборщик клавиатур
    builder.add(types.KeyboardButton(text="Начать игру"))
    # Логика обработки команды /start
    await message.answer("Добро пожаловать в Квиз!", reply_markup = builder.as_markup(resize_keyboard=True))

# Хэндлер на команду /quiz, Начать игру
@dp.message(F.text == ("Начать игру"))
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Отправляем сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
     # Запускаем новый квиз
    await new_quiz(message)

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer(f"Команды бота: \n/start - Запуск бота\n/quiz - Начать квиз\n/help - Список команд")

# callback на правильнй ответ
@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Получаем текущий счет правильных ответов пользователя
    current_score = await get_user_score(callback.from_user.id)
    # Отправляем в чат сообщение, что ответ верный
    await callback.message.answer("Верно!")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    # Обновляем счет пользователя
    current_score += 1

    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_user_score(callback.from_user.id, current_score)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш счет:{current_score}")

# callback на неправильный ответ
@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Получаем текущий счет правильных ответов пользователя
    current_score = await get_user_score(callback.from_user.id)

    correct_option = quiz_data[current_question_index]['correct_option']

    # Отправляем в чат сообщение об ошибке с указанием верного ответа
    await callback.message.answer(f"Неправильно.\nПравильный ответ: \n{quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1

    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_user_score(callback.from_user.id, current_score)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш счет:{current_score}")    