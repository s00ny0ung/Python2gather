from lib2to3.pgen2.token import NAME
import psycopg2
from psycopg2 import InternalError, OperationalError, IntegrityError, ProgrammingError
import mvc_exceptions as mvc_exc

# db = psycopg2.connect(host='localhost', dbname='postgres',
#                       user='postgres', password='postgres', port=5432)
# cur = db.cursor()
# cur.execute("select version()")
# print(cur.fetchone())

DB_name = 'myDB'

def connect_to_db(db=None):
    connection = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', password='postgres', port=5432)
    # db.autocommit = True
    # connection = db
    return connection

def connect(func):
    def inner_func(conn, *args, **kwargs):
        try:
            conn.execute("select version()")
        except (AttributeError, ProgrammingError):
            pass
        return func(conn, *args, **kwargs)
    return inner_func

def disconnect_from_db(db=None, conn=None):
     if conn is not None:
        conn.close()

@connect
def create_table(conn, table_name):
    cur = conn.cursor()
    table_name = scrub(table_name)
    sql = 'CREATE TABLE {} (rowid SERIAL PRIMARY KEY,' \
          'name TEXT UNIQUE, price REAL, quantity INTEGER)'.format(table_name)
    try:
        cur.execute(sql)
    except OperationalError as e:
        print(e)

def scrub(input_string):
    return ''.join(k for k in input_string if k.isalnum())

@connect
def insert_one(conn, name, price, quantity, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql = "INSERT INTO {} (name, price, quantity) VALUES (%s,%s,%s)".format(table_name)
    try:
        cur.execute(sql, (name, price, quantity))
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        raise mvc_exc.ItemAlreadyStored(
            '{}: "{}" already stored in table "{}"'.format(e, name, table_name))


@connect
def insert_many(conn, items, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql = "INSERT INTO {} (name, price, quantity) VALUES (%s,%s,%s)".format(table_name)
    entries = list()
    for x in items:
        entries.append((x['name'], x['price'], x['quantity']))
    try:
        cur.executemany(sql, entries)
        conn.commit()
    except IntegrityError as e:
        print('{}: at least one in {} was already stored in table "{}"'
              .format(e, [x['name'] for x in items], table_name))

def tuple_to_dict(mytuple):
    mydict = dict()
    mydict['id'] = mytuple[0]
    mydict['name'] = mytuple[1]
    mydict['price'] = mytuple[2]
    mydict['quantity'] = mytuple[3]
    return mydict


@connect
def select_one(conn, item_name, table_name):
    cur = conn.cursor()
    table_name = scrub(table_name)
    item_name = scrub(item_name)
    # sql = 'SELECT * FROM {} WHERE name="{}"'.format(table_name, item_name)
    sql = "SELECT * FROM {} WHERE name='{}'".format(table_name, item_name)
    cur.execute(sql)
    result = cur.fetchone()
    if result is not None:
        return tuple_to_dict(result)
    else:
        raise mvc_exc.ItemNotStored(
            'Can\'t read "{}" because it\'s not stored in table "{}"'
            .format(item_name, table_name))


@connect
def select_all(conn, table_name):
    cur = conn.cursor()
    table_name = scrub(table_name)
    sql = 'SELECT * FROM {}'.format(table_name)
    cur.execute(sql)
    results = cur.fetchall()
    return list(map(lambda x: tuple_to_dict(x), results))

@connect
def update_one(conn, name, price, quantity, table_name):
    cur =  conn.cursor()
    table_name = scrub(table_name)
    sql_check = "SELECT EXISTS(SELECT 1 FROM {} WHERE name='{}' LIMIT 1)"\
        .format(table_name, name)
    sql_update = 'UPDATE {} SET price=%s, quantity=%s WHERE name=%s'\
        .format(table_name)
    cur.execute(sql_check, (name,))
    result = cur.fetchone()
    if result[0]:
        cur.execute(sql_update, (price, quantity, name))
        conn.commit()
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t update "{}" because it\'s not stored in table "{}"'
            .format(name, table_name))




@connect
def delete_one(conn, name, table_name):
    cur = conn.cursor()
    table_name = scrub(table_name)
    sql_check = 'SELECT EXISTS(SELECT 1 FROM {} WHERE name=%s LIMIT 1)'\
        .format(table_name)
    table_name = scrub(table_name)
    sql_delete = 'DELETE FROM {} WHERE name=%s'.format(table_name)
    cur.execute(sql_check, (name,))  # we need the comma
    result = cur.fetchone()
    if result[0]:
        cur.execute(sql_delete, (name,))  # we need the comma
        conn.commit()
    else:
        raise mvc_exc.ItemNotStored(
            'Can\'t delete "{}" because it\'s not stored in table "{}"'
            .format(name, table_name))


# sqlite_backend.py
def main():

    table_name = 'items'
    conn = connect_to_db()  # in-memory database
    # conn = connect_to_db(DB_name)  # physical database (i.e. a .db file)

    create_table(conn, table_name)

    my_items = [
        {'name': 'bread', 'price': 0.5, 'quantity': 20},
        {'name': 'milk', 'price': 1.0, 'quantity': 10},
        {'name': 'wine', 'price': 10.0, 'quantity': 5},
    ]

    # CREATE
    insert_many(conn, my_items, table_name='items')
    insert_one(conn, 'beer', price=2.0, quantity=5, table_name='items')
    # if we try to insert an object already stored we get an ItemAlreadyStored
    # exception
    # insert_one(conn, 'milk', price=1.0, quantity=3, table_name='items')

    # READ
    print('SELECT milk')
    print(select_one(conn, 'milk', table_name='items'))
    print('SELECT all')
    print(select_all(conn, table_name='items'))
    # if we try to select an object not stored we get an ItemNotStored exception
    # print(select_one(conn, 'pizza', table_name='items'))

    # conn.close()  # the decorator @connect will reopen the connection

    # UPDATE
    print('UPDATE bread, SELECT bread')
    update_one(conn, 'bread', price=1.5, quantity=5, table_name='items')
    print(select_one(conn, 'bread', table_name='items'))
    # if we try to update an object not stored we get an ItemNotStored exception
    # print('UPDATE pizza')
    # update_one(conn, 'pizza', price=1.5, quantity=5, table_name='items')

    # DELETE
    print('DELETE beer, SELECT all')
    delete_one(conn, 'beer', table_name='items')
    print(select_all(conn, table_name='items'))
    # if we try to delete an object not stored we get an ItemNotStored exception
    # print('DELETE fish')
    # delete_one(conn, 'fish', table_name='items')

    # save (commit) the changes
    # conn.commit()

    # close connection
    conn.close()

if __name__ == '__main__':
    main()