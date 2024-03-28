import hashlib
import random
import string
import threading
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from telethon import TelegramClient, events, errors
from telethon import Button
from utils import Utils
from flask import Flask, request

import paho.mqtt.client as mqtt

import asyncio
import json
import time
import setting

# 存放用户充值队列,最大长度为50,防止程序臃肿
# 达到50时删除第一个进入队列的用户
session = {}

app = Flask(__name__)


@app.route('/pay_notice', methods=['POST'])
def webhook_event():
    # 监听付款成功信息，付款成功后将用户从session队列中删除。
    json_data = request.get_json()
    status = json_data['status']
    print(json_data)

    if status == 2:
        amount = json_data['amount']

        user_id = json_data['order_id'].split('_')[0]
        response = utils.etc_user(user_id, amount)
        if response:
            # 充值完毕，为用户发送提醒
            reply_info = f'''
订单已完成！

订单编号：{json_data['trade_id']}
充值金额：{amount}CNY

您的最新余额：{utils.query_user(user_id)['amount']}CNY
            '''
            asyncio.run_coroutine_threadsafe(client.send_message(int(user_id), reply_info), loop)
            remove_session(int(user_id))

            # 添加充值记录
            utils.etc_history(user_id, json_data['trade_id'], json_data['order_id'], json_data['amount'],
                              json_data['actual_amount'], json_data['token'])
            return 'ok'
    return '-1'


api_id = setting.api_id
api_hash = setting.api_hash
bot_token = setting.bot_token

utils = Utils()
if setting.proxy_on:
    client = TelegramClient('zfbot', api_id, api_hash, proxy=setting.proxy)
else:
    client = TelegramClient('zfbot', api_id, api_hash)
loop = asyncio.get_event_loop()


async def split_username(first_name, last_name):
    user_name = f'{first_name} {last_name}'
    if not first_name:
        user_name = f'{last_name}'
    elif not last_name:
        user_name = f'{first_name}'
    return user_name


@client.on(events.NewMessage(pattern='(?i)/start'))
async def start(event):
    sender = event.sender_id
    user_info = await event.get_sender()
    username = await split_username(user_info.first_name, user_info.last_name)
    msg = f'\uD83D\uDC4B Welcome, {username}, 欢迎使用支付宝口令红包自助兑换机器人'
    if not utils.query_user(sender):
        # 如果用户第一次使用，为用户注册
        utils.register(sender, username)

    await client.send_message(sender, msg)
    await client.send_message(sender, message=setting.hello, buttons=setting.hello_button, link_preview=False)


@client.on(events.NewMessage(pattern='(?i)/exchange'))
async def exchange(event):
    sender = event.sender_id
    user_info = utils.query_user(sender)
    if not await is_registered(sender, user_info): return
    await client.send_message(sender, message=setting.exchange_content, buttons=setting.exchange_button)

    await event.answer()


@client.on(events.NewMessage(pattern='(?i)/info'))
async def info(event):
    sender = event.sender_id
    user_info = utils.query_user(sender)
    if not await is_registered(sender, user_info): return

    reply = f'''
您的个人ID：{sender}
您的余额：**{user_info.get('amount')}**CNY
    '''
    await client.send_message(sender, reply)
    await event.answer()


def gen_id(k=8):
    # 生成k位随机字符, k默认为8
    return ''.join(random.sample(string.ascii_letters, k))


async def etc_hander(event, cny):
    if session.get(event.sender_id, 0) != 0:
        # 用户已经在订单队列中了
        await event.respond('您有订单正在进行中！进行其他操作前请先取消此订单！', buttons=[
            Button.inline('点我取消订单', f'removeSession_{event.sender_id}')
        ])
        return
    # 自动充值
    base_url = 'https://usdtpay.uk/'
    api_auth_token = setting.api_auth_token
    order_id = f'{event.sender_id}_{str(int(time.time()))}_{gen_id()}'

    data = {
        'order_id': order_id,
        'amount': int(cny),
        'notify_url': setting.notify_url,
        'redirect_url': setting.redirect_url  # 支付成功后的回调地址，对应上面的webhook
    }

    url_a = f"amount={data['amount']}&notify_url={data['notify_url']}&order_id={data['order_id']}&redirect_url={data['redirect_url']}{api_auth_token}"

    md5 = hashlib.md5()
    md5.update(url_a.encode())
    signature = md5.hexdigest()

    data['signature'] = signature
    create_url = base_url + 'api/v1/order/create-transaction'
    response = requests.post(create_url, json=data)

    if response.status_code != 200:
        return None
    response = json.loads(response.text)
    response_data = response['data']

    # 生成订单，向支付队列中添加该用户
    session[event.sender_id] = response_data['expiration_time']

    reply_info = f'''
订单编号：{response_data['trade_id']}
充值金额：**{response_data['amount']}CNY**

实际付款金额：**{response_data['actual_amount']}USDT**
**\u203c\ufe0f请核对好金额，转账金额不能多不能少，否则系统无法识别！**

请向下方地址付款 **{response_data['actual_amount']}** USDT(TRC20网络)，即可自动充值到账户（点击地址可复制）
`{response_data['token']}`

**\u203c\ufe0f请在十分钟内支付，否则订单将过期。**
__在订单自动取消或者您手动取消之前请不要做其他操作，防止订单失败__
    '''

    await client.send_message(event.sender_id, reply_info)


def remove_session(sender):
    if sender in session.keys():
        session.pop(sender)


@client.on(events.CallbackQuery)
async def cancel_etc(event):
    if event.data.decode('utf-8') == 'cancel_etc':
        remove_session(event.sender_id)
        await event.edit('您已取消支付。')
        await event.answer()
        return


async def etc(event):
    if event.sender_id in session.keys():
        # 用户已经在订单队列中了
        await event.respond('您有订单正在进行中！进行其他操作前请先取消此订单！', buttons=[
            Button.inline('点我取消订单', f'removeSession_{event.sender_id}')
        ])
        return
    if event.sender_id not in session:
        session[event.sender_id] = 0
    await event.answer()

    # 提醒用户发送要充值的数量
    await event.respond(
        '请向我发送充值CNY的数量，只发送数字。\n请不要多次发送，以免创建多个订单。',
        buttons=[
            Button.inline('取消支付', b'cancel_etc')
        ]
    )


@client.on(events.NewMessage)
async def handle_message(event):
    if event.text == '/start':
        return
    if event.sender_id not in session.keys():
        # 用户不在充值队列中则不回复
        return
    try:
        amount = int(event.text)
    except:
        await event.respond('您输入的格式有误！请重新发送。')
        return
    if amount <= 0:
        await event.respond('您输入充值数量有误！请重新发送。')
        return
    await event.respond('收到，订单正在处理中...')

    cny = amount

    await etc_hander(event, cny)


async def developing(event):
    sender = event.sender_id
    await client.send_message(sender, '正在开发中, 请联系人工客服 @chinaLeijun')

    # 对点击按钮进行答复，否则按钮会出现加载动画
    await event.answer()


switch = {
    'exchange': exchange,
    'scan': developing,
    'info': info,
    'etc': etc,
}


@client.on(events.CallbackQuery)
async def handler(event):
    sender = event.sender_id
    decode_data = event.data.decode('utf-8')
    if decode_data in switch.keys():
        await switch[decode_data](event)
    if event.data.isdigit():
        amount = int(event.data.decode('utf-8'))
        balance = utils.query_user(sender).get('amount', 0)
        new_balance = balance - amount
        if new_balance < 0:
            await event.edit('您的余额不足！', buttons=[
                [Button.inline('返回上一页', b'back')]
            ])
            return

        await event.edit(f'确认交易？\n当前余额：{balance}CNY\n交易后余额{new_balance}CNY', buttons=[
            [Button.inline('确认交易', b'confirm_' + str(amount).encode()), Button.inline('取消交易', b'cancel')],
            [Button.inline('返回上一页', b'back')]
        ])
    elif event.data.startswith(b'confirm_'):
        amount = int(event.data.decode('utf-8').split('_')[1])
        passport = utils.send_passport(amount)
        if passport:
            utils.update_user_balance(sender, amount)
            balance = utils.query_user(sender).get('amount', 0)

            user_info = await event.get_sender()
            username = await split_username(user_info.first_name, user_info.last_name)
            utils.save_recorded(sender, passport, amount, username)
            await event.edit(f'交易成功！您的新余额为：{balance}CNY\n您的口令为：{passport}')
            await event.answer()
            return
        await event.edit(f'{amount}面值的口令红包已经没有了，如果需要请联系人工客服。', buttons=[
            [Button.inline('返回上一页', b'back'), Button.url('人工客服', setting.consultant_url)]
        ])
        await event.answer()
    elif event.data == b'cancel':
        await event.edit('交易已取消', buttons=[
            [Button.inline('返回上一页', b'back')]
        ])
        await event.answer()
    elif event.data == b'back':
        # 返回初始交易选择界面
        await event.edit(setting.exchange_content, buttons=setting.exchange_button)
        await event.answer()
    elif event.data == b'trx':
        await client.send_message(sender, '''
\ud83d\udfe2**USDT兑换TRX**\ud83d\udd34
**往\ud83d\udd3b下方地址转USDT,会5秒内自动回你TRX**
**点击地址自动复制【汇率1U=8.4651T】**
``

**往\ud83d\udd3b下方地址转TRX,会5秒内自动回你能量**
**TRX能量兑换地址：【点击地址自动复制】**
``

1.8TRX=33000能量，时效1小时
3.6TRX=66000能量，针对没有u的地址，时效1小时
        ''')
        await event.answer()
    elif event.data.startswith(b'removeSession_'):
        user_id = decode_data.split('_')[1]
        remove_session(int(user_id))
        await event.edit('您的订单已经取消.')
        await event.answer()


async def is_registered(sender, uid):
    if not uid:
        await client.send_message(sender, '您还未注册，请 /start 后使用。')
        return False
    return True


@client.on(events.NewMessage(pattern='(?i)/artificial'))
async def artificial(event):
    sender = event.sender_id
    await client.send_message(sender, '人工客服： @chinaLeijun')


def on_connect(client, userdata, flags, rc):
    """
    连接mqtt服务器，mqtt服务用于接收django传过来的用户余额变动
    """
    print('Connected with result code' + str(rc))
    client.subscribe(topic='notice')


def on_message(c, userdata, msg):
    # 有新消息到来
    reply = json.loads(msg.payload.decode('utf-8'))
    sender = int(reply.get('sender'))
    content = reply.get('content')

    asyncio.run_coroutine_threadsafe(client.send_message(sender, content), loop)


def run_app():
    app.run(host='0.0.0.0', port=8668, threaded=True)


def detect_expired_orders():
    if not session:
        return
    try:
        for item in session:
            if session[item] == 0:
                continue
            if int(session[item]) - int(time.time()) <= 0:
                # print(f'{item}的订单已过期')
                remove_session(item)
                asyncio.run_coroutine_threadsafe(client.send_message(int(item), '您的订单已过期，请勿发起支付！'),
                                                 loop)
    except RuntimeError:
        pass


async def notice_user():
    for user in utils.all_user():
        await client.send_message(int(user), '''
        ''')


if __name__ == '__main__':
    first_start_time = time.time()

    client_mqtt = mqtt.Client()
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.connect('localhost', 1883, 60)
    print(f'**mqtt服务启动成功，耗时{round(time.time() - first_start_time, 2)}s**\n')
    client_mqtt.loop_start()

    # 开启新线程，防止阻塞
    flask_thread = threading.Thread(target=run_app)
    flask_thread.start()

    # 检测订单过期
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(detect_expired_orders, 'interval', seconds=3)
    scheduler.start()

    print('********webhook监听中********\n')

    first_start_time = time.time()
    client.start(bot_token=bot_token)
    print(f'**telethon服务启动成功，耗时{round(time.time() - first_start_time, 2)}s**')

    # 向所有用户发送通知
    # asyncio.run_coroutine_threadsafe(notice_user(), loop)
    client.run_until_disconnected()
