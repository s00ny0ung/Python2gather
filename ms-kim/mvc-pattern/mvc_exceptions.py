"""
발생할 수 있는 에러 처리
"""

class ItemAlreadyStored(Exception):
    pass

class ItemNotStored(Exception):
    pass

# Q. class로 구현하는 이유는?