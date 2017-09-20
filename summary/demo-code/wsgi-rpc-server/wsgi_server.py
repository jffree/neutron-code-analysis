from paste.deploy import loadapp
import os
from eventlet import wsgi
import eventlet
import ConfigParser
from oslo_service import service

class Wsgi_Server(service.ServiceBase):
    def __init__(self,config_file = None):
        if not config_file:
            config_file = 'wsgi.conf'
        self.config_file = os.path.abspath(config_file)
        self.paste()
        self.pool = eventlet.GreenPool(1)
        self._server  = None

    def paste(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        self.deploy_file = self.config.get('server', 'deploy_file')
        self.app = loadapp('config:%s' % os.path.abspath(self.deploy_file), 'main')
        self.bind_addr = self.config.get('server', 'bind_addr')
        self.bind_port = int(self.config.get('server', 'bind_port'))

    def _start(self):
        print 'Starting WSGI Server...'
        wsgi.server(eventlet.listen((self.bind_addr, self.bind_port)), self.app)

    def start(self):
        self._server = self.pool.spawn(self._start)

    def wait(self):
        if isinstance(self._server, eventlet.greenthread.GreenThread):
            print 'Wsgi server waiting...'
            self._server.wait()

    def stop(self):
        if isinstance(self._server, eventlet.greenthread.GreenThread):
            self._server.kill()
            self._server = None

    def reset(self):
        if self._server:
            self.stop()
        self.start()

