import itertools
import random
import asyncio
import aiogram.utils.exceptions
from create_bot import bot, dp
from aiogram import types, Dispatcher


def get_board(size, alive_cons):
    return [['⬛' if (i, j) in alive_cons else '⬜'
             for j in range(size)]
            for i in range(size)]


def get_neighbors(con):
    x, y = con
    neighbors = [(x + i, y + j)
                 for i in range(-1, 2)
                 for j in range(-1, 2)
                 if not i == j == 0]
    return neighbors


def calculate_alive_neighbors(con, alive_cons):
    return len(list(filter(lambda x: x in alive_cons,
                           get_neighbors(con))))


def is_alive_con(con, alive_cons):
    alive_neighbors = calculate_alive_neighbors(con, alive_cons)
    if (alive_neighbors == 3 or
            (alive_neighbors == 2 and con in alive_cons)):
        return True
    return False


def new_step(alive_cons):
    board = itertools.chain(*map(get_neighbors, alive_cons))
    new_board = set([con
                     for con in board
                     if is_alive_con(con, alive_cons)])
    return list(new_board)


def is_correct_con(size, con):
    x, y = con
    return all(0 <= coord <= size - 1 for coord in [x, y])


def correct_cons(size, cons):
    return list(filter(lambda x: is_correct_con(size, x), cons))


async def print_board(board, message):
    lines = ''
    for line in board:
        line = str(line)
        lines += line.replace('[', ''). \
            replace(']', "'\n").replace(',', '').replace('0', '⬜'). \
            replace('1', '⬛').replace(' ', '').replace("''", '').replace("'", '')
    try:
        await asyncio.sleep(5)
        await bot.edit_message_text(text=lines, chat_id=message.chat.id, message_id=message.message_id)
    except aiogram.exceptions.RetryAfter as e:
        await asyncio.sleep(e.timeout)
        pass
    except aiogram.exceptions.MessageNotModified:
        pass


async def main(message: types.Message):
    message = await bot.send_message(chat_id=message.chat.id, text='Loading')
    size = 8
    board = [(random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8)),
             (random.randint(1, 8), random.randint(1, 8))]
    await print_board(get_board(size, board), message)
    for _ in range(100):
        board = correct_cons(size, new_step(board))
        await print_board(get_board(size, board), message)


def reg_game(dp: Dispatcher):
    dp.register_message_handler(main, commands=['жизнь'])
