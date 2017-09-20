from oslo_service import service
from oslo_config import cfg
import eventlet
from wsgi_server import Wsgi_Server
from rpc.rpc_server import RPC_Worker

class Service(object):
    def __init__(self):
        self.servers = []
        self.server_launcher = service.ProcessLauncher(cfg.CONF, wait_interval = 1.0)
        self.pool = eventlet.GreenPool()

    def add_server(self, server):
        if not isinstance(server, service.ServiceBase):
            print 'A server should be a subclass of ServiceBase.'
            return
        self.servers.append(server)

    def start(self):
        """ Start multi process. """
        for server in self.servers:
            self.server_launcher.launch_service(server)

    def wait(self):
        self.server_launcher.wait()

if __name__ == "__main__":
    ser = Service()
    ser.add_server(Wsgi_Server())
    ser.add_server(RPC_Worker(url = 'rabbit://stackrabbit:abc123@172.16.100.192:5672/'))
    ser.start()
    ser.wait()



