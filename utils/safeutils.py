#encoding: utf-8

from urllib.parse import urlparse, urljoin
from flask import request

def is_safe_url(target):
    '''
    拼接期望的目标url，并与传入url比较主体是否一致
    :param target: String 需要验证的url
    :return: True/False
    关于urlparse：
        将URL解析为六个组件，返回一个6元组。这对应于URL的一般结构：scheme://netloc/path;parameters?query#fragment。每个元组项都是一个字符串，可能为空。
    '''
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc