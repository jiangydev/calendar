#encoding: utf-8

'''


'''

import memcache
from config import MEMCACHED_INFO

cache = memcache.Client([MEMCACHED_INFO], debug=True)

def set(key, value, timeout=60):
    return cache.set(key, value, timeout)

def get(key):
    try:
        return cache.get(key)
    except memcache.Client.MemcachedKeyError:
        # 如果传入的key为空，或其他问题导致出现memcache键方面的异常，就直接返回False
        return False


def delete(key):
    try:
        return cache.delete(key)
    except memcache.Client.MemcachedKeyError:
        return False