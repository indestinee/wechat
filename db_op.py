from tools import db

import json
with open('./data/config.json') as f:
    _cfg_ = json.load(f)


def set_admin():
    for admin in _cfg_['admins']:
        db.upd_row('user', limitation={'wechat': admin}, data={'level': 100})

def check_user():
    users = db.select('user', limitation={'level': 0})
    for user in users:
        print(user)
        n_level = input('new level: ')
        n_level = int(n_level)
        assert n_level >= 0 and n_level <= 100
        db.upd_row('user', limitation={'wechat': user['wechat']}, data={'level': n_level})

if __name__ == '__main__':
    # set_admin()

    check_user()


    pass
    

