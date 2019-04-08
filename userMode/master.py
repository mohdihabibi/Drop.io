import threading
import sys
import time
sys.path.append("../")
from time import sleep
from config.config import my_ip, list_of_ips
from util.utility import clear_ports

from super import serve as super_server
from server import serve as slave_server

from raft.raft import  TestObj
leader=""

def onAdd(res, err, cnt):
        print('onAdd %d:' % cnt, res, err)

def run():
    print("inside run")
    print(list_of_ips)
    ip = my_ip
    print(ip)
    partners = list_of_ips
    o = TestObj(ip, partners)
    n = 0
    old_value = -1
    while True:
        time.sleep(0.5)
        if o.getCounter() != old_value:
            old_value = o.getCounter()
            print('Current Counter value:', old_value)
        if o._getLeader() is None:
            continue
        if n < 20:
            if (ip == 'localhost:2000'):
                o.addValue(10, n)
        n += 1
        if n % 20 == 0:
            if True:
                global leader
                leader = o._getLeader
                print('===================================')
                print('Server running on port:', ip)
                print('Current Counter value:', o.getCounter())
                print('Current Leader running at address:', o._getLeader())
                print('Current Log Size:', o._getRaftLogSize())

if __name__ == '__main__':
    clear_ports()
    t = threading.Thread(target=run)
    t.start()
    while leader == "":
        pass

    if leader == my_ip:
        sleep(2)
        super_server()
    else:
        slave_server()
