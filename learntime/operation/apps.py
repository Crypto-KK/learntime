from django.apps import AppConfig


class OperationConfig(AppConfig):
    name = 'learntime.operation'

    def ready(self):
        try:
            import learntime.operation.signals
        except ImportError:
            pass
