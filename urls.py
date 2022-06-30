from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils

router = routers.DefaultRouter()
router.register(r'api/page', views.PageViewSet, basename='page')
router.register(r'api/work', views.WorkViewSet, basename='work')
router.register(r'api/cluster', views.ClusterViewSet, basename='cluster')
router.register(r'api/author', views.AuthorViewSet, basename='author')
router.register(r'api/exchange', views.ExchangeViewSet, basename='exchanges')
router.register(r'api/segment', views.SegmentViewSet, basename='segment')


urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('litteraturlabbet', 'api', exclude=['page', 'author', 'work', 'cluster', 'segment']),
]