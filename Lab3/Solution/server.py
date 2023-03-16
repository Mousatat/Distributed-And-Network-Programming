import sys
import time
import zmq

PORT1 = 5555
PORT2 = 5556
PORT3 = 5557
PORT4 = 5558
context = zmq.Context()
client_input = context.socket(zmq.REP)
client_input.bind(f"tcp://*:{PORT1}")

client_output = context.socket(zmq.PUB)
client_output.bind(f"tcp://*:{PORT2}")

worker_inputs = context.socket(zmq.PUB)
worker_inputs.bind(f"tcp://*:{PORT3}")

worker_outputs = context.socket(zmq.SUB)
worker_outputs.bind(f"tcp://*:{PORT4}")
worker_outputs.setsockopt_string(zmq.SUBSCRIBE, '')

def check_unvalid_prime(rec):
    if len(rec)<9:
        return True
    if rec[:8] !="isprime ":
        return True
    for i in range(8,len(rec)):
        if rec[i]<'0' or rec[i]>'9':
            return True
    return False
def check_unvalid_gcd(rec):
    if len(rec)<7:
        return True
    if rec[:4] != "gcd ":
        return True
    space_num = 0
    for i in range(4,len(rec)):
        if rec[i]>='0' and rec[i]<='9':
            continue
        elif rec[i] == ' ':
            space_num += 1
        else:
            return False
    if space_num != 1:
        return True
    return False
try:
    PORT1 = sys.argv[1]
    PORT2 = sys.argv[2]
    PORT3 = sys.argv[3]
    PORT4 = sys.argv[4]
    while True:
        message = client_input.recv_string()
        client_input.send_string("done")
        client_output.send_string(message)
        if check_unvalid_prime(message) == True and check_unvalid_gcd(message) == True:
            continue
        worker_inputs.send_string(message)
        try:
            while True:
                ans=worker_outputs.recv_string()
                if len(ans) != 0:
                    client_output.send_string(ans)
                    break
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print("Server Terminating")
    sys.exit(0)