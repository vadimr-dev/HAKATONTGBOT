import xlrd
import sqlite3
from handlers.counter import load_counter

book = ''
con = ''
cur = ''


def bd_start():
    global cur, con
    con = sqlite3.connect('Schedule.db')
    if con:
        print('Connect DB!')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS messages(ID INTEGER PRIMARY KEY, User VARCHAR(100),\
                    Count INTEGER, ChatID VARCHAR(100))')
    cur.execute(f'CREATE TABLE IF NOT EXISTS chats_msg (ID INTEGER PRIMARY KEY, MSG VARCHAR(600),'
                f' CHATID VARCHAR(100))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS raspesmsg (ID INTEGER PRIMARY KEY, MSGID varchar(100), CHATID varchar(100), '
        'ARG1 varchar(20), '
        'ARG2 varchar(20), PAGE INTEGER)')
    cur.execute(f'CREATE TABLE IF NOT EXISTS chats (ID INTEGER PRIMARY KEY, CHATID VARCHAR(100))')
    con.commit()
    load_counter()


def select_many(text):
    try:
        a = cur.execute(f'SELECT * FROM {text}').fetchall()
        return a
    except sqlite3.OperationalError:
        pass


def select_one(line1, line2):
    try:
        a = cur.execute(f'SELECT {line1} FROM {line2}').fetchall()
        return a
    except sqlite3.OperationalError:
        pass


def select_one_filtered(line1, line2, line3, line4):
    try:
        a = cur.execute(f'SELECT {line1} FROM {line2} WHERE ({line3}) = ({line4})').fetchall()
        return a
    except sqlite3.OperationalError:
        pass


def select_many_filtered_order(line1, line2, line3, line4):
    try:
        a = cur.execute(f'SELECT * FROM {line1} WHERE ({line2}) = ({line3}) ORDER BY {line4} DESC').fetchall()
        return a
    except sqlite3.OperationalError:
        pass


def select_many_filtered(line1, line2, line3):
    try:
        a = cur.execute(f'SELECT * FROM {line1} WHERE ({line2}) = ({line3})').fetchall()
        return a
    except sqlite3.OperationalError:
        pass


def delete_from_table(table, condition, conditionvalue):
    cur.execute(f'DELETE FROM {table} WHERE ({condition}) = ({conditionvalue})')
    con.commit()


def insert_universal(table, valuesname, values):
    match len(values):
        case 1:
            cur.execute('INSERT INTO ' + str(table) + ' (' + str(valuesname) + ') VALUES (' + str(values[0]) + ')')
        case 2:
            cur.execute('INSERT INTO ' + str(table) + ' ( ' + str(valuesname[0]) + ', ' + str(
                valuesname[1]) + ') VALUES (?, ?)', [values[0], values[1]])
        case 3:
            cur.execute(
                'INSERT INTO ' + str(table) + ' (' + str(valuesname[0]) + ', ' + str(valuesname[1]) + ', ' + str(
                    valuesname[2]) + ') VALUES (?,?,?)', [values[0], values[1], values[2]])
        case 4:
            cur.execute('INSERT INTO ' + str(
                table) + ' ([' + str(valuesname[0]) + '], [' + str(valuesname[1]) + '], [' + str(valuesname[2]) + '], [' + str(
                valuesname[3]) + ']) VALUES (?, ?, ?, ?)', [values[0], values[1], values[2], values[3]])
        case 5:
            cur.execute('INSERT INTO ' + str(
                table) + ' ([' + str(valuesname[0]) + '], [' + str(valuesname[1]) + '], [' + str(valuesname[2]) + '], [' + str(
                valuesname[3]) + '], [' + str(valuesname[4]) + ']) VALUES (?, ?, ?, ?, ?)', [values[0], values[1], values[2], values[3], values[4]])
    con.commit()


def update_universal(table, setname, setvalue, coionname, conditionvalue):
    cur.execute(f'UPDATE {table} SET {setname} = {setvalue} WHERE {coionname} = {conditionvalue}')
    con.commit()


def update_2_condition(table, setname, setvalue, conditionname, conditionvalue, conditionname2, conditionvalue2):
    cur.execute(
        f'UPDATE {table} SET {setname} = {setvalue} WHERE {conditionname} = {conditionvalue} AND {conditionname2} = {conditionvalue2}')
    con.commit()


def drop_tables():
    for i in range(int(book.nsheets)):
        sh = book.sheet_by_index(i)
        for j in range(sh.ncols):
            if get_value(sh, 6, j) is None:
                group1 = sh.cell_value(6, j)

            else:
                group1 = get_value(sh, 6, j)
            try:
                cur.execute('DROP TABLE ' + group1.replace('-', '_'))
                con.commit()
            except sqlite3.OperationalError:
                pass


def insert(groupname, value, subgroup_id, day, c, week):
    cur.execute('INSERT INTO ' + groupname + ' ([Name], [subgroup], [day], [count], [week]) VALUES (?, ?, ?, ?, ?)',
                [value, subgroup_id, day, c, week])
    con.commit()


def get_value(sh, x, y):
    for i in range(len(sh.merged_cells)):
        if sh.merged_cells[i][0] < x + 1 <= sh.merged_cells[i][1] and sh.merged_cells[i][2] < y + 1 <= \
                sh.merged_cells[i][3]:
            return sh.cell_value(sh.merged_cells[i][0], sh.merged_cells[i][2])


def get_numberator(sh, x, y, j, groupname, subgroup_id, day):
    c = 0
    for f in range(x, y):
        values = sh.row_values(f)
        value = sh.cell_value(f, j)
        if value == '' and 'Чис.' in values:
            c += 1
            value = get_value(sh, f, j)
            if value is None:
                insert(groupname, '-', subgroup_id, day, c, 1)
            elif value == '':
                insert(groupname, '-', subgroup_id, day, c, 1)
            else:
                insert(groupname, value, subgroup_id, day, c, 1)
        elif value != '' and 'Чис.' in values:
            c += 1
            insert(groupname, value, subgroup_id, day, c, 1)


def get_denominator(sh, x, y, j, groupname, subgroup_id, day):
    c = 0
    for f in range(x, y):
        values = sh.row_values(f)
        value = sh.cell_value(f, j)
        if value == '' and 'Знам.' in values:
            c += 1
            value = get_value(sh, f, j)
            if value is None:
                insert(groupname, '-', subgroup_id, day, c, 2)
            elif value == '':
                insert(groupname, '-', subgroup_id, day, c, 2)
            else:
                insert(groupname, value, subgroup_id, day, c, 2)
        elif value != '' and 'Знам.' in values:
            c += 1
            insert(groupname, value, subgroup_id, day, c, 2)


temp = 'Миша дай 1 место пж'
group = 'Женя дай 1 место пж'


def get_groups():
    global temp
    global group
    for i in range(int(book.nsheets)):
        sh = book.sheet_by_index(i)
        for j in range(sh.ncols):
            xfx = book.xf_list[sh.cell_xf_index(6, j)]
            if xfx.background.background_colour_index == 65:
                if get_value(sh, 6, j) is None:
                    group = sh.cell_value(6, j)
                else:
                    group = get_value(sh, 6, j)

                if group == temp:
                    subgroup_id = 2
                else:
                    subgroup_id = 1
                if group != '':
                    temp = group
                    cur.execute('CREATE TABLE IF NOT EXISTS ' + group.replace('-', '_') + ' (Id INTEGER PRIMARY KEY,\
                     Name varchar[200] NOT NULL, subgroup INTEGER, day INTEGER, count INTEGER, week INTEGER)')
                    con.commit()
                    advanced_name = group.replace('-', '_')
                    get_numberator(sh, 10, 19, j, advanced_name, subgroup_id, 1)
                    get_denominator(sh, 10, 20, j, advanced_name, subgroup_id, 1)
                    get_numberator(sh, 21, 30, j, advanced_name, subgroup_id, 2)
                    get_denominator(sh, 21, 31, j, advanced_name, subgroup_id, 2)
                    get_numberator(sh, 32, 41, j, advanced_name, subgroup_id, 3)
                    get_denominator(sh, 32, 42, j, advanced_name, subgroup_id, 3)
                    get_numberator(sh, 43, 52, j, advanced_name, subgroup_id, 4)
                    get_denominator(sh, 43, 53, j, advanced_name, subgroup_id, 4)
                    get_numberator(sh, 54, 63, j, advanced_name, subgroup_id, 5)
                    get_denominator(sh, 54, 64, j, advanced_name, subgroup_id, 5)
                else:
                    pass
            else:
                pass


async def parse(text):
    global book
    bd_start()
    book = xlrd.open_workbook(text, formatting_info=True)
    drop_tables()
    get_groups()
