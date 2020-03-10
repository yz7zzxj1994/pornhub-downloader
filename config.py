# -*- coding: utf-8 -*-
import random

# 下载的链接
download_urls = [
    # 三姉妹とのドキドキ共同生活
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e34f2e965204",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e26a9c4dc4d2",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e26b33e5fc1b",

    # ~星にお願い
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e34f72674af7",

    # 小胖丁
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e02113017593",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5ca9824ad0f90",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5d55ac31a7682",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e02113017593",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e31a3081a442",

    # FC2PPV-778927 ことり19歳Icup
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e492f9126b4e",
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e492f9149423",

    # 小嶋ひより
    "https://cn.pornhub.com/view_video.php?viewkey=ph5de6570431fd0",
    # FC2PPV-1261799
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e5271e68415b",
    # FC2PPV 1288053
    "https://cn.pornhub.com/view_video.php?viewkey=ph5e5e7756b90d4",
]

down_path = "D:/ph/other"

# 批量下载链接
batch_url = "https://cn.pornhub.com/channels/ours-hd-tv/videos?o=vi"
batch_down_path = "D:/ph/batch"


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
