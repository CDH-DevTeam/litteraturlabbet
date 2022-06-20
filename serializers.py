from distutils import dep_util
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from diana.utils import DEFAULT_EXCLUDE
from . import models

from diana.abstract.models import get_fields

class PageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = get_fields(models.Page, exclude=DEFAULT_EXCLUDE + ['text_vector'])

class WorkPageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = models.Work
        fields = get_fields(models.Work, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['pages']
        depth = 1
