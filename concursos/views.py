from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Cargo, Concurso
from .serializers import (
    CargoSerializer, 
    CargoListSerializer,
    CargoSelectSerializer,
    ConcursoSerializer, 
    ConcursoListSerializer,
    ConcursoSelectSerializer
)
from .utils import CustomPagination


class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.query_params.get('formato') == 'select':
                return CargoSelectSerializer
            return CargoListSerializer
        return CargoSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos os cargos.
        Se formato=select, retorna sem paginação.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Se for formato select, retornar sem paginação
        if request.query_params.get('formato') == 'select':
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        # Formato normal com paginação
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ConcursoViewSet(viewsets.ModelViewSet):
    queryset = Concurso.objects.all()
    serializer_class = ConcursoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['nome']
    search_fields = ['nome']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['-criado_em']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.query_params.get('formato') == 'select':
                return ConcursoSelectSerializer
            return ConcursoListSerializer
        return ConcursoSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos os concursos.
        Se formato=select, retorna sem paginação.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Se for formato select, retornar sem paginação
        if request.query_params.get('formato') == 'select':
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        # Formato normal com paginação
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
