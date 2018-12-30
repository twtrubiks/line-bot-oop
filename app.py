from config import Config
from flask import Flask, request, abort

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import StickerMessage, MessageEvent, \
    TextMessage

from strategy import TaskStrategy, eyny_movie, apple_news, \
    ptt_beauty, imgur_beauty, random_beauty, ptt_hot, \
    ptt_gossiping, movie, youtube_video, technews, panx, \
    oil_price

from strategy import TemplateStrategy, start_template, news_template, \
    movie_template, ptt_template, beauty_template, imgur_bot_template

from strategy import ImageStrategy

from my_dict import MyDict

config = Config()
handler = config.handler
app = Flask(__name__)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


class Bot:
    task_map = {
        MyDict.eyny_movie: eyny_movie,
        MyDict.apple_news: apple_news,
        MyDict.ptt_beauty: ptt_beauty,
        MyDict.imgur_beauty: imgur_beauty,
        MyDict.random_beauty: random_beauty,
        MyDict.ptt_hot: ptt_hot,
        MyDict.ptt_gossiping: ptt_gossiping,
        MyDict.movie: movie,
        MyDict.youtube_video: youtube_video,
        MyDict.technews: technews,
        MyDict.panx: panx,
        MyDict.oil_price: oil_price
    }

    template_map = {
        MyDict.start_template: start_template,
        MyDict.news_template: news_template,
        MyDict.movie_template: movie_template,
        MyDict.ptt_template: ptt_template,
        MyDict.beauty_template: beauty_template,
        MyDict.imgur_bot_template: imgur_bot_template,
    }

    def __init__(self, val):
        self.val = val
        self.special_handle()

    def strategy_action(self):
        strategy_class = None
        action_fun = None
        if self.val in self.task_map:
            strategy_class = TaskStrategy
            action_fun = self.task_map.get(self.val)
        elif self.val in self.template_map:
            strategy_class = TemplateStrategy
            action_fun = self.template_map.get(self.val)
        return strategy_class, action_fun

    def special_handle(self):
        if self.val.lower() == MyDict.eyny_movie:
            self.val = self.val.lower()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # print("event.reply_token:", event.reply_token)
    # print("event.message.text:", event.message.text)
    message = event.message.text
    bot = Bot(message)
    strategy_class, action_fun = bot.strategy_action()
    if strategy_class:
        task = strategy_class(action_fun, event)
        task.name = str(action_fun)
        task.execute()
        return 0
    default_task = TemplateStrategy(event=event)
    default_task.execute()


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # print("package_id:", event.message.package_id)
    # print("sticker_id:", event.message.sticker_id)
    image_strategy = ImageStrategy(event=event)
    image_strategy.execute()


if __name__ == '__main__':
    app.run()
