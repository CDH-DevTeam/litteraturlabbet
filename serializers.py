from distutils import dep_util
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from diana.abstract.serializers import DynamicDepthSerializer
from diana.utils import DEFAULT_EXCLUDE
from . import models
from diana.abstract.models import get_fields


class PageSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    excerpts = serializers.CharField(default="")

    class Meta:
        model = models.Page
        fields = get_fields(models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['excerpts']

class WorkPageSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    class Meta:
        model = models.Work
        fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['pages']
        depth = 1

class AuthorSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    class Meta:
        model = models.Author
        fields = get_fields(models.Author, exclude=DEFAULT_EXCLUDE)
        depth = 1

class SegmentSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    class Meta:
        model = models.Segment
        fields = "__all__"
        # depth = 0

class TIFFGraphicSerializer(DynamicDepthSerializer):
    page = PageSerializer()  

    class Meta:
        model = models.Graphics
        fields = get_fields(models.Graphics, exclude=DEFAULT_EXCLUDE+['similar_extractions'])


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'page' in representation and isinstance(representation['page'], dict):
            # Exclude 'text' and 'text_vector' fields from the 'page' object
            page_data = representation['page']
            page_data.pop('text', None)
            page_data.pop('text_vector', None)
        return representation

class ClusterSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    # authors = AuthorSerializer(read_only=True, many=True)

    segments = SegmentSerializer
    works = WorkPageSerializer
    # authors = serializers.ListField(source='segments.page.work.authors', child=serializers.IntegerField())

    class Meta:
        model = models.Cluster
        fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE) + ['segments']
        depth = 4

class ClusterMetaViewSet(DynamicDepthSerializer):
    
        class Meta:
            model = models.ClsuterMeta
            fields = "__all__"


class NearestNeighboursSerializer(DynamicDepthSerializer):
    
        class Meta:
            model = models.NearestNeighbours
            fields = "__all__"

class AuthorExchangeSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    authors = serializers.ListField(child=serializers.IntegerField())
    works = WorkPageSerializer
    segments = SegmentSerializer
    # count = serializers.IntegerField()

    class Meta:
        model = models.Cluster
        # fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE) + ['authors', 'count']
        fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE) + ['authors', 'segments']


class TargetSourceSerializer(serializers.Serializer):

    source = serializers.IntegerField()
    target = serializers.IntegerField()
    weight = serializers.IntegerField()


class ClusterInfoSerializer(DynamicDepthSerializer, DynamicFieldsMixin):

    works = WorkPageSerializer
    segments = SegmentSerializer


    class Meta:
        model = models.Cluster
        fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE) + ['segments']
        depth = 4