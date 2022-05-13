# -*- coding: utf-8 -*-
import mvc_pattern_101.basic_backend as basic_backend
import mvc_exceptions as mvc_exc

class Model(object):
    def __init__(self, application_items):
        self._item_type = 'picture-book'
        self.create_items(application_items)

    @property
    def item_type(self):
        return self._item_type
    
    @item_type.setter
    def item_type(self, new_item_type):
        self._item_type = new_item_type
    
    def create_item(self, title, writer, painter, publisher, position):
        basic_backend.create_item(title, writer, painter, publisher, position)
    
    def create_items(self, items):
        basic_backend.create_items(items)

    def read_item(self, title):
        return basic_backend.read_item(title)

    def read_items(self):
        return basic_backend.read_items()

    def update_item(self, title, writer, painter, publisher, position):
        basic_backend.update_item(title, writer, painter, publisher, position)

    def delete_item(self, title):
        basic_backend.delete_item(title)

class View(object):

    @staticmethod
    def show_bullet_point_list(item_type, items):
        print('--- {} LIST ---'.format(item_type.upper()))
        for item in items:
            print('* {}'.format(item))

    @staticmethod
    def show_number_point_list(item_type, items):
        print('--- {} LIST ---'.format(item_type.upper()))
        for i, item in enumerate(items):
            print('{}. {}'.format(i+1, item))
    
    @staticmethod
    def show_item(item_type, item, item_info):
        print('/////////////////////////////////')
        print('good news, we have some {}!'.format(item.upper()))
        print('{} info : {}'.format(item_type.upper(), item_info))
        print('/////////////////////////////////')

    @staticmethod
    def display_missing_item_error(item, err):
        print('*********************************')
        print('we are sorry, we have no {}!'.format(item.upper()))
        print('{}'.format(item_type.upper(), item_info()))
        print('*********************************')
    
    @staticmethod
    def display_item_already_stored_error(item, item_type, err):
        print('*********************************')
        print('hey! we already have {} in our {} list!'.format(item.upper(), item_type))
        print('{}'.format(err.args[0]))
        print('*********************************')
    
    @staticmethod
    def display_item_not_yet_stored_error(item, item_type, err):
        print('*********************************')
        print('we don\'t have any {} in our {} list! please insert it first'.format(item.upper(), item_type))
        print('{}'.format(err.args[0]))
        print('*********************************')
     
    @staticmethod
    def display_item_stored(item, item_type):
        print('*********************************')
        print('hooray! we have just added some {} to our {} list!'.format(item.upper(), item_type))
        print('*********************************')

    @staticmethod
    def display_change_item_type(older, newer):
        print('--- ---- ------ ---- --- --- --- -')
        print('Change item type from "{}" to "{}"'.format(older, newer))
        print('--- ---- ------ ---- --- --- --- -')

    @staticmethod
    def display_item_updated(item, o_position, n_position):
        print('--- ---- ------ ---- --- --- --- -')
        print('Change {} Position: {} --> {}'.format(item, o_position, n_position))
        print('--- ---- ------ ---- --- --- --- -')

    @staticmethod
    def display_item_deletion(title):
        print('----------------------------------')
        print('we have just removed {} from our list'.format(title))
        print('----------------------------------')
    

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
  myitems = [
    {'title':'여름이 온다', 'writer':'이수지', 'paitner':'이수지', 'publisher':'비룡소', 'position':2},
    {'title':'코끼리 비밀요원', 'writer':'오원 맥클로플린', 'paitner':'로스 콜린스', 'publisher':'다림', 'position':3},
    {'title':'그들은 결국 브레멘에 가지 못했다', 'writer':'루리', 'paitner':'루리', 'publisher':'비룡소', 'position':4}
  ]

  c = Controller(Model(myitems), View())
  c.show_items()
  c.show_items(bullet_points=True)
  c.show_item('우리는 안녕')
  c.insert_item(title = '우리는 안녕', writer = '박준', painter='김한나', publisher='난다요', position = 4)
  c.show_item('우리는 안녕')
  c.update_item(title = '우리는 안녕', writer = '박준', painter='김한나', publisher='난다요', position = 3)
  c.delete_item('여름이 온다')

if __name__ == '__main__':
    main()