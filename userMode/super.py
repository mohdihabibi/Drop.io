import sys
from config.config import list_of_ips, leader_ip, my_ip
sys.path.append('../')
import threading
import grpc
import fileIO.fileService_pb2 as fileservice
import fileIO.fileService_pb2_grpc as fileservice_grpc
import time
from concurrent import futures
from storage.database import Database
from time import sleep
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

DEBUG = False

class SimpleFileService(fileservice_grpc.FileserviceServicer):

    def __init__(self):
        self.client = Database()
        self.list_of_stubs = {}
        self.ips = list_of_ips
        self.stat = [None] * len(self.ips)
        self.make_list_of_stubs()
        #TODO: uncomment this in real Demo
        self.send_leader_info()
        for i, ip in enumerate(self.ips):
            t = threading.Thread(target=self.get_status_of_slaves, args=(ip, i))
            t.start()

    def make_list_of_stubs (self):
        for ip in self.ips:
            channel = grpc.insecure_channel(ip + ':3001')
            stub = fileservice_grpc.FileserviceStub(channel)
            self.list_of_stubs[ip] = stub

    def get_hash(self,filename, username):
        return str(filename)+str(username)

    def callUpload(self,iterator,ip):
        try:
#            print "ip is " + ip
            resp = self.list_of_stubs[ip].UploadFile(iterator)
            print resp
        except:
            if DEBUG:
                print "couldn't send the data"

    def gen_stream(self,list_of_chunks):
        for chunk in list_of_chunks:
            yield chunk
    def send_leader_info(self):
        channel = grpc.insecure_channel(leader_ip)
        stub = fileservice_grpc.FileserviceStub(channel)
        resp = stub.getLeaderInfo(fileservice.ClusterInfo(ip=my_ip,port='3000',clusterName='Drop.io'))
        if resp.success:
            print "Connected with SuperNode successfully!"
        else:
            print "Error when connecting to super node!"

    def getClusterStats(self, request, context):
        cpu_usage_avg = 0
        mem_usage_avg = 0
        disk_usage_avg = 0
        num_of_live = 0
        for status in self.stat:
            if not status['live']:
                continue
            num_of_live+=1
            cpu_usage_avg+=status['cpu_usage']
            mem_usage_avg+=status['mem_usage']
            disk_usage_avg+=status['disk_usage']
        return fileservice.ClusterStats(cpu_usage=str(cpu_usage_avg/num_of_live),disk_space=str(100-(disk_usage_avg/num_of_live)),used_mem=str(mem_usage_avg/num_of_live))

    def UploadFile(self, request_iterator, context):
        ip = self.get_least_busy_server()
        print "ip is "
        print ip
        with open('temp.txt', "w") as f:
            for data in request_iterator:
                f.write(data.data)
        with open('temp.txt', "rb") as f:
            seq_list = []
            for seq in iter(lambda: f.read(1024 * 1024), b""):
                    seq_list.append(fileservice.FileData(username=data.username, filename=data.filename, data=seq))
            #TODO: replace localhost with IP
            self.callUpload(self.gen_stream(seq_list), ip)
        hashed_val = self.get_hash(data.filename, data.username)
        try:
            #TODO: change it to IP
            self.client.store_data(hashed_val, 'localhost')
        except:
            print "couldn't store in database"
        return fileservice.ack(success=True, message="File is stored!")

    def DownloadFile(self, request, context):
        print "inside download file"
        hashed_val = self.get_hash(request.filename, request.username)
        print hashed_val
        if self.client.is_data_available(hashed_val):
            print "inside if statement"
            ip = self.client.get_data(hashed_val)
            return self.list_of_stubs[ip].DownloadFile(request)
        else:
            return fileservice.FileData(
                username='', filename='', data=''
            )

    #This function doesn't need to be implemented for slave server
    def FileSearch(self, request, context):
        hashed_val = self.get_hash(request)
        if self.client.is_data_available(hashed_val):
            return fileservice.ack(
                success=True, message="File is available!"
            )
        else:
            return fileservice.ack(
                success=False, message="File is not available"
            )

    #This function doesn't need to be implemented for super server
    def ReplicateFile(self, request_iterator, context):
        pass

    #This function doesn't need to be implemented for slave server
    def FileList(self, request, context):
        pass

    def FileDelete(self, request, context):
        hashed_val = self.get_hash(request)
        if self.client.is_data_available(hashed_val):
            ip = self.client.get_data(hashed_val)
            return self.list_of_stubs[ip].FileDelete(request)
        else:
            return fileservice.ack(
                success=False, message="File is not available"
            )

    def UpdateFile(self, request_iterator, context):
        hashed_val = self.get_hash(request_iterator)
        if self.client.is_data_available(hashed_val):
            ip = self.client.get_data(hashed_val)
            return self.list_of_stubs[ip].FileUpload(request_iterator)
        else:
            return fileservice.ack(
                success=False, message="File is not available"
            )

    def get_least_busy_server(self):
        least = 100
        ip = ""
        for i,s in enumerate(self.stat):
            if not s['live']:
                continue
            if s['cpu_usage'] < least:
                ip = self.ips[i]
                least = s['cpu_usage']
        return ip

    def get_status_of_slaves(self, target, index):
        while True:
            stat_resp = {}
            try:
                response = self.list_of_stubs[target].getStatus(fileservice.HeartBeatRequest(ip=target, leader=True))
                stat_resp['live'] = True
                stat_resp['cpu_usage'] = response.cpu_usage
                stat_resp['mem_usage'] = response.used_mem
            except:
                stat_resp['live'] = False
                stat_resp['cpu_usage'] = 0
                stat_resp['mem_usage'] = 0
            self.stat[index] = stat_resp
            sleep(2)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    fileservice_grpc.add_FileserviceServicer_to_server(SimpleFileService(), server)
    server.add_insecure_port('[::]:3000')
    print('starting super node.......')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

