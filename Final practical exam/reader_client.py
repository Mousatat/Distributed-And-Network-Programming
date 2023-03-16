import sys
import zmq

PORT1 = 5555

context = zmq.Context()
print("Waiting to recieve from server")
client_output = context.socket(zmq.SUB)
client_output.connect(f"tcp://localhost:{PORT1}")
client_output.setsockopt_string(zmq.SUBSCRIBE, '')

client_output.RCVTIMEO = 100

try:
    PORT1 = sys.argv[1]
    while True:
        try:
            rec = client_output.recv_string()
            print(rec)
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print("Terminating reader")
    sys.exit(0)
