from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.context_processors import csrf
from MegacademiaAPP.interest.extract_interest import get_top_k, get_interest_status
from MegacademiaAPP.share.handle_share import handle_upload_file, handle_download_file


def handle_interest(request):
    """
    获取用户兴趣
    :param request: 请求
    :return: 用户兴趣集
    """
    if request.method == 'POST':
        # 用户ID
        user_id = request.POST.get('user_id')
        # 用户token
        user_token = request.POST.get('user_token')
        # 用户个人简介
        user_note = request.POST.get('user_note')
        # 模式 True->Weibo False->Megacademia
        mode = request.POST.get('mode')
        k = request.POST.get('num')
        if k == '':
            k = 10
        result = get_top_k(is_weibo=(mode == 'True'), user_id=user_id, user_token=user_token, user_note=user_note, k=int(k))
        return JsonResponse(result)
    else:
        return HttpResponse('Fail to get user\'s interest')


def upload_file(request):
    """
    上传分享文件
    :param request: 请求
    :return: 分享路径
    """
    if request.method == 'POST':
        my_file = request.FILES.get("file", None)
        user_id = request.POST.get('user_id')
        if my_file:
            sharing_path = handle_upload_file(my_file, user_id)
        return JsonResponse({'sharing_path': sharing_path})
    else:
        return HttpResponse('Fail to Upload')


def download_file(request, sharing_code=None):
    """
    下载分享文件
    :param request: 请求
    :param sharing_code: 分享码
    :return: 文件
    """
    if request.method == 'GET':
        if sharing_code is None:
            return JsonResponse({'file': ''})
        else:
            response = HttpResponse(handle_download_file(sharing_code))
            response['Content-Type'] = 'application/octet-stream'
            return response


def get_csrf(request):
    """
    生成 csrf 数据，发送给前端
    :param request:
    :return:
    """
    if request.method == 'GET':
        data = str(csrf(request)['csrf_token'])
        return JsonResponse({'csrf_token': data})


def get_interest_statuses(request):
    """
    获取感兴趣的动态
    :param request: 请求
    :return: 感兴趣的动态
    """
    if request.method == 'GET':
        # 用户ID
        user_id = request.GET.get('user_id')
        # 用户token
        user_token = request.GET.get('user_token')
        # 关键词
        q = request.GET.get('q')
        result = get_interest_status(user_id=user_id, user_token=user_token, q=q)
        return JsonResponse(result)
    else:
        return HttpResponse('Fail to get user interested statuses')