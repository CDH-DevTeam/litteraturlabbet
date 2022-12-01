from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, BaseFilterBackend, OrderingFilter
from django_filters import rest_framework as filters
from . import models, serializers
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline
from rest_framework.compat import coreapi, coreschema
from django.utils.encoding import force_str
from diana.abstract.views import DynamicDepthViewSet
from diana.abstract.models import get_fields, DEFAULT_EXCLUDE

class FragmentFilter(BaseFilterBackend):

    search_param = 'search'
    search_title = 'Full-text search in the documents' # Shows up in DRF docs interactive query pop-up menu as the title for the query section of the field1
    search_description = 'Lists excerpts, or fragments, containing the search term.'

    def filter_queryset(self, request, queryset, view):


        config = 'simple'
        fragment_delimiter = '...<br/><br/>...'

        text          = request.query_params.get('search', None)

        max_fragments = request.query_params.get('max_fragments', 1000)
        max_words = request.query_params.get('max_words', 50)
        min_words = request.query_params.get('min_words', 10)

        if text:
            search_vector   = SearchVector("text_vector")
            search_query    = SearchQuery(text),
            search_rank     = SearchRank(search_vector, search_query)

            queryset = (
                queryset
                    .filter(text_vector=SearchQuery(text, search_type='raw', config=config))
                    .annotate(
                        excerpts = SearchHeadline(
                                    'text',
                                    SearchQuery(text, search_type='raw', config=config),
                                    config=config, 
                                    max_fragments=max_fragments, 
                                    max_words=max_words, 
                                    min_words=min_words, 
                                    fragment_delimiter=fragment_delimiter
                                )
                        # rank=search_rank
                        )

                    .order_by("id")
            )

        return queryset


    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
                coreapi.Field(
                    name=self.search_param,
                    required=False,
                    location='query',
                    schema=coreschema.String(
                        title=force_str(self.search_title),
                        description=force_str(self.search_description)
                    )
                )
            ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.search_description),
                'schema': {
                    'type': 'string',
                },
            },
        ]


class WorkFilter(filters.FilterSet):
    has_author = filters.NumberFilter(
        field_name='authors__id',
        lookup_expr='exact',
    )

    class Meta:
        model = models.Work
        fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['page__text_vector', 'authors'])


class ClusterFilter(filters.FilterSet):
    has_author = filters.NumberFilter(
        field_name='segments__page__work__authors__id',
        lookup_expr='exact',
        distinct=True
    )


    work = filters.NumberFilter(
        field_name='segments__page__work__id',
        lookup_expr='exact',
        distinct=True
    )
    class Meta:
        model = models.Cluster
        fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE)


class SegmentFilter(filters.FilterSet):
    has_author = filters.NumberFilter(
        field_name='page__work__authors__id',
        lookup_expr='exact',
        distinct=True
    )

    work = filters.NumberFilter(
        field_name='page__work__id',
        lookup_expr='exact',
        distinct=True
    )


    class Meta:
        model = models.Segment
        fields = get_fields(models.Segment, exclude=DEFAULT_EXCLUDE)


class AuthorFilter(filters.FilterSet):
    # in_cluster = filters.NumberFilter(
    #     field_name='works__pages__segments__cluster__id',
    #     lookup_expr='exact',
    # )

    class Meta:
        model = models.Author
        fields = get_fields(models.Author, exclude=DEFAULT_EXCLUDE)


class WorkPageViewSet(DynamicDepthViewSet):
    
    queryset = models.Work.objects.all()
    serializer_class = serializers.WorkPageSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['page__text_vector'])
    filter_class = WorkFilter
    search_fields = ['title', 'short_title', 'modernized_title', 'authors__name']


class PageViewSet(DynamicDepthViewSet):
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer

    # GIS filters
    filter_backends = [DjangoFilterBackend, FragmentFilter]
    filterset_fields = get_fields(models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector'])

class AuthorViewSet(DynamicDepthViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = get_fields(models.Author, exclude=DEFAULT_EXCLUDE)
    filter_class = AuthorFilter
    search_fields = ['name', 'surname', 'formatted_name']
    ordering = ["formatted_name"]


class ClusterViewSet(DynamicDepthViewSet): 
    queryset = models.Cluster.objects.all()
    serializer_class = serializers.ClusterSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_class = ClusterFilter
    ordering = ['-size']

class SegmentViewSet(DynamicDepthViewSet): 
    queryset = models.Segment.objects.all()
    serializer_class = serializers.SegmentSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_class = SegmentFilter
    search_fields = ['text']