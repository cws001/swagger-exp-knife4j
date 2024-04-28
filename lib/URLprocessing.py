#!/usr/bin/env python
# coding=utf-8
  ################
 #      v1.0    #
################

import codecs
import copy
import json
import os
import sys
import urllib
import requests
from termcolor import cprint

from lib.chrome import server_open
from lib.common import print_msg, is_url_alive, headers

scheme = 'http'    # 请求方式默认http
api_set_list = []    # 接口列表默认空
requests.packages.urllib3.disable_warnings()    #禁用requests发送https请求时，未校验证书的警告
auth_bypass_detected = False

def run_URLprocessing(url):
    global scheme
    scheme = urllib.parse.urlparse(url).scheme.lower()
    if scheme.lower() == 'https':
        scheme = 'https'
    find_all_api_set(url)
    for url in api_set_list:
        process_doc(url)
    # 打开chrome
    server_open()

def find_all_api_set(start_url):
    cprint("======开始扫描 %s ======" % start_url, "cyan")
    try:
        text = requests.get(start_url, headers=headers, timeout=6, verify=False).text
        if text.strip().startswith('{"swagger":"'):    # from swagger.json
            api_set_list.append(start_url)
            print_msg('[OK] [API set] %s' % start_url)
            with codecs.open('api-docs.json', 'w', encoding='utf-8') as f:
                f.write(text)
        elif text.find('"swaggerVersion"') > 0:    # from /swagger-resources/
            base_url = start_url[:start_url.find('/swagger-resources')]
            json_doc = json.loads(text)
            for item in json_doc:
                url = base_url + item['location']
                find_all_api_set(url)
        elif text.strip().startswith('<!-- HTML'):    # from /swagger-ui.html （解决原工具访问 v2版本 swagger-ui.html 时，无法爬取到目标 api-docs 问题）
            print_msg('[OK] [符合SwaggerUI特征] %s' % start_url)
            # url切割 拼接路径
            rsplit_start_url = start_url.rsplit('/', 1)
            url_api_docs = rsplit_start_url[0] + "/v2/api-docs"
            if (is_url_alive(url_api_docs)):
                print_msg('[OK] [GET API-Doc URL:] %s' % url_api_docs)
                # 内容写为 api-docs.json
                text_api_docs = requests.get(url_api_docs, headers=headers, timeout=6, verify=False).text
                with codecs.open('api-docs.json', 'w', 'utf-8') as f:
                    f.write(text_api_docs)
                path = os.path.dirname(os.path.abspath(__file__))
                print_msg('[OK] [API-Doc write in:] %s' % path)
                # 打开chrome
                server_open()
        else:
            print_msg('[FAIL] Invalid API Doc: %s' % start_url)
    except Exception as e:
        print_msg('[FAIL] process error in %s' % e)

def process_doc(url):
    try:
        json_doc = requests.get(url, headers=headers, timeout=6, verify=False).json()
        base_url = scheme + '://' + json_doc['host'] + json_doc['basePath']
        base_url = base_url.rstrip('/')
        for path in json_doc['paths']:

            for method in json_doc['paths'][path]:
                if method.upper() not in ['GET', 'POST', 'PUT']:
                    continue

                params_str = ''
                sensitive_words = ['url', 'path', 'uri']
                sensitive_params = []
                if 'parameters' in json_doc['paths'][path][method]:
                    parameters = json_doc['paths'][path][method]['parameters']

                    for parameter in parameters:
                        para_name = parameter['name']
                        # mark sensitive parma
                        for word in sensitive_words:
                            if para_name.lower().find(word) >= 0:
                                sensitive_params.append(para_name)
                                break

                        if 'format' in parameter:
                            para_format = parameter['format']
                        elif 'schema' in parameter and 'format' in parameter['schema']:
                            para_format = parameter['schema']['format']
                        elif 'schema' in parameter and 'type' in parameter['schema']:
                            para_format = parameter['schema']['type']
                        elif 'schema' in parameter and '$ref' in parameter['schema']:
                            para_format = parameter['schema']['$ref']
                            para_format = para_format.replace('#/definitions/', '')
                            para_format = '{OBJECT_%s}' % para_format
                        else:
                            para_format = parameter['type'] if 'type' in parameter else 'unkonwn'
                        is_required = '' if parameter['required'] else '*'
                        params_str += '&%s=%s%s%s' % (para_name, is_required, para_format, is_required)
                    params_str = params_str.strip('&')
                    if sensitive_params:
                        print_msg('[*] Possible vulnerable param found: %s, path is %s' % (
                            sensitive_params, base_url+path))
                scan_api(method, base_url, path, params_str)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print_msg('[process_doc error][%s] %s' % (url, e))

def scan_api(method, base_url, path, params_str, error_code=None):
    # 定义默认请求接口的内容
    _params_str = params_str.replace('*string*', 'a')
    _params_str = _params_str.replace('*int64*', '1')
    _params_str = _params_str.replace('*int32*', '1')
    _params_str = _params_str.replace('=string', '=test')
    api_url = base_url + path
    if not error_code:
        print_msg('[%s] %s %s' % (method.upper(), api_url, params_str))
    try:
        # 请求GET
        if method.upper() == 'GET':
            r = requests.get(api_url + '?' + _params_str, headers=headers, timeout=6, verify=False)
            if not error_code:
                print_msg('[Request] %s %s' % (method.upper(), api_url + '?' + _params_str))
                # 状态码200判断未授权,结果写入文件
                if r.status_code == 200:
                    cprint('[+][+][+] [' + method.upper() + ']' + api_url + '?' + _params_str, 'red')
                    f2 = open("result_UnAuthorized.txt", "a")
                    f2.write(api_url + '?' + _params_str + '\n')
                    f2.close()
        # 请求POST
        else:
            r = requests.post(api_url, data=_params_str, headers=headers, timeout=6, verify=False)
            # 状态码200判断未授权,结果写入文件
            if r.status_code == 200:
                cprint('[+][+][+] [' + method.upper() + ']' + api_url + '?' + _params_str, 'red')
                f2 = open("result_UnAuthorized.txt", "a")
                f2.write(api_url + '?' + _params_str + '\n')
                f2.close()
            if not error_code:
                print_msg('[Request] %s %s \n%s' % (method.upper(), api_url, _params_str))
        content_type = r.headers['content-type'] if 'content-type' in r.headers else ''
        content_length = r.headers['content-length'] if 'content-length' in r.headers else ''
        if not content_length:
            content_length = len(r.content)
        if not error_code:
            print_msg('[Response] Code: %s Content-Type: %s Content-Length: %s' % (
            r.status_code, content_type, content_length))
            print('\n' + '\n')
        # 401 403 再跑一遍，尝试绕过
        else:
            if r.status_code not in [401, 403] or r.status_code != error_code:
                global auth_bypass_detected
                auth_bypass_detected = True
                print_msg('[VUL] *** URL Auth Bypass ***')
                if method.upper() == 'GET':
                    print_msg('[Request] [%s] %s' % (method.upper(), api_url + '?' + _params_str))
                else:
                    print_msg('[Request] [%s] %s \n%s' % (method.upper(), api_url, _params_str))
        if not error_code and r.status_code in [401, 403]:
            path = '/' + path
            scan_api(method, base_url, path, params_str, error_code=r.status_code)
    except KeyboardInterrupt:
        print("Ctrl + C 手动终止了进程")
        sys.exit()
    except:
        cprint("[-] URL为 " + '[' + method.upper() + ']' + api_url + params_str + " 的目标积极拒绝请求，予以跳过！", "magenta")
        f3 = open("result_RequestDeny.txt", "a")
        f3.write(api_url + '?' + _params_str + '\n')
        f3.close()
        print('\n')

def process_doc(url):
    try:
        json_doc = requests.get(url, headers=headers, timeout=6, verify=False).json()
        base_url = scheme + '://' + json_doc['host'] + json_doc['basePath']
        base_url = base_url.rstrip('/')
        for path in json_doc['paths']:
            for method in json_doc['paths'][path]:
                if method.upper() not in ['GET', 'POST', 'PUT']:
                    continue
                params_str = ''
                # 自定义敏感参数
                sensitive_words = ['url', 'path', 'uri']
                sensitive_params = []
                if 'parameters' in json_doc['paths'][path][method]:
                    parameters = json_doc['paths'][path][method]['parameters']
                    for parameter in parameters:
                        para_name = parameter['name']
                        # mark sensitive parma
                        for word in sensitive_words:
                            if para_name.lower().find(word) >= 0:
                                sensitive_params.append(para_name)
                                break
                        if 'format' in parameter:
                            para_format = parameter['format']
                        elif 'schema' in parameter and 'format' in parameter['schema']:
                            para_format = parameter['schema']['format']
                        elif 'schema' in parameter and 'type' in parameter['schema']:
                            para_format = parameter['schema']['type']
                        elif 'schema' in parameter and '$ref' in parameter['schema']:
                            para_format = parameter['schema']['$ref']
                            para_format = para_format.replace('#/definitions/', '')
                            para_format = '{OBJECT_%s}' % para_format
                        else:
                            para_format = parameter['type'] if 'type' in parameter else 'unkonwn'
                        is_required = '' if parameter['required'] else '*'
                        params_str += '&%s=%s%s%s' % (para_name, is_required, para_format, is_required)
                    params_str = params_str.strip('&')
                    if sensitive_params:
                        # print_msg('[*] Possible vulnerable param found: %s, path is %s' % (sensitive_params, base_url + path))
                        sensitive_params_result = "".join(sensitive_params)
                        cprint("发现敏感参数:[" + sensitive_params_result + ']URL为：' + base_url + path, "green")
                        f3 = open("result_sensitive.txt", "a")
                        f3.write('参数:[' + sensitive_params_result + '] ' + base_url + path + '\n')
                        f3.close()
                # 接口发起请求
                scan_api(method, base_url, path, params_str)
        # api测试结果提示
        count = len(open("result_UnAuthorized.txt", 'r').readlines())
        count2 = len(open("result_RequestDeny.txt", 'r').readlines())
        count3 = len(open("result_sensitive.txt", 'r').readlines())
        if count >= 1:
            cprint("[+][+][+] 发现目标接口存在未授权，已经导出至 result_UnAuthorized.txt ，共%d行记录" % count, "yellow")
        else:
            cprint("=========未发现接口存在未授权，请手工测试 %s =========" % base_url, "red")
        if count2 >= 1:
            cprint("[+][+][+] 存在请求被拒绝的接口，已经导出至 result_RequestDeny.txt ，共%d行记录" % count2, "yellow")
        if count3 >= 1:
            cprint("[+][+][+] 发现存在敏感参数接口，已经导出至 result_sensitive.txt ，共%d行记录" % count3, "yellow")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print_msg('[process_doc error][%s] %s' % (url, e))

