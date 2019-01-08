from tools import db

import json
with open('./data/config.json') as f:
    _cfg_ = json.load(f)


def set_admin(wechat):
    for admin in _cfg_:
        db.upd_row('user', limitation={'wechat': admin}, data={'level': 100})
if __name__ == '__main__':
    set_admin()

