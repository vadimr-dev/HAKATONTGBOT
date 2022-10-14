from create_bot import bot, dp
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
import random


# @dp.message_handler(Text(contains="Привет", ignore_case=True))
async def send_welcome(message: types.message):
    lines = ["Добро пожаловать в чат!", "Приветик", "Дарова", "Приятного времяпрепровождения"]
    await message.reply(lines[random.randint(0, len(lines) - 1)])


# @dp.message_handler(commands='help')
async def help_func(message: types.Message):
    await bot.send_message(message.chat.id, text='Функции:\n\n1 - /рандомсооб - попытай свою удачу ' +
                                                 'ну или нет(отправка рандомного сообщения)\n\n2 - /го'
                                                 ' - хочешь позвать кого-то' +
                                                 ' поиграть функция как раз для тебя (/го'
                                                 ' Название игры) '
                                                 'создай опрос и найди тиммейтов\n\n3 '
                                                 '- ' + '/котики, /кот, /коты - отправка'
                                                        ' рандомного котика <3\n\n' + '4 - '
                                                                                    '/рандом - не можешь'
                                                                                    ' выбрать число - ' +
                                                 'бот поможет (/рандом - любое число от 0 до 100, /рандом [число] - '
                                                 'рандомное число до заданного, /рандом [число1] [число2] - ' +
                                                 'рандомное число в заданном диапазоне)\n\n 5 - /расписание '
                                                 '- команду которую ты '
                                                 'сразу полюбишь это то чего ты давно хотел - '
                                                 'расписание в  нормальном виде, да так бывает(/расписание'
                                                 ' [Название группы] '
                                                 '[Подгруппа - по умолчанию 1])\n\n 6 - /рейтинг - топ 5 пользователей по количеству сообщений'
                                                 '\n\n7 - /жизнь - Игра в жизнь с визуализацией')


def reg_hello_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, Text(contains='Привет', ignore_case=True))
    dp.register_message_handler(help_func, commands=['help'])
