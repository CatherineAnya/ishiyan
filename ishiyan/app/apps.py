from django.apps import AppConfig
from suit.apps import DjangoSuitConfig


class AppConfig(AppConfig):
    name = 'app'
    verbose_name = '爱实验'


class SuitConfig(DjangoSuitConfig):
    layout = 'vertical'

    def ready(self):
        super().ready()

