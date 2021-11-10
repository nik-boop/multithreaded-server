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
logs = []
ls_send_mes = []

lock = threading.Lock()

def Exit():
    global fex
    fex = True


def workWclient(addr):
    '''Работа с клиентом'''
    def del_user(addr, com=''):
        '''Удаление пользователя'''
        print(f"User_delete {addr}: {dict_us[addr]['nik']} {com}")
        logs.append(f"{time.strftime( '%d%m%Y %H:%M:%S', time.localtime())} del user {addr} {com}")
        dict_us.pop(addr)

    while True:
        lock.acquire()
        try:
            # Проверка на флаг exo
            if dict_us[addr]['exo'] == False:
                dict_us[addr]['exo'] = time.time()
                sock.sendto('exoc'.encode(), addr)

            # Удаление неактивного пользователя
            elif type(dict_us[addr]['exo']) == float:
                if time.time() - dict_us[addr]['exo'] > 10:
                    del_user(addr, 'time out')
                    break
            # Удаление пользователя
            elif dict_us[addr]['del'] == True:
                del_user(addr,  'exit')
                break
        finally:
            lock.release()



        while len(dict_us[addr]['messages']) > 0:
            message = dict_us[addr]['messages'].pop(0)
            print(f"{addr}: {message}")
            ls_send_mes.append(f" {addr}: {message}")
            sock.sendto(message.encode(), addr)



def get_inf():
    '''Прием информации от клиентов'''

    global dict_us
    print("Server stert!")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except BlockingIOError as err:
            continue
        except ConnectionResetError as err:
            continue
        else:
            if dict_us.get(addr) is None:
                dict_us[addr] = {'nik': 'no_name', 'messages': [], 'exo': True, 'del': False}
                logs.append(f"{time.strftime( '%d%m%Y %H:%M:%S', time.localtime())} add new user {addr}")
                thread = threading.Thread(target=workWclient, args=(addr, ))
                thread.daemon = True
                thread.start()

            ls_all_mes.append(
                {
                    'mos_mes': "Get",
                    'time': time.strftime('%H:%M:%S', time.localtime()),
                    'addr': addr,
                    'len': len(data),
                    'nik': dict_us.get(addr).get('nik'),
                    'mes': data
                }
            )

            t = ls_all_mes[-1]['time']
            #lock.acquire()
            #try:
                #print(f"get_mes len: {len(data)}Byte".ljust(20), f'{t}'.ljust(7))
            #finally:
                #lock.release()

            data = data.decode()

            if data == 'exos':
                lock.acquire()
                dict_us[addr]['exo'] = True
                logs.append(f"{time.strftime( '%d%m%Y %H:%M:%S', time.localtime())} exo from {addr}")
                lock.release()

            elif 'nik<<' in data:
                data = data.split('<<')
                if dict_us[addr]['nik'] == 'no_name':
                    print(f"App user {data[1]}")
                else:
                    print(f'Reset user {data[1]}')
                logs.append(f"{time.strftime( '%d%m%Y %H:%M:%S', time.localtime())} rename user {addr}")
                sock.sendto('User_set'.encode(), addr)
                dict_us[addr]['nik'] = data[1]

            elif data == 'exit':
                dict_us[addr]['del'] = True
                logs.append(f"{time.strftime( '%d%m%Y %H:%M:%S', time.localtime())} user {addr} came out")
            elif data == 'pass':
                pass
            else:
                ls_mes.append((dict_us[addr]['nik'], data))
                mess.append((data, addr))



def send_mes():
    '''
    Отправка сообщений пользователям
    '''
    while True:
        while len(mess) > 0:
            k = 0
            weight_mes = 0
            (messag, addrm) = mess.pop(0)
            lock.acquire()
            try:
                dict_usc = dict_us.copy()
                for addr, param in dict_usc.items():
                    if addr != addrm:
                        if addrm == (0, 0):
                            data = f"admin: {messag}"
                        else:
                            data = f"\33 [ {dict_us[addrm]['nik']}: {messag}"
                        dict_us[addr]['messages'].append(data)
                        dict_us[addr]['exo'] = False
                        k += 1
                        weight_mes += len(data)

                        pass
                #print(f"send mes all: col_mes {k}, weight_all_mes {weight_mes}Byte")
            finally:
                lock.release()
        else:
            continue



def Input():
    '''Команды консоли сервера'''
    global dict_us, logs
    while True:
        data = input()
        data = data.split(":")
        # Словарь пользователей
        if data[0] == 'ls':
            print(*[(k, v) for k, v in dict_us.items()], sep='\n')
        # Очистить данные пользователей
        elif data[0] == 'rm dict':
            dict_us = {}
        # Выключить сервер
        elif data[0] == 'quit':
            Exit()
        # Показать полученые сообщения
        elif data[0] == "ls_mes":
            print(*ls_mes, sep='\n')
        # Показать полученые сообщения включая служебные
        elif data[0] == "ls_all_mes":
            print(*ls_all_mes, sep='\n')
        # Показать логи
        elif data[0] == 'log':
            print(*logs, sep='\n')
        # Отправить сообщение пользователю send_mes:'127.0.0.1', port:message'
        elif data[0] == 'send_mes':
            data[1] = data[1].split(',')
            data[1] = (data[1][0], int(data[1][1]))
            dict_us[data[1]]['messages'].append(f"Server-admin {data[2]}".encode())
        # Остановить прослушивание
        elif data[0] == 'stop_l':
            lock.acquire()
            print('stop listening')
        # Возрбновить пролслушивание
        elif data[0] == 'start_l':
            lock.release()
            print('start_listening')
        # удалить логи
        elif data[0] == 'del_logs':
            logs = []
        # написать всем
        elif data[0] == 'send_all':
            mess.append((data[1], (0, 0)))
        # Показать отправленные сообщения
        elif data[0] == 'ls_send_m':
            print(*ls_send_mes, sep='\n')


get_inft = threading.Thread(target=get_inf, name='get_inf')
get_inft.daemon = True
get_inft.start()

Inputt = threading.Thread(target=Input, name='Input')
Inputt.daemon = True
Inputt.start()

Send_mes = threading.Thread(target=send_mes, name='Send_mes')
Send_mes.daemon = True
Send_mes.start()

while True:
    if fex:
        print('Server close')
        exit()
