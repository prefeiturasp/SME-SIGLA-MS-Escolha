from .escolha import EscolhaViewSet
from .escola import EscolaViewSet
from .dre import DreViewSet
from .vagas_escolas import VagasEscolasViewSet
from .parametrizacao import ParametrizacaoViewSet
from .swagger import SwaggerFromFileView

__all__ = [
    'EscolhaViewSet',
    'EscolaViewSet',
    'DreViewSet',
    'VagasEscolasViewSet',
    'ParametrizacaoViewSet',
    'SwaggerFromFileView',
] 