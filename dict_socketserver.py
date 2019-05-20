import socketserver
import time
import pymysql
import uuid
import hashlib
import json


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
                elif self.data[0] == 'S':
                    self.show_customer()
                elif self.data[0] == 'C':
                    self.chat_each(self.data)
                elif self.data[0] == 'O':



            except ConnectionResetError as e:
                print('erro:', e)
                break

    def __connect_dbs(self):
        '''
        连接数据库
        :return:
        '''
        db = pymysql.connect('localhost', 'root', '123456', 'chat_room', charset='utf8')
        return db

    def __create_uid(self):
        '''
        生成唯一uid
        :return:
        '''
        return str(uuid.uuid1())

    def __create_id(self, string):
        '''
        明文密码转密文
        :param string: 明文密码
        :return:
        '''
        m = hashlib.md5(str(string).encode())
        return m.hexdigest()

    def do_register(self, data):
        '''
        处理注册操作
        :param data: 用户注册信息
        :return:
        '''
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
        # 用户注册存入customer_base表,记录uuid,用户名,密码,昵称
        sql1 = "insert into customer_base (uuid,uid,password,nname) VALUES ('%s','%s','%s','%s')" % (
            uuid, name, passwd, nname)
        # 用户注册同时存入customer_statue表,记录uuid,用户名,在线状态;在登录功能中修改地址
        sql2 = "insert into customer_statue (uuid,uid,nname,address) VALUES ('%s','%s','%s','%s')" % (
        uuid, name, nname, 'outline')
        try:
            cursor.execute(sql1)
            cursor.execute(sql2)
            self.db.commit()
            self.request.send(b'OK')
        except Exception as e:
            self.db.rollback()
            self.request.send('注册失败'.encode())
            print(self.request)#得到地址
            print(e)

    def do_login(self, data):
        '''登录功能,更改在线状态,写入登录地址'''
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
        if r[0] != 'outline':
            self.request.send('该用户已登录'.encode())
            return
        # 将用户地址写入customer_status表,
        sql_status = "update customer_statue set address = '%s' where uid = '%s'" % (self.client_address[0], name)
        try:
            cursor.execute(sql_status)
            self.db.commit()
            self.request.send(B'OK')
        except Exception as e:
            print(e)
            self.request.send('登录失败'.encode())

    def show_customer(self):
        '''
        展示在线用户
        :return:
        '''
        # 查询在线用户,查询customer_statue表
        dict_online = {}
        cursor = self.db.cursor()
        sql_show = "select nname,address from customer_statue where address is not 'outline'"
        cursor.execute(sql_show)
        r = cursor.fetchall()
        for item in r:
            dict_online[item[0]] = item[1]
        dict_send = json.dumps(dict_online)
        self.request.send(dict_send.encode())


    def chat_each(self,data):
        tmp = data.split(' ')
        self.request =tmp[1]
        msg = tmp[2]
        self.request.send(msg.encode())

    def do_out(self):
        cursor = self.db.cursor()
        sql_outline = "update customer_statue set address = 'outline' where address = '%s' "%self.client_address[0]
        try:
            cursor.execute(sql_outline)
            self.db.commit()
            self.request.send(B'OUT')
        except Exception as e:
            print(e)
            self.request.send('登出失败'.encode())


if __name__ == '__main__':
    server_addr = ('176.122.15.131', 12345)
    server = socketserver.ThreadingTCPServer(server_addr, MyTCPHandler)
    server.serve_forever()
