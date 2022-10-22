from msilib.schema import Error

from parser import parse_from_postit
from goo_labs import get_morph

import os
from argparse import ArgumentParser

from wordcloud import WordCloud
from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FileMessage, ImageSendMessage)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    try:
        message_content = line_bot_api.get_message_content(event.message.id)
        # TODO: iteratorに複数ある場合の対処
        text = next(message_content.iter_content()).decode()
        
        # TODO: テキストファイルじゃないものが送られてきた時の対処。(Excelファイルなら別途それ用のパーサー作りたい)
        response = parse_from_postit(text)

        # とりあえず結合したリストでワードクラウド作成
        # TODO: せっかくグループ分けしているのでいつか活用する
        entire_words = ' '.join(sum([element['list'] for element in response['data']],[]))
        text = ' '.join(get_morph(entire_words))
        wordcloud = WordCloud(
            width=800,
            height=600,
            font_path='komorebi-gothic.ttf',
            background_color="white",
        ).generate(text)
        filename = response['title'].replace(' ', '_').replace('　', '_') + str(event.timestamp) + '.png'

        wordcloud.to_file('./static/' + filename)

        url = request.url_root + '/static/' + filename
        app.logger.info("url=" + url)
        line_bot_api.push_message(
            event.source.user_id,
            ImageSendMessage(url, url)
        )
    except Error as e:
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text='エラーが発生しました。再度お試しください。')
        )
        print(e)

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
