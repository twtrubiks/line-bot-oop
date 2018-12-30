# line-bot-oop

[Youtube Tutorial - 使用 oop 重構 ( refactor )-封裝 繼承 Singleton-PART 1](https://youtu.be/6j_IVQUH8yk)

[Youtube Tutorial - 使用 oop 重構 ( refactor )-Strategy-PART 2](https://youtu.be/fdPkZ3sqfI8)

本篇文章主要是將 [line-bot-tutorial](https://github.com/twtrubiks/line-bot-tutorial) repo refactor 成 oop 📝

oop 全名為 Object-oriented programming ( 物件導向 )，如不了解請自行 google :smile:

我會使用 code 說明一些我 refactor 的重點 ( design pattern )。

## 說明

### Singleton

首先，來看 [config.py](config.py)，

```python
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self, file='config.ini'):
        ......
```

這邊我主要是使用了 design pattern 中的 singleton ( 單例模式 )，可參考 [creating-a-singleton-in-python](https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python)，

什麼是 singleton，簡單說就是假如你希望一個系統中，某一個 class **只能出現一個** instance 時，就能使用它。

像這邊使用在 `Config` 就很適合，因為整個系統，我只需要一個 `Config` 的 instance，我不需要很多個，多個

除了浪費資源外，沒有什麼好處，看下面的例子，

```python
>>> from config import Config
>>> c1 = Config()
>>> c2 = Config()
>>> print( id(c1) == id(c2) ) # <1>
True
```

<1> 的部分為 `True`，代表它是同一個 instance ( 如果沒有使用 singleton，c1 和 c2 的 id 一定不一樣)。

### 封裝 和 繼承

接著看 [task.py](task.py)，

這裡主要是將原本寫的一堆 function programming 改成 oop，把每個功能 **封裝** 成 class，

然後使用到 **繼承** 的概念，說明如下，

```python
class Crawler:
    rs = requests.session()

    def __init__(self, target_url, method='get'):
        print('Start Crawler....{}'.format(self.__class__.__name__))
        self.url = target_url
        self.content = self.analyze(method)

    def analyze(self, method):
        .......
        return soup

class EynyMovie(Crawler):
    def parser(self):
        ......
        return result

    @staticmethod
    def pattern_mega(text):
        ......
        return match
```

我先定義 `Crawler` class，然後其他的功能 ( 像是 `EynyMovie` class ) 都去繼承這個 `Crawler`，

依照自己的需求再去實作 `parser` 這個 method。

這邊有使用到 `staticmethod`，如果你不了解，可參考 [What is the classmethod and staticmethod](https://github.com/twtrubiks/python-notes/tree/master/what_is_classmethod_and_staticmethod)。

以下再說明一個 `staticmethod` 的例子，

```python
class PttBeauty(Crawler):
    parser_page = 2  # crawler count
    push_rate = 10  # 推文

    def parser(self):
        url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'
        index_seqs = PttBeauty.get_all_index(self.content, url, self.parser_page)
        ......

    def crawler_info(self, res):
        ......

    @staticmethod
    def get_all_index(content, url, parser_page): # <1>
        max_page = PttBeauty.get_max_page(content.select('.btn.wide')[1]['href'])
        ......
        return queue

    @staticmethod
    def get_max_page(content): # <2>
        ......
        return int(page_number) + 1


class PttGossiping(Crawler):
    parser_page = 2  # crawler count

    def parser(self):
        url = 'https://www.ptt.cc/bbs/Gossiping/index{}.html'
        index_seqs = PttBeauty.get_all_index(self.content, url, self.parser_page) # <3>
        ......
```

因為 `PttBeauty` class 以及 `PttGossiping` class 都會使用到 `get_all_index` 以及 `get_max_page`

這兩個 function，所以我將它們加上 `staticmethod` (<1> 和 <2> )，然後看 <3> 的部分，這裡

直接使用 `PttBeauty.get_all_index()` 去得到我們需要的資訊。

雖然這邊也可以將 `get_all_index` 以及 `get_max_page` 這兩個 function 單獨抽出去，但為了

方便管理以及維護，統一寫在 `PttBeauty` class 中。

### Strategy

再來是 [strategy.py](strategy.py)，

這邊使用了 design pattern 中的 strategy ( 策略模式 )，

先來說明一下策略模式，主要是利用 python 是動態語言的關係，動態去抽換 function，

可參考 [python-patterns-strategy.py](https://github.com/faif/python-patterns/blob/master/behavioral/strategy.py)

```python
import type
class StrategyExample:
    def __init__(self, func=None):
        self.name = 'Strategy Example 0'
        if func is not None:
            self.execute = types.MethodType(func, self) # <1>

    def execute(self):
        print(self.name)

def execute_replacement1(self):
    print(self.name + ' from execute 1')

def execute_replacement2(self):
    print(self.name + ' from execute 2')

if __name__ == '__main__':
    strat0 = StrategyExample()

    strat1 = StrategyExample(execute_replacement1)
    strat1.name = 'Strategy Example 1'

    strat2 = StrategyExample(execute_replacement2)
    strat2.name = 'Strategy Example 2'

    strat0.execute()
    strat1.execute()
    strat2.execute()
```

<1> 的部分就是去抽換 function，有點 Monkey Patch 的概念，

`types.MethodType(func, self)` 的用法之前也介紹過了，

可參考 [What is the Monkey Patch](https://github.com/twtrubiks/fluent-python-notes/tree/master/what_is_the_Monkey_Patch)。

了解完 strategy 之後，接著來看如何應用，

這邊建立 3 個 strategy，然後主要繼承 `TaskStrategy` class，

程式碼請看 [strategy.py](strategy.py)，

```python
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

class TemplateStrategy(TaskStrategy):
    def execute(self):
        ......
        self.reply_message(carousel_template_message)

class ImageStrategy(TaskStrategy):
    def execute(self):
        ......
        self.reply_message(sticker_message)
```

`TaskStrategy` class，主要是給個別的 task ( 功能 ) 使用。

在 [task.py](task.py) 中，我們已經依照功能建立很多 class，

所以在這階段使用就很簡單，像是要呼叫新聞的爬蟲，

直接寫這樣即可，如下，

```python
def apple_news(self):
    task = AppleNews('https://tw.appledaily.com/new/realtime')
    self.reply_message(TextSendMessage(text=task.parser()))
```

依照 class 建立 instance，然後都去執行 parser 這個 method。

`TemplateStrategy` class，處理 template ( 清單顯示 )，所以獨立出來。

`ImageStrategy` class，專門處理圖片 ( 雖然目前只有一個 )。

最後是 [app.py](app.py)，

首先是 import 的部分，盡量不要使用 `from xx import *` 這種方法，

需要什麼再 import 就好，像是 `from xx import a,b,c` 這樣，另外

還要小心 **Circular Imports** 的問題，我之前也介紹過了，

可參考 [circular import](https://github.com/twtrubiks/python-notes/tree/master/python_circular_import)。

來看 `Bot` 這個 class，

```python
class Bot:
    # <1>
    task_map = {
        MyDict.eyny_movie: eyny_movie,
        .....
    }

    # <2>
    template_map = {
        MyDict.start_template: start_template,
        .....
    }

    def __init__(self, val):
        self.val = val
        self.special_handle()

    def strategy_action(self): # <3>
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
```

<1> 和 <2> 的部分主要是將 message 和 function 名稱 mapping 起來，

<3> 的部分則是 mapping Strategy ( strategy_class ) 以及 action ( action_fun )，

需要 <1> 和 <2> 的部分，主要是可以避免很多的 `if` `else`。

最後看 `handle_message` 的部分，

這邊和當初未 refactor ([app.py](https://github.com/twtrubiks/line-bot-tutorial/blob/master/app.py)) 的相比，明顯簡潔有力多了，

```python
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    bot = Bot(message)
    strategy_class, action_fun = bot.strategy_action() # <1>
    if strategy_class:
        # <2>
        task = strategy_class(action_fun, event)
        task.name = str(action_fun)
        task.execute()
        return 0
    default_task = TemplateStrategy(event=event) # <3>
    default_task.execute()
```

<1> 的部分得到 strategy_class 和 action_fun，

接著在 <2> 的部分直接將 strategy_class 和 action_fun 丟進去 ( 依照 strategy ) 就可以了。

最後 <3> 的部分則是 default 的 template 顯示 ( message 完全沒有 mapping )。

## 結論

功能和之前未 refactor ( [app.py](https://github.com/twtrubiks/line-bot-tutorial/blob/master/app.py) ) 的完全一模一樣，

主要是修改成 oop，然後應用一些 design patterns，方便後續的維護。

程式碼也都部署到 heroku 上了，有興趣可掃下面的 QRCODE 玩玩看:smile:

## 執行結果

line 的 QRCODE

![alt tag](http://i.imgur.com/Kkpzt4p.jpg)

或是手機直接點選 [https://line.me/R/ti/p/%40vbi2716y](https://line.me/R/ti/p/%40vbi2716y)

![alt tag](http://i.imgur.com/oAgR5nr.jpg)

## 執行環境

* Python 3.6.6

## Donation

文章都是我自己研究內化後原創，如果有幫助到您，也想鼓勵我的話，歡迎請我喝一杯咖啡:laughing:

![alt tag](https://i.imgur.com/LRct9xa.png)

[贊助者付款](https://payment.opay.tw/Broadcaster/Donate/9E47FDEF85ABE383A0F5FC6A218606F8)

## License

MIT license