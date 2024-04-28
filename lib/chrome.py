#!/usr/bin/env python
# coding=utf-8
  ################
 #      v1.0    #
################

import codecs
import copy
import json
import os
import platform
import subprocess
import sys
import threading
import time
import requests
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer

from termcolor import cprint

from lib.common import print_msg, headers

auth_bypass_detected = False

def get_chrome_path_win():
    try:
        import _winreg as reg
    except Exception as e:
        import winreg as reg
    # chrome默认安装时注册表路径： HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\
    conn = reg.ConnectRegistry(None, reg.HKEY_LOCAL_MACHINE)
    _path = reg.QueryValue(conn, 'Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe\\')
    reg.CloseKey(conn)
    if not os.path.exists(_path):
        raise Exception('chrome.exe not found.')
    return _path


def get_chrome_path_linux():
    folders = ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin', '/opt/google/','/Applications/Google Chrome.app/Contents/MacOS']
    names = ['google-chrome', 'chrome', 'chromium', 'chromium-browser','Google Chrome']
    for folder in folders:
        for name in names:
            if os.path.exists(os.path.join(folder, name)):
                return os.path.join(folder, name)


def get_chrome_path():
    if platform.system() == 'Windows':
        return get_chrome_path_win()
    else:
        return get_chrome_path_linux()

# 打开禁用CORS的chrome ，打开/result_ApiScanSummary.txt
def chrome_open(chrome_path, url, server):
    print_msg('[LOADING] 正在打开禁用CORS的chrome')
    time.sleep(2.0)
    if chrome_path:
        url_txt = url + '/result_ApiScanSummary.txt'
        # chrome 路径处理
        cwd = os.path.split(os.path.abspath(__file__))[0]
        user_data_dir = os.path.abspath(os.path.join(cwd, 'CORS_chrome_Swagger'))
        # 传递给Chrome二进制文件来覆盖用户数据目录
        cmd = '"%s" --disable-web-security --no-sandbox --new-window--disable-gpu ' \
              '--user-data-dir=%s %s %s' % (chrome_path, user_data_dir, url, url_txt)
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        while p.poll() is None:
            time.sleep(1.0)
        server.shutdown()
        print_msg('[OK] 本地 web 服务终止')

# 本地开http服务并打开chrome
def server_open():
    cprint("======开始本地开启 http 服务======", "cyan")
    server = ThreadingSimpleServer(('127.0.0.1', 0), RequestHandler)
    url = 'http://127.0.0.1:%s' % server.server_port
    chrome_path = get_chrome_path()
    print_msg('[OK] [本地http服务地址:] %s' % url)
    if not chrome_path:
        path = os.path.dirname(os.path.abspath(__file__))
        print_msg('[ERROR] 未找到chrome')
        cprint("请修改chrome.py 中 get_chrome_path_win() 中 chrome.exe 注册表位置", "red")
    else:
        cprint("======开始命令行打开“禁用CORS”的chrome.exe======", "cyan")
        threading.Thread(target=chrome_open, args=(chrome_path, url, server)).start()
    server.serve_forever()
class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy?url='):
            url = self.path[11:]
            if url.lower().startswith('http') and url.find('@') < 0:
                text = requests.get(url, headers=headers, verify=False).content
                if text.find('"schemes":[') < 0:
                    text = text[0] + '"schemes":["https","http"],' + text[1:]    # HTTP(s) Switch
                global auth_bypass_detected
                if auth_bypass_detected:
                    json_doc = json.loads(text)
                    paths = copy.deepcopy(json_doc['paths'].keys())
                    for path in paths:
                        json_doc['paths']['/' + path] = json_doc['paths'][path]
                        del json_doc['paths'][path]

                    text = json.dumps(json_doc)
            else:
                text = 'Request Error'
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(text))
            self.end_headers()
            self.wfile.write(text)
        return SimpleHTTPRequestHandler.do_GET(self)

