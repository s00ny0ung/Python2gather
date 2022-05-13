# -*- coding: utf-8 -*-
import mvc_exceptions as mvc_exc

import psycopg2
from psycopg2 import OperationalError, IntegrityError, ProgrammingError

# DB_name = 'template1'

def connect_to_db(db=None):
    # if db is None:
    #     mydb = 'memory'
    #     print('New connection to in-memory SQLite DB...')
    # else:
    #     mydb = '{}.db'.format(db)
    #     print('New connection to SQLite DB...')
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=1234 port=5432")
    return connection

def disconnect_from_db(db=None):
    if db is not DB_name:
        print('You are trying to disconnect from a wrong DB')
    if conn is not None:
       conn.close()

def connect(func):
    def inner_func(conn, *args, **kwargs):
        try:
            conn.execute(
                'SELECT name FROM temp_table WHERE type="table";'
            )
        except (AttributeError, ProgrammingError):
            conn = connect_to_db()
        return func(conn, *args, **kwargs)
    return inner_func

@connect
def create_table(conn, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql = 'CREATE TABLE {0} (rowid SERIAL PRIMARY KEY, title TEXT UNIQUE, writer TEXT, painter TEXT, publisher TEXT, position INTEGER)'.format(table_name)
    try:
        cur.execute(sql)
        conn.commit()
    except OperationalError as e:
        conn.rollback()
        print(e)

def scrub(input_string):
    return ''.join(k for k in input_string if k.isalnum())

@connect
def insert_one(conn, title, writer, painter, publisher, position, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql = "INSERT INTO {} (title, writer, painter, publisher, position) VALUES (%s,%s,%s,%s,%s)".format(table_name)
    try:
        cur.execute(sql, (title, writer, painter, publisher, position))
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        raise mvc_exc.ItemAlreadyStored(
            '{}: "{}" already stored in table "{}"'.format(e, title, table_name)
        )
    # sql injection 발생할 수 있음, 어떻게 방지할 수 있을까?

@connect
def insert_many(conn, items, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql = "INSERT INTO {} (title, writer, painter, publisher, position) VALUES (%s,%s,%s,%s,%s)".format(table_name)
    entries = list()
    for x in items:
        entries.append((x['title'], x['writer'], x['painter'], x['publisher'], x['position']))
    try:
        cur.executemany(sql, entries)
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        print('{}: at least one in {} was already stored in table "{}"'
              .format(e, [x['title'] for x in items], table_name))

def tuple_to_dict(mytuple):
    mydict = dict()
    mydict['id'] = mytuple[0]
    mydict['title'] = mytuple[1]
    mydict['writer'] = mytuple[2]
    mydict['painter'] = mytuple[3]
    mydict['publisher'] = mytuple[4]
    mydict['position'] = mytuple[5]
    return mydict

@connect
def select_one(conn, item_name, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    item_name = scrub(item_name)
    sql = "SELECT * FROM {} WHERE title='{}'".format(table_name, item_name)
    cur.execute(sql)
    # conn.commit()
    result = cur.fetchone()
    if result is not None:
        return tuple_to_dict(result)
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t read "{}" because it\'s not stored in table "{}"'
            .format(item_name, table_name)
        )

@connect
def select_all(conn, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql = 'SELECT * FROM {}'.format(table_name)
    cur.execute(sql)
    results = cur.fetchall()
    return list(map(lambda x: tuple_to_dict(x), results))

@connect
def update_one(conn, title, writer, painter, publisher, position, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql_check = "SELECT EXISTS(SELECT 1 FROM {} WHERE title='{}' LIMIT 1)"\
        .format(table_name, title)
    sql_update = 'UPDATE {} SET writer=%s, painter=%s, publisher=%s, position=%s WHERE title=%s'\
        .format(table_name)
    cur.execute(sql_check, (title,))
    result = cur.fetchone()
    if result[0]:
        cur.execute(sql_update, (writer, painter, publisher, position, title))
        conn.commit()
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t update "{}" because it\'s not stored in table "{}"'
            .format(title, table_name))


@connect
def delete_one(conn, title, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql_check = 'SELECT EXISTS(SELECT 1 FROM {} WHERE title=%s LIMIT 1)'\
        .format(table_name)
    table_name = scrub(table_name)
    sql_delete = 'DELETE FROM {} WHERE title=%s'.format(table_name)
    cur.execute(sql_check, (title,))
    result = cur.fetchone()
    if result[0]:
        cur.execute(sql_delete, (title,))
        conn.commit()
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t delete "{}" because it\'s not stored in table "{}"'
            .format(title, table_name))



def main():
    table_name = 'items'
    conn = connect_to_db()

    # create_table(conn, table_name)
    myitems = [
        {'title':'여름이온다4', 'writer':'이수지', 'painter':'이수지', 'publisher':'비룡소', 'position':'2'},
        {'title':'코끼리비밀요원4', 'writer':'오원 맥클로플린', 'painter':'로스 콜린스', 'publisher':'다림', 'position':'3'},
        {'title':'그들은결국브레멘에가지못했다4', 'writer':'루리', 'painter':'루리', 'publisher':'비룡소', 'position':'4'}
    ]

    insert_many(conn, myitems, table_name='items')
    insert_one(conn, '우리는안녕5',  writer = '박준', painter='김한나', publisher='난다요', position = '4', table_name='items')
    print('SELECT 우리는안녕2')
    print(select_one(conn, '여름이온다1', table_name='items'))
    print('SELECT ALL')
    print(select_all(conn, table_name='items'))
    print('update!')
    print(update_one(conn, '우리는안녕',  writer = '박준', painter='김한나', publisher='난다요', position = '1', table_name='items'))
    print('delete!')
    print(delete_one(conn, '여름이온다1',table_name='items'))

    conn.close()

if __name__ == '__main__':
    main()