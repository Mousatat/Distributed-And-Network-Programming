import sys
import zmq

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
    if len(rec)<9:
        return True
    if rec[:8] !="isprime ":
        return True
    for i in range(8,len(rec)):
        if rec[i]<'0' or rec[i]>'9':
            return True
    return False
def worker(N):
    N=N[8:]
    N= int(N)
    if is_prime(N):
        return f"{N} is Prime"
    else:
        return f"{N} is not Prime"
def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True

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