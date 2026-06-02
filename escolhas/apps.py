from django.apps import AppConfig


class EscolhasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "escolhas"

    def ready(self):
        """
        Importa os signals quando a aplicação estiver pronta.
        """
        import escolhas.signals  # noqa
