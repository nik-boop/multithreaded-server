import socket, threading, time

NAME = ''
PORT = 50000
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind((NAME, PORT))
sock.setblocking(False)
dict_us = {}
fex = False
ls_mes = []
ls_all_mes = []
mess = []
del_dict = {}
lock = threading.Lock()

def Exit():
    global fex
    fex = True


def get_inf():
    '''Прием информации от клиентов'''
    print("Server stert!")
    global dict_us

    def get_nik_name(data, addr):
        '''Создание или перезапись ника клиента'''
        global dict_us
        data = data.split('<>')
        if dict_us.get(addr) is None:
            print(f"App user {data[1]}")
        else:
            print(f'Reset user {data[1]}')
        dict_us[addr] = data[1]
        del_dict[addr] = True

    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except BlockingIOError as err:
            continue
        except ConnectionResetError as err:
            continue
        else:
            ls_all_mes.append(
                (
                    "Get",
                    time.strftime('%H:%M:%S', time.localtime()),
                    addr,
                    len(data),
                    dict_us.get(addr, "noname_user"),
                    data
                )
            )
            dict_us.setdefault(addr, 'no_name')
            data = data.decode()

            if 'nik<>' in data:
                get_nik_name(data, addr)
                sock.sendto('User_set'.encode(), addr)
            elif data == 'exit':
                del_us(addr)
                sock.sendto('User_delete'.encode(), addr)
            elif data == "exos":
                if type(del_dict.get(addr)) == float:
                    del_dict[addr] = True
            else:
                ls_mes.append((dict_us[addr], addr, data))
                mess.append((data, addr))

            lock.acquire()
            try:
                t = ls_all_mes[-1][1]
                print(f'get_mes len: {len(data)}Byte'.ljust(20), f'{t}'.ljust(7), sep="    ", end='\n')
            finally:
                lock.release()

def del_us(addr):
    global dict_us
    print(f'User_delete {addr}: {dict_us.pop(addr, "del failed")}')


def send_mes():
    '''
    Отправка сообщений пользователям
    '''
    while True:
        if len(mess) != 0:
            k = 0
            weight_mes = 0
            (mes, addrm) = mess.pop(0)
            for addr, nik in dict_us.items():
                if addr != addrm:
                    data = f"\33[ {dict_us[addr]}: {mes}".encode()
                    sock.sendto(data, addr)
                    sock.sendto('exoc'.encode(), addr)
                    del_dict[addr] = time.time()
                    k += 1
                    weight_mes += len(data)
            lock.acquire()
            try:
                print(f"send mes all: col_mes {k}, weight_all_mes {weight_mes}Byte")
            finally:
                lock.release()
        else:
            continue

def check_del():
    '''
    Проверка на отлючившихся пользователей
    '''
    while True:
        del_list = []
        lock.acquire()
        try:
            del_dictc = del_dict.copy()
            for addr, t in del_dictc.items():
                if t != True and time.time() - t > 10:
                    del_us(addr)
                    del_list.append(addr)
            for i in del_list:
                del_dict.pop(i)
        finally:
            lock.release()

def Input():
    '''Команды консоли сервера'''
    global dict_us
    while True:
        data = input()
        data = data.split(":")
        if data[0] == 'ls':
            print(dict_us)

        elif data[0] == 'rm dict':
            dict_us = {}

        elif data[0] == 'quit':
            Exit()

        elif data[0] == "ls_mes":
            print(*ls_mes, sep='\n')

        elif data[0] == "ls_all_mes":
            print(*ls_all_mes, sep='\n')

        elif data[0] == 'send_mes':
            data[1] = data[1].split(',')
            data[1] = (data[1][0], int(data[1][1]))
            sock.sendto(data[2].encode(), data[1])


get_inft = threading.Thread(target=get_inf, name='get_inf')
get_inft.daemon = True
get_inft.start()

Inputt = threading.Thread(target=Input, name='Input')
Inputt.daemon = True
Inputt.start()

Send_mes = threading.Thread(target=send_mes, name='Send_mes')
Send_mes.daemon = True
Send_mes.start()

check_delt = threading.Thread(target=check_del, name='check_del')
check_delt.daemon = True
check_delt.start()

while True:
    if fex:
        print('Server close')
        exit()
