from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from sqlalchemy.pool import NullPool

import setting

Base = declarative_base()

engine = create_engine(
    f'mysql+pymysql://{setting.username}:{setting.password}@localhost:{setting.port}/{setting.database}?charset=utf8mb4',
    echo=False,
    poolclass=NullPool
)

Session = sessionmaker(bind=engine)
session = scoped_session(Session)


class User(Base):
    __tablename__ = setting.user_table

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    uid = Column(String(32), primary_key=True, comment='永久id')
    balance = Column(Integer, default=0, nullable=False, comment='剩余金额')
    register_date = Column(String(64))

    def __str__(self) -> str:
        return f'object : <uid:{self.uid} amount:{self.balance}>'


class Passport(Base):
    __tablename__ = setting.table

    id = Column(Integer, primary_key=True, autoincrement=True)
    passport = Column(String(16))
    amount = Column(Integer)
    date = Column(String(64))
    status = Column(String(16))

    def __str__(self) -> str:
        return f'object : <id:{self.id} passport:{self.passport} amount:{self.amount} date:{self.date} status:{self.status}>'


class Records(Base):
    __tablename__ = setting.records_table

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(32), primary_key=True)
    passport = Column(String(32))
    amount = Column(Integer)
    exchange_time = Column(String(32))
    username = Column(String(255))


class Recharge_records(Base):
    __tablename__ = setting.recharge_records_table

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(32))
    trade_id = Column(String(32), primary_key=True)
    order_id = Column(String(64))
    amount = Column(Integer)
    actual_amount = Column(Float)
    address = Column(String(64))
    time = Column(String(64))


if __name__ == '__main__':
    # 运行此文件时创建User表
    Base.metadata.create_all(engine)
