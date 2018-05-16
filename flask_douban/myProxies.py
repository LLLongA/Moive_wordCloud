#coding:utf-8
from bs4 import BeautifulSoup
import requests
import random

# 返回ip列表
def get_ip_list(url, headers):
    web_data = requests.get(url, headers = headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

# 在列表中随机选择IP
def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://'+ip)

    proxy_ip = random.choice(proxy_list)
    proxies = {'http':proxy_ip}
    return proxies

def get_ip():
    url = 'http://www.xicidaili.com/nn/'    #这是一个免费IP的网站
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    ip_list = get_ip_list(url, headers=headers) #获得IP列表
    print(len(ip_list)) #第一页100个
    testurl = 'http://ip.chinaz.com/getip.aspx' #测试网址，如果可以访问，则表示这个IP可以用
    for item in ip_list:
        ip = 'http://' + item
        proxies = {'http': ip}
        try:
            res = requests.get(testurl, proxies=proxies, timeout=2)
            print(ip, 'ok')
            return ip
        except:
            print(ip, u'超时')
    return -1
if __name__ == '__main__':
    get_ip()