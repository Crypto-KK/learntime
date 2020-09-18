import hashlib

from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework_jwt.compat import PasswordField
from rest_framework_jwt.settings import api_settings
from learntime.operation.models import StudentActivity
from learntime.student.models import SimpleStudent
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

class StudentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentActivity
        fields = ('activity_name', 'credit', 'credit_type', 'create_time', 'join_type', "status")

    join_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()


    def get_join_type(self, obj):
        join_type = int(obj.join_type)
        if join_type == 1:
            return "参加者"
        if join_type == 2:
            return "观众"
        if join_type == 3:
            return "工作人员"
        return "未知"

    def get_status(self, obj):
        status = int(obj.status)
        if status == 1:
            return "已报名"
        if status == 2:
            return "签到成功"
        if status == 3:
            return "签退成功"
        return "未知"


class MyJSONWebTokenSerializer(Serializer):
    """
    Serializer class used to validate a username and password.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(MyJSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields['uid'] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

    def gen_md5(self, src: str):
        m1 = hashlib.md5()
        m1.update(src.encode('utf-8'))
        return m1.hexdigest()

    def validate(self, attrs):
        credentials = {
            'uid': attrs.get('uid'),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = SimpleStudent.objects.get(uid=credentials['uid'])

            if user:
                if user.password == self.gen_md5(credentials['password']):
                    payload = jwt_payload_handler(user)
                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user
                    }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            raise serializers.ValidationError(msg)


class PasswordUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, max_length=20,
                                 error_messages={"max_length": "密码不能超过20个字符"})
    class Meta:
        model = SimpleStudent
        fields = ('password',)
