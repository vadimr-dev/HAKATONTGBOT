from create_bot import bot, dp
from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


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


async def show_day(day, chat_id, msg_id, kb):
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=msg_id,
                                text=f'{day["День"]}\nПідгруппа: ' +
                                     f'{day["Подгруппа"]}\n\nЧисельник:\n1:' + f'{day["ч1"]}\n2: {day["ч2"]}\n3: ' +
                                     f'{day["ч3"]}\n4: {day["ч4"]}\n5: {day["ч5"]}\n\nЗнаменник:\n1: {day["з1"]}\n2: ' +
                                     f'{day["з2"]}\n3: {day["з3"]}\n4: {day["з4"]}\n5:{day["з5"]}\n',
                                reply_markup=kb)


async def get_day(i, b, c, day, subgroupid):
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
        return day, b, c


async def get_schedule(msg_id, chat_id):
    from bd import select_many, select_many_filtered
    data = select_many_filtered('raspesmsg', 'MSGID', msg_id)
    my_param = int(data[0][5])
    subgroupid = int(data[0][4])
    args = [data[0][3]]
    mond = select_many(args[0])
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
    if subgroupid > 2:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Куда полез?')
    else:
        b = 1
        c = 1
        for i in mond:
            match my_param:
                case 1:
                    day['День'] = 'Понеділок'
                    if i[3] == 1:
                        try:
                            day, b, c = await get_day(i, b, c, day, subgroupid)
                        except TypeError:
                            pass
                case 2:
                    day['День'] = 'Вівторок'  #
                    if i[3] == 2:  # Вот эти 3 строки менять
                        try:
                            day, b, c = await get_day(i, b, c, day, subgroupid)
                        except TypeError:
                            pass
                case 3:
                    day['День'] = 'Середа'  #
                    if i[3] == 3:  # Вот эти 3 строки менять
                        try:
                            day, b, c = await get_day(i, b, c, day, subgroupid)
                        except TypeError:
                            pass
                case 4:
                    day['День'] = 'Четверг'  #
                    if i[3] == 4:  # Вот эти 3 строки менять
                        try:
                            day, b, c = await get_day(i, b, c, day, subgroupid)
                        except TypeError:
                            pass
                case 5:
                    day['День'] = "П'ятниця"  #
                    if i[3] == 5:  # Вот эти 3 строки менять
                        try:
                            day, b, c = await get_day(i, b, c, day, subgroupid)
                        except TypeError:
                            pass
        if my_param == 5:
            await show_day(day, chat_id, msg_id, inkb3)
        elif my_param == 1:
            await show_day(day, chat_id, msg_id, inkb1)
        else:
            await show_day(day, chat_id, msg_id, inkb2)


async def schedule_command(message: types.message):
    from bd import insert_universal
    groupname = message.text
    groupname = groupname[12:]
    groupname = groupname.replace('-', '_')
    groupname = groupname.split(' ')
    print(groupname)
    await message.delete()
    mes = await bot.send_message(message.chat.id, 'Loading')
    if len(groupname) == 2:
        insert_universal('raspesmsg', ['MSGID', 'CHATID', 'ARG1', 'ARG2', 'PAGE'], [mes.message_id, mes.chat.id, groupname[0], groupname[1], 1])
        # cur.execute('INSERT INTO raspesmsg (MSGID, CHATID, ARG1, ARG2, PAGE) VALUES (?, ?, ?, ?, ?)',
        #            [mes.message_id, mes.chat.id, groupname[0], groupname[1], 1])
    else:
        insert_universal('raspesmsg', ['MSGID', 'CHATID', 'ARG1', 'ARG2', 'PAGE'],  [mes.message_id, mes.chat.id, groupname[0], 1, 1])
        # cur.execute('INSERT INTO raspesmsg (MSGID, CHATID, ARG1, ARG2, PAGE) VALUES (?, ?, ?, ?, ?)',
        #            [mes.message_id, mes.chat.id, groupname[0], 1, 1])
    # con.commit()
    await get_schedule(mes.message_id, message.chat.id)


async def pages(callback: CallbackQuery):
    from bd import select_many_filtered, update_universal, delete_from_table
    my_param = int(select_many_filtered('raspesmsg', 'MSGID', callback.message.message_id)[0][5])
    if callback.data == '1':
        if my_param != 1:
            my_param -= 1
            update_universal('raspesmsg', 'PAGE', my_param, 'MSGID', callback.message.message_id)
            await get_schedule(callback.message.message_id, callback.message.chat.id)
            return await callback.answer('Назад')
        else:
            my_param = 1
            update_universal('raspesmsg', 'PAGE', my_param, 'MSGID', callback.message.message_id)
            await get_schedule(callback.message.message_id, callback.message.chat.id)
            return await callback.answer('Воскресенье выходной')

    elif callback.data == '2':
        if my_param != 5:
            my_param += 1
            update_universal('raspesmsg', 'PAGE', my_param, 'MSGID', callback.message.message_id)
            await get_schedule(callback.message.message_id, callback.message.chat.id)
            return await callback.answer('Вперёд')
        else:
            my_param = 5
            update_universal('raspesmsg', 'PAGE', my_param, 'MSGID', callback.message.message_id)
            await get_schedule(callback.message.message_id, callback.message.chat.id)

            return await callback.answer('Уже пятница')
    if callback.data == 'close':
        message = callback.message
        delete_from_table('raspesmsg', 'MSGID', callback.message.message_id)
        # cur.execute(f'DELETE FROM raspesmsg WHERE MSGID={callback.message.message_id}')
        # con.commit()
        await message.delete()
        return await callback.answer('Видалив')


def reg_schedule(dp: Dispatcher):
    dp.register_message_handler(schedule_command, commands=['расписание'])
    dp.register_callback_query_handler(pages)
