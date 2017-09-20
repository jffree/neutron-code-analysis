

login_check = True

def pipeline_factory(loader, global_config, **local_config):
    # space-separated list of filter and app names:
    pipeline = local_config['auth'].split() if login_check else local_config['noauth'].split()
    filters = [loader.get_filter(n) for n in pipeline[:-1]]
    app = loader.get_app(pipeline[-1])
    filters.reverse() # apply in reverse order!
    for filter in filters:
        app = filter(app)
    return app

def login(global_conf, req_usernames):
    # space-separated list of usernames:
    req_usernames = req_usernames.split()
    def filter(app):
        return AuthFilter(app, req_usernames)
    return filter

class AuthFilter(object):
    def __init__(self, app, req_usernames):
        self.app = app
        self.req_usernames = req_usernames

    def __call__(self, environ, start_response):
        if environ.get('REMOTE_USER') in self.req_usernames:
            return self.app(environ, start_response)
        start_response(
            '403 Forbidden', [('Content-type', 'text/html')])
        return ['You are forbidden to view this resource']

def wsgi_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return '<h1>Hello, web!</h1>'

def log(global_config, **local_conf):
    return wsgi_app

def version(global_config, **local_conf):
    version = local_conf['ver']
    return wsgi_app

