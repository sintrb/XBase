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
        key = key.encode('utf-8')
        if keypath:
            val = self.kv.get(key)
            if val:
                self.write(val)
        else:
            key = '%s:'%domain #.encode('utf-8')
            key = key.encode('utf-8')
            l = len(key)
            self.write(';'.join([k[l:] for k in self.kv.getkeys_by_prefix(key)]))
    def post(self, domain, keypath=None):
        if not keypath:
            keypath = uuid()
        key = '%s:%s'%(domain, keypath)
        key = key.encode('utf-8')
        self.kv.set(key, self.request.body)
        self.write(key)
    def put(self, domain, keypath=None):
        self.post(domain, keypath)
    def delete(self, domain, keypath=None):
        key = '%s:%s'%(domain, keypath)
        key = key.encode('utf-8')
        self.kv.delete(key)
        self.write(key)
        
class MainHandler(BaseHandler):
    def get(self):
        import time
        self.write("Hello, world %d" % time.time())

class StcHandler(BaseHandler):
    def get(self):
        info = self.kv.get_info()
        info['keys'] = [k for k in self.kv.getkeys_by_prefix('')]
        self.write(json.dumps(info))
        # self.write(r'<pre>%s</pre>'%cgi.escape(str(self.kv.__module__)))
        # self.write('d')


url = [
    (r"/", MainHandler),
    (r"/stc", StcHandler),
    (r"/([a-zA-Z0-9\-_\.]+)[/:]([a-zA-Z0-9\-_\.]*)", DBHandler),
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


