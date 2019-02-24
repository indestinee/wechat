import requests, re
from lxml import etree
from tools import *



headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

re_dir = re.compile(r'<a .*?data-uuid="(.*?)">(.*?)</a>', re.S)
re_station = re.compile(r'<a .*?data-seq="(.*?)">(.*?)</a>', re.S)
query_url = 'https://www.bjbus.com/home/ajax_rtbus_data.php'

__all__ = ['Bus']
class Bus(object):
    def __init__(self):
        self.sess = requests.Session()
        self.re = re.compile(\
                r'^(bus|b)*[ \n\r\t]*([^ \n\r\t]*[0-9]+[^ \n\r\t]*)*[ \n\r\t]*([0-9]*)[ \n\r\t]*([0-9]*)$')
        self.re_bus_id = re.compile(r'<dd id="selBLine">(.*?)</dd>', re.S)
        self.re_h2 = re.compile('<h2.*?>(.*?)</h2>', re.S)
        self.re_article = re.compile('<article.*?>(.*?)</article>', re.S)
        self.re_tag = re.compile(r'<[^>]*>', re.S)
        self.bus_id_url = 'https://www.bjbus.com/home/index.php'
        bus_id_db_name = 'bus_id'
        self.bus_id = db.get_global(bus_id_db_name, None)
        if self.bus_id is None:
            self.bus_id = self.get_bus_id()
            db.set_global(bus_id_db_name, self.bus_id, 86400)

    def show_bus(self):
        msg = '请发送正确指令，如发送"bus 公交车号"或者"公交车号"查询。'
        return msg

    def get_bus_id(self):
        response = self.sess.get(self.bus_id_url)
        response.encoding = 'utf-8'
        tree = etree.HTML(self.re_bus_id.findall(response.text)[0])
        items = tree.xpath('//a[contains(@href, \'javascript:;\')]')
        items = [item.text for item in items]
        ids = {x for x in items}
        return ids


    def satisfy(self, msg):
        msg = msg.lower()
        return self.re.match(msg) is not None

    def reply(self, msg, level):
        if level < NORMAL:
            return LEVEL_REQUIRED
        msg = msg.lower()
        _, bus_id, bus_dir, station_id = self.re.match(msg).groups()
        if bus_id is None or bus_id not in self.bus_id:
            return self.show_bus()

        if bus_dir == '':
            dirs = self.get_bus_dirs(bus_id)
            lmsg = LinkMsg()
            for item_k, item in enumerate(dirs):
                lmsg.add_item(item[1], 'bus_{}_{}'.format(bus_id, item_k))
            res = lmsg.dump()
            return res
        elif station_id == '':
            dirs = self.get_bus_dirs(bus_id)
            lmsg_error = LinkMsg()
            lmsg_error.add_item(bus_id, bus_id)
            dir_id = bus_dir
            try: bus_dir = dirs[int(bus_dir)][0]
            except: return '非法路线！请重新查询{}。'.format(lmsg_error.dump())
            stations = self.get_bus_stations(bus_id, bus_dir)

            lmsg = LinkMsg()
            for i, s in enumerate(stations):
                lmsg.add_item(s[1], 'bus_{}_{}_{}'.format(bus_id, dir_id, i))
            res = lmsg.dump('->')

            if len(res) > 2000:
                lmsg.msgs.clear()
                for i, s in enumerate(stations):
                    lmsg.add_msg('【{}: "{} {} {}"】'.format(s[1], bus_id, dir_id, i))
                res = [lmsg.dump('->'),\
                        '请发送对应站后面引号内的指令。',\
                        '如查询{}的到站时间，则发送"{} {} {}"。'.format(\
                        stations[0][1], bus_id, dir_id, 0)]
            return res
        else:
            dirs = self.get_bus_dirs(bus_id)
            lmsg_error = LinkMsg()
            lmsg_error.add_item(bus_id, bus_id)
            dir_id = bus_dir
            try:
                bus_dir = dirs[int(bus_dir)][0]
                stations = self.get_bus_stations(bus_id, bus_dir)
                station_id = stations[int(station_id)][0]
            except: return '非法路线！请重新查询{}。'.format(lmsg_error.dump())

            _time = self.get_bus_time(bus_id, bus_dir, station_id)
            return _time

        return _, bus_id, dir_id, station_id
    def get_bus_time(self, bus_id, selBDir, station_id):
        data = {
            'act': 'busTime',
            'selBLine': bus_id,
            'selBDir': selBDir,
            'selBStop': station_id, 
        }
        response = self.sess.get(query_url, params=data, headers=headers)
        response.encoding = 'utf-8'
        res = response.json()
        articles = self.re_article.findall(res['html'])
        h2s = self.re_h2.findall(res['html'])
        
        article = articles[0]

        article = self.re_tag.sub('', article).replace('&nbsp;', ' ')
        return '{}: {}\n当前站：{}\n{}'.format(bus_id, h2s[0], res['seq'], article.strip())

    def get_bus_dirs(self, bus_id):# {{{
        x = db.get_global('bus {}'.format(bus_id))
        if x is not None:
            return x
        data = {
            'act': 'getLineDir',
            'selBLine': bus_id,
        }
        response = self.sess.get(query_url, params=data, headers=headers)
        response.encoding = 'utf-8'
        dirs = re_dir.findall(response.text)
        db.set_global('bus {}'.format(bus_id), dirs, expired_time=300)
        return dirs
    # }}}
    def get_bus_stations(self, bus_id, selBDir):# {{{
        x = db.get_global('bus {} {}'.format(bus_id, selBDir))
        if x is not None:
            return x
        data = {
            'act': 'getDirStation',
            'selBLine': bus_id, 
            'selBDir': selBDir,
        }
        response = self.sess.get(query_url, params=data, headers=headers)
        response.encoding = 'utf-8'
        stations = re_station.findall(response.text)
        db.set_global('bus {} {}'.format(bus_id, selBDir), stations, expired_time=300)
        return stations
    # }}}
