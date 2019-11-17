from django.apps import AppConfig


class ActivityConfig(AppConfig):
    name = 'learntime.activity'

    def ready(self):
        import learntime.activity.signals
