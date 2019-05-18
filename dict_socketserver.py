import socketserver
import time
import pymysql
import uuid
import hashlib


class MyTCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.db = self.__connect_dbs()
        super(MyTCPHandler, self).__init__(request, client_address, server)

    def handle(self):
        while True:
            try:
                self.data = self.request.recv(1024).decode()
                # funciton:save address
                # print(self.client_address)得到端口和地址
                print(self.client_address[0], ":", self.data)
                if not self.data or self.data == 'E':
                    break
                elif self.data[0] == 'R':
                    self.do_register(self.data)
                elif self.data[0] == 'L':
                    self.do_login(self.data)

            except ConnectionResetError as e:
                print('erro:', e)
                break

    def __connect_dbs(self):
        db = pymysql.connect('localhost', 'root', '123456', 'chat_room', charset='utf8')
        return db

    def __create_uid(self):
        return str(uuid.uuid1())

    def __create_id(self,string):
        m = hashlib.md5(str(string).encode())
        return m.hexdigest()

    def do_register(self, data):
        # db = self.__connect_dbs()
        tmp = data.split(' ')
        name = tmp[1]
        passwd = tmp[2]
        nname = tmp[3]
        cursor = self.db.cursor()
        sql = 'select * from customer_base where uid="%s"' % name
        cursor.execute(sql)
        r = cursor.fetchone()
        if r != None:
            self.request.send('该用户已存在'.encode())
            return
        uuid = self.__create_uid()
        # 用户注册存入customer_base数据库,记录uuid,用户名,密码,昵称
        sql1 = "insert into customer_base (uuid,uid,password,nname) VALUES ('%s','%s','%s','%s')" % (
            uuid, name, passwd, nname)
        # 用户注册同时存入customer_status数据库,记录uuid,用户名,在线状态;在登录功能中修改地址
        sql2 = "insert into customer_statue (uuid,uid,nname,address) VALUES ('%s','%s','%s','%s')" % (uuid, name, nname,'outline')
        try:
            cursor.execute(sql1)
            cursor.execute(sql2)
            self.db.commit()
            self.request.send(b'OK')
        except Exception as e:
            self.db.rollback()
            self.request.send('注册失败'.encode())
            # print(self.request)得到地址
            print(e)

    def do_login(self, data):
        # 登录功能,更改在线状态,写入登录地址
        tmp = data.split(' ')
        name = tmp[1]
        passwd = tmp[2]
        cursor = self.db.cursor()

        # 密码验证
        sql_code = "select password from customer_base where uid = '%s'" % name
        cursor.execute(sql_code)
        r = cursor.fetchone()[0]
        code = self.__create_id(r)
        if code != passwd:
            self.request.send('密码错误'.encode())

        sql_addr = 'select address from customer_statue where uid="%s"' % name
        cursor.execute(sql_addr)
        r = cursor.fetchone()
        if  r[0] != 'outline':
            self.request.send('该用户已登录'.encode())
            return
        # 将用户地址写入customer_status数据库,
        sql_status = "update customer_statue set address = '%s' where uid = '%s'" % (self.client_address[0], name)
        try:
            cursor.execute(sql_status)
            self.db.commit()
            self.request.send(B'OK')
        except Exception as e:
            print(e)
            self.request.send('登录失败'.encode())


if __name__ == '__main__':
    server_addr = ('176.122.15.131', 12345)
    server = socketserver.ThreadingTCPServer(server_addr, MyTCPHandler)
    server.serve_forever()
