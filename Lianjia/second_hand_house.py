# -*- coding:utf-8 -*-

import csv
import json
import re
import requests
import pymongo
from multiprocessing import Pool
from lxml import etree
from requests.exceptions import RequestException


def get_page(url):
    """
    获取页面内容
    参数
        url: http请求url
    返回值
        返回页面内容
    """

    # 设置HTTP请求头部
    headers = {
        'Host': 'hz.lianjia.com',
        'User-Agent': 'User-Agent  Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN'
    }
    try:
        response = requests.get(url, headers=headers)
        # 判断HTTP response状态码，若状态码是200，返回页面内容；反之，返回None
        if response.status_code == 200:
            return response.text
        else:
            return None
    # 请求发生异常时返回None
    except RequestException:
        return None


def parse_page(html):
    """
    解析页面内容

    参数
        html：HTTP页面内容

    返回值
        HTTP页面处理结果
    """
    for item in etree.HTML(html).xpath('//div[@class="info clear"]'):
        # 链接
        link = item.xpath('string(.//div[@class="title"]/a/@href)')
        # 编号
        index_id = re.search(r'\d+',link).group()
        # 标题
        title = item.xpath('string(.//div[@class="title"]/a/text())')
        # 小区
        community = item.xpath('string(.//div[@class="address"]//a/text())')
        house_text = item.xpath('string(.//div[@class="houseInfo"]/text())').split(' | ')
        # 户型
        layout = house_text[1]
        # 面积
        try:
            area_obj = re.match(r'\d+\.\d+',house_text[2])
            area = area_obj.group()
        except Exception:
            area = None
        # 朝向
        facing = house_text[3]

        # 装修
        renovation = house_text[4]
        position =item.xpath('string(.//div[@class="positionInfo"]/text())')
        try:
            ind = position.index("年")
            # 楼层
            floor = position[:ind - 4]
            # 建筑时间
            year = position[ind-4:ind]
        except Exception:
            floor = None
            year = None
        # 小区
        district = item.xpath('string(.//div[@class="flood"]//a/text())')
        # 关注人数
        follow_info = item.xpath('string(.//div[@class="followInfo"]/text())')
        follow_num = re.match(r'\d+',follow_info.split("/")[0]).group()
        # 总价
        total_price = item.xpath('string(.//div[@class="totalPrice"]/span/text())')
        # 单价
        unit_price_str = item.xpath('string(.//div[@class="unitPrice"]/span/text())')
        unit_price = re.search(r'\d+',unit_price_str).group()
        yield {
            'index_id':index_id,
            'link':link,
            'title':title,
            'community':community,
            'layout':layout,
            'area':area,
            'facing':facing,
            'renovation':renovation,
            'floor':floor,
            'year':year,
            'district':district,
            'follow_num':follow_num,
            'total_price':total_price,
            'unit_price':unit_price
        }


def save_csv_file(content, path):
    """
    保存csv文件
    参数
        content：保存内容
        path：保存csv文件路径
    返回值
        None
    """

    with open(path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['index_id', 'link', 'title', 'community', 'layout', 'area','facing','renovation','floor','year','district','follow_num','total_price','unit_price']
        f_csv = csv.DictWriter(f,fieldnames=fieldnames)
        f_csv.writerow(content)


def save_text_file(content,path):
    """
    保存文本文件
    参数
        content：文本内容
        path：文件路径
    返回值
        None
    """
    with open(path, 'a', encoding='utf-8') as f:
      f.write(json.dumps(content, ensure_ascii=False) + "\n")
      f.close()


def save_mongodb(item):
    """
    保存到mongodb

    """
    # 连接mongodb
    client = pymongo.MongoClient('mongodb://192.168.1.11:27017')
    db = client['lianjia']
    colc = db['second_hand_house']
    colc.insert_one(item)
    client.close()

def main(page):
    url = 'https://hz.lianjia.com/ershoufang/pg' + str(page)
    html = get_page(url)
    for item in parse_page(html):
        save_text_file(item,'second_hand_house.txt')
        save_csv_file(item,'second_hand_house.csv')
        save_mongodb(item)


if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
