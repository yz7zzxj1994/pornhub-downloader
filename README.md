# pornhub-downloader

# 简介
使用Python语言编写的，P站视频下载工具

技术点：requests re threading queue tqdm

实现多线程断点续传的功能

# 使用方式
1.config.py 为配置类
  
    download_urls  存放待下载链接"https://cn.pornhub.com/view_video.php?viewkey=xxxxxx"
  
    down_path  下载路径
  
    cookie 默认使用空用户的cookie,可自行替换自己的账号cookie,作用:使用账号的cookie可以保存浏览记录 观看记录

2.pornhub.py 为核心类
  
    配置好config.py后,运行pornhub.py即可进行下载


3.下载过程需要翻墙且为全局!!!

# 运行截图
![运行截图](1.png)

# 交流方式
QQ: 1791592482 邮箱: 1791592482@qq.com

