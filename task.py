import requests
import re
import random
import time
import urllib3
from config import Config
from queue import Queue
from bs4 import BeautifulSoup

urllib3.disable_warnings()

config = Config()
line_bot_api = config.line_bot_api
client_id = config.client_id
client_secret = config.client_secret
album_id = config.album_id
API_Get_Image = config.API_Get_Image


class Crawler:
    rs = requests.session()

    def __init__(self, target_url, method='get'):
        print('Start Crawler....{}'.format(self.__class__.__name__))
        self.url = target_url
        self.content = self.analyze(method)

    def analyze(self, method):
        if method == 'get':
            res = self.rs.get(self.url, verify=False)
        else:
            # post
            load = {
                'from': '/bbs/Gossiping/index.html',
                'yes': 'yes'
            }
            res = self.rs.post('https://www.ptt.cc/ask/over18', verify=False, data=load)

        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup


class EynyMovie(Crawler):
    def parser(self):
        result = ''
        for url in self.content.select('.bm_c tbody .xst'):
            href = url['href']
            title = url.text
            if '11379780-1-3' in href:
                continue
            if self.pattern_mega(title):
                result += '{}\nhttp://www.eyny.com/{}\n\n'.format(title, href)
        return result

    @staticmethod
    def pattern_mega(text):
        patterns = [
            'mega', 'mg', 'mu', 'ＭＥＧＡ', 'ＭＥ', 'ＭＵ',
            'ｍｅ', 'ｍｕ', 'ｍｅｇａ', 'GD', 'MG', 'google',
        ]
        match = False
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match = True
                break
        return match


class AppleNews(Crawler):
    def parser(self):
        result = ''
        for index, data in enumerate(self.content.select('.rtddt a')):
            if index == 5:
                break
            result += '{}\n\n'.format(data['href'])
        return result


class ArticleInfo:
    def __init__(self, title=None, url=None, rate=None):
        self.title = title
        self.url = url
        self.push = rate


class PttBeauty(Crawler):
    parser_page = 2  # crawler count
    push_rate = 10  # 推文

    def parser(self):
        url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'
        index_seqs = PttBeauty.get_all_index(self.content, url, self.parser_page)
        articles = []
        while not index_seqs.empty():
            index = index_seqs.get()
            res = self.rs.get(index, verify=False)
            # 如網頁忙線中,則先將網頁加入 index_seqs 並休息1秒後再連接
            if res.status_code != 200:
                index_seqs.put(index)
                time.sleep(1)
            else:
                articles += self.crawler_info(res)
            time.sleep(0.05)

        return ''.join('[{} push] {}\n{}\n\n'.format(article.push,
                                                     article.title,
                                                     article.url)
                       for article in reversed(articles))

    def crawler_info(self, res):
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = []
        # 抓取 文章標題 網址 推文數
        for r_ent in soup.find_all(class_="r-ent"):
            try:
                # 先得到每篇文章的篇url
                link = r_ent.find('a')['href']
                if not link:
                    break
                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                rate = r_ent.find(class_="nrec").text
                url = 'https://www.ptt.cc' + link
                if rate:
                    rate = 100 if rate.startswith('爆') else rate
                    rate = -1 * int(rate[1]) if rate.startswith('X') else rate
                else:
                    rate = 0
                # 比對推文數
                if int(rate) >= self.push_rate:
                    articles.append(ArticleInfo(title, url, rate))
            except Exception as e:
                print('本文已被刪除', e)
        return articles

    @staticmethod
    def get_all_index(content, url, parser_page):
        max_page = PttBeauty.get_max_page(content.select('.btn.wide')[1]['href'])
        queue = Queue()
        for page in range(max_page - parser_page + 1, max_page + 1, 1):
            queue.put(url.format(page))
        return queue

    @staticmethod
    def get_max_page(content):
        start_index = content.find('index')
        end_index = content.find('.html')
        page_number = content[start_index + 5: end_index]
        return int(page_number) + 1


class PttGossiping(Crawler):
    parser_page = 2  # crawler count

    def parser(self):
        url = 'https://www.ptt.cc/bbs/Gossiping/index{}.html'
        index_seqs = PttBeauty.get_all_index(self.content, url, self.parser_page)
        articles = []
        while not index_seqs.empty():
            index = index_seqs.get()
            res = self.rs.get(index, verify=False)
            # 如網頁忙線中,則先將網頁加入 index_seqs 並休息1秒後再連接
            if res.status_code != 200:
                index_seqs.put(index)
                time.sleep(1)
            else:
                articles += self.crawler_info(res)
            time.sleep(0.05)

        result = ''
        for index, article in enumerate(reversed(articles)):
            if index == 15:
                break
            result += '{}\n{}\n\n'.format(article.title, article.url)

        return result

    @staticmethod
    def crawler_info(res):
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = []
        for r_ent in soup.find_all(class_="r-ent"):
            try:
                # 先得到每篇文章的篇url
                link = r_ent.find('a')['href']
                if not link:
                    break

                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                url = 'https://www.ptt.cc' + link
                articles.append(ArticleInfo(title, url))
            except Exception as e:
                print('本文已被刪除', e)
        return articles


class PttHot(Crawler):
    def parser(self):
        result = ''
        for data in self.content.select('#list div.row2 div span.listTitle'):
            title = data.text
            href = data.find('a')['href']
            if href == "796-59l9":
                break
            result += '{}\nhttp://disp.cc/b/{}\n\n'.format(title, href)
        return result


class Movie(Crawler):
    def parser(self):
        result = ''
        for index, data in enumerate(self.content.select('ul.filmNextListAll a')):
            if index == 20:
                break
            title = data.text.replace('\t', '').replace('\r', '')
            result += '{}\nhttp://www.atmovies.com.tw{}\n'.format(title, data['href'])
        return result


class TechNews(Crawler):
    def parser(self):
        result = ''
        for index, data in enumerate(self.content.select('article div h1.entry-title a')):
            if index == 12:
                break
            result += '{}\n{}\n\n'.format(data.text, data['href'])
        return result


class Panx(Crawler):
    def parser(self):
        result = ''
        for data in self.content.select('div.container div.row div.desc_wrap h2 a'):
            result += '{}\n{}\n\n'.format(data.text, data['href'])
        return result


class OilPrice(Crawler):
    def parser(self):
        title = self.content.select('#main')[0].text.replace('\n', '').split('(')[0]
        gas_price = self.content.select('#gas-price')[0].text.replace('\n\n\n', '').replace(' ', '')
        cpc = self.content.select('#cpc')[0].text.replace(' ', '')
        return '{}\n{}{}'.format(title, gas_price, cpc)


class YoutubeVideo(Crawler):
    def parser(self):
        videos = ['https://www.youtube.com{}'.format(data.find('a')['href'])
                  for data in self.content.select('.yt-lockup-title')]
        return videos

    @staticmethod
    def random(videos):
        return videos[random.randint(0, len(videos) - 1)]
