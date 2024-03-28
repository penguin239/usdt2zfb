from telethon import Button

# debug
api_id = 0
api_hash = ''
bot_token = ''

# release
# api_id = 0
# api_hash = ''
# bot_token = ''

# 异步回调地址
notify_url = 'http://127.0.0.1:8668/pay_notice'
# 支付成功重定向地址
redirect_url = 'http://127.0.0.1:8668/pay_notice'
# api请求token
api_auth_token = 'token'

# 是否启用代理
proxy_on = True
proxy = {
    'proxy_type': 'socks5',
    'addr': '127.0.0.1',
    'port': 7890,
}

# database
host = '127.0.0.1'
database = 'db'
port = 3306
username = 'root'
password = 'root'
table = 'passport'
user_table = 'user'
records_table = 'records'
recharge_records_table = 'recharge_records'

channel_url = ''
consultant_url = ''

# 欢迎语
hello = f'''
\ud83e\udde7 支付宝口令兑换
✅ 微信支付宝扫码代付
\ud83d\udcf1 票务、民宿、话费
\ud83c\udf10 24小时高效秒出
\u267b\ufe0f TRX、能量，自动兑换
\ud83d\udcb0 充U智能上账，无需等待

\ud83e\udd70 售后客服：
\ud83d\udd75\ud83c\udffb\u200d\u2640\ufe0f 商业合作请联系：
'''
hello_button = [
    [Button.inline('口令兑换', b'exchange'), Button.inline('扫码代付', b'scan')],
    [Button.inline('账户信息', b'info'), Button.inline('我要充值', b'etc')],
    [Button.url('进交流群', channel_url), Button.inline('TRX兑换', b'trx')],
]

# exchange界面
exchange_content = '''
请点击下方按钮进行兑换
'''
exchange_button = [
    [Button.inline('50', b'50'), Button.inline('100', b'100'), Button.inline('200', b'200')],
    [Button.inline('300', b'300'), Button.inline('500', b'500'), Button.inline('1000', b'1000')],
    [Button.inline('2000', b'2000'), Button.inline('3000', b'3000'), Button.inline('5000', b'5000')],
]
