
from __future__ import print_function
import logging

import grpc

import payload_pb2
import payload_pb2_grpc


def run():
  channel = grpc.insecure_channel('localhost:3000')
  stub = payload_pb2_grpc.RouteServiceStub(channel)
  response = stub.request(payload_pb2.Route(payload='Mohdi'))
  print("Status from server received. Server's IP address is: {}".format(response))

if __name__ == '__main__':
    logging.basicConfig()
    run()
