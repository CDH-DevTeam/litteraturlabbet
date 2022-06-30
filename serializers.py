from distutils import dep_util
from django.db.models import PositiveBigIntegerField
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from django.contrib.postgres.fields import ArrayField
from diana.utils import DEFAULT_EXCLUDE
from . import models

from diana.abstract.models import get_fields

class AuthorSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = get_fields(models.Author)

class PageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = get_fields(models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector'])
        depth = 1

class WorkPageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = models.Work
        fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['pages']
        depth = 1

class WorkSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = models.Work
        fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['text_vector'])

class ClusterSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = models.Cluster
        fields = get_fields(models.Cluster, exclude=DEFAULT_EXCLUDE)

class ExchangeSerializer(serializers.ModelSerializer):

    # authors = serializers.ListField(child=serializers.IntegerField(min_value=0))
    author = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = models.Cluster
        # fields = ["id", "authors"]
        fields = ["size", "id", "author", "name",]

class SmallAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Author
        fields = ["id", "name", "lbauthorid"]


class SmallWorkSerializer(serializers.ModelSerializer):

    main_author = SmallAuthorSerializer(read_only=True)
    class Meta:
        model = models.Work
        fields = ["id", "lbworkid", "main_author", "short_title"]
        depth = 1


class SmallPageSerializer(serializers.ModelSerializer):

    work = SmallWorkSerializer(read_only=True)

    class Meta:
        model = models.Page
        fields = ["id", "work"]

class SegmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    page = SmallPageSerializer(read_only=True)

    class Meta:
        model = models.Segment
        fields = get_fields(models.Segment, exclude=DEFAULT_EXCLUDE + ["page"]) + ["page"]
        depth = 3