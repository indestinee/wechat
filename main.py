from __future__ import absolute_import, unicode_literals
import os, json
from flask import Flask, request, abort, render_template
from wechatpy.crypto import WeChatCrypto
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.exceptions import InvalidAppIdException

from utils import cp

from reply import rpl
# set token or get from environments
with open('./data/config.json') as f:
    _cfg_ = json.load(f)


TOKEN = _cfg_['Token']
EncodingAESKey = _cfg_['EncodingAESKey']
AppId = _cfg_['AppID']

app = Flask(__name__)


@app.route('/')
def index():
    host = request.url_root
    return host


@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    encrypt_type = request.args.get('encrypt_type', '')
    msg_signature = request.args.get('msg_signature', '')
    

    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)

    if request.method == 'GET':
        return echo_str
    else:
        crypto = WeChatCrypto(TOKEN, EncodingAESKey, AppId)
        try:
            msg = crypto.decrypt_message(
                request.data,
                msg_signature,
                timestamp,
                nonce
            )
        except (InvalidSignatureException, InvalidAppIdException):
            abort(403)

        msg = parse_message(msg)
        
        reply = create_reply(rpl.reply(msg), msg)

        return crypto.encrypt_message(
            reply.render(),
            nonce,
            timestamp
        )


if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)
