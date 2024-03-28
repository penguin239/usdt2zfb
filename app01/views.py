from django.shortcuts import render, HttpResponse, redirect
from app01.models import user  # 管理员表
from app01.models import passport  # 口令管理表
from app01.models import Records  # 兑换记录表
from app01.models import bot_user  # 机器人用户表
from app01.models import Recharge  # 充值记录表
from django.contrib import messages
from django.http.response import JsonResponse
from zfbkl import settings

import paho.mqtt.publish as publish

import hashlib
import asyncio
import json
import math
import time
import os


# Create your views here.
def login(request):
    if request.method == 'GET':
        cookie = request.session.get('cookie', None)
        if not cookie:
            return render(request, 'login.html')
        return redirect('/')
    account = request.POST.get('account')
    password = request.POST.get('password')

    passmd5 = hashlib.md5(str(password).encode())
    password = passmd5.hexdigest()

    user_info = user.objects.filter(account=account)
    if user_info:
        if user_info.first().password == password:
            request.session['cookie'] = {
                'account': account,
                'password': password
            }
            return redirect('/')
    return render(request, 'login.html', {'tips': '用户名或密码错误'})


def get_user(request):
    username = None
    userinfo = request.session.get('cookie', None)
    if userinfo:
        username = userinfo.get('account', None)
    return username


def index(request):
    username = get_user(request)
    return render(
        request, 'index.html',
        {
            'username': username
        }
    )


def logout(request):
    request.session.clear()

    return redirect('/login/')


def page_split(all_pass):
    passport_numbers = len(all_pass)
    # 16条记录分页
    per_page = 16
    split_passports = [all_pass[i:i + per_page] for i in range(0, len(all_pass), per_page)]
    # 页码index
    page_num = math.ceil(passport_numbers / 16)
    pages_all = [i + 1 for i in range(page_num)]

    return split_passports, pages_all


def passmng(request):
    username = get_user(request)
    all_pass = passport.objects.all()
    if not all_pass:
        return render(request, 'pass_manage.html', {
            'username': username,
            'now_page': 0
        })
    page = 1
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))

    split_passports, pages_all = page_split(all_pass)

    return render(request, 'pass_manage.html', {
        'username': username,
        'passports': split_passports[page - 1],
        'page_num': pages_all,
        'now_page': page
    })


def redeemed(request):
    username = get_user(request)
    all_pass = passport.objects.filter(status='已使用')
    if not all_pass:
        return render(request, 'redeemed.html', {
            'username': username,
            'now_page': 0
        })
    page = 1
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
    split_passports, pages_all = page_split(all_pass)

    return render(request, 'redeemed.html', {
        'username': username,
        'passports': split_passports[page - 1],
        'page_num': pages_all,
        'now_page': page
    })


def add(request):
    username = get_user(request)
    if request.method == 'POST':
        passport1 = request.POST.get('passport', None)
        if not passport1:
            messages.error(request, '口令为空，请检查输入')
            return render(request, 'add.html', {
                'username': username,
            })
        amount = request.POST.get('amount', None)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        status = '可用'
        feedback = passport.objects.create(passport=passport1, amount=amount, date=date, status=status)
        if feedback:
            return render(request, 'add.html', {
                'username': username,
                'tips': f'口令{passport1}，金额{amount}。添加成功'
            })
    return render(request, 'add.html', {
        'username': username
    })


def edit(request):
    keyword = request.POST
    uid = keyword['id']
    passport1 = keyword['passport']
    amount = keyword['amount']
    status = keyword['status']

    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    passport_obj = passport.objects.filter(id=uid)
    feedback = passport_obj.update(passport=passport1, amount=amount, status=status, date=date)

    return redirect('/')


def delete(request):
    keyword = request.POST.get('deleteID', None)
    obj = passport.objects.filter(id=keyword)
    obj.delete()

    return redirect('/')


def mul_add(request):
    username = get_user(request)
    received_file = request.FILES.get('upload_file')
    if not received_file:
        messages.error(request, '请选择文件')
        return render(request, 'add.html', {
            'username': username,
        })
    file_name = os.path.join(settings.BASE_DIR, 'app01\\uploads', received_file.name)

    with open(file_name, 'wb') as f:
        f.write(received_file.read())
    with open(file_name, 'r', encoding='utf8') as f:
        content = f.read().splitlines()
        len_ = len(content)
    for item in content:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        try:
            passport1, amount = item.split('-')
        except:
            messages.error(request, '文件内容有误！请检查文件内容后重新上传')
            return render(request, 'add.html', {
                'username': username,
            })
        else:
            passport.objects.create(passport=passport1, amount=amount, date=date, status='可用')
    return render(request, 'add.html', {
        'username': username,
        'tips1': f'文件{received_file.name}读取成功，共{len_}行，导入成功。'
    })


def mul_del(request):
    response = request.POST
    result = response.get('selected').strip('[').strip(']').split(',')
    will_del_id = list(map(int, result))

    error_ids = ''
    flag = True
    for id_ in will_del_id:
        feedback = passport.objects.filter(id=id_).delete()
        if not feedback:
            flag = False
            error_ids += f'{id_}/'
            continue
    if flag:
        mes = json.dumps({
            'success': True,
            'error_ids': error_ids,
        })
        return JsonResponse(mes, safe=False)
    mes = {
        'success': False,
        'error_ids': error_ids,
    }
    return JsonResponse(mes, safe=False)


def user_mul_del(request):
    response = request.POST
    result = response.get('selected').strip('[').strip(']').split(',')
    will_del_id = list(map(int, result))

    error_ids = ''
    flag = True
    for id_ in will_del_id:
        feedback = bot_user.objects.filter(id=id_).delete()
        if not feedback:
            flag = False
            error_ids += f'{id_}/'
            continue
    if flag:
        mes = json.dumps({
            'success': True,
            'error_ids': error_ids,
        })
        return JsonResponse(mes, safe=False)
    mes = {
        'success': False,
        'error_ids': error_ids,
    }
    return JsonResponse(mes, safe=False)


def user_manage(request):
    username = get_user(request)
    all_user = bot_user.objects.all()

    if not all_user:
        return render(request, 'usermanage.html', {
            'username': username,
            'now_page': 0
        })
    page = 1
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
    split_passports, pages_all = page_split(all_user)
    return render(request, 'usermanage.html', {
        'username': username,
        'all_user': split_passports[page - 1],
        'page_num': pages_all,
        'now_page': page
    })


def personal_delete(request):
    user_id = request.POST.get('user_id', None)
    feedback = bot_user.objects.filter(uid=user_id).delete()
    if feedback:
        return HttpResponse(status=200)
    return HttpResponse(status=500)


def etc(request):
    """
    充值函数
    :param request:
    :return:
    """
    uid = request.POST.get('uid', None)
    balance = request.POST.get('balance', None)
    etc_num = request.POST.get('etc_num', None)

    money = int(balance) + int(etc_num)

    userObj = bot_user.objects.filter(uid=uid)
    feedback = userObj.update(balance=money)
    if not feedback:
        return HttpResponse(status=500)
    # mqtt发消息给telethon，telethon发消息给用户提醒
    mqtt_sender('notice', uid, True, etc_num, money)
    return HttpResponse(status=200)


def search_personal(request):
    uid = request.POST.get('uid', None)
    if not uid:
        return HttpResponse(status=500)
    userObj = bot_user.objects.filter(uid=uid).first()

    if not userObj:
        return HttpResponse(0)

    data = json.dumps({
        'id': userObj.id,
        'username': userObj.username,
        'uid': userObj.uid,
        'balance': userObj.balance,
        'register_date': userObj.register_date
    })
    return JsonResponse(data, safe=False)


def records(request):
    username = get_user(request)
    all_record = Records.objects.all()
    if not all_record:
        return render(request, 'records.html', {
            'username': username,
            'now_page': 0
        })
    page = 1
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
    split_passports, pages_all = page_split(all_record)
    return render(request, 'records.html', {
        'username': username,
        'all_record': split_passports[page - 1],
        'page_num': pages_all,
        'now_page': page
    })


def search_record_by_date(request):
    date = request.POST.get('date', None)
    will_ret = []
    if not date:
        return HttpResponse(status=500)
    for item in Records.objects.all():
        if date in item.exchange_time:
            # 从所有数据库中找到date这一天的记录
            data = {
                'id': item.id,
                'username': item.username,
                'uid': item.uid,
                'passport': item.passport,
                'amount': item.amount,
                'exchange_time': item.exchange_time
            }
            will_ret.append(data)

    if not len(will_ret):
        return JsonResponse([], safe=False)
    return JsonResponse(will_ret, safe=False)


def save_to_csv(request):
    # 使用js保存文件，此函数暂时停用
    # 导入pandas准备保存csv
    import pandas as pd

    info = request.POST.get('info', False)
    if not info:
        return HttpResponse('null', status=502)

    # 接收到数据后反序列化，否则为字符串格式，无法格式化
    # for item in json.loads(info):
    #     print(item)
    df = pd.DataFrame(json.loads(info))
    df.columns = ['编号', '用户名', '永久ID', '口令', '金额', '交易时间']
    df.to_csv('data.csv', index=False, encoding='gbk')
    return HttpResponse(0)


def search_record(request):
    uid = request.POST.get('uid', None)
    if not uid:
        return HttpResponse(status=500)
    feedback = []
    userObj = Records.objects.filter(uid=uid)
    if not userObj:
        return JsonResponse([], safe=False)
    for user_ in userObj:
        data = {
            'id': user_.id,
            'uid': user_.uid,
            'username': user_.username,
            'amount': user_.amount,
            'exchange_time': user_.exchange_time,
            'passport': user_.passport
        }
        feedback.append(data)
    return JsonResponse(feedback, safe=False)


def mqtt_sender(topic, sender, flag, amount, new_amount, host='localhost', port=1883):
    """
    用户账户余额变动时，向telethon传递消息，让telethon通知用户。
    :param new_amount: 变动后余额
    :param amount: 变动金额
    :param topic: 主题，要保证本程序topic与telethon的topic相同
    :param sender: 发送人永久ID，对应数据库中uid
    :param flag: True对应充值，False对应扣款
    :param host: mqtt连接地址
    :param port: mqtt端口
    :return: None
    """
    msg = json.dumps({
        'sender': sender,
        'content': f'提醒：您的帐户成功充值{amount}CNY\n最新余额：{new_amount}CNY。'
    }, ensure_ascii=False)
    if not flag:
        msg = json.dumps({
            'sender': sender,
            'content': f'提醒：您的帐户被扣除{amount}CNY\n最新余额：{new_amount}CNY。'
        }, ensure_ascii=False)

    publish.single(topic, msg, hostname=host, port=port)


def de_amount(request):
    """
    扣款函数
    :param request:
    :return:
    """
    uid = request.POST.get('uid', None)
    de_num = request.POST.get('de_num', None)
    if not (uid and de_num):
        return HttpResponse(status=500)

    user_ = bot_user.objects.filter(uid=uid).first()
    if not user_:
        return HttpResponse(status=500)

    balance = user_.balance
    new_amount = int(balance) - int(de_num)
    userObj = bot_user.objects.filter(uid=uid)
    feedback = userObj.update(balance=new_amount)
    if feedback:
        mqtt_sender('notice', uid, False, de_num, new_amount)
        return JsonResponse('ok', safe=False)
    return HttpResponse(status=500)


def etc_history(request):
    username = get_user(request)
    all_etc_history = Recharge.objects.all()
    if not all_etc_history:
        return render(request, 'etc_history.html', {
            'username': username,
            'now_page': 0
        })
    page = 1
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
    split_passports, page_all = page_split(all_etc_history)
    return render(request, 'etc_history.html', {
        'username': username,
        'all_etc_history': split_passports[page - 1],
        'page_num': page_all,
        'now_page': page
    })


def search_recharge(request):
    print(request.POST)
    uid = request.POST.get('uid', None)
    print(uid)
    if not uid:
        return HttpResponse(status=500)
    feedback = []
    userObj = Recharge.objects.filter(user=uid)
    if not userObj:
        return JsonResponse([], safe=False)
    for user_ in userObj:
        data = {
            'id': user_.id,
            'uid': user_.user,
            'trade_id': user_.trade_id,
            'amount': user_.amount,
            'actual_amount': user_.actual_amount,
            'address': user_.address,
            'time': user_.time
        }
        feedback.append(data)
    return JsonResponse(feedback, safe=False)
