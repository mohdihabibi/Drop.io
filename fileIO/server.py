from concurrent import futures
import time
import grpc
import fileService_pb2
import fileService_pb2_grpc
import psutil
import os

import sys


sys.path.append('../')
from util.utility import getMyIp
from storage.database import Database

from config.config import server_config

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEBUG = True

class FileService(fileService_pb2_grpc.FileserviceServicer):

    client = Database()
#    replicationClient = RedisDatabase.RedisDatabase()
    def __init__(self):
        self.my_ip = getMyIp()

    def UploadFile(self, request_iterator, context):
        #TODO: replace it with in disk and memory database
        print "inside upload file slave server"
        for data in request_iterator:
            print data
        print data.filename
        try:
            self.client.store_data(data.filename, data.data)
            return fileService_pb2.ack(
                success=True, message="Data successfully stored!"
            )
        except:
            print "couldn't store data"
            return fileService_pb2.ack(
                success=False, message="Data wasn't stored!"
            )


    def callUpload(self,iterator,ip):
        self.list_of_stubs[ip].UploadFile(iterator)

    def gen_stream(self,list_of_chunks):
        for chunk in list_of_chunks:
            yield chunk

    def strBin(self, s_str):
        binary = []
        for s in s_str:
            if s == ' ':
                binary.append('00100000')
            else:
                binary.append(bin(ord(s)))
        return binary

    def DownloadFile(self, request, context):
        filename = request.filename
        if self.client.is_data_available(filename):
            payload = self.client.get_data(filename)
            # TODO: replace the file reading piece with binary operation
            # binary = self.strBin(payload)
            # for data in binary:
            #     yield fileService_pb2.FileData(username=request.filename, filename=request.username, data=data)

            with open('file.txt', 'w') as f:
                f.write(payload)
            with open('file.txt', "rb") as f:
                for data in iter(lambda: f.read(1024 * 1024), b""):
                    yield fileService_pb2.FileData(username=request.filename, filename=request.username, data=data)

    #This function doesn't need to be implemented on slave server
    def FileSearch(self, request, context):
        pass

    def ReplicateFile(self, request_iterator, context):
        data = request_iterator.data
        filename = request_iterator.filename
        if self.store_replicated_data(filename, data):
            return fileService_pb2.ack(
                success=True, message="Data successfully replicated!"
            )
        else:
            return fileService_pb2.ack(
                success=False, message="Replication was unsuccesful!"
            )

    #This function doesn't need to be implemented on slave server
    def FileList(self, request, context):
        pass

    def FileDelete(self, request, context):
        filename = request.filename
        if self.client.delete_data(filename):
            return fileService_pb2.ack(
                success=True, message="Data successfully deleted!"
            )
        else:
            return fileService_pb2.ack(
                success=False, message="Deletion was unsuccessful!"
            )

    def UpdateFile(self, request_iterator, context):
        data = request_iterator.data
        filename = request_iterator.filename
        if self.client.store_data(filename, data):
            return fileService_pb2.ack(
                success=True, message="Data successfully updated!"
            )
        else:
            return fileService_pb2.ack(
                success=False, message="Couldn't update the instance!"
            )
    def getStatus(self, request, context):
        print("Request recieved from client. Client's IP address is: {}".format(request.ip))
        process = psutil.Process(os.getpid())
        return fileService_pb2.HeartBeatResponse(
            ip=self.my_ip,
            live=True,
            cpu_usage= psutil.cpu_percent(),
            disk_space=0.7,
            num_process=11,
            num_thread=10,
            idle=0.9,
            tot_mem=1.5,
            used_mem=process.memory_percent() * 100,
            data_read_per_sec=100.0,
            data_write_per_sec=200.0,
            data_recieve_per_sec=20.0,
            data_sent_per_sec=10.0
        )

def serve():
    print ("Slave server is running ...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    fileService_pb2_grpc.add_FileserviceServicer_to_server(FileService(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
#
# if __name__ == '__main__':
#     logging.basicConfig()
#     serve()
