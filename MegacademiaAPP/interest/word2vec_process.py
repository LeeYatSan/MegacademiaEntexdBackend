from gensim.models import KeyedVectors
import numpy as np

# wv_from_text = KeyedVectors.load_word2vec_format(r'mg_santi_word2vec_binary.bin', binary=True)
wv_from_text = KeyedVectors.load_word2vec_format(r'MegacademiaAPP/interest/mg_santi_word2vec_binary.bin', binary=True)

#导入模型
# file = 'Tencent_AILab_ChineseEmbedding/Tencent_AILab_ChineseEmbedding.txt'
# file = 'Tencent_AILab_ChineseEmbedding_Min.txt'
# wv_from_text = KeyedVectors.load_word2vec_format(file, binary=False)
wv_from_text.init_sims(replace=True)


# 未知词、短语向量补齐
def compute_ngrams(word, min_n, max_n):
    # BOW, EOW = ('<', '>')  # Used by FastText to attach to all words as prefix and suffix
    extended_word =  word
    ngrams = []
    for ngram_length in range(min_n, min(len(extended_word), max_n) + 1):
        for i in range(0, len(extended_word) - ngram_length + 1):
            ngrams.append(extended_word[i:i + ngram_length])
    return list(set(ngrams))


def __word_vector(word, wv_from_text, min_n=1, max_n=3):
    '''
    ngrams_single/ngrams_more,主要是为了当出现oov的情况下,最好先不考虑单字词向量
    '''
    # # 确认词向量维度
    # word_size = wv_from_text.vectors.shape[0]
    # 计算word的ngrams词组
    ngrams = compute_ngrams(word, min_n=min_n, max_n=max_n)
    # 如果在词典之中，直接返回词向量
    if word in wv_from_text.vocab.keys():
        return wv_from_text[word]
    else:
        # 不在词典的情况下
        word_vec = np.zeros(200, dtype=np.float32)
        # word_vec = np.zeros(word_size, dtype=np.float32)
        ngrams_found = 0
        ngrams_single = [ng for ng in ngrams if len(ng) == 1]
        ngrams_more = [ng for ng in ngrams if len(ng) > 1]
        # 先只接受2个单词长度以上的词向量
        for ngram in ngrams_more:
            if ngram in wv_from_text.vocab.keys():
                word_vec += wv_from_text[ngram]
                ngrams_found += 1
                #print(ngram)
        # 如果，没有匹配到，那么最后是考虑单个词向量
        if ngrams_found == 0:
            for ngram in ngrams_single:
                try:
                    curr_vec = wv_from_text[ngram]
                except KeyError:
                    continue
                word_vec += curr_vec
                ngrams_found += 1
        if word_vec.any():
            return word_vec / max(1, ngrams_found)
        else:
            # raise KeyError('all ngrams for word %s absent from model' % word)
            return np.zeros(200, dtype=np.float32) / max(1, ngrams_found)


def get_key_vector(key):
    """
    获取某个词的词向量
    :param key: 查询词
    :return: 词向量
    """
    return __word_vector(key, wv_from_text, min_n=1, max_n=3)


def get_init_vec():
    return np.zeros(200, dtype=np.float32)


def cos_sim(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim


# vec0 = get_init_vec()
# vec1 = __word_vector('Java', wv_from_text, min_n=1, max_n=3)
# vec2 = __word_vector('JVM', wv_from_text, min_n=1, max_n=3)
# wv_from_text.most_similar(positive=[vec], topn=20)


# print(vec1)
# print(vec2)
# print(vec1*2)
# sim = cos_sim(vec1, vec2)
# print(sim)

# print(len(vec))
# print(len(wv_from_text.vocab))
# print(wv_from_text.most_similar(positive=['JVM'], topn=10))
# print(wv_from_text.similarity('虚拟机', 'JVM'))

