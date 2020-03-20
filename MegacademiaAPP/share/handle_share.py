from os.path import join
from django.core.cache import cache
from MegacademiaAPP.models import SharingFileInfo
from MegacademiaAPP.util import load_config
import hashlib


def handle_upload_file(my_file, user_id):
    """
    处理上传文件
    :param my_file: 上传的文件
    :return:
    """
    # 计算文件MD5
    md5_obj = hashlib.md5()
    while True:
        d = my_file.read(8096)
        if not d:
            break
        md5_obj.update(d)
    hash_code = md5_obj.hexdigest()
    md5 = str(hash_code).lower()
    # 检查缓存
    file_path = cache.get('%s_FP' % md5)
    if file_path is not None:
        print("Redis hit: %s" % file_path)
    else:
        print("No cache")
        # 检查数据库是否有记录
        md5_check = SharingFileInfo.objects.filter(file_md5=md5)
        if len(md5_check) != 0:
            print("Find record at database: %s" % md5_check[0].file_md5)
        else:
            print("New record")
            file_name = my_file.name.split('.')
            storage_path = load_config('storage_path')
            file_path = join(storage_path, '%s.%s' % (md5, file_name[-1]))
            with open(file_path, 'wb+') as destination:
                for chunk in my_file.chunks():
                    destination.write(chunk)
            # 保存文件信息
            file_info = SharingFileInfo(file_name=my_file.name, file_md5=md5, file_path=file_path, uploader_id=user_id)
            file_info.save()
    # 保存缓存(一天)
    cache.set('%s_FP' % md5, file_path, timeout=86400)
    extended_server_domain = load_config('extended_server_domain')
    sharing_url = '%s/api/v1/extend/sharing_file/%s' % (extended_server_domain, md5)
    return sharing_url


def handle_download_file(sharing_code):
    """
    下载文件
    :param sharing_code: 分享码
    :return: 下载文件
    """
    # 检查缓存
    file_path = cache.get('%s_FP' % sharing_code)
    if file_path is not None:
        print("Redis hit: %s" % file_path)
    else:
        # 检查数据库
        md5_check = SharingFileInfo.objects.filter(file_md5=sharing_code)
        if len(md5_check) != 0:
            print("Find record at database: %s" % md5_check[0].file_path)
            file_path = md5_check[0].file_path
        else:
            print('Invalid sharing code: %s' % sharing_code)
            return None
    print("file path: %s" % str(file_path))
    with open(str(file_path), 'rb') as file_location:
        my_file = file_location.read()
    # 保存缓存(一天)
    cache.set('%s_FP' % sharing_code, file_path, timeout=86400)
    return my_file