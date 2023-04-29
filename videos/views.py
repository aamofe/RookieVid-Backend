from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.

@csrf_exempt

def video_upload(request):
    if request.method=='POST':
        return JsonResponse({'errno':0,'msg':'上传成功'})
    return JsonResponse({'errno':1,'msg':'上传失败'})

