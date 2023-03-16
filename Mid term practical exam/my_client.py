import socket
import sys

try:
    hostname = sys.argv[1].split(":")
    hostname[1] = int(hostname[1])
    hostname = tuple(hostname)
    client_name= sys.argv[2]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(client_name)
    s.send(str(client_name).encode())
    while(True):
        message = s.recv(1024)
        print(message.decode())
    print('Done')
except:
    print('Terminated')