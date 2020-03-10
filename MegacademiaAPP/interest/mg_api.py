from MegacademiaAPP.interest.util import load_config

domain = ''
api_v1 = ''


def load_domain():
    """
    加载主域名
    :return: 主域名
    """
    global domain
    global api_v1
    if domain == '':
        domain = load_config('domain')
        api_v1 = '%s/api/v1' % domain


def get_someone_statuses(user_id):
    load_domain()
    return '%s/accounts/%s/statuses' % (api_v1, user_id)


def get_home_time():
    load_domain()
    return '%s/timelines/home' % api_v1


def get_favourite_statuses():
    load_domain()
    return '%s/favourites' % api_v1


def get_user_info(user_id):
    load_domain()
    return '%s/accounts/%s' % (api_v1, user_id)