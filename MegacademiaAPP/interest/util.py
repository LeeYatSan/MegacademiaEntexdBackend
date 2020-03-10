import json
import os
import sys
from traceback import print_exc


def load_config(attribute):
    """
    加载配置文件特定属性
    :return: 配置文件特定属性
    """
    try:
        config_path = os.path.split(
            os.path.realpath(__file__))[0] + os.sep + 'config.json'
        if not os.path.isfile(config_path):
            sys.exit(u'当前路径：%s 不存在配置文件config.json' %
                     (os.path.split(os.path.realpath(__file__))[0] + os.sep))
        with open(config_path) as f:
            try:
                config = json.loads(f.read())
            except ValueError:
                sys.exit(u'config.json.json 格式不正确，请参考 '
                         u'https://github.com/dataabc/weiboSpider#3程序设置')
        return config.get(attribute)
    except Exception as e:
        print('Error: ', e)
        print_exc()