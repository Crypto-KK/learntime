import tempfile

from PIL import Image
from django.test import override_settings
from test_plus import TestCase
from django.urls import reverse, resolve

from learntime.activity.models import Activity
from users.enums import RoleEnum



def get_temp_img():
    """什么临时图片文件并打开"""
    size = (200, 200)
    color = (255, 0, 0, 0)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        image = Image.new("RGB", size, color)
        image.save(f, "PNG")
    return open(f.name, mode="rb")


class ActivityViewsTest(TestCase):
    def setUp(self) -> None:
        self.user = self.make_user(username="testuser", password="123456")
        self.client.login(email="testuser@example.com", password="123456")
        self.test_image = get_temp_img()

    def tearDown(self) -> None:
        self.test_image.close()


    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_activity(self):
        response = self.client.post(
            reverse("activities:activity_create"),
            {
                "name": "测试活动",
                "logo": self.test_image,
                "sponsor": "主办方",
                "credit_type": "fl_credit",
                "place": "di",
                "time": "2019-02-02",
                "deadline": "2019-02-02",
                "desc": "Sdfsdf",

            }

        )
        assert response.status_code == 302
