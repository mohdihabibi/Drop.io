import sys
sys.path.append('../')
import fileIO.server as super_server
import heartbeat.heartbeat_client as hb_client
import threading
from config.config import server_config
import grpc
import fileIO.fileService_pb2 as fileservice
import fileIO.fileService_pb2_grpc as fileservice_grpc
import time
from concurrent import futures
from util.db import RedisDatabase

DEBUG = False

#TODO: replace with IP addresses
# ips = ['ip1','ip2','ip3']
ips = ['localhost']
stat = [None]*len(ips)

#TODO: fix simple file service to read and write. right now just write
#TODO: implement system file logging to understand where the file is (Hashing)

class SimpleFileService(fileservice_grpc.FileserviceServicer):
    client = RedisDatabase.RedisDatabase()
    list_of_stubs = {}

    def __init__(self):
        self.make_list_of_stubs()

    def make_list_of_stubs (self):
        for ip in ips:
            channel = grpc.insecure_channel(ip + ':' + str(server_config.get('port')))
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
        self.store_data(hashed_val, self.get_least_busy_server())
        return self.list_of_stubs[ip].UploadFile(request_iterator)

    def DownloadFile(self, request, context):
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
        for s in stat:
            if s.cpu_usage < least:
                ip = s.ip
                least = s.cpu_usage
        return ip

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    fileservice_grpc.add_FileserviceServicer_to_server(SimpleFileService(), server)
    server.add_insecure_port('[::]:'+ str(server_config.get('port')))

    server.start()
    try:
        while True:
            time.sleep(super_server._ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    # global ips
    print "Super node started..."
    server_thread = threading.Thread(target=serve())

    server_thread.start()
    for i, ip in enumerate(ips):
        hb = hb_client.HeartBeatClient(ip, stat, i)
        t = threading.Thread(target=hb.run())
        t.start()

