from __future__ import print_function

import grpc
import SimpleService_pb2_grpc as bidirectional_pb2_grpc
import SimpleService_pb2 as bidirectional_pb2

def make_message(message):
    return bidirectional_pb2.Message(
        message=message
    )


def generate_messages():
    messages = [
        make_message("isprime 1 2 3 4 5"),
    ]
    while True:
        m=input("write the command: ")
        if m=="exit":
            print("termination")
            break
        else:
            yield make_message(m)

def send_message(stub):
    responses = stub.GetServerResponse(generate_messages())
    for response in responses:
            print(response.message)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bidirectional_pb2_grpc.BidirectionalStub(channel)
        send_message(stub)


if __name__ == '__main__':
    run()