import models
import time


class Utils:
    def current_date(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def register(self, sender, username):
        user = models.User(uid=sender, balance=0, username=username, register_date=self.current_date())
        try:
            models.session.add(user)
            models.session.commit()
        except Exception as e:
            models.session.rollback()
            raise e
        finally:
            models.session.close()

    def query_user(self, uid):
        """
        在进行查询前先将session对象中的缓存全部提交，清空缓存,
        下次查询时查询到的就是新数据，而不是先查询缓存。
        :param uid:
        :return: dict{uid, amount}
        """
        try:
            models.session.commit()
        except Exception as e:
            models.session.rollback()
            raise e
        else:
            result = models.session.query(models.User).filter(models.User.uid == uid).first()

            if not result:
                return None
            uid = result.uid
            amount = result.balance

            return {'uid': uid, 'amount': amount}
        finally:
            models.session.close()

    def etc_user(self, uid, amount):
        """
        自动充值
        :param uid: 永久id
        :param amount: 金额（CNY）
        :return: boolean
        """
        try:
            models.session.commit()
            user_obj = models.session.query(models.User).filter(models.User.uid == uid).first()
            if not user_obj:
                return False
            new_balance = user_obj.balance + amount
            user_obj.balance = new_balance
            models.session.commit()

            return True
        except Exception as error:
            models.session.rollback()
            return False
        finally:
            models.session.close()

    def update_user_balance(self, uid, amount):
        """
        更新用户余额
        :param uid: 用户永久id
        :param amount: 扣除金额
        :return: boolean
        """
        try:
            models.session.commit()
            user_obj = models.session.query(models.User).filter(models.User.uid == uid).first()
            if not user_obj:
                return False
            new_balance = user_obj.balance - amount
            user_obj.balance = new_balance
            models.session.commit()
        except Exception as error:
            # commit错误必须回滚，否则可能用户余额异常
            models.session.rollback()
            raise error
        finally:
            models.session.close()

    def send_passport(self, amount):
        """
        发送口令
        :param amount: 金额
        :return: passport
        """
        try:
            models.session.commit()
        except Exception as e:
            models.session.rollback()
            raise e
        else:
            passport = models.session.query(models.Passport).filter(
                models.and_(
                    models.Passport.amount == amount,
                    models.Passport.status == '可用'
                )
            ).first()
            if not passport:
                return None
            passport.status = '已使用'
            models.session.commit()
            return passport.passport
        finally:
            models.session.close()

    def save_recorded(self, sender, passport, amount, username):
        exchange_time = self.current_date()

        obj = models.Records(uid=sender, passport=passport, amount=amount, exchange_time=exchange_time,
                             username=username)
        try:
            models.session.add(obj)
            models.session.commit()
        except Exception as error:
            models.session.rollback()
            raise error
        finally:
            models.session.close()

    def etc_history(self, user, trade_id, order_id, amount, actual_amount, address):
        """
        充值记录保存
        :param user: 永久id
        :param trade_id: 交易单号
        :param order_id: 交易自定义id
        :param amount: 交易金额CNY
        :param actual_amount: 实际付款金额USDT
        :param address: TRC20网络地址
        :return:
        """
        info = models.Recharge_records(
            user=user,
            trade_id=trade_id,
            order_id=order_id,
            amount=amount,
            actual_amount=actual_amount,
            address=address,
            time=self.current_date()
        )

        try:
            models.session.add(info)
            models.session.commit()
        except Exception as e:
            models.session.rollback()
            raise e
        finally:
            models.session.close()

    def all_user(self):
        return [user.uid for user in models.session.query(models.User).all()]


if __name__ == '__main__':
    utils = Utils()
    utils.all_user()
