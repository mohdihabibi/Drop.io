from concurrent import futures
import time
import grpc
import fileService_pb2
import fileService_pb2_grpc
from util.db import RedisDatabase

import sys
sys.path.append('../')

from config.config import server_config

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEBUG = True

class FileService(fileService_pb2_grpc.FileserviceServicer):

    client = RedisDatabase.RedisDatabase()
    replicationClient = RedisDatabase.RedisDatabase()

    def store_data(self, id, data):
        if DEBUG:
            print "Inside store data. Data stored with id : {} successfully".format(id)
        return self.client.conn.set(id, data)

    def store_replicated_data(self, id, data):
        self.replicationClient.conn.set(id, data)
        return True

    def get_data(self, id):
        data = self.client.conn.get(id)
        if DEBUG:
            print "Inside get data. Data is : {}".format(id)
        return data

    def is_data_available(self, id):
        if self.client.conn.get(id):
            return True
        else:
            return False

    def delete_data(self, id):
        return self.client.conn.delete(id)

    def UploadFile(self, request_iterator, context):
        data = request_iterator.data
        self.store_data(request_iterator.filename, data)
        return fileService_pb2.ack(
            success=True, message="Data successfully stored!"
        )

    def DownloadFile(self, request, context):
        filename = request.filename
        if self.is_data_available(filename):
            data = self.get_data(filename)
        else:
            return "File is not available"
        return fileService_pb2.FileData(
            username="",filename=filename, data = data
        )

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
        if self.delete_data(filename):
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
        if self.store_data(filename, data):
            return fileService_pb2.ack(
                success=True, message="Data successfully updated!"
            )
        else:
            return fileService_pb2.ack(
                success=False, message="Couldn't update the instance!"
            )

def serve():
    print "Slave server is running ..."
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    fileService_pb2_grpc.add_FileserviceServicer_to_server(FileService(), server)
    server.add_insecure_port('[::]:' + str(server_config.get('port')))
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
