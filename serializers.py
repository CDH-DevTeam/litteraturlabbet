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

