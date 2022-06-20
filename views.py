from rest_framework import viewsets
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import InBBoxFilter
from . import models, serializers

from diana.abstract.views import CountModelMixin, GenericPagination
from diana.abstract.models import get_fields, DEFAULT_EXCLUDE


class WorkPageViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    
    queryset = models.Work.objects.all()
    serializer_class = serializers.WorkPageSerializer
    pagination_class = GenericPagination

    filter_backends = [DjangoFilterBackend]
    filterset_fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['page__text_vector'])

class PageViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer
    pagination_class = GenericPagination

    # GIS filters
    filter_backends = [DjangoFilterBackend]
    filterset_fields = get_fields(models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector'])

    schema = AutoSchema()