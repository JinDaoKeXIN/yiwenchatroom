from socket import *
import sys
import getpass

HOST = '176.122.15.131'
PORT = 12345
ADDR = (HOST, PORT)
sockfd = socket()
try:
    sockfd.connect(ADDR)
except Exception as e:
    print(e)
    sys.exit()

def main():
    while True:
        print('''********w*e*l*c*o*m*e**********
                1-- 注册    2-- 登录    3-- 退出''')
        cmd = input('输入选项:')
        if cmd not in ['1', '2', '3']:
            print('请输入正确选项')
        elif cmd == '1':
            do_register()
        elif cmd == '2':
            do_login()
        elif cmd == '3':
            sockfd.send(b'E')
            print('谢谢使用')
            return
        sockfd.send(cmd.encode())


def do_register():
    while True:
        customer = input('请输入用户名')
        passwd = getpass.getpass('请输入密码')
        passwd_ms = getpass.getpass('请再次输入密码')
        if passwd == passwd_ms:
            break
        if (' ' in customer) or (' ' in passwd):
            print('用户名密码不能有空格')
            continue
        if passwd != passwd_ms:
            print('两次密码不一致')
            continue
    msg = 'R %s %s' % (customer, passwd)
    # 　发送请求
    sockfd.send(msg.encode())
    #  等待回复
    data = sockfd.recv(128).decode()
    if data == 'OK':
        print('注册成功')
        login(customer)
    else:
        print(data)


def do_login():
    customer = input('请输入用户名')
    passwd = getpass.getpass('密码')
    msg = 'L %s %s' % (customer, passwd)
    sockfd.send(msg.encode())
    data = sockfd.recv(128).decode()
    if data == 'OK':
        print('登录成功')
        login(customer)
    else:
        print(data)


def login(customer):
    while True:
        print('''********查询界面**********
                1-- 查单词    2-- 历史记录    3-- 注销''')
        cmd = input('输入选项:')
        if cmd not in ['1', '2', '3']:
            print('请输入正确选项')
        elif cmd == '1':
            do_query(customer)
        elif cmd == '2':
            do_hist(customer)
        elif cmd == '3':
            return

def do_query(customer):
    while True:
        word = input("单词：")
        if word == '##':
            break
        msg = 'Q %s %s'%(customer,word)
        sockfd.send(msg.encode())
        data = sockfd.recv(10240).decode()
        print(data)


def do_hist(name):
    msg = "H %s"%name
    sockfd.send(msg.encode())
    data = sockfd.recv(128).decode()
    if data =='OK':
        while True:
            data =sockfd.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print(data)

if __name__ == '__main__':
    main()
