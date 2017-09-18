
class Version(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if Version._instance is None:
            cls._instance = super(Version,cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, version):
        self.version = version

    def __call__(self,environ,start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return 'Current version is: %s' % self.version

def version_factory(global_config, **local_conf):
    ver_app = Version(local_conf['ver'])
    return ver_app









