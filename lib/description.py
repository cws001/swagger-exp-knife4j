#!/usr/bin/env python
# coding=utf-8
  ################
 #      v1.0    #
################

import time, os, sys

def logo():
    logo0 = r'''
  ____                                     _____
/ ___|_      ____ _  __ _  __ _  ___ _ __| ____|_  ___ __
\___ \ \ /\ / / _` |/ _` |/ _` |/ _ \ '__|  _| \ \/ / '_ \
 ___) \ V  V / (_| | (_| | (_| |  __/ |  | |___ >  <| |_) |
|____/ \_/\_/ \__,_|\__, |\__, |\___|_|  |_____/_/\_\ .__/
                    |___/ |___/                     |_|
                    
 _  __      _  __      _  _   _     +-------+
| |/ /_ __ (_)/ _| ___| || | (_)    + v1.1  +
| ' /| '_ \| | |_ / _ \ || |_| |    +-------+
| . \| | | | |  _|  __/__   _| |
|_|\_\_| |_|_|_|  \___|  |_|_/ |
                           |__/
    '''
    print(logo0)

def usage():
    print('''
参数：
    -u  --url       指定 Swagger 相关URL
    -c  --chrome    本地打开chrome禁用CORS，打开 Knife4j 界面
    
用法:
    只打开Knife4j 进行分析：             python3 swagger-exp-knife4j.py -c 
    扫描所有API集，分析接口是否存在未授权：  python3 swagger-exp-knife4j.py -u http://example.com/swagger-resources 
    扫描一个API集，分析接口是否存在未授权：  python3 swagger-exp-knife4j.py -u http://example.com/v2/api-docs 
    扫描一个API集，爬取api-doc打开Chrome：python3 swagger-exp-knife4j.py -u http://example.com/swagger-ui.html 

注意：
    1、Knife4j 界面里一定要在 '个性化设置' 手动勾选 HOST 刷新页面,才能进行正常测试。
    2、部分 HTTPS 网站测试时报错Network Error，可在个性化设置 HOST 处加上协议号，如 https://example.com

''', end='')
