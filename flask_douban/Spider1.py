#coding:utf-8
import requests
import json #json解析数据
from bs4 import BeautifulSoup   #解析网页数据
import jieba    #结巴分词
import matplotlib.pyplot as plt #读取图片形状
from wordcloud import WordCloud, ImageColorGenerator,STOPWORDS  #词云
import time #time模块
import queue    #队列
import threading    #多线程
import myProxies

Share_Q = queue.Queue() #工厂模式，使用队列
THREAD_NUM = 5  #开启5个线程

#电影的信息
class Movie(object):
    def __init__(self):
        self.id = ''
        self.title = ''
        self.score = 0
        self.director = ''
        self.actor = ''
        self.year = ''
        self.sub_title = ''

#词云类
class DoubaMovieWordCloud:
    def __init__(self, moviename):
        self.moviename = moviename
        self.allcomment = u''   #评论内容
        self.ip = ''    #通过myProxies获得IP

    #获得要查询电影的id号
    def get_content(self):
        search_url = 'https://movie.douban.com/j/subject_suggest?q='+self.moviename
        response1 = requests.get(url=search_url)
        content1 = response1.text
        items = json.loads(content1)
        if len(items) == 0:
            return
        movies = []
        for item in items:
            if item['type'] != 'movie':
                continue
            movie = Movie()
            movie.id = item['id']
            movie.title = item['title']
            movie.year = item['year']
            movie.sub_title = item['sub_title']
            movies.append(movie)
            return movies

    #生成词云
    def get_wordcloud(self, name):
        jieba_text = self.jieba_split()
        backgroud_Image = plt.imread('static/templatesPicture/abc.jpg')  # 词云的形状
        wc = WordCloud(background_color='black',  # 设置背景颜色
                       mask=backgroud_Image,  # 设置背景图片
                       max_words=2000,  # 设置最大现实的字数
                       stopwords=STOPWORDS,  # 设置停用词
                       font_path='stzhongs.ttf',  # 设置字体格式，如不设置显示不了中文
                       max_font_size=100,  # 设置字体最大值
                       random_state=30,  # 设置有多少种随机生成状态，即有多少种配色方案
                       )
        wc.generate(jieba_text)
        image_colors = ImageColorGenerator(backgroud_Image)
        wc.recolor(color_func=image_colors)
        wc.to_file('static/images/'+name+'.png')
        pass

    #分词
    def jieba_split(self):
        comment = self.get_comment()
        jieba_text = u''
        jieba_text += ' '.join(jieba.cut(comment))
        return jieba_text

    #利用多线程爬取网页
    def worker(self):
        global Share_Q
        while not Share_Q.empty():
            url = Share_Q.get()
            self.get_one_comment(url)

    #获得一页评论
    def get_one_comment(self, url, ):
        # print (url)
        proxies = {"http":self.ip}
        response = requests.get(url=url, proxies = proxies)
        content = response.text
        soup = BeautifulSoup(content, "html.parser")  # 利用Beautifulsoup进行解析
        content = soup.find('div', id='comments')  # 找到评论
        tdlist = content.find_all('p')  # 观察可发现p标签下就评论
        comment = u''
        for item in tdlist:
            if item.string != None:  # 有的p标签下面还有子标签，那么item.string为None。不为None的就是我们需要的评论
                comment += item.string.strip()
        self.allcomment += comment

    #获得全部评论
    def get_comment(self):
        movies = self.get_content()
        if len(movies) < 1: #电影不存在
            print ('没有匹配的电影')
            return -1
        else:
            self.ip = myProxies.get_ip()
            if self.ip == -1:   #代理ip错误
                print ("代理IP错误，请再次尝试")
                return -2
            print("代理ip%s"%self.ip)
            movie = movies[0]   #获得第一部电影
            id = movie.id
            for i in range(0, 200, 20):
                comment_url = 'https://movie.douban.com/subject/' + str(id) + '/comments?start=' + str(
                    i) + '&limit=20&sort=new_score&status=P&percent_type='  # 豆瓣热门评论网址
                Share_Q.put(comment_url)

            threads = []
            for i in range(THREAD_NUM):
                thread = threading.Thread(target=self.worker)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        return self.allcomment

def save_picture(name):
    begin = time.time()
    g = DoubaMovieWordCloud(name)
    g.get_wordcloud(name)
    end = time.time()
    print (end - begin)

if __name__ == '__main__':
    save_picture(u'银魂')