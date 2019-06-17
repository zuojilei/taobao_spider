import requests
import threading
import multiprocessing
import random
# from config import *
import json
import pymongo
from urllib.parse import quote
from fake_useragent import UserAgent

agent_list = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",]

# client = pymongo.MongoClient(MONGO_URL, connect=False)


class TaoBao:
    def __init__(self):
        global agent_list
        self.ua = random.choice(agent_list)
        self.url_temp = 'https://s.taobao.com/search?data-key=s&data-value={}&ajax=true&ie=utf8&spm=aa21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&q='
        self.headers = {"Origin": "https://login.taobao.com",
                        "Upgrade-Insecure-Requests": "1",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Referer": "https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "User-Agent": self.ua }
        self.cookies = {}  # 申明一个用于存储手动cookies的字典
        self.res_cookies_txt = ""  # 申明刚开始浏览器返回的cookies为空字符串
        self.keyword = "美食"

    # 读取mycookies.txt中的cookies
    def read_cookies(self):
        with open("mycookies.txt", 'r', encoding='utf-8') as f:
            cookies_txt = f.read().strip(';')  # 读取文本内容
            # 由于requests只保持 cookiejar 类型的cookie，而我们手动复制的cookie是字符串需先将其转为dict类型后利用requests.utils.cookiejar_from_dict转为cookiejar 类型
            for cookie in cookies_txt.split(';'):
                name, value = cookie.strip().split('=', 1)  # 用=号分割，分割1次
                self.cookies[name] = value  # 为字典cookies添加内容
        # 将字典转为CookieJar：
        cookiesJar = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)
        return cookiesJar

    # 保存模拟登陆成功后从服务器返回的cookies，通过对比可以发现是有所不同的
    def set_cookies(self, cookies):
        # 将CookieJar转为字典：
        res_cookies_dic = requests.utils.dict_from_cookiejar(cookies)
        # 将新的cookies信息更新到手动cookies字典
        for i in res_cookies_dic.keys():
            self.cookies[i] = res_cookies_dic[i]

        # 将更新后的cookies写入到文本
        for k in self.cookies.keys():
            self.res_cookies_txt += k + "=" + self.cookies[k] + ";"
        # 将服务器返回的cookies写入到mycookies.txt中实现更新
        with open('mycookies.txt', "w", encoding="utf-8") as f:
            f.write(self.res_cookies_txt)

    def parse_url(self, url):
        # 开启一个session会话
        session = requests.session()
        # 设置请求头信息
        session.headers = self.headers
        # 将cookiesJar赋值给会话
        session.cookies = self.read_cookies()
        # 向目标网站发起请求
        response = session.get(url)
        self.set_cookies(response.cookies)
        return response.content.decode()

    def get_goods_list(self, json_str):
        dirt_ret = json.loads(json_str)
        goods_list = dirt_ret["mods"]["itemlist"]["data"]["auctions"]
        if goods_list:
            for goods in goods_list:
                goods_content = {}
                goods_content['title'] = goods['raw_title']  # 名称
                goods_content['url'] = goods['detail_url']  # 商品详情页链接
                goods_content['price'] = goods['view_price']  # 价格
                goods_content['address'] = goods['item_loc']  # 发货地址
                goods_content['sales'] = goods['view_sales']  # 已付款人数
                goods_content['shops'] = goods['nick']  # 店名
                goods_content['comment_count'] = goods['comment_count']  # 评论数
                print(goods_content)
                # self.save_to_mongo(goods_content)

    # def save_to_mongo(self, goods_content):
    #     db = client[taget_DB]
    #     if db[taget_TABLE].update_one(goods_content, {'$set': goods_content}, upsert=True):
    #         print('Successfully Saved to Mongo', goods_content)

    def run(self, page_num):
        page_size = page_num * 44
        url = self.url_temp.format(page_size) + quote(self.keyword)
        json_str = self.parse_url(url)
        self.get_goods_list(json_str)


if __name__ == '__main__':
    page_num = 2  # 总页码数
    taobao = TaoBao()
    pool = multiprocessing.Pool()
    # 多进程
    thread = threading.Thread(target=pool.map, args=(taobao.run, [i for i in range(page_num)]))
    thread.start()
    thread.join()

