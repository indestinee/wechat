import requests, re
from lxml import etree
from tools import *
from html import unescape

__all__ = ['Admin', ]

class Admin(object):
    def __init__(self):
        self.users = db.select('user')
        self.re = re.compile(r'^(admin|op)[ \t\r\n]*(.*?)$', re.S)

        self.re_show_user = re.compile(\
                r'^db[ \t\r\n]*select[\t\r\n ]*(\w+)[\t\r\n ]*([^ \r\r\n]*)[\t\r\n ]*(.*)$')
        self.re_clear_global = re.compile(\
                r'^db[ \t\r\n]*clear$')
        self.re_chmod = re.compile(\
                r'^db[ \t\r\n]*chmod[ \t\r\n]*(\d*)[ \t\r\n]*(\d*)$')

    def satisfy(self, msg):
        return self.re.match(msg) is not None
    def reply(self, msg, level):
        if level < ADMIN:
            return LEVEL_REQUIRED
        op = self.re.match(msg).groups()[-1]

        match = self.re_show_user.match(op)
        if match is not None:
            ops = match.groups()
            keys = ops[1]
            if keys == '': keys = '*'
            data = db.select(ops[0], limitation=ops[2], keys=keys)
            return '{}'.format(data)
        
        match = self.re_clear_global.match(op)
        if match is not None:
            ops = match.groups()
            db.del_row('GLOBAL')
            return 'Done'

        match = self.re_chmod.match(op)
        if match is not None:
            ops = match.groups()
            try:
                db.upd_row('user', limitation={'id': ops[0]}, data={'level': ops[1]})
                return '用户{}权限变为{}。'.format(ops[0], ops[1])
            except Exception as e:
                return e
        return '未知操作。'
        


