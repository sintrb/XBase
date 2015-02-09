# -*- coding: UTF-8 -*
'''
Created on 2015年2月09日

@author: RobinTang
'''
import tornado.web
import json
import time
import os
def md5(v):
    import hashlib
    return hashlib.md5(v).hexdigest()

def uuid():
    return md5(str(time.time()))

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        try:
            import sae.kvdb
            self.kv = sae.kvdb.KVClient()
        except:
            import saekvdb
            self.kv = saekvdb.KVClientCheat.get_instance()

class DBHandler(BaseHandler):
    """docstring for DBHandler"""
    def get(self, domain, keypath=None):
        key = '%s:%s'%(domain, keypath)
        if key:
            val = self.kv.get(key)
            if val:
                self.write(val)
        else:
            self.set_status(404)
    def post(self, domain, keypath=None):
        if not keypath:
            keypath = uuid()
        key = '%s:%s'%(domain, keypath)
        self.kv.set(key, self.request.body)
    def put(self, domain, keypath=None):
        self.port(domain, keypath)
    def delete(self, domain, keypath=None):
        key = '%s:%s'%(domain, keypath)
        self.kv.delete(key)
        
class MainHandler(BaseHandler):
    def get(self):
        import time
        self.write("Hello, world %d" % time.time())

class StcHandler(BaseHandler):
    def get(self):
        import json
        self.write(json.dumps(self.kv.get_info()))


url = [
    (r"/", MainHandler),
    (r"/~stc", StcHandler),
    (r"/([a-zA-Z0-9\-_\.])+/([a-zA-Z0-9\-_\./]*)", DBHandler),
]

import os
settings = {
    "debug": True,
    "static_path" : os.path.join(os.path.dirname(__file__), "static"),
    "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
}



if __name__ == "__main__":
    import sys
    import tornado.ioloop
    port = int(sys.argv[1]) if len(sys.argv) >= 2 else 9999
    application = tornado.web.Application(url, **settings)
    print 'listen at :%d' % port
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


