from concurrent import futures
import time
import logging
import grpc
import heartbeat_pb2
import heartbeat_pb2_grpc
import subprocess
import ps_utils

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEBUG = False

myIp = ""


class Heartbeat(heartbeat_pb2_grpc.HearBeatServicer):

    def getStatus(self, request, context):
        print("Request recieved from client. Client's IP address is: {}".format(request.ip))
        global myIp, myCPU, myMem
        process = psutil.Process(os.getpid())
        return heartbeat_pb2.HeartBeatResponse(
            ip=myIp,
            live=True,
            cpu_usage= psutil.cpu_percent(),
            disk_space=0.7,
            num_process=11,
            idle=0.9,
            tot_mem=1.5,
            used_mem=process.memory_percent() * 100,
            data_read_per_sec=100.0,
            data_write_per_sec=200.0,
            data_recieve_per_sec=20.0,
            data_sent_per_sec=10.0
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    heartbeat_pb2_grpc.add_HearBeatServicer_to_server(Heartbeat(), server)
    server.add_insecure_port('[::]:3000')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def getMyIp():
    global myIp
    ip_list = subprocess.check_output(
        "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' \
        | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'",
        shell=True)
    my_ips = ip_list.split()
    if DEBUG:
        print "Inside get my ips. My device ip list is ", my_ips
    myIp = ','.join(my_ips)

if __name__ == '__main__':
    getMyIp()
    logging.basicConfig()
    serve()
