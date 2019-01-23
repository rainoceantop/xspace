from django.apps import AppConfig


class HomespaceConfig(AppConfig):
    name = 'HomeSpace'

    def ready(self):
        import HomeSpace.signals
