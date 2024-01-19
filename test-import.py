# encoding: UTF-8
import time
import datetime
import sqlite3
import mysql.connector
# 导入框架提供的函数，我们这里先引入订阅股票回调函数，订阅股票，下单
from strategy_platform.api import (sub_realmd, register_realmd_cb)
from strategy_platform.api import (sub_order, register_order_cb)
from strategy_platform.api import (submit_order, query_position)
from strategy_platform.api import (add_argument,query_order)
from strategy_platform.api import (cancel_timer)
from strategy_platform.api import (minute_timer)
from strategy_platform.api import (hour_timer)
from strategy_platform.api import (at_hour_timer)
from strategy_platform.api import (at_day_timer)
import sys
import pandas as pd
import threading
pending_order_dict = {}
order_dict_lock = threading.Lock()
dpFile = "D:/tianlinyu/cat_stocks.db"
# 标的
universe = "600030.SH"
# 买入数量
qty = 1000
# 判断价格
price = 19.5
# 账户类型和账户名称， 在策略启动时输入
acct_type = "S0"
acct = "8009131865"
start_time = "09:30:00"
end_time = "20:55:00"

# 启动时配置账号类型和账号等信息
add_argument("acct_type", str, 0, acct_type)
add_argument("acct", str, 0, acct)
add_argument("symbol", str, 0, universe)
add_argument("qty", int, 0, qty)
add_argument("price", float, 2, price)
add_argument("start_time", str, 0, start_time)
add_argument("end_time", str, 2, end_time)

def on_init(argument_dict):
    # 注册订阅标的的回调函数
    register_realmd_cb(on_realmd, None)
    # 订阅标的
    sub_realmd(universe)
    register_order_cb(on_order_update, None)
    sub_order(acct_type, acct)
    at_day_timer("10:00", at_day_handler)
    # query_position(acct_type, acct)
    #aa(acct_type, acct)
    #insert_data_into_table(order_obj,ultimate_time)
    insert_data_into_table(acct_type, acct, dpFile)
#登记订单信息
def add_order_info(order_no,order_obj):
    order_dict_lock.aquire()
    pending_order_dict[order_no]=order_obj
    order_dict_lock.release()

#根据时间字符串获取时间戳
def get_time_stamp(time_str):
    import time
    local_time=time.localtime(int(time.time()))
    day=time.strftime("%Y-%m-%d",local_time)
    full_date_str=day+""+time_str
    time_array=time.strftime(full_date_str,"%Y-%m-%d %H:%M:%S")
    time_stamp=time.mktime(time_array)
    return time_stamp

def config_init_argument(argument_dict):
    for k, v in argument_dict.items():
        log.info("argument: [key: {}, value: {}]".format(k, v))
        if k == "acct":
            global acct
            acct = v
        elif k == "acct_type":
            global acct_type
            acct_type = v
        elif k == "symbol":
            global universe
            universe = v
        elif k == "price":
            global price
            price = v
        elif k == "qty":
            global qty
            qty = v
        elif k == "start_time":
            global start_time
            start_time = v
        elif k == "end_time":
            global end_time
            end_time = v


xzhs = 300

def on_realmd(realmk_obj, cb_arg):
    global xzhs
    if xzhs > 0:
        pce = realmk_obj.preClosePrice
        pce1 = pce * 1.01
        c1 = pce * (1 - 0.005)
        c2 = pce * (1 - 0.01)
        c3 = pce * (1 - 0.015)
        submit_order(acct_type, acct, "600030.SH", 1, 0, c1, 100, None, on_order, None)
        submit_order(acct_type, acct, "600030.SH", 1, 0, c2, 100, None, on_order, None)
        submit_order(acct_type, acct, "600030.SH", 1, 0, c3, 100, None, on_order, None)
        submit_order(acct_type, acct, "600030.SH", 2, 0, pce1,300, None, on_order, None)
        xzhs = xzhs - 300

def on_order(result, cb_arg):
    if result.rc != "0":
        log.info("order failed,reason:{}".format(result.resp))
        return
    log.info("order succeed,order no :{}".format(result.resp))


#  下单的回调函数，函数名不限，下单操作时需要传入该函数
def at_day_handler(*args, **kwargs):
    log.info("this is at day timer")


def aa(acct_type, acct):
    try:
        pos_list = query_position(acct_type, acct)
        log.info("begin go to print position information")
        for i in range(len(pos_list)):
            pos_obj = pos_list[i]
            log.info("position: [symbol:{}, currentQty:{}, direction:{}, longFrozen:{}]".format(pos_obj.symbol,
                                                                                                pos_obj.currentQty,
                                                                                                pos_obj.direction,
                                                                                                pos_obj.longFrozen))
        log.info("begin go to print position information")
    except Exception as e:
        log.exception(e)

# 订单状态变化回调函数，打印委托时间，成交数量等信息
def on_order_update(order_obj, cb_arg):
    add_order_info(order_obj.orderNo, order_obj)
    log.info(
        "order update: [symbol:{}, orderNo:{}, price:{}, qty:{}, stauts:{}, filledQty:{}, avgPrice:{}, cancelQty:{}, orderTime:{}, orderDate:{}]".format(
            order_obj.symbol, order_obj.orderNo, order_obj.price, order_obj.qty, order_obj.status, order_obj.filledQty,
            order_obj.avgPrice, order_obj.cancelQty, order_obj.orderTime, order_obj.orderDate))
    ysea=order_obj.filledQty
    return ysea
""""
def insert_data_into_table(order_obj,ultimate_time):
    dpConn = sqlite3.connect(dpFile)
    c=dpConn.cursor()
    c.execute("INSERT INTO stock_vol (datetime1, cjl) VALUES (?, ?)", (timestamp_date, jj))
    log.info(
        "order update: [symbol:{}, orderNo:{}, price:{}, qty:{}, stauts:{}, filledQty:{}, avgPrice:{}, cancelQty:{}, orderTime:{}, orderDate:{}]".format(
            order_obj.symbol, order_obj.orderNo, order_obj.price, order_obj.qty, order_obj.status, order_obj.filledQty,
            order_obj.avgPrice, order_obj.cancelQty, order_obj.orderTime, order_obj.orderDate))
"""
sum=0
def insert_data_into_table(acct_type, acct, dpFile):
    global sum
    uyegewhx=query_order(acct_type, acct)
    for i in range(len(uyegewhx)):
         uyegewhx_obj= uyegewhx[i]
         fqty=uyegewhx_obj.filledQty
         if uyegewhx_obj.side=="1":
             sum += fqty
         else:
             sum=sum-fqty
    print(fqty)
    print(sum)
    obj_today = datetime.date.today()
    print(obj_today)
    dpConn = sqlite3.connect(dpFile)
    c = dpConn.cursor()
    c.execute("INSERT INTO stock_vol (datetime1,cjl) VALUES (?,?)",(obj_today,sum))
    dpConn.commit()
    c.close()


