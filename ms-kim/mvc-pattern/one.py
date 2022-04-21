aa = [
    {'name': 'bread', 'price': 0.5, 'quantity': 20},
    {'name': 'milk', 'price': 1.0, 'quantity': 10},
    {'name': 'wine', 'price': 10.0, 'quantity': 5},
]

aaa = list(
        filter(lambda idx: idx[1]['name'] == 'bread', enumerate(aa))
    )

for i in enumerate(aa):
    print(i[0])