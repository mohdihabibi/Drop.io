from concurrent import futures
import os
import sys
import time
import logging
import grpc
import payload_pb2
import payload_pb2_grpc
import subprocess
from os import path
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEBUG = False

class FileService(payload_pb2_grpc.RouteServiceServicer):

    #TODO: store paylaod in database or local
    def request(self, request, context):
        print("Request recieved from client. Client's IP address is: {}".format(request.payload))
        return payload_pb2.Route(
            payload= "server"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    payload_pb2_grpc.add_RouteServiceServicer_to_server(FileService(), server)
    server.add_insecure_port('[::]:3000')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig()
    serve()
