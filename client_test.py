from socket import *
import sys
import getpass
import hashlib

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
        print('1.注册   2.登录   3.退出')
        cmd = input('输入选项')
        if cmd not in ['1','2','3']:
            print('请输入正确选项')
        elif cmd =='1':
            do_register()
        elif cmd =='2':
            do_login()
        elif cmd =='3':
            do_exit()

def do_register():
    while True:
        customer = input('请输入用户名')
        passwd = getpass.getpass('请输入密码')
        passwd_ms = getpass.getpass('再请输入密码')
        nname = input('请输入昵称')
        if passwd == passwd_ms:
            break
        if (' ' in customer) or (' ' in passwd) or (' ' in nname):
            print('用户名密码不能有空格')
            continue
        if passwd != passwd_ms:
            print('两次密码不一致')
            continue
        if  not nname:
            print('昵称不能为空')
            continue
    msg = 'R %s %s %s'%(customer,passwd,nname)
    sockfd.send(msg.encode())
    data = sockfd.recv(128).decode()
    if data =='OK':
        print('注册成功')
    else:
        print(data)

def do_login():
    while True:
        uname = input('输入用户名')
        passwd = input('输入密码')
        passwd = create_id(passwd)
        if uname and passwd:
            break
        else:
            continue
    msg = 'L %s %s'%(uname,passwd)
    sockfd.send(msg.encode())
    data = sockfd.recv(128).decode()
    if data == 'OK':
        print('登录成功')
    else:
        print(data)

def do_exit():
    sockfd.send(b' ')

def create_id(string):
    m = hashlib.md5(str(string).encode())
    return m.hexdigest()

if __name__ == '__main__':
    main()








