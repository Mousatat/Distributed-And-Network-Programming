from atexit import register
from concurrent import futures
from os.path import isfile
from math import ceil
import random as rand
from time import time, sleep
import grpc
import sys
import raft_pb2
import raft_pb2_grpc

#Main class for RAFT server.
class Raft_server(raft_pb2_grpc.RaftServerServicer):
    #Initialization.
    def __init__(self, my_dict_address, node_id):
        self.my_state = 'follower'
        self.last_log_idx = 0
        self.last_log_term = 0
        self.commit_idx = 0
        self.id = int(node_id)
        self.leader_id = None
        self.log = {}
        self.temp_add = []
        for i in my_dict_address.values():
            self.temp_add.append(i)
        self.my_dict_address = my_dict_address
        self.my_dict_address.pop(str(self.id))
        self.port_addr = []
        self.term = 0
        self.trand = rand.randint(150,300)/1000
        self.timeout = time() + self.trand
        self.vote_count = 0
        self.voted_for = -1
        self.stub_list = []
        self.suspended = False
        self.suspend_time = time() + 0
        print("I am a Follower. Term:{}".format(self.term))
        #Storing address of all channels to be contacted to.
        for i in self.my_dict_address:
            tmp = i,self.my_dict_address[i]
            self.port_addr.append(tmp)
        if (isfile('log.txt')):
            with open('log.txt', 'r') as fp:
                line = fp.readline()
                while (line):
                    temp_list = line.strip('\n').split(' ')
                    entry = raft_pb2.Entry(term=int(temp_list[0]), index=int(temp_list[1]), key=temp_list[2], value=temp_list[3])
                    self.log[entry.index] = entry
                    self.last_log_idx = entry.index
                    self.last_log_term = entry.term
                    line = fp.readline()
        print("Opening Channel...")
        for self.address in self.my_dict_address.values():
            channel = grpc.insecure_channel(self.address)
            stub = raft_pb2_grpc.RaftServerStub(channel)
            self.stub_list.append(stub)

#Function to Update my state once in a while.
    def update(self):
        if self.suspended:
            print("Sleeping for {} seconds".format(self.suspend_time))
            sleep(self.suspend_time)
            self.timeout = time() + self.trand
            self.suspended = False
            self.suspend_time = 0

        elif (self.my_state == 'follower'):
            if(time()>self.timeout):
                    print('The Leader is dead. Term: {}'.format(self.term))
                    self.leader_id = None
                    self.my_state = 'candidate'
                    self.term +=1
        elif (self.my_state == 'candidate'):
            if (time() > self.timeout):
                self.term += 1
                self.vote_count = 1
                self.timeout = time()+ self.trand
                self.voted_for = self.id
                print('I am a Candidate')
                #Requesting Vote.
                print('Requesting vote....')
                req = raft_pb2.RequestVoteRequest(term=self.term, cadidateId=self.id, lastLogIndex=self.last_log_idx,
                                                  lastLogTerm=self.last_log_term)
                i = 0
                for stub in self.stub_list:
                    try:
                        #Store Response.
                        response = stub.RequestVote(req)
                        print('Got request vote response: {}'.format(response))
                        if (response.voteGranted):
                            self.vote_count += 1
                    except:
                        print('cannot connect to ' + str(self.port_addr[i]))
                    i += 1
                self.timeout = time() + self.trand
            elif (self.vote_count >= (len(self.my_dict_address) + 1) // 2 + 1):
                self.my_state = 'leader'
                self.vote_count = 1
                self.voted_for = self.id
                self.timeout = time()
                print('I am a Leader')
        elif (self.my_state == 'leader'):
            if (time() > self.timeout):
                prevLogIndex = self.last_log_idx
                if (prevLogIndex in self.log):
                    entry = self.log[prevLogIndex]
                else:
                    entry = None
                #Append Entries Request.
                req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id, prevLogIndex=prevLogIndex,
                                                    prevLogTerm=self.last_log_term, entry=entry,
                                                    leaderCommit=self.commit_idx)
                i = 0
                for stub in self.stub_list:
                    try:
                        response = stub.AppendEntries(req)
                        while (response.success == False):
                            prevLogIndex -= 1
                            entry = self.log[prevLogIndex]
                            #Append Entries Request.
                            req = raft_pb2.AppendEntriesRequest(term=self.term,leaderId=self.id,
                                                                prevLogIndex=prevLogIndex, prevLogTerm=entry.term,
                                                                entry=entry, leaderCommit=self.commit_idx)
                            response = stub.AppendEntries(req)
                        while (prevLogIndex < self.last_log_idx):
                            prevLogIndex += 1
                            entry = self.log[prevLogIndex]
                            #Append Entries Request.
                            req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id,
                                                                prevLogIndex=prevLogIndex, prevLogTerm=entry.term,
                                                                entry=entry, leaderCommit=self.commit_idx)
                            response = stub.AppendEntries(req)
                    except:
                        print('cannot connect to ' + str(self.port_addr[i]))
                    i += 1
                self.timeout = time() + 50/1000

#function to Get Leader in server
    def GetLeader(self, req, context):
        print("Command from client: getleader")
        if self.leader_id!= None:
            l = f'{self.leader_id} {self.temp_add[self.leader_id]}'
            return raft_pb2.GetLeaderResponse(leader= l)
        elif self.voted_for == -1:
            return raft_pb2.GetLeaderResponse(leader= 'nothing')
        else:
            v = f"{self.voted_for} {self.temp_add[self.voted_for]}"
            return raft_pb2.GetLeaderResponse(leader= v)

#function to Suspend
    def Suspend(self, req, context):
        self.suspended = True
        self.suspend_time = req.period
        print("Command from client: suspend {}".format(self.suspend_time))
        return raft_pb2.SuspendResponse(res='suspend {}'.format(req.period))

#Function to Request Vote.
    def RequestVote(self, req, context):
        if (req.term > self.term):
            self.term = req.term
            self.voted_for = -1
        if (req.term < self.term):
            print('Returning Vote Response as false since requested term is less')
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)
        if ((self.voted_for == -1 or self.voted_for == req.cadidateId) and (req.lastLogTerm > self.last_log_term or (
                req.lastLogTerm == self.last_log_term and req.lastLogIndex >= self.last_log_idx))):
            self.my_state = 'follower'
            print('I am a Follower')
            self.voted_for = req.cadidateId
            self.trand = rand.randint(150,300)/1000 #random from 150 to 300ms
            self.timeout = time() + self.trand
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=True)
        return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)

#Function to handle Append Entries.
    def AppendEntries(self, req, context):
        if (req.term < self.term or (
                req.prevLogIndex in self.log and self.log[req.prevLogIndex].term != req.prevLogTerm)):
           return raft_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.my_state = 'follower'
        self.term = req.term
        self.leader_id = req.leaderId
        self.timeout = time() + self.trand
        if (req.prevLogIndex == self.last_log_idx + 1 and req.prevLogTerm >= self.last_log_term):
            self.log[req.entry.index] = req.entry
            self.last_log_idx += 1
            self.last_log_term = req.prevLogTerm
            print(self.log)
            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        if (req.prevLogIndex == self.last_log_idx and req.prevLogTerm == self.last_log_term):
            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        return raft_pb2.AppendEntriesResponse(term=self.term, success=False)


    def SetVal(self, req, context):
        print('Got client append: {}'.format(req))
        if (self.my_state != 'leader'):
            # find the leader
            channel = grpc.insecure_channel(self.temp_add[self.voted_for])
            self.stubTemp = raft_pb2_grpc.RaftServerStub(channel)
            preq = raft_pb2.SetValRequest(key=req.key, value=req.value)
            leaderReply = self.stubTemp.SetVal(preq)
            return raft_pb2.SetValResponse(suc=leaderReply.suc)

        self.last_log_term = self.term
        self.last_log_idx += 1
        entry = raft_pb2.Entry(term=self.term, index=self.last_log_idx, key = req.key , value =req.value)
        self.log[self.last_log_idx] = entry
        # Append Entries Request.
        print('Sending Append entries Request...')
        req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id, prevLogIndex=self.last_log_idx,
                                            prevLogTerm=self.last_log_term, entry=entry, leaderCommit=self.commit_idx)
        i = 0
        for stub in self.stub_list:
            try:
                response = stub.AppendEntries(req)
                print('I am the Leader')
                print('Got append entries response: {}'.format(response))
            except:
                print('cannot connect to ' + str(self.port_addr[i]))
            i += 1
        self.commit_idx += 1
        self.timeout = time() + 50 / 1000
        return raft_pb2.SetValResponse(suc=True)

    def GetVal(self, req, context):
        print('Got client request index: {}'.format(req))
        for i in range(1,len(self.log)+1):
            if req.key == self.log[i].key:
                return raft_pb2.GetValResponse(suc=True, value=self.log[i].value)
        return raft_pb2.GetValResponse(suc=False,value="None")
#Storing Log Information.
    def get_log(self):
        return self.log

#Function to write to disk.
def writeToDisk():
    print("Writing...")
    with open('log.txt', 'w') as f:
        log = raftserver.get_log()
        for entry in log.values():
            f.write(str(entry.term) + ' ' + str(entry.index) + ' ' + entry.key + ' ' + entry.value + '\n')


#Function to write to disk.
node_id = sys.argv[1]

#Read the text file and store replica_number and address:Port as (key,value) pair in a Dictionary.
my_dict_address = {}
with open('Config.conf', 'r') as f:
    line = f.readline()
    while (line):
        temp_list = line.split()
        my_dict_address[temp_list[0]] = temp_list[1]+":"+temp_list[2]
        line = f.readline()

#Calling the Raft_server class.
temp= my_dict_address[node_id].split(':')
ip = temp[0]
port = temp[1]
raftserver = Raft_server(my_dict_address, node_id)
server = grpc.server(futures.ThreadPoolExecutor())
raft_pb2_grpc.add_RaftServerServicer_to_server(raftserver, server)
#Set default IP address and Port number is taken as argument.
server.add_insecure_port(ip+":"+ port)

#Calling the write to disk function.
register(writeToDisk)

#Start the server.
server.start()
while True:
        raftserver.update()
#END,