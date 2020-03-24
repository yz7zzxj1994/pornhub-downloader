# -*- coding: utf-8 -*-
import os
import random
import re
import time
import requests
from retrying import retry


class Pornhub():
    def __init__(self, url):
        self.url = url
        self.rootpath = down_path + "/"

    @retry(stop_max_attempt_number=15)
    def parse_html(self, url):
        resp = requests.get(url, headers=random_header(), timeout=3)
        return resp.text

    def save_mp4(self, item):
        if item["quality_720p"]:
            url = item["quality_720p"]
        elif item["quality_480p"]:
            url = item["quality_480p"]
        else:
            return 0

        file_path = self.rootpath + re.sub(r"[/\\:*?\"<>|]", "_", item["video_title"]) + ".mp4"
        self.download_from_url(url, file_path, random_header())
        return 1

    @retry(stop_max_attempt_number=9999)
    def download_from_url(self, url, filepath, headers):
        with open(filepath,'wb') as f:
            f.write(requests.get(url,headers).content)

    def run(self):
        try:
            url = self.url
            html_str = self.parse_html(url)
            item = {}
            item["video_title"] = re.findall('"video_title":"(.*?)",', html_str)[0].encode('utf-8').decode(
                'unicode_escape')
            item["quality_720p"] = re.findall('"quality_720p":"(.*?)",', html_str)
            if item['quality_720p']:
                item["quality_720p"] = item["quality_720p"][0].replace('\\', '')
            item["quality_480p"] = re.findall('"quality_480p":"(.*?)",', html_str)
            if item['quality_480p']:
                item["quality_480p"] = item["quality_480p"][0].replace('\\', '')

            result = self.save_mp4(item)
            if result == 0:
                print("此视屏清晰度过低,忽略下载:", url)
        except Exception as e:
            print(e)


download_urls = [
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e02113017593",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5ca9824ad0f90",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e62cb456ca62"
]

down_path = "D:/ph/other"


# 随机请求头
# 使用前,填上你的账号cookie
def random_header():
    headers_list = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Mozilla/5.0 (MeeGo; NokiaN9) AppleWebKit/534.13 (KHTML, like Gecko) NokiaBrowser/8.5.0 Mobile Safari/534.13',
    ]
    return {
        'cookie': "ua=237aa6249591b6a7ad6962bc73492c77; platform_cookie_reset=pc; platform=pc; bs=kkfbi66h9zevjeq5bt27j0rvno182xdl; ss=205462885846193616; RNLBSERVERID=ded6699",
        'user-agent': random.choice(headers_list)
    }


if __name__ == '__main__':
    start_time = time.time()
    if not os.path.exists(down_path):
        os.makedirs(down_path)
    print("读取存放目录为:", down_path)
    try:
        print("将要爬取的链接为:")
        for url in download_urls:
            print(url)
        for url in download_urls:
            p = Pornhub(url)
            p.run()

    except Exception as e:
        print("\n*" * 20)
        print("程序运行错误:", e)
        print("*" * 20, "\n")
    finally:
        end_time = time.time()
        d_time = end_time - start_time
        print("程序运行时间：%.8s s" % round(d_time, 2))
