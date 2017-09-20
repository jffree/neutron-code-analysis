from oslo_config import cfg
from oslo_service import service
import oslo_messaging
import eventlet

class ServerControlEndpoint(object):
    target = oslo_messaging.Target(namespace='control',
                                   version='2.0')
    def __init__(self, server):
        self.server = server

    def stop(self, ctx):
        if self.server:
            self.server.stop()

class TestEndpoint(object):

    def test(self, ctx, arg):
        print 'Received a rpc call/cast from client, arg is: ', arg
        return arg

class RPC_Worker(service.ServiceBase):
    def __init__(self, topic = 'rpc_test', conf = cfg.CONF, server = 'localhost', url = None, executor = "blocking"):
        self.endpoints = [ServerControlEndpoint(None), TestEndpoint(),]
        self.pool = eventlet.GreenPool(1)
        self.transport = oslo_messaging.get_transport(conf,url)
        self.target = oslo_messaging.Target(topic=topic, server=server)
        self.rpc_server = oslo_messaging.get_rpc_server(self.transport, self.target, self.endpoints, executor=executor)
        self._server = None

    def _start(self):
        print 'Starting RPC Server...'
        self.rpc_server.start()
        self.rpc_server.wait()

    def start(self):
        self._server = self.pool.spawn(self._start)

    def wait(self):
        if isinstance(self._server, eventlet.greenthread.GreenThread):
            print 'Wsgi server waiting...'
            self._server.wait()

    def stop(self):
        if self._server:
            self._server.kill()
            self._server = None

    def reset(self):
        if self._server :
            self.stop()
        self.start()






