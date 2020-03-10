from os.path import isfile


# 获取停用词的List
def get_list_of_stop_words(filepath):
    f_stop = open(filepath)
    try:
        f_stop_text = f_stop.read()
    finally:
        f_stop.close()
    f_stop_seg_list = f_stop_text.split('\n')

    return f_stop_seg_list


# 保存List
def save_file(stop_word_list, filename):
    f_stop = open(filename, 'w')
    for item in range(len(stop_word_list)):
        if item != len(stop_word_list):
            f_stop.writelines(stop_word_list[item] + '\n')
        else:
            f_stop.writelines(stop_word_list[item])
    f_stop.close()


# 求List并集
def get_list_union(list_name):
    list_union = ['!']
    for item in list_name:
        # print item
        list_union.extend(get_list_of_stop_words(item))
    return list(set(list_union))


def load_stop_words(list_of_file_name, file_name='stopwords.txt',  reload=False):
    if isfile(file_name) and not reload:
        return get_list_of_stop_words(file_name)
    else:
        list_union = get_list_union(list_of_file_name)
        save_file(list_union, file_name)
        return list_union


def get_stop_word_list(customer_list_of_file_name=[]):
    if len(customer_list_of_file_name) == 0:
        list_of_file_name = [
            'MegacademiaAPP/interest/stop_word/中文停用词表.txt',
            'MegacademiaAPP/interest/stop_word/stopwords_en.txt',
            'MegacademiaAPP/interest/stop_word/stopwords_zh.txt',
            'MegacademiaAPP/interest/stop_word/四川大学机器智能实验室停用词库.txt',
            'MegacademiaAPP/interest/stop_word/哈工大停用词表.txt',
            'MegacademiaAPP/interest/stop_word/百度停用词表.txt'
        ]
        return load_stop_words(list_of_file_name, file_name='stopwords.txt', reload=False)
    else:
        list_of_file_name = customer_list_of_file_name
        return load_stop_words(list_of_file_name, file_name='stopwords.txt', reload=True)


def get_stop_word_list_file_path(customer_list_of_file_name=[]):
    file_path = 'stopwords.txt'
    if len(customer_list_of_file_name) == 0:
        list_of_file_name = [
            'MegacademiaAPP/interest/stop_word/中文停用词表.txt',
            'MegacademiaAPP/interest/stop_word/stopwords_en.txt',
            'MegacademiaAPP/interest/stop_word/stopwords_zh.txt',
            'MegacademiaAPP/interest/stop_word/四川大学机器智能实验室停用词库.txt',
            'MegacademiaAPP/interest/stop_word/哈工大停用词表.txt',
            'MegacademiaAPP/interest/stop_word/百度停用词表.txt'
        ]
        load_stop_words(list_of_file_name, file_name=file_path, reload=False)
    else:
        list_of_file_name = customer_list_of_file_name
        load_stop_words(list_of_file_name, file_name=file_path, reload=True)
    return file_path