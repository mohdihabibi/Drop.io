import sys
sys.path.append('../')

#TODO: fix this for running as server or client

from fileIO import server as io_server
from heartbeat import heartbeat_server as hb_server

NODES = {
    'ip1' : False,
    'ip2' : False,
    'ip3' : False,
    'ip4' : False
}

if __name__ == '__main__':

