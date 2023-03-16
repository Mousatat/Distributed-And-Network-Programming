from socket import socket, AF_INET, SOCK_STREAM
import time
from multiprocessing import Queue
import queue
from threading import Thread , Lock

IP_ADDR = '127.0.0.1'
PORT = 65432
BUF_SIZE = 1024

q = queue.Queue()
q_size = 1
current_size = 0
lock = Lock()
lock1 = Lock()
def message_converter_to_list(data):
    indeces = []
    for index, el in enumerate(data):
        if el == 124:
            indeces.append(index)
    list = []
    for i in range(0, len(indeces), 1):
        if i < len(indeces) - 1:
            list.append(data[indeces[i] + 1: indeces[i + 1]])
    list.append(data[indeces[len(indeces) - 1] + 1:])
    final_list = []
    for i in list:
        final_list.append(int(i.decode()))
    return final_list


def connection(conn, addr):
    message = conn.recv(BUF_SIZE)
    message = message_converter_to_list(message)
    answer = []
    for i in message:
        answer.append(is_prime(i))
    data = messages_converter(answer)
    data = data.encode()
    conn.send(data)
    print(f"data sent to client{addr}")


def messages_converter(messages):
    x = ""
    for message in messages:
        x = x + "|" + str(message)
    return x


def is_prime(n):
    if n in (2, 3):
        return 1
    if n % 2 == 0:
        return 0
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return 0
    return 1


def accept():
    global current_size
    while True:
        if current_size < q_size:
            conn, addr = s.accept()
            print(f"accept from {addr}")
            lock.acquire()
            current_size = current_size + 1
            lock.release()
            q.put(Thread(target=connection, args=(conn, addr)))


with socket(AF_INET, SOCK_STREAM) as s:
    s.bind((IP_ADDR, PORT))
    try:
        s.listen()
        print("waiting for connection.")
        t = Thread(target=accept)
        t.start()
        while True:
            if q.empty():
                continue
            q.get().start()
            lock1.acquire()
            current_size = current_size - 1
            lock1.release()
    except KeyboardInterrupt:
        print("Keyboard interrupt, server is shutting down.")
