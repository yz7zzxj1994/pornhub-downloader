# -*- coding: utf-8 -*-
import os
import re
import time
import requests
from tqdm import tqdm
from queue import Queue
from retrying import retry
from threading import Thread
from config import random_header, download_urls, down_path


class Pornhub(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.rootpath = down_path + "/"

    @retry(stop_max_attempt_number=15)
    def parse_html(self, url):
        resp = requests.get(url, headers=random_header(), timeout=3)
        return resp.text

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

    @retry(stop_max_attempt_number=5)
    def get_filesize(self, url, headers):
        response = requests.get(url, headers=headers, stream=True, timeout=3)
        file_size = int(response.headers['content-length'])
        return file_size

    @retry(stop_max_attempt_number=9999)
    def download(self, url, filepath, headers, chunk_size, file_size, page_url):
        if os.path.exists(filepath):
            first_byte = os.path.getsize(filepath)
            print(
                "视频存在,总大小:{}M,实际大小:{}M,继续下载...".format(round(file_size / 1024 / 1024), round(first_byte / 1024 / 1024)))
        else:
            first_byte = 0
        if first_byte >= file_size:
            print("文件已经下载,跳过此链接")
            print("文件跳过,总大小:{}M,实际大小:{}M".format(round(file_size / 1024 / 1024), round(first_byte / 1024 / 1024)))
            print("原链接:", page_url)
            return file_size

        headers["Range"] = f"bytes=%s-%s" % (first_byte, file_size)

        pbar = tqdm(initial=first_byte, total=file_size, unit='B', unit_scale=True, desc=filepath)
        req = requests.get(url, headers=headers, stream=True, timeout=3)
        with(open(filepath, 'ab')) as f:
            for chunk in req.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    pbar.update(chunk_size)
        pbar.close()
        print("下载完成:", page_url)
        return file_size

    def download_from_url(self, url, filepath, headers, chunk_size, page_url):
        file_size = self.get_filesize(url, headers)
        self.download(url, filepath, headers, chunk_size, file_size, page_url)

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
        finally:
            self.queue.task_done()


if __name__ == '__main__':
    start_time = time.time()
    if not os.path.exists(down_path):
        os.makedirs(down_path)
    print("读取存放目录为:", down_path)
    try:
        queue = Queue()
        for x in range(len(download_urls)):
            pornhub = Pornhub(queue)
            pornhub.daemon = True
            pornhub.start()

        print("将要爬取的链接为:")
        for url in download_urls:
            print(url)
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
