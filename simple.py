import requests, re
from lxml import etree
from tools import *
from html import unescape

__all__ = ['Help', 'AirQuality', 'Weather']
re_tag = re.compile(r'<[^>]*>', re.S)
class Help(object):
    def __init__(self): pass
    def satisfy(self, msg):
        return msg.lower() in {'h', 'help', 'helps', 'bz', '帮助', 'bangzhu'}
    def reply(self, msg):
        lmsg = LinkMsg()
        res = '''\
(1) 获取帮助，如发送{}。
(2) 查询北京公交，如发送{}, {}, {}。
(3) 查询雾霾指数，如发送{}，{}，{} （无城市则默认北京）。
(4) 查询北京天气，如发送{}。
'''.format(lmsg.add_item('h'), lmsg.add_item(549),\
        lmsg.add_item(579), lmsg.add_item(543),\
        lmsg.add_item('wm'), lmsg.add_item('aq'),\
        lmsg.add_item('wm_北京'), lmsg.add_item('tq'))
        return res

class Weather(object):
    def __init__(self):
        self.re = re.compile(\
                r'^(tq|w)[ \t\n\r]*(.*?)$', re.S)
    
    def satisfy(self, msg):
        return self.re.match(msg) is not None

    def reply(self, msg):
        _, city = self.re.match(msg).groups()
        if city == '':
            city = '北京'
        return '查询城市：{}。\n功能尚未完成。'.format(city)

class AirQuality(object):
    def __init__(self):
        self.re = re.compile(\
                r'^(wm|aq)[ \t\n\r]*(.*?)$', re.S)
        self.url = 'http://106.37.208.228:8082/CityForecast'
        self.sess = requests.Session()

        cities_db_name = 'aq_cities'
        self.cities = db.get_global(cities_db_name, None)
        if self.cities is None:
            self.cities = self.get_cities()
            db.set_global(cities_db_name, self.cities, 86400)

    def get_cities(self):
        response = self.sess.get(self.url)
        response.encoding = 'utf-8'
        tree = etree.HTML(response.text)
        items = tree.xpath('//a[contains(@class, \'city_item\')]')
        items = [item.text for item in items]
        city = {x for x in items}
        return city

    def satisfy(self, msg):
        return self.re.match(msg) is not None

    def reply(self, msg):
        _, city = self.re.match(msg).groups()
        if city == '':
            city = '北京'
        if city not in self.cities:
            city += '市'
        if city in self.cities:
            return self.query(city)
        return ['城市列表: ' + ', '.join(list(self.cities.keys())),\
                '目前只支持以上城市，发送"aq 城市名"查询。']

    def query(self, city):
        name = 'aq ' + city
        x = db.get_global(name)
        if x is not None:
            return x
        response = self.sess.post(self.url, data={'CityName': city})
        response.encoding = 'utf-8'
        tree = etree.HTML(response.text)

        items = tree.xpath('//div[contains(@class, \'hourAqiDiv\')]')
        res = '{}空气质量：\n'.format(city)
        print(res)

        for item in items:
            _item = etree.tostring(item)
            item = etree.HTML(_item)
            # print(_item)
            date = item.xpath('//div[contains(@class, \'aqi_title\')]')[0]
            value = item.xpath('//div[contains(@class, \'aqi_value\')]')[0]
            
            date = etree.tostring(date)
            value = etree.tostring(value)
            date = date.decode('utf-8')
            value = value.decode('utf-8')
            
            date = unescape(date)
            value = unescape(value)

            date = re_tag.sub('', date).replace(' ', '').\
                    replace('\n', ' ').replace('\r', '').strip()
            value = re_tag.sub('', value).replace(' ', '').\
                    replace('\n', ' ').replace('\r', '').strip()
            res += date + value + '\n'
        db.set_global(name, res, expired_time=300)
        return res
        
