from __future__ import print_function
import grpc

import fileService_pb2
import fileService_pb2_grpc

import sys
sys.path.append('../')
if __name__ == '__main__':
  channel = grpc.insecure_channel('localhost' + ':3000')
  stub = fileService_pb2_grpc.FileserviceStub(channel)
  # response = stub.UploadFile(fileService_pb2.FileData(username='mohdi',filename='file', data='helooooooooooooooooooooooooooooooooooooooooooooooooooooooo'))
  # print("Status from server received. response is : {}".format(response.message))
  response = stub.DownloadFile(fileService_pb2.FileInfo(username='mohdi',filename='file'))
  print("Status from server received. response is : {}".format(response.message))

