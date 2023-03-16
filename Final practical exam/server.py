import sys
import time
import zmq

import threading
import time

PORT1 = 5001
PORT2 = 5555
context = zmq.Context()
client_input = context.socket(zmq.REP)
client_input.bind(f"tcp://*:{PORT1}")
Summery ={}
client_output = context.socket(zmq.PUB)
client_output.bind(f"tcp://*:{PORT2}")

def worker():       #this worker Thread to deal with the sammary and checking about if we need to reset the Summary
    while True:
        dic = Summery.copy()
        time.sleep(5)
        for i in dic:
            if dic[i]==Summery[i]:
                Summery[i]=0
        print_summery()
def make_summery(message): #this Function to increase the Sammary sorry for the wrong name 
    NAME, content = message.split(':')
    if NAME in Summery.keys():
        Summery[NAME] += 1
    else:
        Summery[NAME] = 1
        
def print_summery():    #This function to print the Summary
    client_output.send_string("SUMMARY")
    for i in Summery:
        respond = str(i) +": "+ str(Summery[i]) 
        client_output.send_string(respond)
try:
    PORT1 = sys.argv[1]
    PORT2 = sys.argv[2]
    x = threading.Thread(target=worker)
    x.start()
    print("SERVER is ready")
    while True:
        message = client_input.recv_string()
        client_input.send_string("done")
        client_output.send_string(message)
        make_summery(message)

except KeyboardInterrupt:
    print("Server Terminating")
    sys.exit(0)