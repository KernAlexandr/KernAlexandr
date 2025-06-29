import asyncio
import logging
from aiogram import Bot                                
from functions import *
from handlers import *

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
# API_TOKEN = 'YOUR_BOT_TOKEN'
API_TOKEN = ''

# Объект бота
bot = Bot(token=API_TOKEN)

# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()
    # Запускаем плотинг(бесконечный цикл принятия изменений в боте)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
