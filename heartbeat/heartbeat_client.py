
from __future__ import print_function
import logging

import grpc

import heartbeat_pb2
import heartbeat_pb2_grpc


def run():
  channel = grpc.insecure_channel('localhost:3000')
  stub = heartbeat_pb2_grpc.HearBeatStub(channel)
  response = stub.getStatus(heartbeat_pb2.HeartBeatRequest(ip='1111', leader=False))
  print("Status from server received. Server's IP address is: {}".format(response))

if __name__ == '__main__':
    logging.basicConfig()
    run()
