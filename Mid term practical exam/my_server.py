import multiprocessing
import threading
import socket
import time
import sys
updates = 0
def recieve(s, addr):
    dectionary={}
    while True:
        data = s.recv(2048)
        data = data.decode()
        if data:
            dectionary = {"address": addr, "name": data}
            map.append(dectionary)
        else:
            map.remove(dectionary)
            s.close()
def send():
    send_message=""
    for i in map:
        send_message= send_message + i["name"]
    send_message.encode()
    for i in map:
        addr= i["addr"]
        name= i["name"]
        s= i["s"]
        s.send(send_message)
    return
def thread_manager(s, addr):
    dectionary = {}
    while True:
        data = s.recv(2048)
        data = data.decode()
        if data:
            dectionary = {"addr": addr, "name": data, "s": s}
            map.append(dectionary)
            send()
        else:
            map.remove(dectionary)
            send()
            s.close()
terminate = False
map=[]
port = int(sys.argv[1])
try:

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('127.0.0.1', port))
    s.settimeout(None)
    s.listen()

    while terminate == False:
        conn,addr = s.accept()
        thread = threading.Thread(target=thread_manager, args=(conn, addr))
        thread.start()
except KeyboardInterrupt:
    print("Shuting down")
    terminate = True
    for i in map:
        i["s"].close()
    print("Done")

