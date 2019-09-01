# -*- coding:utf-8 -*-

import csv
import json
import os
import re
import requests

from multiprocessing import Pool
from requests.exceptions import RequestException


def get_page(url):
    """
    获取页面内容

    参数
    url:请求URL地址
    """
    # 设置HTTP请求头部
    headers = {
        'Host': 'maoyan.com',
        'User-Agent': 'User-Agent  Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None


def parse_page(html):
    """
    解析页面内容

    参数
    html：页面内容
    """
    pattern = re.compile('<dd>.*?board-index.*?>(\d*)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">'
                         + '(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i></p>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3],
            'time': item[4],
            'score': item[5] + item[6]
        }


def save_text_file(content, path):
    """
    保存文本文件

    参数
    content：待保存内容
    path：文本文件保存路径
    """
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + "\n")
        f.close()


def save_image_file(url, path):
    """
    保存图片文件

    参数
    url：图片url地址
    path：图片文件保存路径
    """
    image_file = requests.get(url)
    try:
        if image_file.status_code == 200:
            with open(path, 'ab+') as f:
                f.write(image_file.content)
                f.close()
    except RequestException:
        return None


def save_csv_file(content, path):
    """
    保存csv文件

    参数
    content：保存内容
    path：保存csv文件路径
    """

    with open(path,'a',newline='',encoding='utf-8') as f:
        fieldnames = ['index', 'image', 'title', 'actor', 'time', 'score']
        f_csv = csv.DictWriter(f,fieldnames=fieldnames)
        f_csv.writerow(content)


def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_page(url)
    parse_page(html)
    if not os.path.exists('images'):
        os.mkdir('images')
    for item in parse_page(html):
        print(item)
        save_text_file(item,'movie.txt')
        save_csv_file(item,'movie.csv')
        save_image_file(item['image'], 'images/' + '%03d-' % int(item['index']) + item['title'] + '.jpg')


if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
    #main(1)
