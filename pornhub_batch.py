# -*- coding: utf-8 -*-
import re
import os
import time
import random
import requests
from lxml import etree
from tqdm import tqdm
from queue import Queue
from retrying import retry
from threading import Thread
from config import random_header, batch_url, batch_down_path


class Pornhub(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        # 下载路径
        self.rootpath = batch_down_path + "/"

    # 解析视频页面
    @retry(stop_max_attempt_number=15)
    def parse_html(self, url):
        resp = requests.get(url, headers=random_header(), timeout=3)
        return resp.text

    # 保存视频
    def save_mp4(self, item, page_url):
        if item["quality_1080p"]:
            url = item["quality_1080p"]
        elif item["quality_720p"]:
            url = item["quality_720p"]
        else:
            return 0

        file_path = self.rootpath + re.sub(r"[/\\:*?\"<>|]", "_", item["video_title"]) + ".mp4"
        self.download_from_url(url, file_path, random_header(), 1048576, page_url)
        return 1

    # 获取请求文件的大小
    @retry(stop_max_attempt_number=5)
    def get_filesize(self, url, headers):
        # 发起网络请求
        response = requests.get(url, headers=headers, stream=True, timeout=3)
        # 获取返回的文件的大小
        file_size = int(response.headers['content-length'])
        return file_size

    # 进度条模式 断点续传 下载视频
    @retry(stop_max_attempt_number=9999)
    def download(self, url, filepath, headers, chunk_size, file_size, page_url):
        # 判断当前目录中是否有该文件，如果有获取文件的大小，从而实现断点续传
        if os.path.exists(filepath):
            first_byte = os.path.getsize(filepath)
            print(
                "视频存在,总大小:{}M,实际大小:{}M,继续下载...".format(round(file_size / 1024 / 1024), round(first_byte / 1024 / 1024)))
        else:
            first_byte = 0
        # 如果文件大小已经超过了服务器返回的文件的大小，返回文件长度
        if first_byte >= file_size:
            print("文件已经下载,跳过此链接")
            print("文件跳过,总大小:{}M,实际大小:{}M".format(round(file_size / 1024 / 1024), round(first_byte / 1024 / 1024)))
            print("原链接:", page_url)
            return file_size

        # 设置断点续传的位置
        headers["Range"] = f"bytes=%s-%s" % (first_byte, file_size)

        # desc :进度条的前缀
        # unit 定义每个迭代的单元。默认为"it"，即每个迭代，在下载或解压时，设为"B"，代表每个“块”。
        # unit_scale 默认为False，如果设置为1或者True，会自动根据国际单位制进行转换 (kilo, mega, etc.) 。比如，在下载进度条的例子中，如果为False，数据大小是按照字节显示，设为True之后转换为Kb、Mb。
        # total：总的迭代次数，不设置则只显示统计信息，没有图形化的进度条。设置为len(iterable)，会显示黑色方块的图形化进度条。
        pbar = tqdm(initial=first_byte, total=file_size, unit='B', unit_scale=True, desc=filepath)
        # 发送网络请求
        req = requests.get(url, headers=headers, stream=True, timeout=3)
        # 这里的二进制需要采用追加的方式写入文件，不然无法实现断点续传
        with(open(filepath, 'ab')) as f:
            for chunk in req.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    pbar.update(chunk_size)
        pbar.close()
        print("下载完成:", page_url)
        return file_size

    #  # 拆分2次请求
    def download_from_url(self, url, filepath, headers, chunk_size, page_url):
        file_size = self.get_filesize(url, headers)
        self.download(url, filepath, headers, chunk_size, file_size, page_url)

    # 主方法
    def run(self):
        try:
            url = self.queue.get()
            html_str = self.parse_html(url)
            item = {}
            item["video_title"] = re.findall('"video_title":"(.*?)",', html_str)[0].encode('utf-8').decode(
                'unicode_escape')
            item["quality_1080p"] = re.findall('"quality_1080p":"(.*?)",', html_str)
            if item['quality_1080p']:
                item["quality_1080p"] = item["quality_1080p"][0].replace('\\', '')

            item["quality_720p"] = re.findall('"quality_720p":"(.*?)",', html_str)
            if item['quality_720p']:
                item["quality_720p"] = item["quality_720p"][0].replace('\\', '')

            result = self.save_mp4(item, url)
            if result == 0:
                print("此视屏清晰度过低,忽略下载:", url)
        except Exception as e:
            print(e)
        finally:  # 释放队列
            self.queue.task_done()


video_list = []


# 解析视频页面链接
@retry(stop_max_attempt_number=9999)
def parse_batch_urls(url):
    resp = requests.get(url, headers=random_header())
    html = etree.HTML(resp.text)
    links = html.xpath(".//ul[contains(@class,'videoList')]/li//a/@href")
    for link in links:
        video_list.append("https://cn.pornhub.com" + link)
        print("解析出链接: https://cn.pornhub.com" + link)
    # 下一页
    nextPage = html.xpath(".//div[contains(@class,'page_next')]/a/@href")
    if nextPage and nextPage[0] != '':
        print("下一页:", "https://cn.pornhub.com" + nextPage[0])
        parse_batch_urls("https://cn.pornhub.com" + nextPage[0])
    else:
        print("没有下一页,解析页面链接完成")


if __name__ == '__main__':
    start_time = time.time()
    if not os.path.exists(batch_down_path):
        os.makedirs(batch_down_path)
    print("读取存放目录为:", batch_down_path)

    url_list = batch_url

    try:
        queue = Queue()
        for x in range(len(url_list)):
            pornhub = Pornhub(queue)
            pornhub.daemon = True
            pornhub.start()

        for url in url_list:
            queue.put(url)

        queue.join()

    except Exception as e:
        print("\n*" * 20)
        print("程序运行错误:", e)
        print("*" * 20, "\n")
    finally:
        end_time = time.time()
        d_time = end_time - start_time
        print("程序运行时间：%.8s s" % round(d_time, 2))
        time.sleep(4)
