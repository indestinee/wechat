from utils.database import DataBase


__tables__ = [{
        "name": "global",
        "attr": [{
                "key": "name",
                "db_type": "TEXT UNIQUE NOT NULL",
            }, {
                "key": "value",
                "db_type": "BLOB",
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
