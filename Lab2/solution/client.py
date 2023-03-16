from socket import socket, AF_INET, SOCK_STREAM, timeout
import sys
DEST_IP_ADDR = '127.0.0.1'
DEST_PORT = 65432
BUF_SIZE = 1024
messages = [15492781, 15492787, 15492803,
15492811, 15492810, 15492833,
15492859, 15502547, 15520301,
15527509, 15522343, 1550784]
def messages_converter():
    x=""
    for message in messages:
        x=x+"|"+str(message)
    return x

def message_converter_to_list(data):
    indeces=[]
    for index, el in enumerate(data):
        if el==124:
            indeces.append(index)
    list=[]
    for i in range(0,len(indeces),1):
        if i < len(indeces) - 1:
            list.append(data[indeces[i] + 1: indeces[i + 1]])
    list.append(data[indeces[len(indeces) - 1] + 1:])
    final_list=[]
    for i in list:
        final_list.append(int(i.decode()))
    return final_list

class NoServerResponseException(Exception):
    pass
if len(sys.argv) <= 1:
    print("Provide the file name as an argument in command line!")
else:
    add = sys.argv[1]
    x=0
    for i in add:
        if i ==":":
            break
        x += 1
    DEST_IP_ADDR = str(add[:x])
    DEST_PORT = int(add[x+1:])
    with socket(AF_INET, SOCK_STREAM) as s:
        s.settimeout(100)
        try:
            s.connect((DEST_IP_ADDR, DEST_PORT))
            s.send(messages_converter().encode())
            print ("messages all fully sent")
            message = s.recv(BUF_SIZE)
            print ("The answer is received")
            print (message_converter_to_list(message))
        except timeout:
            print("server is not available")
        except NoServerResponseException:
            print("server is not available")

