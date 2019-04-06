import sys
sys.path.append('../')
import fileIO.server as super_server
import threading
from config.config import server_config
import grpc
import fileIO.fileService_pb2 as fileservice
import fileIO.fileService_pb2_grpc as fileservice_grpc
import time
from concurrent import futures
from util.db import RedisDatabase
from time import sleep

DEBUG = False

#TODO: replace with IP addresses
# ips = ['ip1','ip2','ip3']
# ips = ['localhost']
# stat = [None]*len(ips)

#TODO: fix simple file service to read and write. right now just write
#TODO: implement system file logging to understand where the file is (Hashing)

class SimpleFileService(fileservice_grpc.FileserviceServicer):

    def __init__(self):
        self.client = RedisDatabase.RedisDatabase()
        self.list_of_stubs = {}
        self.ips = ['localhost']
        self.stat = [None] * len(self.ips)
        self.make_list_of_stubs()
        for i, ip in enumerate(self.ips):
            t = threading.Thread(target=self.get_status_of_slaves, args=(ip, i))
            t.start()

    def make_list_of_stubs (self):
        for ip in self.ips:
            channel = grpc.insecure_channel(ip + ':3001')
            stub = fileservice_grpc.FileserviceStub(channel)
            self.list_of_stubs[ip] = stub

    def store_data(self, id, data):
        if DEBUG:
            print "Inside store data. Data stored with id : {} successfully".format(id)
        return self.client.conn.set(id, data)

    def store_replicated_data(self, id, data):
        pass

    def get_data(self, id):
        data = self.client.conn.get(id)
        if DEBUG:
            print "Inside get data. Data is : {}".format(id)
        return data

    def is_data_available(self, id):
        if self.client.conn.exists(id):
            return True
        else:
            return False

    def delete_data(self, id):
        return self.client.conn.delete(id)

    def get_hash(self,request):
        return str(request.filename)+str(request.username)
    def UploadFile(self, request_iterator, context):
        hashed_val = self.get_hash(request_iterator)
        ip = self.get_least_busy_server()
        self.store_data(hashed_val, ip)
        return self.list_of_stubs[ip].UploadFile(request_iterator)

    def DownloadFile(self, request, context):
        print "inside download file"
        hashed_val = self.get_hash(request)
        if self.is_data_available(hashed_val):
            ip = self.get_data(hashed_val)
            return self.list_of_stubs[ip].DownloadFile(request)
        else:
            return "File is not available"

    #This function doesn't need to be implemented for slave server
    def FileSearch(self, request, context):
        hashed_val = self.get_hash(request)
        if self.is_data_available(hashed_val):
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
        if self.is_data_available(hashed_val):
            ip = self.get_data(hashed_val)
            return self.list_of_stubs[ip].FileDelete(request)
        else:
            return fileservice.ack(
                success=False, message="File is not available"
            )

    def UpdateFile(self, request_iterator, context):
        hashed_val = self.get_hash(request_iterator)
        if self.is_data_available(hashed_val):
            ip = self.get_data(hashed_val)
            return self.list_of_stubs[ip].FileUpload(request_iterator)
        else:
            return fileservice.ack(
                success=False, message="File is not available"
            )

    def get_least_busy_server(self):
        least = 0
        ip = ""
        for s in self.stat:
            if s.cpu_usage < least:
                ip = s.ip
                least = s.cpu_usage
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
            time.sleep(super_server._ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()

