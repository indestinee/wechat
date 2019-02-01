from tools import *
import random
from simple import *
from bus import *

def random_str(n=16):
    s = 'qwertyuiopasdfgjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    return ''.join(random.sample(s, n))



items = [Help, Bus, AirQuality, Weather]
instances = [item() for item in items]

def text_reply(s):
    s = s.strip().replace('_', ' ')
    for instance in instances:
        if instance.satisfy(s):
            return instance.reply(s)

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
        return text_reply(content)
    # }}}
    def user_level(self, wechat):# {{{
        users = db.select('user', limitation={'wechat': wechat})
        if len(users) == 0:
            return -1
        return users[0]['level']
    # }}}
    def register(self, wechat):# {{{
        level = self.user_level(wechat)
        if level == -1:
            code = random_str(8)
            db.add_row('user', data={'wechat': wechat, 'level': 0, 'code': code})
            index, = db.select('user', limitation={'wechat': wechat}, keys='id')
            code = '%s%04d'%(code, index['id'])
            return '注册成功，验证码为{}，请联系管理员审核。'.format(code)
        return None
    # }}}
    def wm(self, content):
        return simple.wm(content)

    def tq(self, content):
        return simple.tq(content)
    
    def is_bus(self, content):
        try: 
            bus_id = int(content)
            return True
        except: 
            if content[:3] == 'bus':
                return True
            return False

    def bus_query(self, content):
        if content[:3] == 'bus':
            return bus.bus_query(content)
        return bus.query(content)


    def text_reply(self, msg):
        wechat = msg._data['FromUserName']
        level, _ = self.user_level(wechat)
        if level < 1:
            return _
        
        content = msg.content.strip()

        if self.is_help(content):
            return self.help_query(content)
        
        if self.is_bus(content):
            return self.bus_query(content)
        
        if content[:2] == 'wm':
            return self.wm(content)

        if content[:2] == 'tq':
            return self.tq(content)
        
        return 

rpl = MyReply()

if __name__ == '__main__':
    while True:
        s = input('Q:  ')
        res = text_reply(s.strip())
        if isinstance(res, list):
            res = '\n'.join(res)
        print(res)
        print('nums =', len(res))

