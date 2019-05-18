import uuid
import time,hashlib
import pymysql


def create_uid():
    return str(uuid.uuid1())

def create_id(string):
    m = hashlib.md5(str(string).encode())
    return m.hexdigest()


if __name__ == '__main__':
    print(create_uid())
    print(create_uid())
    print(create_id('xcgdyse'))
    print(create_id('xcgdyse'))
'''
cbfd419ab7ccd21214078e4365f6d14c
cbfd419ab7ccd21214078e4365f6d14c
'''
''''''
db = pymysql.connect('localhost', 'root', '123456', 'chat_room', charset='utf8')
cursor = db.cursor()
sql = 'select address from customer_statue where uid="555"'
cursor.execute(sql)
r = cursor.fetchone()
print(r[0])


