import requests, re
from lxml import etree
from tools import *
import json

__all__ = ['IggCode']

headers = {
'Host': 'lordsmobile.igg.com',
'Origin': 'http://lordsmobile.igg.com',
'Referer': 'http://lordsmobile.igg.com/event/cn/cdkey/',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest',
}
with open('./data/igg.json') as f:
    data = json.load(f)
    iggid = data['iggid']
class IggCode(object):
    def __init__(self):
        self.sess = requests.Session()
        self.re = re.compile(\
                r'^(igg)*[ \t\r\n]*(\w+)$')
        self.url='http://lordsmobile.igg.com/event/cdkey/ajax.php?game_id=1051089902'
    def satisfy(self, msg):
        return self.re.match(msg) is not None
    def reply(self, msg, level):
        if level < ADMIN:
            return LEVEL_REQUIRED
        data = self.re.match(msg).groups()
        code = data[-1]
        data = {
            'ac': 'receive',
            'type': 0,
            'iggid': iggid,
            'charname': '',
            'cdkey': code,
        }
        response = self.sess.post(self.url, data=data, headers = headers)
        return '{}'.format(response.json())


