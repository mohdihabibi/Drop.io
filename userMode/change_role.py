from master import leader
from config.config import my_ip
from super import serve as super_server
from userMode.server import server as slave_server
def change_role():
    if leader == my_ip:
        super_server()
    else:
        slave_server