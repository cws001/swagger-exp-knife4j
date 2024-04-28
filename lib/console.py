#!/usr/bin/env python
# coding=utf-8
  ################
 #      v1.0    #
################

import codecs
import os
import sys
import threading
import requests

from lib.URLprocessing import run_URLprocessing
from lib.chrome import get_chrome_path, chrome_open, server_open
from lib.common import print_msg

# 控制台-参数处理和程序调用
def SpringBoot_Exp_console(args):
    if args.url:
        # 清空接口测试结果-未授权
        f2 = open("result_UnAuthorized.txt", "wb+")
        f2.close()
        # 清空接口测试结果-请求被拒绝
        f3 = open("result_RequestDeny.txt", "wb+")
        f3.close()
        # 清空接口测试结果-敏感参数
        f4 = open("result_sensitive.txt", "wb+")
        f4.close()
        # 运行
        url = args.url
        run_URLprocessing(url)
        # print(args.url)
    if args.chrome:
        server_open()
    else:
        # print('console.py end')
        sys.exit()
