from urllib.parse import urlparse
from pyquery import PyQuery
from MegacademiaAPP.interest.load_stop_word import get_stop_word_list
from gensim.models import Word2Vec
from MegacademiaAPP.interest.mg_api import get_public_timeline
import requests
import re
import jieba.analyse


class MySentence(object):

    stop_word_list = get_stop_word_list()

    def __init__(self, statuses):
        self.statuses = statuses

    def __iter__(self):
        for status in self.statuses:
            status = status['content']
            if status == '':
                continue
            status = status
            # 去除HTML标签、URL和结尾空格、特殊符号
            url_reg = r'[a-z]*[:.]+\S+'  # URL 正则表达式
            status = re.sub(url_reg, '', PyQuery(status).text().rstrip())
            symbol_reg = '[^\u4e00-\u9fa5^a-z^A-Z^0-9]'
            status = re.sub(symbol_reg, ' ', status)
            status = ' '.join(status.split())
            # jieba.cut生成的是生成器，这里要转换为列表
            wordlist = list(jieba.cut(status))
            result = []
            for word in wordlist:
                # print('<%s:%d>' % (word, len(word)))
                if word not in MySentence.stop_word_list and len(word) > 1:
                    result.append(word)
            if len(result) > 0:
                print(result)
                yield result


def load_mg_statuses_data(user_token='', url='', enable_link_header=False):
    """
    加载Megacademia 动态数据
    :param user_token: 用户token（Megacademia 模式）
    :param url: url
    :param enable_link_header: 启用enable_link_header
    :return: Megacademia动态数据
    """
    headers = {'Authorization': user_token}
    # 默认加载10000条动态
    num = 100000
    statuses = []
    max_id = ''
    while num > 0:
        if num == 100000:
            response = requests.get(url=url, headers=headers)
            current_statuses = response.json()
        else:
            data = {'max_id': max_id}
            response = requests.get(url=url, headers=headers, data=data)
            current_statuses = response.json()
        current_statuses_length = len(current_statuses)
        if current_statuses_length > 0:
            statuses += current_statuses
            num -= current_statuses_length
            if enable_link_header:
                max_id = urlparse(response.links.get('next')['url']).query
            else:
                max_id = current_statuses[-1].get('id')
        else:
            break
    return statuses


def refresh_corpus():
    """
    更新语料库
    :return:
    """
    mg_statuses = load_mg_statuses_data(url=get_public_timeline())
    # 处理数据
    my_sentences = MySentence(statuses=mg_statuses)
    # 训练模型
    model = Word2Vec(sentences=my_sentences, size=200, window=10, min_count=3, workers=6)
    # 保存模型
    model.wv.save_word2vec_format(fname=r'MegacademiaAPP/interest/mg_santi_word2vec_binary.bin', binary=True)
    # model.wv.save_word2vec_format(fname=r'mg_santi_word2vec_binary.bin', binary=True)