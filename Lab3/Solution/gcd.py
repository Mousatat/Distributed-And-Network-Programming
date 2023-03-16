import sys
import zmq
import math

PORT3 = 5557
PORT4 = 5558
context = zmq.Context()
print(" connecting")
worker_inputs = context.socket(zmq.SUB)
worker_inputs.connect(f"tcp://localhost:{PORT3}")
worker_inputs.setsockopt_string(zmq.SUBSCRIBE, '')

worker_outputs = context.socket(zmq.PUB)
worker_outputs.connect(f"tcp://localhost:{PORT4}")

worker_inputs.RCVTIMEO = 100
worker_outputs.RCVTIMEO = 100

def check_unvalid(rec):
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
def worker(N):
    g , A , B =N.split(" ")
    A = int(A)
    B = int(B)
    return f"GCD for {A} and {B} is {gcd(A, B)}"
def gcd(A, B):
    return math.gcd(A, B)

try:
    PORT3 = sys.argv[1]
    PORT4 = sys.argv[2]
    print ("Waiting")
    while True:
        try:
            rec = worker_inputs.recv_string()
            if check_unvalid(rec) == False:
                worker_outputs.send_string(worker(rec))
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print("Terminating primer")
    sys.exit(0)