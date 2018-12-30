import requests
import random
import types
import urllib3
from config import Config
from imgurpython import ImgurClient
from task import EynyMovie, AppleNews, PttBeauty, PttGossiping, \
    PttHot, Movie, TechNews, Panx, OilPrice, YoutubeVideo
from linebot.models import TemplateSendMessage, CarouselTemplate, CarouselColumn, \
    MessageAction, URIAction, TextSendMessage, ImageSendMessage, ButtonsTemplate, \
    MessageTemplateAction, ImageCarouselColumn, ImageCarouselTemplate, StickerSendMessage
from my_dict import MyDict

urllib3.disable_warnings()

config = Config()
line_bot_api = config.line_bot_api
client_id = config.client_id
client_secret = config.client_secret
album_id = config.album_id
API_Get_Image = config.API_Get_Image


class TaskStrategy:
    def __init__(self, func=None, event=None):
        self.name = func.__name__ if func else "default"
        self.event = event
        if func:
            self.execute = types.MethodType(func, self)
        print('{} class , task {}'.format(self.__class__.__name__, self.name))

    def execute(self):
        pass

    def reply_message(self, obj):
        line_bot_api.reply_message(self.event.reply_token, obj)


def eyny_movie(self):
    task = EynyMovie('http://www.eyny.com/forum-205-1.html')
    self.reply_message(TextSendMessage(text=task.parser()))


def apple_news(self):
    task = AppleNews('https://tw.appledaily.com/new/realtime')
    self.reply_message(TextSendMessage(text=task.parser()))


def ptt_beauty(self):
    task = PttBeauty('https://www.ptt.cc/bbs/Beauty/index.html')
    self.reply_message(TextSendMessage(text=task.parser()))


def ptt_gossiping(self):
    task = PttGossiping('https://www.ptt.cc/bbs/Gossiping/index.html', 'post')
    self.reply_message(TextSendMessage(text=task.parser()))


def imgur_beauty(self):
    client = ImgurClient(client_id, client_secret)
    images = client.get_album_images(album_id)
    index = random.randint(0, len(images) - 1)
    url = images[index].link
    image_message = ImageSendMessage(
        original_content_url=url,
        preview_image_url=url
    )
    self.reply_message(image_message)


def random_beauty(self):
    image = requests.get(API_Get_Image)
    url = image.json().get('Url')
    image_message = ImageSendMessage(
        original_content_url=url,
        preview_image_url=url
    )

    self.reply_message(image_message)


def ptt_hot(self):
    task = PttHot('http://disp.cc/b/PttHot')
    self.reply_message(TextSendMessage(text=task.parser()))


def movie(self):
    task = Movie('http://www.atmovies.com.tw/movie/next/0/')
    self.reply_message(TextSendMessage(text=task.parser()))


def technews(self):
    task = TechNews('https://technews.tw/')
    self.reply_message(TextSendMessage(text=task.parser()))


def panx(self):
    task = Panx('https://panx.asia/')
    self.reply_message(TextSendMessage(text=task.parser()))


def oil_price(self):
    task = OilPrice('https://gas.goodlife.tw/')
    self.reply_message(TextSendMessage(text=task.parser()))


def youtube_video(self):
    task = YoutubeVideo('https://www.youtube.com/user/truemovie1/videos')
    videos = task.parser()
    self.reply_message(
        [
            TextSendMessage(text=YoutubeVideo.random(videos))
            for _ in range(2)
        ]
    )


class TemplateStrategy(TaskStrategy):
    def execute(self):
        carousel_template_message = TemplateSendMessage(
            alt_text='目錄 template',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/kzi5kKy.jpg',
                        title='選擇服務',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label=MyDict.start_template,
                                text=MyDict.start_template
                            ),
                            URIAction(
                                label='影片介紹 阿肥bot',
                                uri='https://youtu.be/1IxtWgWxtlE'
                            ),
                            URIAction(
                                label='如何建立自己的 Line Bot',
                                uri='https://github.com/twtrubiks/line-bot-tutorial'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/DrsmtKS.jpg',
                        title='選擇服務',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='other bot',
                                text='imgur bot'
                            ),
                            MessageAction(
                                label=MyDict.oil_price,
                                text=MyDict.oil_price
                            ),
                            URIAction(
                                label='聯絡作者',
                                uri='https://www.facebook.com/TWTRubiks?ref=bookmarks'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/h4UzRit.jpg',
                        title='選擇服務',
                        text='請選擇',
                        actions=[
                            URIAction(
                                label='分享 bot',
                                uri='https://line.me/R/nv/recommendOA/@vbi2716y'
                            ),
                            URIAction(
                                label='PTT正妹網',
                                uri='https://ptt-beauty-infinite-scroll.herokuapp.com/'
                            ),
                            URIAction(
                                label='youtube 程式教學分享頻道',
                                uri='https://www.youtube.com/channel/UCPhn2rCqhu0HdktsFjixahA'
                            )
                        ]
                    )
                ]
            )
        )

        self.reply_message(carousel_template_message)


def start_template(self):
    buttons_template = TemplateSendMessage(
        alt_text='開始玩 template',
        template=ButtonsTemplate(
            title='選擇服務',
            text='請選擇',
            thumbnail_image_url='https://i.imgur.com/xQF5dZT.jpg',
            actions=[
                MessageTemplateAction(
                    label=MyDict.news_template,
                    text=MyDict.news_template
                ),
                MessageTemplateAction(
                    label=MyDict.movie_template,
                    text=MyDict.movie_template
                ),
                MessageTemplateAction(
                    label=MyDict.ptt_template,
                    text=MyDict.ptt_template
                ),
                MessageTemplateAction(
                    label=MyDict.beauty_template,
                    text=MyDict.beauty_template
                )
            ]
        )
    )
    self.reply_message(buttons_template)


def news_template(self):
    buttons_template = TemplateSendMessage(
        alt_text='新聞 template',
        template=ButtonsTemplate(
            title='新聞類型',
            text='請選擇',
            thumbnail_image_url='https://i.imgur.com/vkqbLnz.png',
            actions=[
                MessageTemplateAction(
                    label=MyDict.apple_news,
                    text=MyDict.apple_news
                ),
                MessageTemplateAction(
                    label=MyDict.technews,
                    text=MyDict.technews
                ),
                MessageTemplateAction(
                    label=MyDict.panx,
                    text=MyDict.panx
                )
            ]
        )
    )
    self.reply_message(buttons_template)


def movie_template(self):
    buttons_template = TemplateSendMessage(
        alt_text='電影 template',
        template=ButtonsTemplate(
            title='服務類型',
            text='請選擇',
            thumbnail_image_url='https://i.imgur.com/sbOTJt4.png',
            actions=[
                MessageTemplateAction(
                    label=MyDict.movie,
                    text=MyDict.movie
                ),
                MessageTemplateAction(
                    label=MyDict.eyny_movie,
                    text=MyDict.eyny_movie
                ),
                MessageTemplateAction(
                    label=MyDict.youtube_video,
                    text=MyDict.youtube_video
                )
            ]
        )
    )
    self.reply_message(buttons_template)


def ptt_template(self):
    buttons_template = TemplateSendMessage(
        alt_text='看廢文 template',
        template=ButtonsTemplate(
            title='你媽知道你在看廢文嗎',
            text='請選擇',
            thumbnail_image_url='https://i.imgur.com/ocmxAdS.jpg',
            actions=[
                MessageTemplateAction(
                    label=MyDict.ptt_hot,
                    text=MyDict.ptt_hot
                ),
                MessageTemplateAction(
                    label=MyDict.ptt_gossiping,
                    text=MyDict.ptt_gossiping
                )
            ]
        )
    )
    self.reply_message(buttons_template)


def beauty_template(self):
    buttons_template = TemplateSendMessage(
        alt_text='正妹 template',
        template=ButtonsTemplate(
            title='選擇服務',
            text='請選擇',
            thumbnail_image_url='https://i.imgur.com/qKkE2bj.jpg',
            actions=[
                MessageTemplateAction(
                    label=MyDict.ptt_beauty,
                    text=MyDict.ptt_beauty
                ),
                MessageTemplateAction(
                    label=MyDict.imgur_beauty,
                    text=MyDict.imgur_beauty
                ),
                MessageTemplateAction(
                    label=MyDict.random_beauty,
                    text=MyDict.random_beauty
                )
            ]
        )
    )
    self.reply_message(buttons_template)


def imgur_bot_template(self):
    carousel_template_message = TemplateSendMessage(
        alt_text='ImageCarousel template',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/g8zAYMq.jpg',
                    action=URIAction(
                        label='加我好友試玩',
                        uri='https://line.me/R/ti/p/%40gmy1077x'
                    ),
                ),
            ]
        )
    )
    self.reply_message(carousel_template_message)


class ImageStrategy(TaskStrategy):
    def execute(self):
        # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
        sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                       107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                       126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
        index_id = random.randint(0, len(sticker_ids) - 1)
        sticker_id = str(sticker_ids[index_id])
        sticker_message = StickerSendMessage(
            package_id='1',
            sticker_id=sticker_id
        )
        self.reply_message(sticker_message)
