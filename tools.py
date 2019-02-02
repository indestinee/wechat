from utils.database import DataBase
ilegal = '非法操作！'
class LinkMsg(object):
    def __init__(self):
        self.cnt = 0
        self.msgs = []



    def add_msg(self, msg):
        self.msgs.append(msg)

    def add_item(self, msg, code=None):
        if code is None:
            code = msg
        self.cnt += 1
        item = '<a href="weixin://bizmsgmenu?msgmenucontent={}&msgmenuid={}">{}</a>'.format(\
                code, self.cnt, msg)
        self.msgs.append(item)
        return item


    def dump(self, connect='\n'):
        return connect.join(self.msgs)



__tables__ = [{
        "name": "global",
        "attr": [{
                "key": "name",
                "db_type": "TEXT UNIQUE NOT NULL",
            }, {
                "key": "value",
                "db_type": "BLOB",
            }, {
                "key": "duration",
                "db_type": "FLOAT",
            }
        ]
    }, {
        'name': 'user',
        'attr': [{
                'key': 'id',
                'db_type': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            }, {
                'key': 'username',
                'db_type': 'TEXT',
            }, {
                'key': 'code',
                'db_type': 'TEXT',
            }, {
                'key': 'wechat',
                'db_type': 'TEXT NOT NULL UNIQUE',
            }, {
                'key': 'level',
                'db_type': 'INTEGER',
            }
        ]
    }
]


if __name__ == '__main__':
    pass

db = DataBase('data.db', tables=__tables__)

ADMIN = 100
NORMAL = 1
EVERYONE = 0
LEVEL_REQUIRED = '权限不足，请联系管理员获取权限。'
