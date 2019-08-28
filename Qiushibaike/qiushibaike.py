# -*- coding:utf-8 -*-

import json
import re
from urllib.request import urlopen, Request
from multiprocessing import Pool


def get_page(url):
    """
    获取页面内容

    参数
    url：请求页面URL

    返回值
    页面内容
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    # 构造请求request
    request = Request(url, headers=headers)

    # 获取相应内容
    response = urlopen(request)
    if response.code == 200:
        return response.read().decode('utf-8')


def parse_page(html):
    """
    解析页面内容

    参数
    html：页面内容

    返回值
    返回目标数据：昵称，内容，点赞数，评论数
    """
    pattern = re.compile(
        '<div.*?<h2>(.*?)</h2>.*?<div class="content".*?<span>(.*?)</span>.*?<span.*?<i.*?>(.*?)</i>.*?<i.*?>(.*?)</i>',
        re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            '昵称': item[0].strip(),
            '内容': item[1].strip().replace('<br/>', ''),
            '点赞数': item[2],
            '评论数': item[3],
        }


def save_to_file(content, filepath):
    """
    保存到本地文件

    参数
    content：待保存内容
    filepath：文件路径

    返回值
    保存成功返回True
    """
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + "\n")
        f.close()
    return True


def main(offset):
    url = 'https://www.qiushibaike.com/text/page/' + str(offset)
    path = 'qiushibaike.txt'
    html = get_page(url)
    for item in parse_page(html):
        print(item)
        save_to_file(item, path)


if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i for i in range(10)])
