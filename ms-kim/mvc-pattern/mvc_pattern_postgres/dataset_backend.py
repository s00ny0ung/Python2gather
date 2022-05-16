from sqlalchemy.exc import NoSuchTableError, IntegrityError
import mvc_exceptions as mvc_exc
import dataset

conn = dataset.connect('...')

DB_name = 'template2'

def create_table(conn, table_name):
    try:
        conn.load_table(table_name)
    except NoSuchTableError as e:
        print(f'Table {table_name} does not exist. It will be created now')
        # 없으면 만들어주기
        conn.get_table(table_name, primary_id = 'name', primary_type='String')
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

def inset_many(conn, items, table_name):
    table = conn.load_table(table_name)
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