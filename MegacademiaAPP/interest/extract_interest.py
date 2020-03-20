from jieba.analyse import set_stop_words, extract_tags
from json import load
from re import sub
from pyquery import PyQuery
from MegacademiaAPP.interest.load_stop_word import get_stop_word_list_file_path
from MegacademiaAPP.util import load_config
from MegacademiaAPP.interest import mg_api as MgAPI
from urllib.parse import urlparse
from django.core.cache import cache
from MegacademiaAPP.interest.word2vec_process import get_key_vector, get_init_vec, cos_sim
import requests


class InterestInfo:
    """兴趣信息类"""

    # 类型权值（静态变量） 0->原创 1->关注  2->点赞 3->简介
    __type_weight = []

    def __init__(self, name):
        """
        设置兴趣名
        :param name:
        """
        # 兴趣名
        self.__interest_name = name
        # 开关变量 0->不存在 1->存在
        self.__switch_vars = [0, 0, 0, 0]
        # 项权值
        self.__weight = [0.0, 0.0, 0.0, 0.0]
        # 综合权值
        self.__weight_general = 0.0
        if len(InterestInfo.__type_weight) == 0:
            InterestInfo.__load_config()

    def set_weight(self, type_index, value):
        """
        设置分项权值
        :param type_index: 项索引值
        :param value: 项权值
        """
        self.__switch_vars[type_index] = 1
        self.__weight[type_index] = value

    def get_weight(self, type_index):
        """
        获得分项权值
        :param type_index: 项索引值
        """
        return self.__weight[type_index]

    def get_name(self):
        """
        获得分项权值
        """
        return self.__interest_name

    def get_weight_general(self):
        """
        获得综合权值
        """
        if self.__weight_general == 0.0:
            self.__calculate_weight_general()
        return self.__weight_general

    # def __calculate_weight_general(self):
    #     """
    #     计算综合权值
    #     综合权值 = 个体兴趣权值 * 个体兴趣开关变量 + 交互兴趣权值 * 交互兴趣开关变量
    #     :return: 综合权值
    #     """
    #     # 设置个体交互开关变量
    #     switch_var_interaction = self.__switch_vars[1] | self.__switch_vars[2]
    #     weight_interaction = self.__calculate_weight_interaction()
    #     self.__weight_general = self.__switch_vars[0] * self.__weight[0] + switch_var_interaction * weight_interaction

    # def __calculate_weight_interaction(self):
    #     """
    #     计算交互兴趣权值
    #     交互兴趣权值 = 关注兴趣值 * 关注兴趣权值 * 关注兴趣开关变量 + 点赞兴趣值 * 点赞兴趣权值 * 点赞兴趣开关变量
    #     关注/点赞兴趣值：该关键词在关注/点赞动态中所占的权值
    #     关注/点赞兴趣权值：关注兴趣或者点赞兴趣在用户交互兴趣中所占的权值
    #     :return: 交互兴趣权值
    #     """
    #     following_weight = self.__weight[1] * self.__type_weight[0]
    #     like_weight = self.__weight[2] * self.__type_weight[1]
    #     weight_interaction = self.__switch_vars[1] * following_weight + self.__switch_vars[2] * like_weight
    #     return weight_interaction

    def __calculate_weight_general(self):
        """
        计算综合权值
        综合权值 = 原创兴趣值 * 原创兴趣开关变量 + 关注兴趣值 * 关注开关变量 + 点赞兴趣值 * 点赞兴趣开关变量 + 简介兴趣值 * 简介兴趣开关变量
        XX兴趣值 = 某词在该兴趣中的TF-IDF值 * XX兴趣占综合权值中的权值
        :return: 综合权值
        """
        result = 0.0
        for i in range(4):
            result += self.__weight[i] * self.__type_weight[i] * self.__switch_vars[i]
        self.__weight_general = result

    @classmethod
    def __load_config(cls):
        InterestInfo.__type_weight = load_config('type_weight')
        # try:
        #     config_path = os.path.split(
        #         os.path.realpath(__file__))[0] + os.sep + 'config.json.json'
        #     if not os.path.isfile(config_path):
        #         sys.exit(u'当前路径：%s 不存在配置文件config.json' %
        #                  (os.path.split(os.path.realpath(__file__))[0] + os.sep))
        #     with open(config_path) as f:
        #         try:
        #             config.json = json.loads(f.read())
        #         except ValueError:
        #             sys.exit(u'config.json.json.json 格式不正确，请参考 '
        #                      u'https://github.com/dataabc/weiboSpider#3程序设置')
        #     InterestInfo.__type_weight = config.json.get('type_weight')
        # except Exception as e:
        #     print('Error: ', e)
        #     print_exc()


def load_data(is_weibo=True, user_id='', user_token='', user_note=''):
    """
    加载数据
    :param is_weibo: True 微博模式  False Megacademia 模式
    :param user_id: Megacademia数据
    :param user_token: 用户token（Megacademia 模式）
    :param user_note: 用户个人简介（Megacademia 模式）
    :return: 原始关注、原创、点赞的动态内容数据合集
    """
    if is_weibo:
        raw_text = load_weibo_data()
    else:
        raw_text = load_mg_data(user_id=user_id, user_token=user_token, user_note=user_note)
    return raw_text


def load_weibo_data():
    """
    加载微博数据
    :return: 微博数据
    """
    raw_text = []  # 0->原创 1->关注 2->点赞 3->简介
    with open('MegacademiaAPP/interest/data/self_statuses.json', 'r') as self_file:
        raw_text.append(load(self_file))
    with open('MegacademiaAPP/interest/data/weibo_data.json', 'r') as following_file:
        raw_text.append(load(following_file))
    with open('MegacademiaAPP/interest/data/like_statuses.json', 'r') as like_file:
        raw_text.append(load(like_file))
    return raw_text


def load_mg_data(user_id='', user_token='', user_note=''):
    """
    加载Megacademia数据
    :param user_id: Megacademia数据
    :param user_token: 用户token（Megacademia 模式）
    :param user_note: 用户个人简介（Megacademia 模式）
    :return: Megacademia数据
    """
    # 0->原创 1->关注 2->点赞 3->简介
    raw_text = [
        load_mg_statuses_data(user_token=user_token, url=MgAPI.get_someone_statuses(user_id)),
        load_mg_statuses_data(user_token=user_token, url=MgAPI.get_home_timeline()),
        load_mg_statuses_data(user_token=user_token, url=MgAPI.get_favourite_statuses(), enable_link_header=True),
        # requests.get(url=MgAPI.get_user_info(user_id)).json()
        user_note
    ]
    return raw_text


def load_mg_statuses_data(user_token='', url='', enable_link_header=False):
    """
    加载Megacademia 动态数据
    :param user_token: 用户token（Megacademia 模式）
    :param url: url
    :param enable_link_header: 启用enable_link_header
    :return: Megacademia动态数据
    """
    headers = {'Authorization': user_token}
    # 默认加载100条动态
    num = 100
    statuses = []
    max_id = ''
    while num > 0:
        if num == 100:
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


def __extract_string_tag(content='', k=10):
    """
    提取文本关键词及权值
    :param content: 文本内容
    :param k: 提取数量
    :return: 文本关键词及权值
    """
    # 去除HTML标签、URL和结尾空格
    url_reg = r'[a-z]*[:.]+\S+'  # URL 正则表达式
    tmp = sub(url_reg, '', PyQuery(content).text().rstrip())
    # jieba分词、去停用词、计算TF-IDF、提取关键词
    set_stop_words(get_stop_word_list_file_path())
    tags = extract_tags(tmp, topK=k, withWeight=True)
    return tags


def extract_key_words(statuses, is_weibo=True, is_note=False):
    """
    提取关键词
    :param statuses: 输入动态集
    :param is_weibo: True 微博模式  False Megacademia 模式
    :param is_note: True 是个人简介  False 非个人简介
    :return: 关键词集
    """
    # 合并动态内容
    raw_str = ''
    if is_weibo:
        for status in statuses['weibo']:
            raw_str += status['content']
    else:
        if is_note:
            raw_str += statuses
            # raw_str += statuses['note']
        else:
            # 临时措施 【待修改】
            for status in statuses:
                raw_str += status['content']

    # # 去除HTML标签、URL和结尾空格
    # url_reg = r'[a-z]*[:.]+\S+'  # URL 正则表达式
    # tmp = sub(url_reg, '', PyQuery(raw_str).text().rstrip())
    #
    # # jieba分词、去停用词、计算TF-IDF、提取关键词
    # set_stop_words(get_stop_word_list_file_path())
    # tags = extract_tags(tmp, topK=10, withWeight=True)
    tags = __extract_string_tag(content=raw_str, k=10)
    return tags


def extract_interest(is_weibo=True, user_id='', user_token='', user_note=''):
    """
    提取用户兴趣
    :param is_weibo: True 微博模式  False Megacademia 模式
    :param user_id: 用户ID（Megacademia 模式）
    :param user_token: 用户token（Megacademia 模式）
    :param user_note: 用户个人简介（Megacademia 模式）
    """
    # 加载用户微博数据
    raw_text = load_data(is_weibo=is_weibo, user_id=user_id, user_token=user_token, user_note=user_note)
    # 提取原始兴趣关键词
    interest_info_collection = {}   # 兴趣关键词信息集合（并集）
    for single_text_collection in raw_text:
        current_index = raw_text.index(single_text_collection)  # 获取当前处理动态集序号 0->原创 1->关注 2->点赞 3->简介
        # 获取当前动态集原始兴趣：Jieba分词、去停用词、结算TF-IDF值
        current_status_interests = extract_key_words(single_text_collection, is_weibo=is_weibo, is_note=(current_index == 3))
        # 设置当前动态集每个动态的动态信息
        for interest in current_status_interests:
            interest_name = interest[0]
            interest_weight = interest[1]
            # 检查当前兴趣名长度是否大于1
            if len(interest_name) > 1:
                # 检查当前兴趣是否已经存在于兴趣关键词信息集合
                if interest_name in interest_info_collection:
                    interest_info_collection[interest_name].set_weight(current_index, interest_weight)
                else:
                    interest_info_collection[interest_name] = InterestInfo(interest_name)
                    interest_info_collection[interest_name].set_weight(current_index, interest_weight)
    # 计算每个兴趣的综合权重归一化后的值
    interests = {}
    for key, value in interest_info_collection.items():
        print("%s : %f" % (key, value.get_weight_general()))
    for value in interest_info_collection.values():
        interests[value.get_name()] = value.get_weight_general()
    weight_values = interests.values()
    max_weight = max(weight_values)
    for key, value in interests.items():
        interests[key] = value / max_weight
    return interests


def get_top_k(is_weibo=True, user_id='', user_token='', user_note='', k=1):
    """
    获取排名前K的兴趣
    :param is_weibo: True 微博模式  False Megacademia 模式
    :param user_id: 用户ID（Megacademia 模式）
    :param user_token: 用户token（Megacademia 模式）
    :param user_note: 用户个人简介（Megacademia 模式）
    :param k: 前K个兴趣，注意大小不能超过兴趣数量
    :return: 排名前K的兴趣的JSON格式结果
    """
    user_interest = cache.get('%s_IST' % user_id)
    # 命中缓存
    if user_interest is not None:
        # print("Redis hit %s" % user_id)
        cache_note = user_interest['note']
        if cache_note == user_note:
            # print("note not change")
            result = user_interest['info']
            # print(result)
            return result
    # 未命中缓存或者个人简介发生变更
    interests = extract_interest(is_weibo=is_weibo, user_id=user_id, user_token=user_token, user_note=user_note)
    interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
    temp = {}
    if len(interests) < k:
        print("Error: Out of range, %d is bigger than %d, which is the length of interest list" % (k, len(interests)))
        for interest in interests:
            # print("%s  %f" % (interest[0], interest[1]))
            temp[interest[0]] = interest[1]
    else:
        for i in range(k):
            # print("%s  %f" % (interests[i][0], interests[i][1]))
            temp[interests[i][0]] = interests[i][1]
    data = []
    interest_vec = get_init_vec()
    for key, value in temp.items():
        data.append({'interest_name': key, 'weight': value})
        interest_vec += get_key_vector(key) * value
    # print(interest_vec)
    result = {'interest': data}
    # 保存到缓存中（缓存一周 604800s）
    interest_info = {
        "note": user_note,
        "info": result,
        "interest_vector": interest_vec
    }
    cache.set('%s_IST' % user_id, interest_info, timeout=604800)
    # print(result)
    return result


def __get_search_result(user_token='', q=''):
    """
    查询操作
    :param user_token: user token
    :param q: 查询值
    :return: 查询结果
    """
    headers = {'Authorization': user_token}
    data = {'q': q, 'limit': 40}
    response = requests.get(url=MgAPI.search(), headers=headers, data=data)
    return response.json()


def __extract_status_interest_sim(content='', interest_vec=get_init_vec()):
    """
    获取动态关键词向量
    :param content: 动态内容
    :return: 关键词向量
    """
    tags = __extract_string_tag(content=content, k=3)
    if len(tags) < 3:
        return 0.0
    tag_vec = get_init_vec()
    for tag in tags:
        tag_name = tag[0]
        tag_weight = tag[1]
        tag_vec += get_key_vector(tag_name) * tag_weight
    return cos_sim(interest_vec, tag_vec)


def get_interest_status(user_id='', user_token='', q=''):
    """
    获取用户兴趣动态
    :param user_id: Megacademia 用户id
    :param user_token: user token
    :param q: 查询值
    :return: 查询结果
    """
    raw_data = __get_search_result(user_token=user_token, q=q)
    user_interest = cache.get('%s_IST' % user_id)
    # 命中缓存：进行兴趣比对；未命中缓存：直接返回原始查询结果
    if user_interest is not None:
        # print("Redis hit %s" % user_id)
        user_interest_vec = user_interest['interest_vector']
        raw_statuses = raw_data['statuses']
        # print("before:")
        # print(raw_data)
        interest_sim = {}
        id_map = {}
        curr_id = 0
        for raw_status in raw_statuses:
            id_map[curr_id] = raw_status
            interest_sim[curr_id] = __extract_status_interest_sim(content=raw_status['content'], interest_vec=user_interest_vec)
            curr_id += 1
        sorted_interest_sim = sorted(interest_sim.items(), key=lambda x: x[1], reverse=True)
        # print(sorted_interest_sim)
        statuses = []
        max_id = int(0.2*len(sorted_interest_sim))
        count = 0
        for status_id in sorted_interest_sim:
            statuses.append(id_map[status_id[0]])
            count += 1
            if count == max_id:
                break
        raw_data['statuses'] = statuses
        # print("after:")
        # print(raw_data)
    return raw_data