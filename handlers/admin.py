from create_bot import bot, dp
from aiogram import types, Dispatcher


async def check(message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.is_chat_admin()


async def connect_chat_to_bot(message: types.Message):
    from bd import select_one, insert_universal
    if await check(message):
        ids = list()
        try:
            for i in select_one('CHATID', 'chats'):
                ids.append(i[0])
        except TypeError:
            pass
        if str(message.chat.id) in ids:
            pass
        else:
            insert_universal('chats', 'CHATID', [message.chat.id])
        #     cur.execute('INSERT INTO chats (CHATID) VALUES (?)', [message.chat.id])
        # con.commit()


async def disconect_from_bot(message: types.Message):
    from bd import delete_from_table
    if await check(message):
        id_msg = message.chat.id
        delete_from_table('chats', 'CHATID', id_msg)
        delete_from_table('chats_msg', 'CHATID', id_msg)

        # cur.execute('DELETE FROM chats WHERE CHATID = (?)', [id_msg])
        # cur.execute('DELETE FROM chats_msg WHERE CHATID = (?)', [id_msg])
        # con.commit()


async def get_document(message: types.Message):
    from bd import parse
    if await check(message):
        if message.caption == '/raspes':
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            path = file.file_path
            if 'xls' in path:
                await bot.download_file(file_path=path, destination='data.xls')
                await parse('data.xls')
            else:
                pass
            await message.delete()


def reg_admin(dp: Dispatcher):
    dp.register_message_handler(connect_chat_to_bot, commands=['connect'])
    dp.register_message_handler(disconect_from_bot, commands=['disconnect'])
    dp.register_message_handler(get_document, content_types=['document'])
