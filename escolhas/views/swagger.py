from django.conf import settings
from drf_spectacular.views import SpectacularSwaggerView


class SwaggerFromFileView(SpectacularSwaggerView):
    def _get_schema_url(self, request):
        url = super()._get_schema_url(request)
        print(settings.DJANGO_ENVIRONMENT)
        url_com_prefixo = f'{settings.MS_PATH}{url}' if settings.DJANGO_ENVIRONMENT != 'local' else url
        return url_com_prefixo
