from django.urls import path, include
from rest_framework import routers

import diana.utils as utils

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('litteraturlabbet', 'api', exclude=[]),
]