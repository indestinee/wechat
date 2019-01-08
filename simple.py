import requests, re
from lxml import etree
from lxml.html.clean import Cleaner
from tools import *

cleaner = Cleaner(style=True, scripts=True, page_structure=False, safe_attrs_only=False)

sess = requests.Session()
re_tag = re.compile('<[^<>]*?>')
def wm(content):
    x = db.get_global(content)
    if x is not None:
        return x

    url = 'http://106.37.208.228:8082/CityForecast'
    response = sess.post(url, data={'CityName': '北京市'})
    # response.encoding='utf-8'
    tree = etree.HTML(response.text)

    items = tree.xpath('//div[contains(@class, \'hourAqiDiv\')]')
    res = ''

    for item in items:
        _item = etree.tostring(item)
        item = etree.HTML(_item)
        # print(_item)
        date = item.xpath('//div[contains(@class, \'aqi_title\')]')
        value = item.xpath('//div[contains(@class, \'aqi_value\')]')
        date = etree.tostring(date[0])
        value = etree.tostring(value[0])
        date = date.decode('utf-8')
        value = value.decode('utf-8')
        date = cleaner.clean_html(date)
        value = cleaner.clean_html(value)
        date = re_tag.sub('', date).replace(' ', '').replace('\n', ' ').replace('\r', '').strip()
        value = re_tag.sub('', value).replace(' ', '').replace('\n', ' ').replace('\r', '').strip()

        res += date + value + '\n'
    db.set_global('wm', res, expired_time=3600)
    return res
        
def tq(content):
    return '尚未竣工。'

if __name__ == '__main__':
    wm('wm')
