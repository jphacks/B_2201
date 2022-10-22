# TODO: get_morphとget_entiの共通処理をまとめる
# TODO: 10回試行してもエラーになった時にエラーを返す
# TODO: そもそも1秒x10回でいいのか検討（タイムアウトはもっと短い？逆に試行回数増えるほど時間延ばす？）

from dotenv import load_dotenv
load_dotenv()
import os

import requests

def get_morph(text):
    '''
    [形態素解析API](https://labs.goo.ne.jp/api/jp/morphological-analysis/)
    ・info_filterにて形態素情報フィルタ・・・form(表記)、pos(形態素)、read(読み)
    ・pos_filterにて[形態素品詞フィルタ](https://labs.goo.ne.jp/api/jp/morphological-analysis-pos_filter/)
    をフィルタできる。
    '''
    json_data = {
        'app_id': os.getenv('GOO_LABS_KEY'),
        'sentence': text,
        'info_filter': 'form',
        'pos_filter': '名詞',
    }

    res = requests.post('https://labs.goo.ne.jp/api/morph', json=json_data).json()
    return [item[0] for item in res['word_list'][0]]

def get_enti(text):
    '''
    [固有表現抽出API](https://labs.goo.ne.jp/api/jp/named-entity-extraction/)
    ・class_filterにて固有表現種別・・・ART(人工物名)、ORG(組織名)、PSN(人名)、LOC(地名)、DAT(日付表現)、TIM(時刻表現)、MNY(金額表現)、PCT(割合表現)
    をフィルタできる。
    '''
    output = {}
    counter = 0
    json_data = {
        'app_id': os.getenv('GOO_LABS_KEY'),
        'sentence': text,
        'class_filter': 'ART''|''ORG''|''PSN''|''LOC'
    }
    res = {}
    # エラーの場合は10回再試行するループ
    while counter < 10 and 'ne_list' not in res:
        res = requests.post('https://labs.goo.ne.jp/api/entity', json=json_data).json()
        if counter > 0:
            import time
            time.sleep(1)
            # 再試行は10回まで
            counter += 1

    for item in res['ne_list']:
        if not item[1] in output:
            output[item[1]] = [item[0]]
        else:
            output[item[1]].append(item[0])
    return output
    
if __name__ == '__main__':
    print(get_morph('今日はいい天気ですね。'))
    print(get_enti('子どもの日の今日、渋谷駅のハチ公前は大変混雑していますが、島原駅は空いています。'))