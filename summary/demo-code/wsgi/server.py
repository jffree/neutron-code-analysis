from paste.deploy import loadapp
import os
from eventlet import wsgi
import eventlet
import ConfigParser

class Server(object):
    def __init__(self,config_file = None):
        if not config_file:
            config_file = 'wsgi.conf'
        self.config_file = os.path.abspath(config_file)
        self.paste()

    def paste(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        self.deploy_file = self.config.get('server', 'deploy_file')
        self.app = loadapp('config:%s' % os.path.abspath(self.deploy_file), 'main')
        self.bind_addr = self.config.get('server', 'bind_addr')
        self.bind_port = int(self.config.get('server', 'bind_port'))


    def start(self):
        wsgi.server(eventlet.listen((self.bind_addr, self.bind_port)), self.app)








if __name__ == '__main__':
    server = Server()
    server.start()
