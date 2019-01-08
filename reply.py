from tools import db
class MyReply(object):

    def __init__(self):
        self.db = db



    def text_reply(self, msg):
        user = msg._data['FromUserName']
        
        user_db = db.select('user', limitation={'user': user})
        if len(user_db) == 0:
            return '尚未注册，请取消关注后重新关注！'
        user_db = user_db[0]
        if user_db['level'] == 0:
            return '已经注册，尚未通过审核，请联系管理员！'

        return 'hi, ' + user

    def event_reply(self, msg):
        print(msg)
        return 'hi'
