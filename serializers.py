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
    similar_extractions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    similar_count = serializers.SerializerMethodField()

    class Meta(PageSerializer.Meta):
        exclude = ['text'] 
    class Meta:
        model = models.Graphics
        fields = get_fields(models.Graphics, exclude=DEFAULT_EXCLUDE + ['similar_extractions']) + ['similar_count']

    def get_similar_count(self, instance):
        return instance.similar_extractions.count()

    def to_representation(self, instance):
        representation = super(TIFFGraphicSerializer, self).to_representation(instance)

        # Handle depth serialization for related fields
        depth = self.context.get('depth')
        if depth is not None:
            representation['page'] = PageSerializer(instance.page, context={'depth': depth}).data
            representation['page'].pop('text', None)

        # Add similar_count to the representation
        representation['similar_count'] = self.get_similar_count(instance)
        
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


class NeighboursSerializer(DynamicDepthSerializer):
    class Meta(TIFFGraphicSerializer.Meta):
        exclude = ['similar_extractions'] 

    class Meta:
        model = models.Neighbours
        fields = get_fields(models.Neighbours, exclude=DEFAULT_EXCLUDE) 

    def to_representation(self, instance):
        representation = super(NeighboursSerializer, self).to_representation(instance)

        # Handle depth serialization for related fields
        depth = self.context.get('depth')
        if depth is not None:
            representation['image'] = TIFFGraphicSerializer(instance.image, context={'depth': depth}).data
            representation['image'].pop('similar_extractions', None)

        return representation


class NearestNeighboursSerializer(DynamicDepthSerializer):
    
    class Meta(TIFFGraphicSerializer.Meta):
        exclude = ['similar_extractions'] 

    class Meta(NeighboursSerializer.Meta):
        exclude = ['similar_extractions'] 

    class Meta:
        model = models.NearestNeighbours
        fields = get_fields(models.NearestNeighbours, exclude=DEFAULT_EXCLUDE)

    def to_representation(self, instance):
        representation = super(NearestNeighboursSerializer, self).to_representation(instance)

        # Handle depth serialization for related fields
        depth = self.context.get('depth')
        if depth is not None:
            representation['image'] = TIFFGraphicSerializer(instance.image, context={'depth': depth}).data
            representation['image'].pop('similar_extractions', None)

            representation['neighbours'] = NeighboursSerializer(instance.neighbours, context={'depth': depth}, many=True).data
            for neighbour in representation['neighbours']:
                neighbour.pop('similar_extractions', None)

        return representation

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