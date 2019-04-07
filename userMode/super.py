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
from storage.database import Database
from time import sleep
import io

DEBUG = False

class SimpleFileService(fileservice_grpc.FileserviceServicer):

    def __init__(self):
        self.client = Database()
        self.list_of_stubs = {}
        #TODO: replace with a list of real IPs
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

    def get_hash(self,filename, username):
        return str(filename)+str(username)

    def callUpload(self,iterator,ip):
        try:
            resp = self.list_of_stubs[ip].UploadFile(iterator)
            print resp
        except:
            print "couldn't send the data"

    def gen_stream(self,list_of_chunks):
        for chunk in list_of_chunks:
            yield chunk

    def UploadFile(self, request_iterator, context):
        ip = self.get_least_busy_server()
        with open('temp.txt', "w") as f:
            for data in request_iterator:
                f.write(data.data)
        with open('temp.txt', "rb") as f:
            seq_list = []
            for seq in iter(lambda: f.read(1024 * 1024), b""):
                #TODO: get file name and username from uploaded data
                    seq_list.append(fileservice.FileData(username='mohdi', filename='file', data=seq))

            resp = self.callUpload(self.gen_stream(seq_list), 'localhost')
        # print("printing file name : {}",data.filename)
        hashed_val = self.get_hash(data.filename, data.username)
        print hashed_val
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
        least = 0
        ip = ""
        print self.stat
        for s in self.stat:
            if s['cpu_usage'] < least:
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

