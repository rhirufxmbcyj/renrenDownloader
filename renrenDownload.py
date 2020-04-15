#coding=utf-8
import re
import os
import sys
import time
import html
import m3u8
import requests
import threading
import urllib.parse
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

lock = threading.Lock()
ts_index = 0
finish_list=[]
thread_num = 8
ts_count = 0
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'}
mac_from = ''

def request_get_func(url = ''):
    res = requests.get(url)
    if(res.status_code == 403):
        for i in range(0,3):
            res = requests.get(url)
            if(res.status_code == 200):
                break
    return res

def download_ts(ts_url='', index=0):
    global ts_count
    file = open(str(index) + '.ts', 'wb')
    while True:
        try:
            res = requests.get(ts_url,headers=headers,verify=False)
            if (res.status_code == 200):
                file.write(res.content)
                break
        except:
            print(u'下载%d出错 3秒后重试' % index)
            time.sleep(3)
    file.close()
    print(u'已下载', index, u'  文件总数', ts_count)

def thread_function(m3u8_segments, m3u8_url):
    global lock
    global ts_index
    global finish_list
    url = ''
    i = 0
    while True:
        lock.acquire()
        if ts_index == ts_count:
            lock.release()
            break
        i = ts_index
        uri = m3u8_segments[i]['uri']
        url = urllib.parse.urljoin(m3u8_url,uri)
        ts_index += 1
        lock.release()
        download_ts(url, i)
        # 下载好的index加入完成列表
        finish_list.append(i)

def merge_files(ts_count=0, name=''):
    global finish_list
    f_out = open(name + '.ts', 'wb')
    index = 0
    while(True):
        if(index == ts_count):
            break
        if(index in finish_list):
            f_in = open(str(index) + '.ts','rb')
            f_out.write(f_in.read())
            f_in.close()
            os.remove(str(index) + '.ts')
        else:
            time.sleep(1)
            index = index - 1
        index = index + 1
    f_out.close()
    print(u'合并文件成功')

def unescape(string):
    string = urllib.parse.unquote(string)
    quoted = html.unescape(string).encode(sys.getfilesystemencoding()).decode('utf-8')
    #转成中文
    return re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), quoted)

def get_name_and_url(html_link=''):
    global mac_from
    js_name = os.path.basename(html_link).split('-')[0] + '.js'
    # js_url = urllib.parse.urljoin(html_link,js_name)
    js_url = ''
    res = request_get_func(html_link)
    if(res.status_code != 200):
        print(u'获取',html_link,u'错误码：', str(res.status_code))
        exit(-1)
    soup = BeautifulSoup(res.content,'html.parser')
    script = soup.find_all('script')
    for i in script:
        if(i.get('src') and js_name in i.get('src')):
            js_url = i.get('src')
            break
    if(js_url == ''):
        print(u'html页面找不到',js_name,u'请将视频播放链接提交issue')
        exit(-1)
    js_url = urllib.parse.urljoin(html_link,js_url)
    res = request_get_func(js_url)
    if(res.status_code != 200):
        print(u'获取',js_url,'错误码：', str(res.status_code))
        exit(-1)
    mac_from = re.findall("mac_from='(.+?)'", res.content.decode('utf-8'))[0]
    m3u8_url = unescape(re.findall("mac_url=unescape\('(.+?)'", res.content.decode('utf-8'))[0])
    m3u8_list = re.split("\$|#",m3u8_url)
    video_name = re.findall("mac_name='(.+?)'", res.content.decode('utf-8'))[0]
    return m3u8_list,video_name


def parse_m3u8_url(m3u8_url=''):
    global mac_from
    if(mac_from == ''):
        print(u"未找到云播，请将视频播放链接提交issue")
        exit(-1)
    if(mac_from == 'pingbi'):
        print(u"该视频已被屏蔽，应该是版权问题，尝试在网站播放，如果网站上可以播放请提交issue")
        exit(-1)
    if(mac_from == 'ckm3u8'):
        # ok云视频 可以直接获取m3u8
        return m3u8_url
    if(mac_from == '8km3u8'):
        # RR云视频 请求m3u8时需要带sign参数
        res = request_get_func('https://okokmis.yueyuw.com/m3u8.php?vid=' + m3u8_url)
        if(res.status_code != 200):
            print(u"获取m3u8.php失败")
            exit(-1)
        param = re.findall("GetQueryString\(\"vid\"\)\+'(.+?)'", res.content.decode('utf-8'))[0]
        return m3u8_url + param
    print(mac_from + u"格式暂未支持，请将视频播放链接提交issue")
    exit(-1)

def download_one(m3u8_list=[], num=0):
    global ts_count
    global thread_num
    global ts_index
    global finish_list
    ts_index = 0
    num = num * 2
    name = m3u8_list[num]
    m3u8_url = parse_m3u8_url(m3u8_list[num + 1])
    print(u"开始下载",name)
    res = request_get_func(m3u8_url)
    if(res.status_code != 200):
        print(name,u"下载失败",u"错误码：",res.status_code)
        return
    m3u8_data = m3u8.parse(res.content.decode('utf-8'))
    m3u8_url = urllib.parse.urljoin(m3u8_url,m3u8_data['playlists'][0]['uri'])
    res = request_get_func(m3u8_url)
    if(res.status_code != 200):
        print(name,u"下载失败",u"错误码：",res.status_code)
        return
    m3u8_data = m3u8.parse(res.content.decode('utf-8'))
    ts_count = len(m3u8_data['segments'])
    thread_list = []
    finish_list = []
    for i in range(0, thread_num):
        t = threading.Thread(target=thread_function, name='LoopThread %s' % i, args=(m3u8_data['segments'],m3u8_url))
        thread_list.append(t)
        t.start()
    # 开始合并文件线程 边下载边合并
    t = threading.Thread(target=merge_files, name='merge_files', args=(ts_count,name))
    thread_list.append(t)
    t.start()
    for t in thread_list:
        t.join()
    print(u"下载",name,u"完成")


def download_all(m3u8_list=[]):
    length = int(len(m3u8_list) / 2)
    for i in range(0,length):
        download_one(m3u8_list,i)


def parse_and_download(m3u8_list=[],choice=''):
    choice = choice.split(',')
    for num in choice:
        num = int(num)
        if(num == 0):
            download_all(m3u8_list)
        else:
            download_one(m3u8_list,num - 1)


# https://www.rrmeiju.cc/Play/2735-1-1.html
if __name__ == "__main__":
    if(len(sys.argv) != 2 or sys.argv[1] == ''):
        print('usage: python renrenDownload.py video_play_page_url')
        print('example:python renrenDownload.py https://www.rrmeiju.cc/Play/2735-1-1.html')
        exit(-1)
    m3u8_list,video_name = get_name_and_url(sys.argv[1])
    print(u"名称：",video_name)
    print(u"共",int(len(m3u8_list) / 2),u"集")
    print(u"请选择要下载的集数：（0：下载全部   1：第一集 2：第二集...   1,4,5,10：第一、四、五、十集）")
    choice = input(u"请输入：")
    parse_and_download(m3u8_list,choice)