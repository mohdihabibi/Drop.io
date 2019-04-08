from __future__ import print_function
import grpc
import fileService_pb2
import fileService_pb2_grpc

import sys
sys.path.append('../')
def get_bytes_from_file(filename):
    return open(filename, "rb").read()
channel = grpc.insecure_channel('localhost' + ':3000')

def callUpload(iterator):
  stub = fileService_pb2_grpc.FileserviceStub(channel)
  stub.UploadFile(iterator)

def gen_stream(list_of_chunks):
  for chunk in list_of_chunks:
    yield chunk

if __name__ == '__main__':

  stub = fileService_pb2_grpc.FileserviceStub(channel)
  with open('test.txt', "rb") as f:
    seq_list = []
    for seq in iter(lambda: f.read(1024 * 1024), b""):
       seq_list.append(fileService_pb2.FileData(username='mohdi',filename='file', data=seq))
    callUpload(gen_stream(seq_list))

  #response = stub.DownloadFile(fileService_pb2.FileInfo(username='mohdi',filename='file'))
  #for data in response:
  #  print("Status from server received. response is : {}".format(data))


