#!/usr/bin/env python
# coding=utf-8
  ################
 #      v1.0    #
################

import codecs
import time

import requests
from termcolor import cprint

headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
auth_bypass_detected = False

def print_msg(msg):
    # out_file = codecs.open('result_ApiScanSummary.txt', 'w', encoding='utf-8')
    out_file = open("result_ApiScanSummary.txt", "a")
    if msg.startswith('[GET] ') or msg.startswith('[POST] '):
        out_file.write('\n')
    _msg = "[%s] %s" % (time.strftime('%H:%M:%S', time.localtime()), msg)
    print(_msg)
    out_file.write(_msg + '\n')
    if out_file:
       out_file.flush()
       out_file.close()

def is_url_alive(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
