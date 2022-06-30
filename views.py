from rest_framework import viewsets
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework_gis.filters import InBBoxFilter
from rest_framework import filters
from . import models, serializers
from django.db.models import F
from django.contrib.postgres.aggregates import ArrayAgg
from diana.abstract.views import CountModelMixin, GenericPagination
from diana.abstract.models import get_fields, DEFAULT_EXCLUDE

class WorkClusterViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):

    queryset = models.Work.objects.select_related('page__segments')

class AuthorViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    pagination_class = GenericPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = get_fields(models.Author, exclude=DEFAULT_EXCLUDE)
    search_fields = ['name', 'formatted_name']
    ordering_fields = ['name']
    ordering = ['name']

class WorkViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    queryset = models.Work.objects.all()
    serializer_class = serializers.WorkSerializer
    pagination_class = GenericPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE)

    search_fields = ['title', 'short_title']
    ordering_fields = ['main_author__name']
    ordering = ['main_author__name']

class WorkPageViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    
    queryset = models.Work.objects.all()
    serializer_class = serializers.WorkPageSerializer
    pagination_class = GenericPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['page__text_vector'])

class PageViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer
    pagination_class = GenericPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = get_fields(models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector'])

    schema = AutoSchema()

class SegmentViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    queryset = models.Segment.objects.all()
    serializer_class = serializers.SegmentSerializer
    pagination_class = GenericPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = get_fields(models.Segment, exclude=DEFAULT_EXCLUDE) 

    schema = AutoSchema()

class ClusterFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(field_name="segments__page__work__main_author",
                                            queryset=models.Author.objects.all())

    work = django_filters.ModelChoiceFilter(field_name="segments__page__work",
                                            queryset=models.Work.objects.all())

    class Meta:
        model = models.Cluster
        fields = ('author', 'work')


class ClusterViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):
    queryset = models.Cluster.objects.all()
    serializer_class = serializers.ClusterSerializer
    pagination_class = GenericPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filter_class = ClusterFilter
    filterset_fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE) 

    schema = AutoSchema()


class ExchangeViewSet(viewsets.ReadOnlyModelViewSet, CountModelMixin):

    serializer_class = serializers.ExchangeSerializer
    pagination_class = GenericPagination

    def get_queryset(self):
        """
        Returns a list of clusters in which the specified author is represented.
        """
        author = self.request.query_params.get('author')
        work = self.request.query_params.get('work')

        queryset = models.Cluster.objects

        if author:
            queryset = queryset.filter(id__in=models.Cluster.objects.filter(segments__page__work__main_author_id=author))

        if work:
            queryset = queryset.filter(id__in=models.Cluster.objects.filter(segments__page__work=work))

        queryset = (queryset
            .annotate(author=F("segments__page__work__main_author__id"), name=F("segments__page__work__main_author__name"))
            .values("size", "id", "author", "name")
            .exclude(author=author)
            .all()
            .order_by("-size")
            )

        
        return queryset