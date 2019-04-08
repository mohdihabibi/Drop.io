import threading
import sys
import time
sys.path.append("../")
from config.config import my_ip, list_of_ips, raft_config
from util.utility import clear_ports
from super import serve as super_server
from server import serve as slave_server
from raft.raft import  TestObj
import os

os.environ['leader'] = ''

def change_role():
    if os.environ['leader'] == my_ip:
        clear_ports('3000')
        super_server()
    else:
        clear_ports('3001')
        slave_server()

def onAdd(res, err, cnt):
        print('onAdd %d:' % cnt, res, err)

def run():
    ip = my_ip + str(raft_config['port'])
    print(ip)
    partners = [s + str(raft_config['port']) for s in list_of_ips]
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
                os.environ['leader'] = str(o._getLeader())
                # print('===================================')
                # print('Server running on address:', ip)
                # print('Current Counter value:', o.getCounter())
                print('Current Leader running at address:', o._getLeader())
                # print('Current Log Size:', o._getRaftLogSize())

if __name__ == '__main__':
    clear_ports('5000')
    t = threading.Thread(target=run)
    t.start()
    while os.environ['leader'] == "":
        pass
    change_role()
