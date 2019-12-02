
from django.test import RequestFactory
from test_plus import TestCase

from learntime.users.views import AdminUpdateView


class BaseUserTestCase(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = self.make_user()


class TestUserUpdateView(BaseUserTestCase):

    def setUp(self) -> None:
        super(TestUserUpdateView, self).setUp()
        self.view = AdminUpdateView()
        request = self.factory.get('/fake')
        request.user = self.user
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        self.view.request = request


    def test_get_success_url(self):
        self.assertEqual(self.view.get_success_url(), '/users/admins/')

    def test_get_obj(self):
        self.assertEqual(self.view.get_object(), self.user)
