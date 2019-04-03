from __future__ import print_function
import grpc

import fileService_pb2
import fileService_pb2_grpc

import sys
sys.path.append('../')

from config.config import server_config

def sendFile(ip, id, payload):
  channel = grpc.insecure_channel(ip + ':' + str(server_config.get('port')))
  stub = fileService_pb2_grpc.RouteServiceStub(channel)
  response = stub.request(fileService_pb2.Route(id=id, payload=payload))
  print("Status from server received. response is : {}".format(response))

