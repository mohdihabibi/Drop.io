from multiprocessing import Process
import sys
sys.path.append('../')

import fileIO.server as server

if __name__=='__main__':
    server.serve()



