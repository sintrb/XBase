# -*- coding: UTF-8 -*
'''
Created on 2015年2月09日
@author: RobinTang
'''

class KVClientCheat:
    def __init__(self):
        self.cache = {}
    def set(self, key, val, min_compress_len=0):
        '''设置key的值为val'''
        self.cache[key] = val
    def add(self, key, val, min_compress_len=0):
        '''同set，但只在key不存在时起作用'''
        if key not in self.cache:
            self.set(key, val, min_compress_len)
    def replace(self, key, val, min_compress_len=0):
        '''同set，但只在key存在时起作用'''
        if key in self.cache:
            self.set(key, val, min_compress_len)
    def delete(self, key):
        '''删除key。'''
        if key in self.cache:
            del self.cache[key]
    def get(self, key):
        '''从KVDB中获取一个key的值，存在返回key的值，不存在则返回None'''
        if key in self.cache:
            return self.cache[key]
        else:
            return None
    def get_multi(self, keys, key_prefix=''):
        '''从KVDB中一次获取多个key的值。返回一个key/value的dict。'''
        return [self.get(key_prefix+k) for k in keys]
    def get_by_prefix(self, prefix, limit=100, marker=None):
        '''从KVDB中查找指定前缀的 key/value pair。返回一个generator，yield的item为一个(key, value)的tuple。'''
        for k in self.cache.keys():
            if k.startswith(prefix):
                yield (k, self.cache[k])
    def getkeys_by_prefix(self, prefix, limit=100, marker=None):
        '''从KVDB中查找指定前缀的key。返回符合条件的key的generator。'''
        return [k for k in self.cache.keys() if k.startswith(prefix)]

    def get_info(self):
        '''获取本应用KVDB统计数据，返回一个字典:'''
        return {
                'count': len(self.cache),
                'keys': [k for k in self.cache.keys()],
                'outbytes': 0,
                'total_size': 0,
                'inbytes': 0,
                'set_count': 0,
                'delete_count': 0,
                'total_count': 0,
                'get_count': 0
                }

    instance = None
    @staticmethod
    def get_instance():
        if not KVClientCheat.instance:
            KVClientCheat.instance = KVClientCheat()
        return KVClientCheat.instance


if __name__ == '__main__':
    kv = KVClientCheat.get_instance()
    kv.add("ax", "t")
    kv.add("ab", "tx")
    print kv.get_multi(['x','b'], 'a')
    print [v for v in kv.get_by_prefix('a')]
    print kv.getkeys_by_prefix('a')
    kv.delete('ax')
    print kv.get('ax')


    print kv.get_info()