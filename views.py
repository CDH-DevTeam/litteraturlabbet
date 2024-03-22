from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, BaseFilterBackend, OrderingFilter
from django_filters import rest_framework as filters
from . import models, serializers
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline
from rest_framework.compat import coreapi, coreschema
from django.utils.encoding import force_str
from diana.abstract.views import DynamicDepthViewSet
from diana.abstract.models import get_fields, DEFAULT_EXCLUDE
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, Q
from rest_framework import viewsets, generics, response
from itertools import combinations
from .data.upload import *

class FragmentFilter(BaseFilterBackend):

    search_param = 'search'
    # Shows up in DRF docs interactive query pop-up menu as the title for the query section of the field1
    search_title = 'Full-text search in the documents'
    search_description = 'Lists excerpts, or fragments, containing the search term.'

    def filter_queryset(self, request, queryset, view):

        config = 'simple'
        fragment_delimiter = '...<br/><br/>...'

        text = request.query_params.get('search', None)

        max_fragments = request.query_params.get('max_fragments', 1000)
        max_words = request.query_params.get('max_words', 50)
        min_words = request.query_params.get('min_words', 10)

        if text:
            search_vector = SearchVector("text_vector")
            search_query = SearchQuery(text),
            search_rank = SearchRank(search_vector, search_query)

            queryset = (
                queryset
                .filter(text_vector=SearchQuery(text, search_type='raw', config=config))
                .annotate(
                    excerpts=SearchHeadline(
                        'text',
                        SearchQuery(
                            text, search_type='raw', config=config),
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
        fields = get_fields(
            models.Work, exclude=DEFAULT_EXCLUDE + ['page__text_vector', 'authors'])


class ClusterFilter(filters.FilterSet):
    has_author = filters.NumberFilter(
        field_name='segments__page__work__main_author__id',
        lookup_expr='exact',
        distinct=True
    )

    work = filters.NumberFilter(
        field_name='segments__page__work__id',
        lookup_expr='exact',
        distinct=True
    )

    year_start = filters.NumberFilter(
        field_name='segments__page__work__imprint_year',
        lookup_expr='gte',
        distinct=True
    )

    year_end = filters.NumberFilter(
        field_name='segments__page__work__imprint_year',
        lookup_expr='lte',
        distinct=True
    )
    class Meta:
        model = models.Cluster
        fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE)


class SegmentFilter(filters.FilterSet):
    has_author = filters.NumberFilter(
        field_name='page__work__main_author__id',
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
    search_fields = ['title', 'short_title',
                     'modernized_title', 'authors__name']


class Work19thCenturyViewSet(DynamicDepthViewSet):

    queryset = models.Work.objects.all().filter(Q(imprint_year__lte=1900) & Q(imprint_year__gte=1800))
    serializer_class = serializers.WorkPageSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['page__text_vector'])
    filter_class = WorkFilter
    search_fields = ['title', 'short_title',
                     'modernized_title', 'authors__name']


class PageViewSet(DynamicDepthViewSet):
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer

    # GIS filters
    filter_backends = [DjangoFilterBackend, FragmentFilter]
    filterset_fields = get_fields(
        models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector'])


class AuthorViewSet(DynamicDepthViewSet):
    work = models.Work.objects.all()
    # queryset = models.Author.objects.all()
    queryset = models.Author.objects.all().filter(id__in=list(work.values_list('main_author', flat=True)))
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

class GraphicViewSet(DynamicDepthViewSet):
    serializer_class = serializers.TIFFGraphicSerializer
    queryset = models.Graphics.objects.all()
    filterset_fields = get_fields(models.Graphics, exclude=DEFAULT_EXCLUDE + ['iiif_file', 'file', 'input_image', 'bbox', 'page', 'similar_extractions'])
    year_start = filters.NumberFilter(
        field_name='page__work__imprint_year',
        lookup_expr='gte',
        distinct=True
    )

    year_end = filters.NumberFilter(
        field_name='page__work__imprint_year',
        lookup_expr='lte',
        distinct=True
    )
    author = filters.NumberFilter(
        field_name='page__work__main_author__id',
        lookup_expr='exact',
        distinct=True
    )

    work = filters.NumberFilter(
        field_name='page__work__id',
        lookup_expr='exact',
        distinct=True
    )

class ClusterMetaViewSet(DynamicDepthViewSet):
    serializer_class = serializers.ClusterMetaViewSet
    queryset = models.ClsuterMeta.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['text']
    filterset_fields = get_fields(models.ClsuterMeta, exclude=DEFAULT_EXCLUDE+['extraction_images', 'distance'])

class NearestNeighboursViewSet(DynamicDepthViewSet):
    serializer_class = serializers.NearestNeighboursSerializer
    queryset = models.NearestNeighbours.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['text']
    filterset_fields = get_fields(models.NearestNeighbours, exclude=DEFAULT_EXCLUDE+['image', 'neighbours'])

class AuthorExchangeView(generics.ListAPIView):

    # serializer_class = serializers.AuthorExchangeSerializer
    # queryset = models.Cluster.objects\
    #     .annotate(
    #         authors=ArrayAgg('segments__page__work__main_author', filter=Q(segments__page__work__main_author__isnull=False), distinct=True),
    #         count=Count('segments__page__work__main_author', distinct=True))\
    #     .filter(count__gt=1)\
    #     .order_by('count')\
    #     .values()\
    #     .all()

    # def list(self, request):
    #     # Note the use of `get_queryset()` instead of `self.queryset`
    #     queryset = self.get_queryset()

    #     # Flatten the list and make all names unique
    #     d = {}
    #     for c in queryset:
    #         l = c['authors']

    #         for i in l:
    #             if i not in d.keys():
    #                 d[i] = {}
    #             for j in l:
    #                 if i != j:
    #                     if j not in d[i].keys():
    #                         d[i][j] = 0
    #                     else:
    #                         d[i][j] += 1

    #     edges = []
    #     for source, value in d.items():
    #         for target, weight in value.items():
    #             if weight > 0:
    #                 edges.append({"source": source, "target": target, "weight": weight})

    queryset = models.Cluster.objects.annotate(
        count=Count('segments__page__work__main_author'),
        authors=ArrayAgg('segments__page__work__main_author'),
        ).filter(count__gt=1)

    def list(self, request):
        import time
        d = {}
        t = time.process_time()
        for cluster in self.get_queryset():
            # authors = models.Author.objects.filter(work__pages__segments__cluster=cluster)

            for source, target in combinations(filter(lambda x: x != None, cluster.authors), 2):

                if source not in d.keys():
                    d[source ] = {}

                if target not in d[source].keys():
                    d[source][target] = 0

                d[source][target] += 1

        edges = []
        for source, value in d.items():
            for target, weight in value.items():
                if weight > 0 and source != target:
                    edges.append(
                        {"source": source, "target": target, "weight": weight})
        elapsed_time = time.process_time() - t
        print(elapsed_time)
        serializer = serializers.TargetSourceSerializer(edges, many=True)

        return response.Response(serializer.data)

 
class AuthorExchangeSegmentsView(DynamicDepthViewSet):
    serializer_class = serializers.ClusterInfoSerializer

    def get_queryset(self):
        source = self.request.GET["author_1"]
        target = self.request.GET["author_2"]
    
        queryset = models.Cluster.objects.annotate(
        count=Count('segments__series__main_author'),
        authors=ArrayAgg('segments__series__main_author'),
        ).filter(count__gt=1).filter(
            segments__series__main_author__id=source).filter(
            segments__series__main_author__id=target    
            )
        
        return queryset
    
# class PhraseSearchViewFast(DynamicDepthViewSet):
#     serializer_class = serializers.SegmentSerializer
#     def get_queryset(self):
#         phrase = self.request.GET["phrase"]
#         vector = SearchVector("text")
#         query = SearchQuery(phrase, search_type='phrase')
#         search_headline = SearchHeadline('text', query)
#         filtered_queryset = models.Segment.objects.annotate(rank=SearchRank(vector, query)).annotate(excerpt=search_headline).order_by('-rank')
#         unique_cluster_ids = filtered_queryset.values_list('cluster__id', flat=True).distinct()
#         additional_data_queryset = models.Segment.objects.filter(cluster__id__in=unique_cluster_ids)
#         queryset = filtered_queryset | additional_data_queryset
#         #queryset = filtered_queryset.prefetch_related(
#         #    Prefetch(
#         #        'cluster__segments',
#         #        queryset=additional_data_queryset,
#         #        to_attr='additional_data'
#         #    )
#         #)
#         return queryset
    
class PhraseSearchView(DynamicDepthViewSet):
    serializer_class = serializers.SegmentSerializer

    def get_queryset(self):
        phrase = self.request.GET["phrase"] 
        filtered_queryset = models.Segment.objects.filter(text__icontains=phrase)
        unique_cluster_ids = filtered_queryset.values_list('cluster__id', flat=True).distinct()
        additional_data_queryset = models.Segment.objects.filter(cluster__id__in=unique_cluster_ids)
        queryset = filtered_queryset | additional_data_queryset
        return queryset
    