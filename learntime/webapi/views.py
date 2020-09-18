import hashlib
import json

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import throttle_classes, api_view
from rest_framework.throttling import AnonRateThrottle
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework_jwt.views import jwt_response_payload_handler
from rest_framework import mixins, viewsets

from rest_framework_jwt.settings import api_settings

from learntime.student.models import SimpleStudent
from learntime.operation.models import StudentActivity
from learntime.webapi.serializers import StudentActivitySerializer, PasswordUpdateSerializer
from learntime.webapi.authentication import MyJSONWebTokenAuthentication, MyIsAuthenticated
from learntime.webapi.throttle import  MyUserRateThrottle

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


@csrf_exempt
@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def login_view(request):
    if request.method == "POST":
        try:
            POST = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({
                "msg": "error decode body"
            })
        credentials = {
            'uid': POST.get('uid'),
            'password': POST.get('password')
        }
        if credentials['uid'].__len__() != 12:
            return JsonResponse({
                "msg": "学号格式错误"
            })
        if all(credentials.values()):
            try:
                user = SimpleStudent.objects.get(uid=credentials['uid'])
            except Exception as e:
                return JsonResponse({"msg": "学号或密码错误"})
            if user and user.password == gen_md5(credentials['password']):
                # 密码校验成功
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                response_data = jwt_response_payload_handler(token, user, request)
                return JsonResponse(response_data)
            else:
                # 查不到该用户
                return JsonResponse({'msg': '学号输入错误'})

        return JsonResponse({
            'msg': "请输入学号或密码"
        })

    else:
        return PermissionDenied()

def gen_md5(src: str):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()


class QueryViewSet(ListCacheResponseMixin, mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """查询参加记录"""
    authentication_classes = (MyJSONWebTokenAuthentication,)
    permission_classes = (MyIsAuthenticated,)
    serializer_class = StudentActivitySerializer
    throttle_classes = [MyUserRateThrottle]
    def get_queryset(self):
        activity_type = self.request.GET.get('type')
        obj = StudentActivity.objects\
            .select_related('student', 'activity')\
            .filter(student_id=self.request.user.uid)
        if activity_type and activity_type in ['思想品德素质', '创新创业素质', '法律素养', '身心素质', '文体素质']:
            obj = obj.filter(credit_type=activity_type)
        return obj


class ResetPasswordView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (MyJSONWebTokenAuthentication,)
    permission_classes = (MyIsAuthenticated,)
    serializer_class = PasswordUpdateSerializer

    def get_object(self):
        return self.request.user

