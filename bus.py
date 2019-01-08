import requests, re
from tools import *
sess = requests.Session()

        

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

re_dir = re.compile('<a .*?data-uuid="(.*?)">(.*?)</a>', re.S)
re_station = re.compile('<a .*?data-seq="(.*?)">(.*?)</a>', re.S)
query_url = 'https://www.bjbus.com/home/ajax_rtbus_data.php'

def get_bus_stations(bus_id, selBDir):
    x = db.get_global('bus {} {}'.format(bus_id, selBDir))
    if x is not None:
        return x
    data = {
        'act': 'getDirStation',
        'selBLine': bus_id, 
        'selBDir': selBDir,
    }
    response = sess.get(query_url, params=data, headers=headers)
    response.encoding = 'utf-8'
    stations = re_station.findall(response.text)
    db.set_global('bus {} {}'.format(bus_id, selBDir), stations, expired_time=60)
    return stations

def get_bus_dirs(content):
    bus_id = int(content)
    x = db.get_global('bus {}'.format(bus_id))
    if x is not None:
        return x

    data = {
        'act': 'getLineDir',
        'selBLine': bus_id,
    }
    response = sess.get(query_url, params=data, headers=headers)
    response.encoding = 'utf-8'
    dirs = re_dir.findall(response.text)
    db.set_global('bus {}'.format(bus_id), dirs, expired_time=60)
    return dirs

def query(content):
    bus_id = int(content)
    dirs = get_bus_dirs(content)

    lmsg = LinkMsg()
    for item_k, item in enumerate(dirs):
        lmsg.add_item(item[1], 'bus {} {}'.format(bus_id, item_k))

    res = lmsg.dump()
    return res


re_h2 = re.compile('<h2.*?>(.*?)</h2>', re.S)
re_article = re.compile('<article.*?>(.*?)</article>', re.S)

def bus_query(content):
    info = content.split(' ')[1:]
    try: bus_id = int(info[0])
    except: bus_id = -1
    try: dir_id = int(info[1])
    except: dir_id = -1
    try: station_id = int(info[2])
    except: station_id = -1

    if bus_id == -1 or dir_id == -1:
        return ilegal



    dirs = get_bus_dirs(bus_id)

    try: selBDir = dirs[dir_id][0]
    except: return ilegal
    
    stations = get_bus_stations(bus_id, selBDir)

    
    if station_id == -1:
        lmsg = LinkMsg()
        for s in stations:
            lmsg.add_item(s[1], 'bus {} {} {}'.format(bus_id, dir_id, s[0]))

        res = lmsg.dump('->')
        return res
    else:
        data = {
            'act': 'busTime',
            'selBLine': bus_id,
            'selBDir': selBDir,
            'selBStop': station_id, 
        }
        response = sess.get(query_url, params=data, headers=headers)
        response.encoding = 'utf-8'
        res = response.json()

        articles = re_article.findall(res['html'])
        h2s = re_h2.findall(res['html'])

        return '{}: {}\n{}'.format(bus_id, h2s[0], articles[0])

        # return re


    # }}}
if __name__ == '__main__':
    
    x = query('549')
    print(x)
    x = bus_query('bus 549')
    print(x)
    x = bus_query('bus 549 5')
    print(x)
    x = bus_query('bus 549 0')
    print(x)
    x = bus_query('bus 549 1 2')
    print(x)

