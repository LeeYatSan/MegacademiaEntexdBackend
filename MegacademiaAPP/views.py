from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.context_processors import csrf
from MegacademiaAPP.interest.extract_interest import get_top_k


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


def get_csrf(request):
    """
    生成 csrf 数据，发送给前端
    :param request:
    :return:
    """
    if request.method == 'GET':
        data = str(csrf(request)['csrf_token'])
        return JsonResponse({'csrf_token': data})
