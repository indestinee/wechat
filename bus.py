import requests, re
sess = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

re_dir = re.compile('<a .*?data-uuid="(.*?)">(.*?)</a>', re.S)
re_station = re.compile('<a .*?data-seq="(.*?)">(.*?)</a>', re.S)

def query(content):
    bus_id = int(content)
    query_url = 'https://www.bjbus.com/home/ajax_rtbus_data.php'

    # @direction query {{{
    data = {
        'act': 'getLineDir',
        'selBLine': bus_id,
    }
    response = sess.get(query_url, params=data, headers=headers)
    response.encoding = 'utf-8'
    dirs = re_dir.findall(response.text)
    # }}}

    # @direction station {{{
    res = []
    menuid = 0
    for item in dirs:
        data = {
            'act': 'getDirStation',
            'selBLine': bus_id, 
            'selBDir': item[0],
        }
        response = sess.get(query_url, params=data, headers=headers)
        response.encoding = 'utf-8'
        stations = re_station.findall(response.text)

        tmp = '{}:\n{}\n'.format(
            item[1], '->'.join([
                '<a href="weixin://bizmsgmenu?msgmenucontent=bustime {}-{}-{}&msgmenuid={}">{}</a>'\
                        .format(bus_id, item[0], s[0], menuid + k, s[1]) for k, s in enumerate(stations)])
        )
        menuid += len(stations)
        res.append(tmp)

    res = '\n'.join(res)
    print(res)
    return res

def time_query(content):
    pass


    # }}}
if __name__ == '__main__':
    
    query('543')
