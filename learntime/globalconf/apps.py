from django.apps import AppConfig


class GlobalconfConfig(AppConfig):
    name = 'learntime.globalconf'

    def ready(self):
        import learntime.globalconf.signals
