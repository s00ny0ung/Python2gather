from sqlalchemy.exc import NoSuchTableError, IntegrityError
import mvc_exceptions as mvc_exc
import dataset

DB_name = 'postgres'

class UnsupportedDatabaseEngine(Exception):
    pass

def connect_to_db(db_name=None, db_engine='sqlite'):
    engines = set(['sqlite', 'postgres'])
    if db_name is None:
        db_string = 'sqlite:///:memory:'
        print('New Connection to in-memory SQLite DB')
    else:
        if db_engine == 'sqlite':
            db_string = f'sqlite:///{DB_name}.db'
            print('New Connection to SQLite DB')
        if db_engine == 'postgres':
            db_string = f"postgresql://postgres:1234@localhost:5432/{DB_name}"
            print('New Connection to PostgreSQL DB')
        else:
            raise UnsupportedDatabaseEngine(
                f'No database engine with this name. Choose one of the following: {engines}'
            )
    return dataset.connect(db_string)


def disconnect_from_db(conn, db=None):
    if conn is not None:
        conn.close()

        
def load_table(conn, table_name):
    try:
        conn.load_table(table_name)
        print(f'load table {table_name}')
    except NoSuchTableError as e:
        print(f'Table {table_name} does not exist. It will be created now')
        # 없으면 만들어주기
        conn.get_table(table_name, primary_id = 'title', primary_type='String')
        print(f'Created table {table_name} on database {DB_name}')


def insert_one(conn, title, writer, painter, publisher, position, table_name):
    table = conn.load_table(table_name)
    try:
        table.insert(dict(
            title = title,
            writer = writer, 
            painter = painter, 
            publisher = publisher, 
            position = position,
        ))
    except IntegrityError as e:
        raise mvc_exc.ItemAlreadyStored(
            f'"{title}" already stored in table "{table_name}".\n Original Exception raised : {e}'
        )

def insert_many(conn, items, table_name):
    table = conn.load_table(table_name)
    print(f'load table {table_name}')
    # 여러개를 집어넣어야 하므로 for문으로 넣기!
    try:
        for item in items:
            table.insert(dict(
                title = item['title'],
                writer = item['writer'], 
                painter = item['painter'], 
                publisher = item['publisher'], 
                position = item['position'],
            ))
    except IntegrityError as e:
        raise mvc_exc.ItemAlreadyStored(
            f"At least one in {[x['title'] for x in items]} already \
                 stored in table '{table_name}'.\n Original \
                     Exception raised : {e}"
        )

def select_one(conn, title, table_name):
    table = conn.load_table(table_name)
    row = table.find_one(title = title)
    if row is not None:
        return dict(row)
    else:
        raise mvc_exc.ItemNotStored(
            f'Can\'t read {title} \
                because it\'s not stored in table {table_name}'
        )

def select_all(conn, table_name):
    table = conn.load_table(table_name)
    rows = table.all()
    return (list(map(lambda x: dict(x), rows)))

def update_one(conn, title, writer, painter, publisher, position, table_name):
    table = conn.load_table(table_name)
    row = table.find_one(title=title)
    if row is not None:
        item = {'title': title,
                'writer': writer,
                'painter': painter,
                'publisher': publisher,
                'position':position}
        table.update(item, keys = ['title'])
    else:
        raise mvc_exc.ItemNotStored(
            f'Can\'t update "{title}" because it\'s not stored in table "{table_name}"'
        )

def delete_one(conn, item_name, table_name):
    table = conn.load_table(table_name)
    row = table.find_one(title = item_name)
    if row is not None:
        table.delete(title = item_name)
    else:
        raise mvc_exc.ItemNotStored(
            f'Can\'t update "{item_name}" because it\'s not stored in table "{table_name}"'
        )

def main():
    conn = connect_to_db(db_name='test_db', db_engine='postgres')
    table_name = 'test2'
    # conn.create_table('test2')
    load_table(conn, table_name)

    myitems = [
        {'title':'여름이온다4', 'writer':'이수지', 'painter':'이수지', 'publisher':'비룡소', 'position':'2'},
        {'title':'코끼리비밀요원4', 'writer':'오원 맥클로플린', 'painter':'로스 콜린스', 'publisher':'다림', 'position':'3'},
        {'title':'그들은결국브레멘에가지못했다4', 'writer':'루리', 'painter':'루리', 'publisher':'비룡소', 'position':'4'}
    ]

    insert_many(conn, myitems, table_name)
    insert_one(conn, '우리는안녕5',  writer = '박준', painter='김한나', publisher='난다요', position = '4', table_name=table_name)
    print('SELECT 우리는안녕2')
    print(select_one(conn, '여름이온다1', table_name=table_name))
    print('SELECT ALL')
    print(select_all(conn, table_name=table_name))
    print('update!')
    print(update_one(conn, '우리는안녕',  writer = '박준', painter='김한나', publisher='난다요', position = '1', table_name=table_name))
    print('delete!')
    print(delete_one(conn, '여름이온다1',table_name=table_name))

    conn.close()

if __name__ == '__main__':
    main()
