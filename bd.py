import xlrd
import sqlite3

def bd_start():
    global cur, con
    con = sqlite3.connect('Schedule.db')
    if con:
        print('Connect DB!')
    cur = con.cursor()

    for i in range(int(book.nsheets)):
        sh = book.sheet_by_index(i)
        for j in range(sh.ncols):
            if getValue(sh, 6, j) is None:
                group1 = sh.cell_value(6, j)

            else:
                group1 = getValue(sh, 6, j)
            try:
                cur.execute('DROP TABLE ' + group1.replace('-', '_'))
                con.commit()
            except:
                pass


def insert(group, value, subgroupId, day, c, week):
    cur.execute('INSERT INTO ' + group + ' ([Name], [subgroup], [day], [count], [week]) VALUES (?, ?, ?, ?, ?)',
                [value, subgroupId, day, c, week])
    con.commit()

def getValue(sh, x, y):
    for i in range(len(sh.merged_cells)):
        if sh.merged_cells[i][0] < x + 1 <= sh.merged_cells[i][1] and sh.merged_cells[i][2] < y + 1 <= \
                sh.merged_cells[i][3]:
            return sh.cell_value(sh.merged_cells[i][0], sh.merged_cells[i][2])


def get_numberator(sh, x, y, j, group, subgroupId, day):
    c = 0
    for f in range(x, y):
        values = sh.row_values(f)
        value = sh.cell_value(f, j)
        if value == '' and 'Чис.' in values:
            c += 1
            value = getValue(sh, f, j)
            if value is None:
                insert(group, '-', subgroupId, day, c, 1)
            elif value == '':
                insert(group, '-', subgroupId, day, c, 1)
            else:
                insert(group, value, subgroupId, day, c, 1)
        elif value != '' and 'Чис.' in values:
            c += 1
            insert(group, value, subgroupId, day, c, 1)


def get_denominator(sh, x, y, j, group, subgroupId, day):
    c = 0
    for f in range(x, y):
        values = sh.row_values(f)
        value = sh.cell_value(f, j)
        if value == '' and 'Знам.' in values:
            c += 1
            value = getValue(sh, f, j)
            if value is None:
                insert(group, '-', subgroupId, day, c, 2)
            elif value == '':
                insert(group, '-', subgroupId, day, c, 2)
            else:
                insert(group, value, subgroupId, day, c, 2)
        elif value != '' and 'Знам.' in values:
            c += 1
            insert(group, value, subgroupId, day, c, 2)


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
                if getValue(sh, 6, j) is None:
                    group = sh.cell_value(6, j)
                else:
                    group = getValue(sh, 6, j)

                if group == temp:
                    subgroupId = 2
                else:
                    subgroupId = 1
                if group != '':
                    temp = group
                    cur.execute('CREATE TABLE IF NOT EXISTS ' + group.replace('-', '_') + ' (Id INTEGER PRIMARY KEY, Name varchar[200] NOT NULL, subgroup INTEGER, day INTEGER, count INTEGER, week INTEGER)')
                    con.commit()
                    advanced_name = group.replace('-', '_')
                    get_numberator(sh, 10, 19, j, advanced_name, subgroupId, 1)
                    get_denominator(sh, 10, 20, j, advanced_name, subgroupId, 1)
                    get_numberator(sh, 21, 30, j, advanced_name, subgroupId, 2)
                    get_denominator(sh, 21, 31, j, advanced_name, subgroupId, 2)
                    get_numberator(sh, 32, 41, j, advanced_name, subgroupId, 3)
                    get_denominator(sh, 32, 42, j, advanced_name, subgroupId, 3)
                    get_numberator(sh, 43, 52, j, advanced_name, subgroupId, 4)
                    get_denominator(sh, 43, 53, j, advanced_name, subgroupId, 4)
                    get_numberator(sh, 54, 63, j, advanced_name, subgroupId, 5)
                    get_denominator(sh, 54, 64, j, advanced_name, subgroupId, 5)
                else:
                    pass
            else:
                pass


def parse(text):
    global book
    book = xlrd.open_workbook('data.xls', formatting_info=True)
    bd_start()
    get_groups()
