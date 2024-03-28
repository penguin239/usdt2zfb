from django.db import models


# Create your models here.
class user(models.Model):
    account = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class passport(models.Model):
    class Meta:
        db_table = 'passport'

    passport = models.CharField(max_length=16)
    amount = models.IntegerField()
    date = models.CharField(max_length=64)
    status = models.CharField(max_length=16)


class bot_user(models.Model):
    class Meta:
        db_table = 'user'

    uid = models.CharField(max_length=32)
    username = models.CharField(max_length=255)
    balance = models.IntegerField()
    register_date = models.CharField(max_length=64)


class Records(models.Model):
    class Meta:
        db_table = 'records'

    uid = models.CharField(max_length=32)
    passport = models.CharField(max_length=32)
    amount = models.IntegerField()
    exchange_time = models.CharField(max_length=32)
    username = models.CharField(max_length=255)


class Recharge(models.Model):
    class Meta:
        db_table = 'recharge_records'

    user = models.CharField(max_length=32)
    trade_id = models.CharField(max_length=32)
    order_id = models.CharField(max_length=64)
    amount = models.IntegerField()
    actual_amount = models.FloatField()
    address = models.CharField(max_length=64)
    time = models.CharField(max_length=64)
