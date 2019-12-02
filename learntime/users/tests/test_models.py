from test_plus.test import TestCase


class TestUser(TestCase):

    def setUp(self) -> None:
        self.user = self.make_user()
        self.user.name = "user01"
        self.user.save()

    def test__str__(self):
        self.assertEqual(self.user.__str__(), "user01")
