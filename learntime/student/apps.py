from django.apps import AppConfig


class StudentConfig(AppConfig):
    name = 'learntime.student'

    def ready(self):
        import learntime.student.signals
