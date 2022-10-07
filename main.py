import hashlib
from aiogram import Bot, Dispatcher, executor, types
from cryptography.fernet import Fernet
import random
import requests
import logging
import time
from aiogram.dispatcher.filters import Text
import sqlite3
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InlineQuery, InputTextMessageContent
from youtube_search import YoutubeSearch
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from bd  import parse

load_dotenv()

async def searcher(row):
    res = YoutubeSearch(row, max_results=10).to_dict()
    return res

logging.basicConfig(level=logging.INFO)

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)

# Кулдаун отправки котов (в секундах)
catCooldownSize = 15
catCooldown = 0

# Кулдаун бекапа данных в бд (в секундах)
backupCooldownSize = 5
backupCooldown = 0

# страничка расписания
MyParam = 1

# Кол-во сообщений
all_users = dict()

close_btn = InlineKeyboardButton(text='Закрити', callback_data='close')

inkb1 = InlineKeyboardMarkup()
inkb1.add(InlineKeyboardButton(text='>', callback_data='2'))
inkb1.add(close_btn)

inkb2 = InlineKeyboardMarkup()
inkb2.add(InlineKeyboardButton(text='<', callback_data='1'), InlineKeyboardButton(text='>', callback_data='2'))
inkb2.add(close_btn)

inkb3 = InlineKeyboardMarkup()
inkb3.add(InlineKeyboardButton(text='<', callback_data='1'))
inkb3.add(close_btn)


@dp.inline_handler()
async def inline_mode(query: InlineQuery):
    text = query.query or 'echo'
    if 'ютуб' in text:
        text = text.replace('ютуб', '')
        links = await searcher(text)
        articles = [types.InlineQueryResultArticle(
            id= hashlib.md5(f'{link["id"]}'.encode()).hexdigest(),
            title= f'{link["title"]}',
            url= f'https://www.youtube.com/watch?v={link["id"]}',
            thumb_url= f'{link["thumbnails"][0]}',
            input_message_content= types.InputTextMessageContent(
                message_text=f'https://www.youtube.com/watch?v={link["id"]}'
            ))for link in links]
        await query.answer(articles, cache_time=60, is_personal=True)
    elif 'музыка' in text:
        text = text.replace('музыка', '')
        link = requests.get('https://soundcloud.com/search?q='+text)
        soup = BeautifulSoup(link.content, 'html.parser')
        quots = soup.find_all('li')
        for i in quots:
            pass

def db():
    global con
    global cur
    con = sqlite3.connect('Schedule.db')
    if con:
        print('База подключена')
    cur = con.cursor()



@dp.message_handler(content_types=["document"])
async def get_document(message: types.Message):
    if message.caption == '/raspes':
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        path = file.file_path
        if 'xls' in path:
            await bot.download_file(file_path=path, destination='data.xls')
            parse('data.xls')
        else:
            pass
        await message.delete()


@dp.message_handler(commands=['go'])
async def poll(message: types.Message):
    await bot.send_poll(message.chat.id, 'Го в ' + message.text[3:], is_anonymous=False, options=['Го', 'Та не'])


@dp.message_handler(Text(contains=("Привет"), ignore_case=True))
async def send_welcome(message: types.message):
    lines = ["Добро пожаловать в чат!", "Приветик", "Дарова", "Приятного времяпрепровождения"]
    await message.reply(lines[random.randint(0, len(lines) - 1)])


# task 2
@dp.message_handler(commands=['Котики'])
async def send_cat(message: types.message):
    global catCooldown
    if catCooldown + catCooldownSize <= time.time():
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        catCooldown = time.time()
        await message.answer_photo(response.json()[0]['url'])
    else:
        await message.answer('Осталось %2d секунд' % (catCooldownSize - (time.time() - catCooldown)))


# task 3
@dp.message_handler(commands=['Рандом'])
async def random_command(message: types.message):
    argslist = message.text.split(' ')
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


@dp.message_handler(commands=['Расписание'])
async def schedule_command(message: types.message):
    cur.execute(
        'CREATE TABLE IF NOT EXISTS raspesmsg (ID INTEGER PRIMARY KEY, MSGID varchar(100), CHATID varchar(100), '
        'ARG1 varchar(20), '
        'ARG2 varchar(20), PAGE INTEGER)')
    groupname = message.text
    groupname = groupname[12:]
    groupname = groupname.replace('-', '_')
    groupname = groupname.split(' ')
    await message.delete()
    mes = await bot.send_message(message.chat.id, 'Loading')
    if len(groupname) == 2:
        cur.execute('INSERT INTO raspesmsg (MSGID, CHATID, ARG1, ARG2, PAGE) VALUES (?, ?, ?, ?, ?)',
                    [mes.message_id, mes.chat.id, groupname[0], groupname[1], 1])
    else:
        cur.execute('INSERT INTO raspesmsg (MSGID, CHATID, ARG1, ARG2, PAGE) VALUES (?, ?, ?, ?, ?)',
                    [mes.message_id, mes.chat.id, groupname[0], 1, 1])
    con.commit()
    await get_schedule(groupname, mes.message_id, message.chat.id, 1)


@dp.callback_query_handler()
async def pages(callback: CallbackQuery):
    MyParam = int(
        cur.execute('SELECT * FROM raspesmsg WHERE (MSGID) = (?)', [callback.message.message_id]).fetchall()[0][5])
    if callback.data == '1':
        if MyParam != 1:
            MyParam -= 1
            cur.execute(f'UPDATE raspesmsg SET PAGE = {MyParam} WHERE MSGID={callback.message.message_id}')
            con.commit()
            await get_schedule(callback.message, callback.message.message_id, callback.message.chat.id, MyParam)
            return await callback.answer('Назад')
        else:
            MyParam = 1
            cur.execute(f'UPDATE raspesmsg SET PAGE = {MyParam} WHERE MSGID={callback.message.message_id}')
            con.commit()
            await get_schedule(callback.message, callback.message.message_id, callback.message.chat.id, MyParam)
            return await callback.answer('Воскресенье выходной')
    elif callback.data == '2':
        if MyParam != 5:
            MyParam += 1
            cur.execute(f'UPDATE raspesmsg SET PAGE = {MyParam} WHERE MSGID={callback.message.message_id}')
            con.commit()
            await get_schedule(callback.message, callback.message.message_id, callback.message.chat.id, MyParam)
            return await callback.answer('Вперёд')
        else:
            MyParam = 5
            cur.execute(f'UPDATE raspesmsg SET PAGE = {MyParam} WHERE MSGID={callback.message.message_id}')
            con.commit()
            await get_schedule(callback.message, callback.message.message_id, callback.message.chat.id, MyParam)

            return await callback.answer('Уже пятница')
    if callback.data == 'close':
        message = callback.message
        cur.execute(f'DELETE FROM raspesmsg WHERE MSGID={callback.message.message_id};')
        con.commit()
        await message.delete()
        return await callback.answer('Видалив')


async def get_schedule(msg, msg_id, chat_id, MyParam):
    global cur
    data = cur.execute('SELECT * FROM raspesmsg WHERE (MSGID) = (?)', [msg_id]).fetchall()
    MyParam = int(data[0][5])
    subgroupid = int(data[0][4])
    args = [data[0][3]]
    mond = cur.execute(f'SELECT * FROM {args[0]}').fetchall()
    day = {
        'День': None,
        'Подгруппа': None,
        'ч1': None,
        'ч2': None,
        'ч3': None,
        'ч4': None,
        'ч5': None,
        'з1': None,
        'з2': None,
        'з3': None,
        'з4': None,
        'з5': None
    }  # типо такого

    b = 1
    c = 1
    for i in mond:
        match MyParam:
            case 1:
                # if MyParam == 1:
                day['День'] = 'Понеділок'
                if i[3] == 1:  # Вот эти 3 строки менять
                    if i[2] == subgroupid:
                        day['Подгруппа'] = subgroupid
                        if i[5] == 1:
                            if b == 1:
                                day['ч1'] = i[1]
                            elif b == 2:
                                day['ч2'] = i[1]
                            elif b == 3:
                                day['ч3'] = i[1]
                            elif b == 4:
                                day['ч4'] = i[1]
                            elif b == 5:
                                day['ч5'] = i[1]
                            b += 1
                        elif i[5] == 2:
                            if c == 1:
                                day['з1'] = i[1]
                            elif c == 2:
                                day['з2'] = i[1]
                            elif c == 3:
                                day['з3'] = i[1]
                            elif c == 4:
                                day['з4'] = i[1]
                            elif c == 5:
                                day['з5'] = i[1]
                            c += 1
            # elif MyParam == 2:#
            case 2:
                day['День'] = 'Вівторок'  #
                if i[3] == 2:  # Вот эти 3 строки менять
                    if i[2] == subgroupid:
                        day['Подгруппа'] = subgroupid
                        if i[5] == 1:
                            if b == 1:
                                day['ч1'] = i[1]
                            elif b == 2:
                                day['ч2'] = i[1]
                            elif b == 3:
                                day['ч3'] = i[1]
                            elif b == 4:
                                day['ч4'] = i[1]
                            elif b == 5:
                                day['ч5'] = i[1]
                            b += 1
                        elif i[5] == 2:
                            if c == 1:
                                day['з1'] = i[1]
                            elif c == 2:
                                day['з2'] = i[1]
                            elif c == 3:
                                day['з3'] = i[1]
                            elif c == 4:
                                day['з4'] = i[1]
                            elif c == 5:
                                day['з5'] = i[1]
                            c += 1
            case 3:
                day['День'] = 'Середа'  #
                if i[3] == 3:  # Вот эти 3 строки менять
                    if i[2] == subgroupid:
                        day['Подгруппа'] = subgroupid
                        if i[5] == 1:
                            if b == 1:
                                day['ч1'] = i[1]
                            elif b == 2:
                                day['ч2'] = i[1]
                            elif b == 3:
                                day['ч3'] = i[1]
                            elif b == 4:
                                day['ч4'] = i[1]
                            elif b == 5:
                                day['ч5'] = i[1]
                            b += 1
                        elif i[5] == 2:
                            if c == 1:
                                day['з1'] = i[1]
                            elif c == 2:
                                day['з2'] = i[1]
                            elif c == 3:
                                day['з3'] = i[1]
                            elif c == 4:
                                day['з4'] = i[1]
                            elif c == 5:
                                day['з5'] = i[1]
                            c += 1
            case 4:
                day['День'] = 'Четверг'  #
                if i[3] == 4:  # Вот эти 3 строки менять
                    if i[2] == subgroupid:
                        day['Подгруппа'] = subgroupid
                        if i[5] == 1:
                            if b == 1:
                                day['ч1'] = i[1]
                            elif b == 2:
                                day['ч2'] = i[1]
                            elif b == 3:
                                day['ч3'] = i[1]
                            elif b == 4:
                                day['ч4'] = i[1]
                            elif b == 5:
                                day['ч5'] = i[1]
                            b += 1
                        elif i[5] == 2:
                            if c == 1:
                                day['з1'] = i[1]
                            elif c == 2:
                                day['з2'] = i[1]
                            elif c == 3:
                                day['з3'] = i[1]
                            elif c == 4:
                                day['з4'] = i[1]
                            elif c == 5:
                                day['з5'] = i[1]
                            c += 1
            case 5:
                day['День'] = "П'ятниця"  #
                if i[3] == 5:  # Вот эти 3 строки менять
                    if i[2] == subgroupid:
                        day['Подгруппа'] = subgroupid
                        if i[5] == 1:
                            if b == 1:
                                day['ч1'] = i[1]
                            elif b == 2:
                                day['ч2'] = i[1]
                            elif b == 3:
                                day['ч3'] = i[1]
                            elif b == 4:
                                day['ч4'] = i[1]
                            elif b == 5:
                                day['ч5'] = i[1]
                            b += 1
                        elif i[5] == 2:
                            if c == 1:
                                day['з1'] = i[1]
                            elif c == 2:
                                day['з2'] = i[1]
                            elif c == 3:
                                day['з3'] = i[1]
                            elif c == 4:
                                day['з4'] = i[1]
                            elif c == 5:
                                day['з5'] = i[1]
                            c += 1
    if MyParam == 5:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                    text=f'{day["День"]}\nПідгруппа: {day["Подгруппа"]}\n\nЧисельник:\n1: {day["ч1"]}\n2: {day["ч2"]}\n3: {day["ч3"]}\n4: {day["ч4"]}\n5: {day["ч5"]}\n\nЗнаменник:\n1: {day["з1"]}\n2: {day["з2"]}\n3: {day["з3"]}\n4: {day["з4"]}\n5: {day["з5"]}\n',
                                    reply_markup=inkb3)
    elif MyParam == 1:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                    text=f'{day["День"]}\nПідгруппа: {day["Подгруппа"]}\n\nЧисельник:\n1: {day["ч1"]}\n2: {day["ч2"]}\n3: {day["ч3"]}\n4: {day["ч4"]}\n5: {day["ч5"]}\n\nЗнаменник:\n1: {day["з1"]}\n2: {day["з2"]}\n3: {day["з3"]}\n4: {day["з4"]}\n5: {day["з5"]}\n',
                                    reply_markup=inkb1)
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                    text=f'{day["День"]}\nПідгруппа: {day["Подгруппа"]}\n\nЧисельник:\n1: {day["ч1"]}\n2: {day["ч2"]}\n3: {day["ч3"]}\n4: {day["ч4"]}\n5: {day["ч5"]}\n\nЗнаменник:\n1: {day["з1"]}\n2: {day["з2"]}\n3: {day["з3"]}\n4: {day["з4"]}\n5: {day["з5"]}\n',
                                    reply_markup=inkb2)


def update_database():
    cur.execute('CREATE TABLE IF NOT EXISTS messages(ID INTEGER PRIMARY KEY, User VARCHAR(100), Count INTEGER)')
    for i in all_users:
        try:
            cur.execute(f"UPDATE messages SET Count = {all_users[i]} WHERE User ={i}")
        except:
            cur.execute('INSERT INTO messages (User, Count) VALUES (?, ?)', [i, all_users[i]])
        con.commit()


@dp.message_handler()
async def count_messages(message: types.message):
    global all_users
    global backupCooldown
    if backupCooldown + backupCooldownSize <= time.time():
        update_database()
        backupCooldown = time.time()
    if all_users.get(message.from_user.id) is None:
        all_users[message.from_user.id] = 1
    else:
        all_users[message.from_user.id] += 1

    for i in all_users:
        print(all_users)
    #print(all_users[message.from_user.id])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=db())
