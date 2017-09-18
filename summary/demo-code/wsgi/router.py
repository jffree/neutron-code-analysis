"""
Building RESTful structure based on Source: blog and book.
"""

from routes import Mapper
import routes.middleware
import webob
import webob.dec
import webob.exc


class Router(object):

    @classmethod
    def factory(cls, global_config, **local_config):
        return cls(**local_config)

    def __init__(self):
        self.map = Mapper()
        self.build_mapper()
        self._router = routes.middleware.RoutesMiddleware(self._dispatch, self.map)

    def build_mapper(self):
        self.map.connect('index', '', controller=self.home_app)
        self.map.connect('blog', '/blog', controller=self.blog_app)
        self.map.connect('book', '/book', controller=self.book_app)

    @webob.dec.wsgify()
    def __call__(self, req):
        return self._router

    @webob.dec.wsgify()
    def _dispatch(self, req):
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app

    @webob.dec.wsgify()
    def home_app(self,req):
        body = "Welcome to wsgi server home"
        return webob.Response(body=body)

    @webob.dec.wsgify()
    def blog_app(self,req):
        body = "Welcome to wsgi server home - blog"
        return webob.Response(body=body)

    @webob.dec.wsgify()
    def book_app(self,req):
        body = "Welcome to wsgi server home - book"
        return webob.Response(body=body)













