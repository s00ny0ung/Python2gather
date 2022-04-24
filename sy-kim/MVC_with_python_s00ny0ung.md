# MVC pattern in Python

- 🐍python 3.5
- 🐘postgreSQL



## Part1. Introduction and BasicModel

### MVC(Model - View - Control) Pattern

- 분리되어 있기 때문에 다른 두개를 다시 작성할 필요 없이 세 개 중 각각을 확장, 수정 및 교체할 수 있습니다.

- Model

  - 데이터를 관리하고 규칙과 동작을 정의
  - 애플리케이션 비즈니스 로직
  - 데이터는 모델 자체 또는 데이터베이스에 저장
  - 모델만 데이터베이스에 액세스 함

- View

  - 사용자에게 데이터를 제공
  - View는 자신의 메서드를 호출해서는 안 됨. 컨트롤러만 수행해야 함

- Control

  - 사용자의 입력을 받아들이고 데이터 표현을 뷰에 위임하고 데이터 처리를 모델에 위임

  

### CRUD

- 작은 식료품점 재고 관리 시스템을 CRUD 구조
- Create
- Read
- Update
- Delete

---

- basic_backend.py
  - Create 작업은 아무 것도 반환하지 않습니다. 
  - 전역 항목 `items` 변수에 새 데이터를 추가하기만 하면 됩니다.

```python
# basic_backend.py
import mvc_exceptions as mvc_exc

items = list()


def create_item(name, price, quantity):
    global items
    results = list(filter(lambda x: x["name"] == name, items))
    if results:
        raise mvc_exc.ItemAlreadyStored('"{}" already stored!'.format(name))

    else:
        items.append({"name": name, "price": price, "quantity": quantity})


def create_items(app_items):
    global items
    items = app_items


def read_item(name):
    global items
    myitems = list(filter(lambda x: x["name"] == name, items))
    if myitems:
        return myitems[0]

    else:
        raise mvc_exc.ItemNotStored(
            "Can't read \"{}\" because it's not stored".format(name)
        )


def read_items():
    global items
    return [item for item in items]


def update_item(name, price, quantity):
    global items
    # Python 3.x removed tuple parameters unpacking (PEP 3113), so we have to do
    # it manually (i_x is a tuple, idxs_items is a list of tuples)
    idxs_items = list(filter(lambda i_x: i_x[1]["name"] == name, enumerate(items)))
    if idxs_items:
        i, item_to_update = idxs_items[0][0], idxs_items[0][1]
        items[i] = {"name": name, "price": price, "quantity": quantity}
    else:
        raise mvc_exc.ItemNotStored(
            "Can't update \"{}\" because it's not stored".format(name)
        )


def delete_item(name):
    global items
    # Python 3.x removed tuple parameters unpacking (PEP 3113), so we have to do
    # it manually (i_x is a tuple, idxs_items is a list of tuples)
    idxs_items = list(filter(lambda i_x: i_x[1]["name"] == name, enumerate(items)))
    if idxs_items:
        i, item_to_delete = idxs_items[0][0], idxs_items[0][1]
        del items[i]
    else:
        raise mvc_exc.ItemNotStored(
            "Can't delete \"{}\" because it's not stored".format(name)
        )


def main():

    # CREATE
    create_items(mock.items())
    create_item("beer", price=3.0, quantity=15)
    # if we try to re-create an object we get an ItemAlreadyStored exception
    # create_item('beer', price=2.0, quantity=10)

    # READ
    print("READ items")
    print(read_items())
    # if we try to read an object not stored we get an ItemNotStored exception
    # print('READ chocolate')
    # print(read_item('chocolate'))
    print("READ bread")
    print(read_item("bread"))

    # UPDATE
    print("UPDATE bread")
    update_item("bread", price=2.0, quantity=30)
    print(read_item("bread"))
    # if we try to update an object not stored we get an ItemNotStored exception
    # print('UPDATE chocolate')
    # update_item('chocolate', price=10.0, quantity=20)

    # DELETE
    print("DELETE beer")
    delete_item("beer")
    # if we try to delete an object not stored we get an ItemNotStored exception
    # print('DELETE chocolate')
    # delete_item('chocolate')

    print("READ items")
    print(read_items())


if __name__ == "__main__":
    main()

```

- mvc_exceptions.py
  - duplicate item
    - 데이터베이스에 데이터가 존재하는 경우
  - non-existing item
    - 데이터베이스에 데이터가 존재하지 않는 경우

```python
class ItemAlreadyStored(Exception):
    pass

class ItemNotStored(Exception):
    pass
```

- model_view_controller.py

```python
import basic_backend
import mvc_exceptions as mvc_exc


class ModelBasic(object):

    def __init__(self, application_items):
        self._item_type = 'product'
        self.create_items(application_items)

    @property
    def item_type(self):
        return self._item_type

    @item_type.setter
    def item_type(self, new_item_type):
        self._item_type = new_item_type

    def create_item(self, name, price, quantity):
        basic_backend.create_item(name, price, quantity)

    def create_items(self, items):
        basic_backend.create_items(items)

    def read_item(self, name):
        return basic_backend.read_item(name)

    def read_items(self):
        return basic_backend.read_items()

    def update_item(self, name, price, quantity):
        basic_backend.update_item(name, price, quantity)

    def delete_item(self, name):
        basic_backend.delete_item(name)


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
        print('//////////////////////////////////////////////////////////////')
        print('Good news, we have some {}!'.format(item.upper()))
        print('{} INFO: {}'.format(item_type.upper(), item_info))
        print('//////////////////////////////////////////////////////////////')

    @staticmethod
    def display_missing_item_error(item, err):
        print('**************************************************************')
        print('We are sorry, we have no {}!'.format(item.upper()))
        print('{}'.format(err.args[0]))
        print('**************************************************************')

    @staticmethod
    def display_item_already_stored_error(item, item_type, err):
        print('**************************************************************')
        print('Hey! We already have {} in our {} list!'
              .format(item.upper(), item_type))
        print('{}'.format(err.args[0]))
        print('**************************************************************')

    @staticmethod
    def display_item_not_yet_stored_error(item, item_type, err):
        print('**************************************************************')
        print('We don\'t have any {} in our {} list. Please insert it first!'
              .format(item.upper(), item_type))
        print('{}'.format(err.args[0]))
        print('**************************************************************')

    @staticmethod
    def display_item_stored(item, item_type):
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('Hooray! We have just added some {} to our {} list!'
              .format(item.upper(), item_type))
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    @staticmethod
    def display_change_item_type(older, newer):
        print('---   ---   ---   ---   ---   ---   ---   ---   ---   ---   --')
        print('Change item type from "{}" to "{}"'.format(older, newer))
        print('---   ---   ---   ---   ---   ---   ---   ---   ---   ---   --')

    @staticmethod
    def display_item_updated(item, o_price, o_quantity, n_price, n_quantity):
        print('---   ---   ---   ---   ---   ---   ---   ---   ---   ---   --')
        print('Change {} price: {} --> {}'
              .format(item, o_price, n_price))
        print('Change {} quantity: {} --> {}'
              .format(item, o_quantity, n_quantity))
        print('---   ---   ---   ---   ---   ---   ---   ---   ---   ---   --')

    @staticmethod
    def display_item_deletion(name):
        print('--------------------------------------------------------------')
        print('We have just removed {} from our list'.format(name))
        print('--------------------------------------------------------------')


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
            item = self.model.read_item(item_name)
            item_type = self.model.item_type
            self.view.show_item(item_type, item_name, item)
        except mvc_exc.ItemNotStored as e:
            self.view.display_missing_item_error(item_name, e)

    def insert_item(self, name, price, quantity):
        assert price > 0, 'price must be greater than 0'
        assert quantity >= 0, 'quantity must be greater than or equal to 0'
        item_type = self.model.item_type
        try:
            self.model.create_item(name, price, quantity)
            self.view.display_item_stored(name, item_type)
        except mvc_exc.ItemAlreadyStored as e:
            self.view.display_item_already_stored_error(name, item_type, e)

    def update_item(self, name, price, quantity):
        assert price > 0, 'price must be greater than 0'
        assert quantity >= 0, 'quantity must be greater than or equal to 0'
        item_type = self.model.item_type

        try:
            older = self.model.read_item(name)
            self.model.update_item(name, price, quantity)
            self.view.display_item_updated(
                name, older['price'], older['quantity'], price, quantity)
        except mvc_exc.ItemNotStored as e:
            self.view.display_item_not_yet_stored_error(name, item_type, e)
            # if the item is not yet stored and we performed an update, we have
            # 2 options: do nothing or call insert_item to add it.
            # self.insert_item(name, price, quantity)

    def update_item_type(self, new_item_type):
        old_item_type = self.model.item_type
        self.model.item_type = new_item_type
        self.view.display_change_item_type(old_item_type, new_item_type)

    def delete_item(self, name):
        item_type = self.model.item_type
        try:
            self.model.delete_item(name)
            self.view.display_item_deletion(name)
        except mvc_exc.ItemNotStored as e:
            self.view.display_item_not_yet_stored_error(name, item_type, e)

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
            item = self.model.read_item(item_name)
            item_type = self.model.item_type
            self.view.show_item(item_type, item_name, item)
        except mvc_exc.ItemNotStored as e:
            self.view.display_missing_item_error(item_name, e)

    def insert_item(self, name, price, quantity):
        assert price > 0, 'price must be greater than 0'
        assert quantity >= 0, 'quantity must be greater than or equal to 0'
        item_type = self.model.item_type
        try:
            self.model.create_item(name, price, quantity)
            self.view.display_item_stored(name, item_type)
        except mvc_exc.ItemAlreadyStored as e:
            self.view.display_item_already_stored_error(name, item_type, e)

    def update_item(self, name, price, quantity):
        assert price > 0, 'price must be greater than 0'
        assert quantity >= 0, 'quantity must be greater than or equal to 0'
        item_type = self.model.item_type

        try:
            older = self.model.read_item(name)
            self.model.update_item(name, price, quantity)
            self.view.display_item_updated(
                name, older['price'], older['quantity'], price, quantity)
        except mvc_exc.ItemNotStored as e:
            self.view.display_item_not_yet_stored_error(name, item_type, e)
            # if the item is not yet stored and we performed an update, we have
            # 2 options: do nothing or call insert_item to add it.
            # self.insert_item(name, price, quantity)

    def update_item_type(self, new_item_type):
        old_item_type = self.model.item_type
        self.model.item_type = new_item_type
        self.view.display_change_item_type(old_item_type, new_item_type)

    def delete_item(self, name):
        item_type = self.model.item_type
        try:
            self.model.delete_item(name)
            self.view.display_item_deletion(name)
        except mvc_exc.ItemNotStored as e:
            self.view.display_item_not_yet_stored_error(name, item_type, e)


if __name__ == "__main__":

    my_items = [
    {'name': 'bread', 'price': 0.5, 'quantity': 20},
    {'name': 'milk', 'price': 1.0, 'quantity': 10},
    {'name': 'wine', 'price': 10.0, 'quantity': 5},
    ]

    c = Controller(ModelBasic(my_items), View())

    c.show_items()
    c.show_items(bullet_points=True)
    c.show_item("chocolate")
    c.show_item("bread")

    c.insert_item("bread", price=1.0, quantity=5)
    c.insert_item("chocolate", price=2.0, quantity=10)
    c.show_item("chocolate")

    c.update_item("milk", price=1.2, quantity=20)
    c.update_item("ice cream", price=3.5, quantity=20)

    c.delete_item("fish")
    c.delete_item("bread")

    c.show_items()
```

- 실행 결과

```cmd
--- PRODUCT LIST ---
1. {'name': 'bread', 'price': 0.5, 'quantity': 20}
2. {'name': 'milk', 'price': 1.0, 'quantity': 10}
3. {'name': 'wine', 'price': 10.0, 'quantity': 5}
--- PRODUCT LIST ---
* {'name': 'bread', 'price': 0.5, 'quantity': 20}
* {'name': 'milk', 'price': 1.0, 'quantity': 10}
* {'name': 'wine', 'price': 10.0, 'quantity': 5}
**************************************************************
We are sorry, we have no CHOCOLATE!
Can't read "chocolate" because it's not stored
**************************************************************
//////////////////////////////////////////////////////////////
Good news, we have some BREAD!
PRODUCT INFO: {'name': 'bread', 'price': 0.5, 'quantity': 20}
//////////////////////////////////////////////////////////////
**************************************************************
Hey! We already have BREAD in our product list!
"bread" already stored!
**************************************************************
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Hooray! We have just added some CHOCOLATE to our product list!
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//////////////////////////////////////////////////////////////
Good news, we have some CHOCOLATE!
PRODUCT INFO: {'name': 'chocolate', 'price': 2.0, 'quantity': 10}
//////////////////////////////////////////////////////////////
---   ---   ---   ---   ---   ---   ---   ---   ---   ---   --
Change milk price: 1.0 --> 1.2
Change milk quantity: 10 --> 20
---   ---   ---   ---   ---   ---   ---   ---   ---   ---   --
**************************************************************
We don't have any ICE CREAM in our product list. Please insert it first!
Can't read "ice cream" because it's not stored
**************************************************************
**************************************************************
We don't have any FISH in our product list. Please insert it first!
Can't delete "fish" because it's not stored
**************************************************************
--------------------------------------------------------------
We have just removed bread from our list
--------------------------------------------------------------
--- PRODUCT LIST ---
1. {'name': 'milk', 'price': 1.2, 'quantity': 20}
2. {'name': 'wine', 'price': 10.0, 'quantity': 5}
3. {'name': 'chocolate', 'price': 2.0, 'quantity': 10}
```



## Part2. PostgreSQL

## Part3. Dataset



