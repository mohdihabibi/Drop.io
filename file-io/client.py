
from __future__ import print_function
import logging

import grpc

import payload_pb2
import payload_pb2_grpc
import time
import sys
sys.path.append('../')

from config.config import server_config

def run():
  channel = grpc.insecure_channel(server_config.get('host')+ ':' + str(server_config.get('port')))
  stub = payload_pb2_grpc.RouteServiceStub(channel)
  response = stub.request(payload_pb2.Route(id = 321,payload='Mohdi'))
  print("Status from server received. response is : {}".format(response))
  time.sleep(1)
  response = stub.request(payload_pb2.Route(id = 321))
  print("Status from server recieved. Response is : {}".format(response))

if __name__ == '__main__':
    logging.basicConfig()
    run()
