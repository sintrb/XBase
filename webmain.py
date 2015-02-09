# -*- coding: UTF-8 -*
'''
Created on 2015年1月18日

@author: RobinTang
'''
import tornado.web

def md5(v):
    import hashlib
    return hashlib.md5(v).hexdigest()

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
    pass
        
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


