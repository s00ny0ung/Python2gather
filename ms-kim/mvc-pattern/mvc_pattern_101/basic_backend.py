# -*- coding: utf-8 -*-
import mvc_exceptions as mvc_exc

items = list()

def create_items(app_items):
    global items
    items = app_items

def create_item(title, writer, painter, publisher, position):
    global items

    results = list(filter(lambda x: x['title']== title, items))
    if results:
        raise mvc_exc.ItemAlreadyStored('"{}" already stored!'.format(title))
    else:
        items.append({
            'title': title,
            'writer': writer,
            'painter': painter,
            'publisher': publisher,
            'position': position
        })

def read_items():
    global items
    return [item for item in items]

def read_item(title):
    global items
    results = list(filter(lambda x: x['title']== title, items))
    if results:
        return results[0]
    else:
        raise mvc_exc.ItemNotStored('Can\'t read "{}" because it\'s not stored'.format(title))

def update_item(title, writer, painter, publisher, position):
    global items

    idx_items = list(
        filter(lambda idx: idx[1]['title'] == title, enumerate(items))
    )

    if idx_items:
        idx, item_to_update = idx_items[0][0], idx_items[0][1] # index, item
        items[idx] = { 'title': title,
            'writer': writer,
            'painter': painter,
            'publisher': publisher,
            'position': position}
    else:
        raise mvc_exc.ItemNotStored('Can\'t update "{}" because it\'s not stored'.format(title))

def delete_item(title):
    global items

    idx_items = list(
        filter(lambda idx: idx[1]['title'] == title, enumerate(items))
    )

    if idx_items:
        idx, item_to_update = idx_items[0][0], idx_items[0][1] # index, item
        del items[idx]
    else:
        raise mvc_exc.ItemNotStored('Can\'t delete "{}" because it\'s not stored'.format(title))


def main():
  myitems = [
    {'title':'여름이 온다', 'writer':'이수지', 'paitner':'이수지', 'publisher':'비룡소', 'position':'2'},
    {'title':'코끼리 비밀요원', 'writer':'오원 맥클로플린', 'paitner':'로스 콜린스', 'publisher':'다림', 'position':'3'},
    {'title':'그들은 결국 브레멘에 가지 못했다', 'writer':'루리', 'paitner':'루리', 'publisher':'비룡소', 'position':'4'}
  ]

  create_items(myitems)
  create_item(title = '우리는 안녕', writer = '박준', painter='김한나', publisher='난다요', position = '4')
  #READ
  print('READ_ITEM')
  print('=========================')
  print(read_items())
  print('=========================')
  print('READ 여름이 온다')
  print('=========================')
  print(read_item('여름이 온다'))
  print('=========================')

  #UPDATE
  print('UPDATE_ITEM')
  print('=========================')
  update_item(title = '우리는 안녕', writer = '박준', painter='김한나', publisher='난다', position = '4')
  print(read_item('우리는 안녕'))
  print('=========================')

  #DELETE
  print('DELETE_ITEM')
  delete_item('우리는 안녕')

  print('READ_ITEM')
  print('=========================')
  print(read_items())

if __name__ == '__main__':
    main()