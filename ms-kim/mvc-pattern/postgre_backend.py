import psycopg2
from psycopg2 import OperationalError, IntegrityError, ProgrammingError

DB_name = 'postgreDB'

def connect_to_db(db=None):
    if db is None:
        mydb = ':memory:'
        print('New connection to in-memory postgreSQL DB')
    else:
        mydb = '{}.db'.format(db)
        print('New connection to postgreSQL DB')
    connection = psycopg2.connect(mydb)
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
                'SELECT name FROM temp_table WHERE type="table;"'
            )
        except (AttributeError, ProgrammingError):
            conn = connect_to_db(DB_name)
        return func(conn, *args, **kwargs)
    return inner_func

@connect
def create_table(conn, table_name):
    table_name = scrub(table_name)
    sql = 'CREATE TABLE {} (rowid INTEGER PRIMARY KEY AUTOINCREMENT,' \
          'title TEXT UNIQUE, writer TEXT, painter TEXT, publisher TEXT,' \
          'position INTEGER)'.format(table_name)
    try:
        conn.execute(sql)
    except OperationalError as e:
        print(e)

def scrub(input_string):
    return ''.join(k for k in input_string if k.isalnum())


@connect
def insert_one(conn, title, writer, painter, publisher, position, table_name):
    table_name = scrub(table_name)
    sql = "INSERT INTO {} ('title', 'writer', 'painter', 'publisher', 'position') VALUES (?, ?, ?, ?, ?)".format(table_name)
    try:
        conn.execute(sql, (title, wirter, painter, publisher, position))
        conn.commit()
    except IntegrityError as e:
        raise mvc_exc.ItemAlreadyStored(
            '{}: "{}" already stored in table "{}"'.format(e, title, table_name)
        )

@connect
def insert_many(conn, items, table_name):
    table_name = scrub(table_name)
    sql = sql = "INSERT INTO {} ('title', 'writer', 'painter', 'publisher', 'position') VALUES (?, ?, ?, ?, ?)".format(table_name)
    entries = list()
    for x in items:
        entries.append(x['title'], x['writer'], x['painter'], x['publisher'], x['position'])
    try:
        conn.executemany(sql, entries)
        conn.commit()
    except IntegrityError as e:
        print('{}: at least one in {} was already stored in table "{}"'
              .format(e, [x['name'] for x in items], table_name))

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
    table_name = scrub(table_name)
    item_name = scrub(itme_name)
    sql = 'SELECT * FROM {} WHERE title="{}"'.format(table_name, item_name)
    c = conn.execute(sql)
    result = c.fetchone()
    if result is not None:
        return tuple_to_dict(result)
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t read "{}" because it\'s not stored in table "{}"'
            .format(item_name, table_name)
        )

@connect
def select_all(conn, table_name):
    table_name = scrub(table_name)
    sql = 'SELECT * FROM {}'.format(table_name)
    c = conn.execute(sql)
    results = c.fetchall()
    return list(map(lambda x: tuple_to_dict(x), results))

@connect
def update_one(conn, title, writer, painter, publisher, position, table_name):
    table_name = scrub(table_name)
    sql_check = 'SELECT EXISTS(SELECT 1 FROM {} WHERE title=? LIMIT 1)'\
        .format(table_name)
    sql_update = 'UPDATE {} SET writer=?, painter=?, publisher=?, positon=? WHERE title=?'\
        .format(table_name)
    c = conn.execute(sql_check, (title,))
    result = c.fetchone()
    if result[0]:
        c.execute(sql_update, (writer, painter, publisher, position, title))
        conn.commit()
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t update "{}" because it\'s not stored in table "{}"'
            .format(title, table_name))


@connect
def delete_one(conn, title, table_name):
    table_name = scrub(table_name)
    sql_check = 'SELECT EXISTS(SELECT 1 FROM {} WHERE title=? LIMIT 1)'\
        .format(table_name)
    table_name = scrub(table_name)
    sql_delete = 'DELETE {} WHERE title=?'.format(table_name)
    c = conn.execute(sql_check, (title,))
    result = c.fetchone()
    if result[0]:
        c.execute(sql_delete, (title,))
        conn.commit()
    else:
        raise mvc_exc.ItemAlreadyStored(
            'Can\'t delete "{}" because it\'s not stored in table "{}"'
            .format(title, table_name))



def main():
    table_name = 'items'
    conn = connect_to_db()

    create_table(conn, table_name)
    myitems = [
        {'title':'여름이온다', 'writer':'이수지', 'paitner':'이수지', 'publisher':'비룡소', 'position':'2'},
        {'title':'코끼리비밀요원', 'writer':'오원 맥클로플린', 'paitner':'로스 콜린스', 'publisher':'다림', 'position':'3'},
        {'title':'그들은결국브레멘에가지못했다', 'writer':'루리', 'paitner':'루리', 'publisher':'비룡소', 'position':'4'}
    ]

    insert_many(conn, my_items, table_name='items')
    insert_one(conn, '우리는안녕',  writer = '박준', painter='김한나', publisher='난다요', position = '4', table_name='items')
    print('SELECT 여름이온다')
    print(select_one(conn, '여름이온다', table_name='items'))
    print('SELECT ALL')
    print(select_all(conn, table_name='items'))

    conn.close()

if __name__ == '__main__':
    main()