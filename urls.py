from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils

router = routers.DefaultRouter()
router.register(r'api/page', views.PageViewSet, basename='page')
router.register(r'api/texts', views.WorkPageViewSet, basename='texts')


urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('litteraturlabbet', 'api', exclude=[]),
]