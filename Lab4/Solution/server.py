from concurrent import futures
import math
import grpc
import SimpleService_pb2_grpc as bidirectional_pb2_grpc
import SimpleService_pb2 as bidirectional_pb2

def make_message(message):
    return bidirectional_pb2.Message(
        message=message
    )

class BidirectionalService(bidirectional_pb2_grpc.BidirectionalServicer):
    def GetServerResponse(self, request_iterator, context):
        for message in request_iterator:
            print (message.message)
            answers = work(message.message)
            ans=""
            j=0
            for i in answers:
                if j == 0:
                    ans = i
                    j=1
                else:
                    ans= ans + "\n" + i
            yield make_message(ans)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bidirectional_pb2_grpc.add_BidirectionalServicer_to_server(BidirectionalService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

def work(message):
    if message[:8] == "reverse ":
        list = reverse(message)
    elif message[:8] == "isprime ":
        list = isprime(message)
    else:
        list = split(message)
    for i in list:
        yield i
def split(message):
    space = []
    for i in range(len(message)):
        if message[i] == " ":
            space.append(i)
    word = []
    for i in range(len(space)):
        if i != 0:
            word.append(message[space[i-1]+1:space[i]])
    word.append(message[space[len(space) - 1]+1:len(message)])
    yield f"number:{len(word)}"
    for w in word:
        yield f"Parts: {w}"
def reverse(message):
    result = "message: "
    j = len(message)-1
    for i in message:
        if j == 6:
            break
        result = result + message[j]
        j -= 1
    yield result
def prime(n):
    return all([(n % j) for j in range(2, int(n**0.5)+1)]) and n>1
def isprime(message):
    space = []
    for i in range(len(message)):
        if message[i] == " ":
            space.append(i)
    primes = []
    for i in range(len(space)):
        if i!=0:
            primes.append(int(message[space[i]-1:space[i]]))
    primes.append(int(message[space[len(space)-1]:len(message)]))
    for prime1 in primes:
        if prime(prime1):
            yield f"{prime1} is prime"
        else:
            yield f"{prime1} is not prime"
if __name__ == '__main__':
    serve()