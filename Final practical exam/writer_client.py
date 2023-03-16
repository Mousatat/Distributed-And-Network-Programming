import sys
import zmq

PORT1 = 5001
NAME = "alice"
context = zmq.Context()
print("Waiting to Write")
client_input = context.socket(zmq.REQ)
client_input.connect(f"tcp://localhost:{PORT1}")

client_input.RCVTIMEO = 100

try:
    PORT1 = sys.argv[1]
    NAME = sys.argv[2]
    while True:
        line = input(">")
        if len(line) != 0:
            client_input.send_string(NAME+":"+line)
            client_input.recv()
except KeyboardInterrupt:
    print("Terminating writer")
    sys.exit(0)
