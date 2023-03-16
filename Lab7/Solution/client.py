import grpc
import sys
import raft_pb2
import raft_pb2_grpc

class Client:
    def init(self):
        print("starts")
        self.server_ip = ""
        self.server_port = -1
        self.stub = None

    def start_client(self):
        try:
            while True:
                try:
                    input_command = input("> ").split(" ")
                    if len(input_command) == 1:
                        if input_command[0] == "getleader":
                            self._get_leader()
                        elif input_command[0] == "quit":
                            print("The client ends")
                            break
                    elif len(input_command) == 2:
                        if input_command[0] == "suspend":
                            self._suspend(int(input_command[1]))
                        elif input_command[0] == "getval":
                            self._getval(str(input_command[1]))
                    elif len(input_command) == 3:
                        if input_command[0] == "connect":
                            self.ip = input_command[1]
                            self.port = input_command[2]
                            channel = grpc.insecure_channel(self.ip+":"+self.port)
                            self.stub = raft_pb2_grpc.RaftServerStub(channel)
                            print(self.stub)
                        elif input_command[0] == "setval":
                            self._setval(str(input_command[1]),str(input_command[2]))
                except ValueError:
                    pass
        except KeyboardInterrupt:
            print("ends")

    def _connect(self, address, port):
        self.server_ip = address
        self.server_port = port
    def _setval(self, key, value):
        req = raft_pb2.SetValRequest(key=key,value=value)
        server_reply = self.stub.SetVal(req)
        print(server_reply.suc)
    def _getval(self, key):
        req = raft_pb2.GetValRequest(key=key)
        server_reply = self.stub.GetVal(req)
        print(server_reply.value)
    def _get_leader(self):
        req = raft_pb2.Empty(empty = "")
        server_reply = self.stub.GetLeader(req)
        print (server_reply.leader)

    def _suspend(self, period):
        req = raft_pb2.SuspendRequest(period = period)
        self.stub.Suspend(req)


Client().start_client()