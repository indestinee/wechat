

def text_reply(msg):
    user = msg._data['FromUserName']
    print(user)
    return 'hi'
