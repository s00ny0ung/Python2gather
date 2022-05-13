import mvc_pattern_postgres.postgre_backend as postgre_backend
import mvc_exceptions as mvc_exc

class ModelPostgres(object):
    def __init__(self, application_items):
        self._item_type = 'picture-book'
        self._connection = postgre_backend.connect_to_db() # connection 객체 생성
        postgre_backend.create_table(self.connection, self._item_type )
        self.create_items(application_items)

    @property # 
    def connection(self):
        return self._connection
    
    @property
    def item_type(self):
        return self._item_type

    # item type 생성
    @item_type.setter
    def item_type(self, new_item_type):
        self._item_type = new_item_type

    def create_item(self, title, writer, painter, publisher, position):
        postgre_backend.insert_one(
            self.connection, title, writer, painter, publisher, position, table_name=self.item_type
        )
    
    def create_items(self, items):
        postgre_backend.insert_many(
            self.connection, items, table_name=self.item_type
        )

    def read_item(self, title):
        return postgre_backend.select_one(
            self.connection, title, table_name=self.item_type
        )

    def read_items(self):
        return postgre_backend.select_all(
            self.connection, table_name=self.item_type
        )

    def update_item(self, title, writer, painter, publisher, position):
        postgre_backend.update_one(
            self.connection, title, writer, painter, publisher, position, table_name=self.item_type
        )
    

    def delete_item(self, title):
         postgre_backend.delete_item(
            self.connection, title, table_name=self.item_type
        )

class Controller(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def show_items(self, bullet_points=False):
        items = self.model.read_items()
        item_type = self.model.item_type

        if bullet_points:
            self.view.show_bullet_point_list(item_type, items)
        else:
            self.view.show_number_point_list(item_type, items)
    
    def show_item(self, item_name):
        try:
            item_info = self.model.read_item(item_name)
            item_type = self.model.item_type
            self.view.show_item(item_type, item_name, item_info)
        except mvc_exc.ItemNotStored as e:
            self.view.display_missing_item_error(item_name, e)

    def insert_item(self, title, writer, painter, publisher, position):
        assert position > 0, 'position must be greater than 0'
        item_type = self.model.item_type
        try:
            self.model.create_item(title, writer, painter, publisher, position)
            self.view.display_item_stored(title, item_type, )
        except mvc_exc.ItemAlreadyStored as e:
            self.view.display_item_already_stored_error(title, item_type, e)
    
    def update_item(self, title, writer, painter, publisher, position):
        assert position > 0, 'position must be greater than 0'
        item_type = self.model.item_type
        try:
            older = self.model.read_item(title)
            self.model.update_item(title, writer, painter, publisher, position)
            self.view.display_item_updated(
                title, older['position'], position)
        except mvc_exc.ItemAlreadyStored as e:
            self.view.display_item_not_yet_stored_error(title, item_type, e)

    def update_item_type(self, new_item_type):
        old_item_type = self.model.item_type
        self.model.item_type = new_item_type
        self.view.display_change_item_type(old_item_type, new_item_type)

    def delete_item(self, title):
        item_type = self.model.item_type
        try:
            self.model.delete_item(title)
            self.view.display_item_deletion(title)
        except mvc_exc.ItemNotStored as e:
            self.view.display_item_not_yet_stored_error(title, item_type, e)


def main():
    # create_table(conn, table_name)
    myitems = [
        {'title':'여름이온다4', 'writer':'이수지', 'painter':'이수지', 'publisher':'비룡소', 'position':'2'},
        {'title':'코끼리비밀요원4', 'writer':'오원 맥클로플린', 'painter':'로스 콜린스', 'publisher':'다림', 'position':'3'},
        {'title':'그들은결국브레멘에가지못했다4', 'writer':'루리', 'painter':'루리', 'publisher':'비룡소', 'position':'4'}
    ]

    c = Controller(ModelPostgres(myitems))

    c.show_items()
    c.show_items(bullet_points=True)
    c.show_item('우리는 안녕')
    c.insert_item(title = '우리는 안녕', writer = '박준', painter='김한나', publisher='난다요', position = 4)
    c.show_item('우리는 안녕')
    c.update_item(title = '우리는 안녕', writer = '박준', painter='김한나', publisher='난다요', position = 3)
    c.delete_item('여름이 온다')

    if type(c.model) is ModelPostgres:
        postgre_backend.disconnect_from_db(c.model.connection)
        # the sqlite backend understands that it needs to open a new connection
        c.show_items()

if __name__ == '__main__':
    main()