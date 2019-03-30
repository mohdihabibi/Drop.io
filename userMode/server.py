import sys
sys.path.append('../')

import fileIO.server as server
import heartbeat.heartbeat_server as hb_server

import threading

t1 = threading.Thread(target=hb_server.serve())
t2 = threading.Thread(target=server.serve())
t1.start()
t2.start()
