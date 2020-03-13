from datetime import datetime

from test_plus.test import TestCase

from activity.tests.test_views import get_temp_img
from learntime.activity.models import Activity


class ActivityModelsTest(TestCase):
    def setUp(self) -> None:
        self.user = self.make_user(username="testuser", password="123456")
        self.client.login(email="testuser@example.com", password="123456")
        self.test_image = get_temp_img()

        self.activity = Activity.objects.create(
            name="测试1",
            logo=self.test_image,
            sponsor="主办方",
            credit_type="fl_credit",
            place="dio",
            time="2019-02-02",
            deadline=datetime.now(),
            desc="dsfjsdklf"
        )

    def tearDown(self) -> None:
        self.test_image.close()

    def test_object_instance(self):
        assert isinstance(self.activity, Activity)
        assert isinstance(Activity.objects.all()[0], Activity)
