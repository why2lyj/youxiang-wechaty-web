'''
并没有遵守什么编码规范
'''

import random
import requests
import hashlib
import json
import urllib
import urllib.parse
import urllib.request
import datetime
import asyncio
import logging
import os
import time
from typing import Optional, Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from wechaty_puppet import FileBox  # type: ignore
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(filename)s <%(funcName)s> %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)

JD_API_ROOT = 'https://router.jd.com/api'

class JdApiClient(object):
    '''

    '''
    def __init__(self, app_key, secret_key):
        self.app_key = app_key
        self.secret_key = secret_key

    def get_sign(self, params):
        params_list = sorted(list(params.items()), key=lambda x: x[0])
        params_bytes = (self.secret_key + ''.join("%s%s" % (k, v) for k, v in params_list) + self.secret_key).encode(
            'utf-8')
        sign = hashlib.md5(params_bytes).hexdigest().upper()
        return sign

    def call(self, method, param_json, **kwargs):
        params = {
            "v": "1.0",
            "method": method,
            "app_key": self.app_key,
            "timestamp": (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "sign_method": "md5"
        }
        if isinstance(param_json, (dict, list)):
            params["param_json"] = json.dumps(param_json)
        else:
            params["param_json"] = param_json
        params['sign'] = self.get_sign(params)
        resp = requests.get(JD_API_ROOT, params=params, **kwargs)
        return resp

class Suo_mi(object):
    '''
    由于京东获取短址的api门槛比较高，而获得的优惠链接非常长，最终选择 suo mi 进行短址
    其中 app_key 是 suo mi  的 token
    需要注册 http://suo.im/ ， 而后获得 token
    '''

    def __init__(self, app_key):
        self.app_key = app_key
        # 我们默认短址一年后过期
        self.expireDate = (datetime.date.today() + datetime.timedelta(days=365)).strftime('%Y-%m-%d')

    def get_short_url(self, url: str)  -> str:
        '''
        :param url: 长址
        :return: 返回suo.im的短址
        '''
        # 取值地址，接口地址
        api_url = f'''http://suo.im/api.htm?format=json&url={urllib.parse.quote(url)}&key={self.app_key}&expireDate={self.expireDate}'''
        request = urllib.request.Request(url=api_url)
        response = urllib.request.urlopen(request)
        data = response.read()
        short_url = json.loads(data)['url']
        return short_url


app_key = "" # 京东联盟获取
secret_key="" # 京东联盟获取
site_id = "" # 京东网站管理的id，需要有备案的网站或app才可获得
suo_mi_token = "" # suo mi 的 token

def jingfen_query():
    '''
    https://union.jd.com/openplatform/api/10421
    :return:
    '''

    info = []
    client = JdApiClient(app_key=app_key, secret_key=secret_key)

    page_no = str(random.randint(1, 25))
    page_size = str(random.randint(3, 5))

    resp = client.call("jd.union.open.goods.jingfen.query",
                       {"goodsReq":
                            {
                             "pageSize": page_size,
                             "pageIndex": page_no,
                             "eliteId": "10"  # 9.9元专区，详见jd api
                             }})

    for data in json.loads(resp.json()['jd_union_open_goods_jingfen_query_response']['result'])['data']:
        sku_name = data['skuName']   ## 商品全名
        skuId = data['skuId']     ## 商品 sku
        material_url = f'''http://{(data['materialUrl'])}''' ## 商品url
        couponInfos = data['couponInfo'] ## 优惠券列表
        # 查找最优优惠券
        coupon_link = ""
        discount = 0
        share_text = ""
        lowest_price_type = data['priceInfo']['lowestPriceType']  ## 什么类型

        if 'isBest' in data: # 如果有券
            for couponInfo in couponInfos['couponList']:
                if int(couponInfo['isBest']) == 1:
                    discount = couponInfo['discount']  ## 优惠券额度
                    coupon_link = couponInfo['link']  ## 优惠券领取地址
            if lowest_price_type == "3":  # 秒杀
                price = data['seckillInfo']['seckillOriPrice'] # 原价
                lowest_price = data['priceInfo']['lowestCouponPrice'] # 秒杀价
                duanzhi = tb_share_text(material_url, coupon_link)
                share_text = f'''【秒杀】{sku_name}\n——————————\n  【原价】¥{price}\n 【券后秒杀价】¥{lowest_price}\n抢购地址：{duanzhi}'''
            elif lowest_price_type == "2": # 拼购
                price = data['priceInfo']['price']  # 原价
                lowest_price = data['priceInfo']['lowestCouponPrice']  # 用券拼购
                duanzhi = tb_share_text(material_url, coupon_link)
                share_text = f'''【拼购】{sku_name}\n——————————\n  【原价】¥{price}\n 【券后拼购价】¥{lowest_price}\n抢购地址：{duanzhi}'''
            else:
                price = data['priceInfo']['price'] ## 商品价格
                lowest_price = data['priceInfo']['lowestCouponPrice']
                duanzhi = tb_share_text(material_url, coupon_link)
                share_text = f'''【京东】{sku_name}\n——————————\n  【爆款价】¥{price}\n 【用卷价】¥{lowest_price}\n抢购地址：{duanzhi}'''

        else: ## 如果没有券
            if lowest_price_type == "3":  # 秒杀
                price = data['seckillInfo']['seckillOriPrice']  # 原价
                lowest_price = data['seckillInfo']['seckillPrice']  # 秒杀价
                duanzhi = tb_share_text(material_url, coupon_link)
                share_text = f'''【秒杀】{sku_name}\n——————————\n  【原价】¥{price}\n 【秒杀价】¥{lowest_price}\n抢购地址：{duanzhi}'''

            elif lowest_price_type == "2":  # 拼购
                price = data['priceInfo']['price']  # 原价
                lowest_price = data['priceInfo']['lowestPrice']  # 用券拼购
                duanzhi = tb_share_text(material_url, coupon_link)
                share_text = f'''【拼购】{sku_name}\n——————————\n  【原价】¥{price}\n 【拼购价】¥{lowest_price}\n抢购地址：{duanzhi}'''
            else:
                lowest_price = data['priceInfo']['price']
                # 得到短址
                duanzhi = tb_share_text(material_url, coupon_link)
                share_text = f'''【京东】{sku_name}\n——————————\n 【爆款价】¥{lowest_price}\n抢购地址：{duanzhi}'''

        ## 获取 images
        image_list = []
        images_count = 0
        for image in data['imageInfo']['imageList']:
            images_count += 1
            if images_count > 3:
                pass
            else:
                image_url = image['url']
                image_list.append(image_url)
        info.append([share_text, image_list])
    return info

def tb_share_text(material_url, couponUrl):
    '''
    :param material_url: 商品物料
    :param couponUrl:  优惠券url
    :return:
    '''
    client = JdApiClient(app_key=app_key, secret_key=secret_key)
    if couponUrl == "":
        resp = client.call("jd.union.open.promotion.common.get",
                           {"promotionCodeReq":
                                {
                                 "siteId": site_id,
                                 "materialId": material_url
                                 }})
    else:
        resp = client.call("jd.union.open.promotion.common.get",
                           {"promotionCodeReq":
                                {
                                 "siteId": site_id,
                                 "materialId": material_url,
                                 "couponUrl": couponUrl
                                 }})
    x = json.loads(resp.json()['jd_union_open_promotion_common_get_response']['result'])['data']['clickURL']

    # 直接返回短址
    url = x
    c = Suo_mi(app_key=suo_mi_token).get_short_url(url)
    return c

async def message(msg: Message):
    """back on message"""
    from_contact = msg.talker()
    text = msg.text()
    room = msg.room()
    if text == '#ding':
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        await conversation.say('dong')

async def dingdong():
    """doc"""
    # pylint: disable=W0603
    global bot
    bot = Wechaty().on('message', message)
    await bot.start()

async def jingdongfenxiang():
	# 由于 python 的 wechaty-puppet（0.0.8）并没有实现 find 方法，
	# 所以这里只能从 _pool 中获取群聊id
    room = bot.Room.load("19679596974@chatroom")
    # room = bot.Room.load(bot.Room.find("京东内部优惠券-爆品区①"))
    await room.ready()
    conversation: Union[Room, Contact] = room
    await conversation.ready()
    infos = jingfen_query()
    for info in infos:
        for image in info[1]:
            file_box = FileBox.from_url(f'''{image}''', name='jing-dong.jpg') # 发送图片
            time.sleep(random.randint(5,10))
            await conversation.say(file_box)
        time.sleep(random.randint(5,10))
        await conversation.say(info[0]) # 发送优惠信息

async def jd_job():
    scheduler = AsyncIOScheduler()
	# 每小时55分45秒时任务启动，抖动时间30秒
    scheduler.add_job(jingdongfenxiang, trigger='cron', minute='55', second=45, jitter=30, id='fenxiang')
    scheduler.start()

async def main():
    ding_dong_task = asyncio.create_task(dingdong())   #创建任务，保留原有ding-dong任务
    jd_task = asyncio.create_task(jd_job())
    await asyncio.gather(ding_dong_task, jd_task) #并发运行任务

os.environ['WECHATY_PUPPET_HOSTIE_TOKEN'] = 'you donut token'
bot: Optional[Wechaty] = None

asyncio.run(main())
