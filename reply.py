from tools import db
import random
import bus

def random_str(n=16):
    s = 'qwertyuiopasdfgjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    return ''.join(random.sample(s, n))



class MyReply(object):

    def __init__(self):
        self.db = db


    def user_level(self, wechat):
        user_db = db.select('user', limitation={'wechat': wechat})
        if len(user_db) == 0:
            return -1, '尚未注册，请取消关注后重新关注！'
        user_db = user_db[0]
        if user_db['level'] == 0:
            return 0, '已经注册，尚未通过审核，请联系管理员！'
        elif user_db['level'] == 1:
            return 1, '正常用户'
        elif user_db['level'] == 100:
            return 100, '管理员'

    def register(self, wechat):
        level, _ = self.user_level(wechat)
        if level == -1:
            try:
                code = random_str(6)
                db.add_row('user', data={'wechat': wechat, 'level': 0, 'code': code})
                return '注册成功，验证码为{}，请等待审核。'.format(code)
            except Exception as e:
                print(e)
                return '注册失败，请联系管理员查看错误日志！'
        elif level == 0:
            code = random_str(6)
            db.upd_row('user', limitation={'wechat': wechat}, data={'code': code})
            return '已通过注册，等待审核，验证码为{}。'.format(code)
        else:
            return '已通过注册及审核，身份为{}。'.format(_)


    def is_help(self, content):
        return content.lower() in ['h', 'help', 'helps', 'bz', '帮助', 'bangzhu']

    def help_query(self, content):
        return '''\
(0) 获取帮助，如发送h。
(1) 查询公交，如发送543。
'''
    
    def is_bus(self, content):
        try: 
            bus_id = int(content)
            return True
        except: return False

    def bus_query(self, content):
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


    def event_reply(self, msg):
        event = msg._data['Event']
        if event == 'subscribe':
            return self.register(msg._data['FromUserName'])
        return '不处理\'{}\'事件。:)'.format(event)

rpl = MyReply()
