from multiprocessing import Process
import sys
sys.path.append('../')

import fileIO.server as server
import heartbeat.heartbeat_server as hb_server

if __name__=='__main__':
    p1 = Process(target=hb_server.serve())
    p1.start()
    p2 = Process(target=server.serve())
    p2.start()



