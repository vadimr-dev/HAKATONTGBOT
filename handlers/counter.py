import time
from create_bot import dp, bot
from aiogram import types, Dispatcher


all_users = dict()
user = dict()
backupCooldownSize = 5
backupCooldown = 0


def load_counter():
    from bd import select_many
    users_for_dict = select_many('messages')
    try:
        for i in users_for_dict:
            user[int(i[1])] = i[2]
            all_users[int(i[3])] = user
    except TypeError:
        pass
    except IndexError:
        pass


def update_database():
    from bd import select_one, insert_universal, update_2_condition
    ids = list()
    for i in select_one('USER', 'messages'):
        ids.append(i[0])
    for i in all_users:
        for j in all_users[i]:
            if str(j) in ids:
                update_2_condition('messages', 'Count', all_users[i][j], 'User', j, ' ChatID', i)
            #  cur.execute(f"UPDATE messages SET Count = {all_users[i][j]} WHERE User ={j} AND ChatID = {i}")
            else:
                insert_universal('messages', ['User', 'Count', 'ChatID'], [j, all_users[i][j], i])
                # cur.execute('INSERT INTO messages (User, Count, ChatID) VALUES (?, ?, ?)', [j, all_users[i][j], i])
        #    con.commit()


async def count_messages(message: types.message):
    from bd import select_one, insert_universal
    global backupCooldown
    if backupCooldown + backupCooldownSize <= time.time():
        update_database()
        backupCooldown = time.time()
    try:
        statement = all_users[message.chat.id][message.from_user.id]
        user[message.from_user.id] += 1
        all_users[message.chat.id] = user
    except KeyError:
        user[message.from_user.id] = 1
        all_users[message.chat.id] = user
    # chat part
    ids = list()

    for i in select_one('CHATID', 'chats'):
        ids.append(i[0])
    if str(message.chat.id) in ids:
        insert_universal('chats_msg', ['MSG', 'CHATID'], [message.text, message.chat.id])


def reg_count(dp: Dispatcher):
    dp.register_message_handler(count_messages)
