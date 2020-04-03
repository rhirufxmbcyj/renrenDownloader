# renrenDownloader
人人美剧视频下载、

支持的网站是https://www.rrmeiju.cc，其他网站不支持

### 使用方法

1、安装python3

2、安装第三方库

```
pip install requests m3u8 bs4
```

3、在命令行里输入

```
python renrenDownload.py video_play_page_url
```

video_play_page_url：视频的播放页链接

例如《行尸之惧第五季》的第一集播放页是https://www.rrmeiju.cc/Play/2735-1-1.html

那么执行脚本的命令就是

```
python renrenDownload.py https://www.rrmeiju.cc/Play/2735-1-1.html
```

脚本内部会解析全部集数的链接，由用户选择下载哪一集或全部

![image-20200404032700168](C:\Users\test\AppData\Roaming\Typora\typora-user-images\image-20200404032700168.png)



### 一些提示

1、只是一个小工具，基本没做输入内容合法性检查，还是不要测试它的健壮性了

2、下载的前提是网站上可以正常播放，如果网站上都不能播放，那脚本也无法绕过

3、thread_num是线程个数，可以根据自己电脑性能设置，默认是8

4、遇到下载失败，错误码是403时，可以尝试多运行几次，如果依旧403，请提交issue

5、写C写习惯了，python野路子出身，变量命名、代码逻辑什么的基本上都是C风格，如果有人愿意按专业的python程序员把它“格式化”一下看起来更优雅的话，那就非常感谢了



### 思路

1、从播放页面，例如https://www.rrmeiju.cc/Play/2735-1-1.html，从html源码中拿到2735.js的地址（js的名称就是html的名称前几个字符），upload/playdata/20190603/2735/2735.js，组装链接为https://www.rrmeiju.cc/upload/playdata/20190603/2735/2735.js

2、从2735.js中获取到mac_url段

```javascript
mac_url = unescape('%u7b2c01%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190603%2F3413_ac65206b%2Findex.m3u8%23%u7b2c02%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190610%2F3687_0259f33a%2Findex.m3u8%23%u7b2c03%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190617%2F3918_d3d03891%2Findex.m3u8%23%u7b2c04%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190624%2F4119_f6877d2a%2Findex.m3u8%23%u7b2c05%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190708%2F4587_fe659d01%2Findex.m3u8%23%u7b2c06%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190708%2F4588_656e166e%2Findex.m3u8%23%u7b2c07%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190714%2F4870_0d86fdfc%2Findex.m3u8%23%u7b2c08%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190720%2F5053_7a6c8ed9%2Findex.m3u8%23%u7b2c09%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190810%2F5777_c9733969%2Findex.m3u8%23%u7b2c10%u96c6%24https%3A%2F%2Fiqiyi.com-t-iqiyi.com%2F20190817%2F6078_5f6845ed%2Findex.m3u8%23%u7b2c11%u96c6%24https%3A%2F%2Fyouku.com-ok-pptv.com%2F20190824%2F6323_01656cd2%2Findex.m3u8%23%u7b2c12%u96c6%24https%3A%2F%2Fyouku.com-ok-pptv.com%2F20190831%2F6558_d9775962%2Findex.m3u8%23%u7b2c13%u96c6%24https%3A%2F%2Fyouku.com-ok-pptv.com%2F20190907%2F6768_84381ffd%2Findex.m3u8%23%u7b2c14%u96c6%24https%3A%2F%2Fyouku.com-ok-pptv.com%2F20190914%2F6998_294ca649%2Findex.m3u8%23%u7b2c15%u96c6%24https%3A%2F%2Fyouku.com-ok-pptv.com%2F20190921%2F7292_cdbb9635%2Findex.m3u8%23%u7b2c16%u96c6%24https%3A%2F%2Fyouku.com-ok-pptv.com%2F20190929%2F7580_de7e9bc2%2Findex.m3u8');
```

unescape是js的一个方法

python实现unescape方法：

```python
import urllib.parse
import sys
import html
import re
def unescape(string):
    string = urllib.parse.unquote(string)
    quoted = html.unescape(string).encode(sys.getfilesystemencoding()).decode('utf-8')
    #转成中文
    return re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), quoted)
```

获得每一集对应的m3u8链接的字符串

```
"第01集$https://iqiyi.com-t-iqiyi.com/20190603/3413_ac65206b/index.m3u8#
第02集$https://iqiyi.com-t-iqiyi.com/20190610/3687_0259f33a/index.m3u8#
第03集$https://iqiyi.com-t-iqiyi.com/20190617/3918_d3d03891/index.m3u8#
第04集$https://iqiyi.com-t-iqiyi.com/20190624/4119_f6877d2a/index.m3u8#
第05集$https://iqiyi.com-t-iqiyi.com/20190708/4587_fe659d01/index.m3u8#
第06集$https://iqiyi.com-t-iqiyi.com/20190708/4588_656e166e/index.m3u8#
第07集$https://iqiyi.com-t-iqiyi.com/20190714/4870_0d86fdfc/index.m3u8#
第08集$https://iqiyi.com-t-iqiyi.com/20190720/5053_7a6c8ed9/index.m3u8#
第09集$https://iqiyi.com-t-iqiyi.com/20190810/5777_c9733969/index.m3u8#
第10集$https://iqiyi.com-t-iqiyi.com/20190817/6078_5f6845ed/index.m3u8#
第11集$https://youku.com-ok-pptv.com/20190824/6323_01656cd2/index.m3u8#
第12集$https://youku.com-ok-pptv.com/20190831/6558_d9775962/index.m3u8#
第13集$https://youku.com-ok-pptv.com/20190907/6768_84381ffd/index.m3u8#
第14集$https://youku.com-ok-pptv.com/20190914/6998_294ca649/index.m3u8#
第15集$https://youku.com-ok-pptv.com/20190921/7292_cdbb9635/index.m3u8#
第16集$https://youku.com-ok-pptv.com/20190929/7580_de7e9bc2/index.m3u8"
```

3、可以从这些链接里获得一个m3u8文件

```
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000,RESOLUTION=1080x608
1000k/hls/index.m3u8
```

内容里是另一个m3u8的地址，将这个地址和上一个m3u8的地址拼接起来，获得真正的m3u8文件地址：https://iqiyi.com-t-iqiyi.com/20190603/3413_ac65206b/1000k/hls/index.m3u8

4、从这个地址获得的m3u8存放着视频分割的ts地址，内容如下

```
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:8
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:5.160000,
5df472edfc9000000.ts
#EXTINF:3.280000,
5df472edfc9000001.ts
#EXTINF:3.560000,
5df472edfc9000002.ts
#EXTINF:5.280000,
5df472edfc9000003.ts
#EXTINF:6.000000,
5df472edfc9000004.ts
...
```

需要将ts也拼接一下，拼接成真正的地址：https://iqiyi.com-t-iqiyi.com/20190603/3413_ac65206b/1000k/hls/5df472edfc9000000.ts

5、多线程requests.get()下载，然后拼接文件即可



---



发现下载电影会失败，例如https://www.rrmeiju.cc/Play/2163-1-1.html，阿丽塔战斗天使

在请求第一个m3u8文件是直接请求，但是网站上请求这个加了参数?sign=xxxxxxxxx

而且下电视剧没有参数，网站上还分开处理了，脚本也要分开处理了

发现将m3u8地址传给了一个网址:https://okokmis.yueyuw.com/m3u8.php?vid=http://cdn.rbhanju.com/20191005/0cZpq89t/index.m3u8，然后php内组装了参数

```php
var vid=GetQueryString("vid")+'?sign=aabfb8745a1a2a66987135ffe3792dc57dc7879ddc0a12c63655bf4c38424120c703de287a85185af4d32ac44639c9ba';
```

这个php文件组装的参数每次访问都会变，应该是后端实现的，所以脚本也请求一些这个php获得参数

而且视频不同，解析的网址也不同，需要找到人人美剧是如何区分的

在html页面发现加载了一个playerconfig.js，这个js里写着各种云播

```javascript
mac_show["pingbi"] = "pb云播";
mac_show["8km3u8"] = "RR云视频";
mac_show["jsm3u8"] = "js云视频";
mac_show["mym3u8"] = "美剧云播";
mac_show["ckm3u8"] = "ok云视频";
mac_show["subom3u8"] = "sub云视频";
mac_show["hkm3u8"] = "哈酷视频";
mac_show["mp4"] = "直连视频";
mac_show["zkm3u8"] = "zk云视频";
mac_show["bjm3u8"] = "bj云视频";
mac_show["youku"] = "yk云视频";
mac_show["qiyi"] = "qy云视频";
mac_show["meiju"] = "mj云视频";
mac_show["sohu"] = "so云视频";
mac_show["le"] = "le云视频";
mac_show["link"] = "在线播放";
mac_show["kb"] = "kb云视频";
```

在html文件源码中有js文件，例如这个网址的就是2163.js，这个js文件里有个变量：mac_from = 8km3u8，这样就和这些列表对应起来了

这些云的解析网址都在名称.js里，例如8km3u8.js，ckm3u8.js，js所在网址是https://www.rrmeiju.cc/player/目录下

**先支持：8km3u8、ckm3u8，其他的发现了再支持，pb云播就不用看了，就是屏蔽的意思**