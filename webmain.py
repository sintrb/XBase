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
                # print 'load kvdb failed'
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
            # print 'save kvdb'
            with open('kvdb', 'w') as f:
                pickle.dump(self.kv.cache, f)

class AuthHandler(SaveHandler):
    def authUserPass(self, username, password):
        kvd = self.kv.get(username)
        if kvd and kvd['password'] == password:
            self.username = username
            self.userkvd = kvd
            self.authed = username
            return True
        else:
            return False
    def prepare(self):
        SaveHandler.prepare(self)
        self.username = None
        self.userkvd = None
        self.authed = None

        try:
            import urllib
            token = self.get_cookie('token')
            if not token:
                token = self.request.headers['Authorization'].split(' ')[1]
            username, password = urllib.base64.b64decode(token).split(':')
            self.authUserPass(username, password)
        except:
             pass

        try:
            self.username = self.get_argument('u').encode('utf-8')
            password = self.get_argument('p')
            self.authUserPass(self.username, password)
        except:
            pass
        # print 'un:%s'%self.username
    def save_userkvd(self):
        self.kv.set(self.username.encode('utf-8'), self.userkvd)
        self.savekvdb()

class LoginHandler(SaveHandler):
    def post(self):
        d = json.loads(self.request.body)
        username = d.get('username').encode('utf-8')
        password = d.get('password').encode('utf-8')
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
        username = d.get('username').encode('utf-8')
        password = d.get('password').encode('utf-8')
        if not username and not password:
            res = {'succ':False, 'msg':'用户名和密码不能为空'}
        elif not username:
            res = {'succ':False, 'msg':'用户名不能为空'}
        elif username in ['trb', 'rest', 'api'] or username[0] in './\~':
            res = {'succ':False, 'msg':'用户名受限'}
        elif not password:
            res = {'succ':False, 'msg':'密码不能为空'}
        elif self.kv.get(username):
            res = {'succ':False, 'msg':'已经存在该用户'}
        else:
            res = {'succ':True}
            self.kv.set(username, {
                'username':username,
                'password':password,
                'apps':[]
                })
            self.savekvdb()
        self.write(json.dumps(res))

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')

class StcHandler(BaseHandler):
    def get(self, username=''):
        info = self.kv.get_info()
        info['keys'] = ['%s: %s'%(k,self.kv.get(k)) for k in self.kv.getkeys_by_prefix(username.encode('utf-8'))]
        self.write(json.dumps(info))
        # self.write(r'<pre>%s</pre>'%cgi.escape(str(self.kv.__module__)))
        # self.write('d')


class UserDBHandler(AuthHandler):
    """docstring for UserDBHandler"""
    def initialize(self):
        AuthHandler.initialize(self)
        # Allow Cross Domain AJAX
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        
    def resjson(self, res):
        self.write(json.dumps(res))
    def resnoauth(self):
        res = {
            'succ':False,
            'msg':'用户未登录'
        }
        self.resjson(res)
    def get_userkey(self):
        return self.authed or self.username
    def get_appkey(self, app):
        return '%s@%s'%(self.get_userkey(), app)
    def get_storagekey(self, app, key):
        return '%s$%s'%(self.get_appkey(app), key)
    def options(self, *args, **kvargs):
        pass
    def get(self, app, split=None, key=None):
        if app:
            app = app.encode('utf-8')
        if key:
            key = key.encode('utf-8')
        # print self.get_argument('username')
        self.authed = None
        # print self.username
        if self.username:
            if app:
                if key:
                    # single value
                    skey = self.get_storagekey(app,key)
                    val = self.kv.get(skey)
                    if val:
                        self.write(val)
                else:
                    # get app's k-v list
                    prefix = self.get_storagekey(app,'')
                    l = len(prefix)
                    d = dict([(k[l:], v) for k,v in self.kv.get_by_prefix(prefix) if len(k)>l])
                    s = json.dumps(d)
                    self.write(s)
            else:
                # get app list
                self.resjson({
                    'succ':True,
                    'apps':[self.kv.get(self.get_appkey(a)) for a in self.userkvd['apps']]
                    })
        else:
            self.resjson({
                'succ':False,
                'msg':'未指用户'
                })

    def post(self, app, split=None, key=None):
        if app:
            app = app.encode('utf-8')
        if key:
            key = key.encode('utf-8')
        if self.authed:
            if app:
                if not app in self.userkvd['apps']:
                    self.userkvd['apps'].append(app)
                    self.save_userkvd()
                    self.kv.set(self.get_appkey(app),{
                        'name':app,
                        'username':self.username
                        })
                if not key and self.request.body:
                    key = str(int(time.time()*1000))
                if key:
                    skey = self.get_storagekey(app, key)
                    # print type(self.request.body)
                    val = self.request.body
                    if isinstance(val, unicode):
                        val = val.encode('utf-8')
                    self.kv.set(skey, val)
                    # print skey
                    self.resjson({
                        'succ':True,
                        'key':key
                        })
                else:
                    self.resjson({
                        'succ':True,
                        'app':self.kv.get(self.get_appkey(app))
                        })
            else:
                self.resjson({
                    'succ':False,
                    'msg':'未指定应用名称'
                    })
            self.savekvdb()
        else:
            self.resnoauth()
    put = post

    def delete(self, app, split=None, key=None):
        if app:
            app = app.encode('utf-8')
        if key:
            key = key.encode('utf-8')
        count = 0
        if self.authed:
            if app:
                if key:
                    skey = self.get_storagekey(app, key)
                    self.kv.delete(skey)
                    count = 1
                else:
                    # 删除app域下全部
                    sk = self.get_storagekey(app, '')
                    for k in self.kv.getkeys_by_prefix(sk):
                        self.kv.delete(k)
                        count += 1
                    ak = self.get_appkey(app)
                    self.kv.delete(ak)
                    if app in self.userkvd['apps']:
                        self.userkvd['apps'].remove(app)
                        self.save_userkvd()
            else:
                # 删除全部app
                uk = self.get_appkey('')
                for k in self.kv.getkeys_by_prefix(uk):
                    self.kv.delete(k)
                    count += 1
                self.userkvd['apps'] = []
                self.save_userkvd()
            self.resjson({
                'succ':True,
                'count':count
                })
        else:
            self.resnoauth()
url = [
    (r"/", IndexHandler),
    (r"/.stc/([a-zA-Z0-9]*)", StcHandler),
    (r"/.login", LoginHandler),
    (r"/.sigin", SiginHandler),
    # (r"/([a-zA-Z0-9\-_\.]+)([/:]{0,1})([a-zA-Z0-9\-_\.]*)", DBHandler),
    (r"/api/([a-zA-Z0-9\-_%\.]*)([/:]{0,1})([a-zA-Z0-9\-_\.%]*)", UserDBHandler),
    (r"/([a-zA-Z0-9\-_%]*)([/:]{0,1})([a-zA-Z0-9\-_\.%]*)", UserDBHandler),
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


