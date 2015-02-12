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
            dic = {}
            try:
                import pickle
                with open('kvdb', 'r') as f:
                    dic = pickle.load(f)
            except:
                print 'load kvdb failed'
                pass
            self.kv = saekvdb.KVClientCheat.get_instance(dic)
        # print self.kv.get_info()

class SaveHandler(BaseHandler):
    """docstring for SaveHandler"""
    def initialize(self):
        BaseHandler.initialize(self)
        time.sleep(0.3)
    def savekvdb(self):
        import saekvdb
        if isinstance(self.kv, saekvdb.KVClientCheat):
            import pickle
            print 'save kvdb'
            with open('kvdb', 'w') as f:
                pickle.dump(self.kv.cache, f)

class AuthHandler(SaveHandler):
    def prepare(self):
        SaveHandler.prepare(self)
        self.username = None
        try:
            import urllib
            token = self.get_cookie('token')
            if not token:
                token = self.request.headers['Authorization'].split(' ')[1]
            username, password = urllib.base64.b64decode(token).split(':')
            kvd = self.kv.get(username)
            if kvd and kvd['password'] == password:
                self.username = username
        except:
             pass
        print self.username

class DBHandler(AuthHandler):
    """docstring for DBHandler"""
    def initialize(self):
        AuthHandler.initialize(self)
        # Allow Cross Domain AJAX
        self.set_header('Access-Control-Allow-Origin', '*')
    def get(self, domain, split=None, keypath=None):
        if keypath:
            key = '%s:%s'%(domain, keypath)
            key = key.encode('utf-8')
            val = self.kv.get(key)
            if val:
                self.write(val)
        else:
            key = '%s:'%domain
            key = key.encode('utf-8')
            l = len(key)
            if split:
                a = [k[l:] for k in self.kv.getkeys_by_prefix(key)]
                self.write(json.dumps(a))
            else:
                # self.write(';'.join())
                d = dict([(k[l:], v) for k,v in self.kv.get_by_prefix(key)])
                self.write(json.dumps(d))
    def post(self, domain, split=None, keypath=None):
        if not keypath:
            keypath = uuid()
        key = '%s:%s'%(domain, keypath)
        key = key.encode('utf-8')
        self.kv.set(key, self.request.body)
        self.write(key)
        self.savekvdb()
    def put(self, domain, split=None, keypath=None):
        self.post(domain, split, keypath)
    def delete(self, domain, split=None, keypath=None):
        if keypath:
            key = '%s:%s'%(domain, keypath)
            key = key.encode('utf-8')
            self.kv.delete(key)
            self.write(key)
        else:
            key = '%s:'%domain
            key = key.encode('utf-8')
            count = 0
            for k in self.kv.getkeys_by_prefix(key):
                self.kv.delete(k)
                count += 1
            self.write(str(count))
        self.savekvdb()

class LoginHandler(SaveHandler):
    def post(self):
        d = json.loads(self.request.body)
        username = d.get('username')
        password = d.get('password')
        if username and password:
            kvd = self.kv.get(username)
            if kvd and kvd['password'] == d['password']:
                import urllib
                token = urllib.base64.b64encode('%s:%s'%(username, password))
                self.set_cookie('token', token)
                res = {'succ':True}
            else:
                res = {'succ':False, 'msg':'用户名或密码不正确'}
        else:
            res = {'succ':False, 'msg':'信息不全'}
        self.write(json.dumps(res))

class SiginHandler(SaveHandler):
    def post(self):
        d = json.loads(self.request.body)
        username = d.get('username')
        password = d.get('password')
        if username and not self.kv.get(username):
            res = {'succ':True}
            self.kv.set(username, d)
            self.savekvdb()
        else:
            res = {'succ':False, 'msg':'已经存在该用户'}
        self.write(json.dumps(res))

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')

class StcHandler(BaseHandler):
    def get(self):
        info = self.kv.get_info()
        info['keys'] = [k for k in self.kv.getkeys_by_prefix('')]
        self.write(json.dumps(info))
        # self.write(r'<pre>%s</pre>'%cgi.escape(str(self.kv.__module__)))
        # self.write('d')


url = [
    (r"/", IndexHandler),
    (r"/stc", StcHandler),
    (r"/.login", LoginHandler),
    (r"/.sigin", SiginHandler),
    (r"/([a-zA-Z0-9\-_\.]+)([/:]{0,1})([a-zA-Z0-9\-_\.]*)", DBHandler),
]

import os
settings = {
    "debug": True,
    "static_path" : os.path.join(os.path.dirname(__file__), "static"),
    "template_path" : os.path.join(os.path.dirname(__file__), "static"),
}

if __name__ == "__main__":
    import sys
    import tornado.ioloop
    port = int(sys.argv[1]) if len(sys.argv) >= 2 else 9999
    application = tornado.web.Application(url, **settings)
    print 'listen at :%d' % port
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


