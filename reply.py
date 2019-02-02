from tools import *
import random
from simple import *
from bus import *
from admin import *
from igg import *

def random_str(n=16):
    s = 'qwertyuiopasdfgjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    return ''.join(random.sample(s, n))



items = [Help, Bus, AirQuality, Weather, Admin, IggCode]
instances = [item() for item in items]

def text_reply(s, level):
    s = s.strip().replace('_', ' ')
    for instance in instances:
        if instance.satisfy(s):
            return instance.reply(s, level)

    lmsg = LinkMsg()
    lmsg.add_msg('未知消息内容。')
    lmsg.add_item('请回复"帮助"来获取帮助。', '帮助')
    lmsg.add_msg('点击蓝色链接即可自动发送。')
    return lmsg.dump()


class MyReply(object):
    def __init__(self):# {{{
        self.db = db
    # }}}
    def reply(self, msg):# {{{
        if msg.type == 'event':
            content = self.event_op(msg)
        elif msg.type == 'text':
            content = self.text_op(msg)
        else:
            content = '未知操作类型，不处理。'
        if isinstance(content, list):
            content = '\n'.join(content)
        return content
    # }}}
    def event_op(self, msg):# {{{
        res = self.register(msg._data['FromUserName'])
        event = msg._data['Event']
        if event == 'subscribe':
            if res is None:
                return text_reply('help')
            return res
        return '不处理\'{}\'事件。:)'.format(event)
    # }}}
    def text_op(self, msg):# {{{
        res = self.register(msg._data['FromUserName'])
        if res is not None:
            return res
        content = msg.content
        level, code = self.user_level_code(msg._data['FromUserName'])
        res = text_reply(content, level)
        if res == LEVEL_REQUIRED:
                return res + '验证码为{}。'.format(code)
        return res
    # }}}
    def user_level_code(self, wechat):# {{{
        users = db.select('user', limitation={'wechat': wechat})
        if len(users) == 0:
            return -1
        return users[0]['level'], '%s%04d'%(users[0]['code'], users[0]['id'])
    # }}}
    def register(self, wechat):# {{{
        level, _ = self.user_level_code(wechat)
        if level == -1:
            code = random_str(8)
            db.add_row('user', data={'wechat': wechat, 'level': 0, 'code': code})
            index, = db.select('user', limitation={'wechat': wechat}, keys='id')
            code = '%s%04d'%(code, index['id'])
            return '注册成功，验证码为{}，请联系管理员审核。'.format(code)
        return None
    # }}}

rpl = MyReply()

if __name__ == '__main__':
    while True:
        s = input('Q:  ')
        res = text_reply(s.strip(), 100)
        if isinstance(res, list):
            res = '\n'.join(res)
        print(res)
        print('nums =', len(res))

