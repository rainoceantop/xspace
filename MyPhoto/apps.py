from django.apps import AppConfig


class MyphotoConfig(AppConfig):
    name = 'MyPhoto'

    def ready(self):
        import MyPhoto.signals
