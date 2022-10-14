from aiogram import types, Dispatcher
import time
import requests
from create_bot import bot, dp
import random
from aiogram.types import InlineQuery
from youtube_search import YoutubeSearch
import hashlib


# Кулдаун отправки котов (в секундах)
catCooldownSize = 15
catCooldown = 0


async def searcher(row):
    res = YoutubeSearch(row, max_results=15).to_dict()
    return res


# @dp.message_handler(commands=['Котики', 'кот', 'КОТЫ', 'коты', 'КОТИКИ', 'КОТ'])
async def send_cat(message: types.message):
    global catCooldown
    if catCooldown + catCooldownSize <= time.time():
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        catCooldown = time.time()
        await message.answer_photo(response.json()[0]['url'])
    else:
        await message.answer('Осталось %2d секунд' % (catCooldownSize - (time.time() - catCooldown)))


async def poll(message: types.Message):
    await bot.send_poll(message.chat.id, 'Го в ' + message.text[3:], is_anonymous=False, options=['Го', 'Та не'])


async def random_command(message: types.message):
    argslist = message.text.split(' ')
    try:
        rand_from = 0
        rand_to = 100
        match len(argslist):
            case 2:
                rand_to = int(argslist[1])
            case 3:
                if argslist[1] > argslist[2]:
                    rand_from = int(argslist[2])
                    rand_to = int(argslist[1])
                else:
                    rand_from = int(argslist[1])
                    rand_to = int(argslist[2])
        await message.answer("Вам выпало число: %2d" % (random.randint(rand_from, rand_to)))
    except TypeError:
        await message.answer('Число - не строка')
    except ValueError:
        await message.answer('Число - не строка')


async def rating(message: types.Message):
    from bd import select_many_filtered_order
    b = 0
    top = {
        '1': None,
        '2': None,
        '3': None,
        '4': None,
        '5': None,
        '6': None,
        '7': None,
        '8': None,
        '9': None,
        '10': None,
    }
    peoples = select_many_filtered_order('messages', 'ChatID', str(message.chat.id), 'Count')
    for i in range(5):
        try:
            a = await bot.get_chat_member(peoples[i][3], peoples[i][1])
            name = a.user.first_name
            last_name = a.user.last_name
            nickname = a.user.username
            if last_name is None:
                if nickname is None:
                    place = name + ' | Сообщений: ' + str(peoples[i][2])
                else:
                    place = name + ' @' + nickname + ' | Сообщений: ' + str(peoples[i][2])
            else:
                place = name + ' ' + last_name + ' @' + nickname + ' | Сообщений: ' + str(peoples[i][2])
            b += 1
        except IndexError:
            place = '-'
            b += 1
        top[str(b)] = place
    await bot.send_message(message.chat.id, text=f'1: {top["1"]}\n2: {top["2"]}\n3: {top["3"]}\n4:' +
                                                 f' {top["4"]}\n5: {top["5"]}\n')


async def inline_mode(query: InlineQuery):
    text = query.query or 'echo'
    if 'ютуб' in text:
        text = text.replace('ютуб ', '')
        links = await searcher(text)
        articles = [types.InlineQueryResultArticle(
            id=hashlib.md5(f'{link["id"]}'.encode()).hexdigest(),
            title=f'{link["title"]}',
            url=f'https://www.youtube.com/watch?v={link["id"]}',
            thumb_url=f'{link["thumbnails"][0]}',
            input_message_content=types.InputTextMessageContent(
                message_text=f'https://www.youtube.com/watch?v={link["id"]}'
            )) for link in links]
        await query.answer(articles, cache_time=60, is_personal=True)


async def random_message(message: types.Message):
    from bd import select_one, select_one_filtered
    id_count = list()
    ids = select_one('ID', 'chats_msg')
    try:
        for i in ids:
            id_count.append(i)
        random_id = random.randint(1, len(id_count))
        await bot.send_message(text=str(select_one_filtered('MSG', 'chats_msg', 'ID',
                                                            random_id)[0][0]), chat_id=message.chat.id)
    except TypeError:
        pass
    await message.delete()


def reg_user(dp: Dispatcher):
    dp.register_message_handler(send_cat, commands=['Котики', 'кот', 'КОТЫ', 'коты', 'КОТИКИ', 'КОТ'])
    dp.register_message_handler(poll, commands=['го'])
    dp.register_message_handler(random_command, commands=['рандом'])
    dp.register_message_handler(rating, commands=['рейтинг'])
    dp.register_inline_handler(inline_mode)
    dp.register_message_handler(random_message, commands=['рандомсооб'])
