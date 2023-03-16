import sys
import zmq

PORT1 = 5555
PORT2 = 5556
context = zmq.Context()
print(" connecting")
client_input = context.socket(zmq.REQ)
client_input.connect(f"tcp://localhost:{PORT1}")

client_output = context.socket(zmq.SUB)
client_output.connect(f"tcp://localhost:{PORT2}")
client_output.setsockopt_string(zmq.SUBSCRIBE, '')

client_input.RCVTIMEO = 100
client_output.RCVTIMEO = 100

try:
    PORT1 = sys.argv[1]
    PORT2 = sys.argv[2]
    while True:
        line = input(">")
        if len(line) != 0:
            client_input.send_string(line)
            client_input.recv()
        try:
            while True:
                rec = client_output.recv_string()
                print(rec)
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print("Terminating client")
    sys.exit(0)
