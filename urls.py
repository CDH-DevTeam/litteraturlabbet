from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("litteraturlabbet")
documentation = utils.build_app_api_documentation("litteraturlabbet", endpoint)


router = routers.DefaultRouter()
router.register(rf'{endpoint}/page', views.PageViewSet, basename='page')
router.register(rf'{endpoint}/work', views.WorkPageViewSet, basename='work')
router.register(rf'{endpoint}/author', views.AuthorViewSet, basename='author')
router.register(rf'{endpoint}/cluster', views.ClusterViewSet, basename='cluster')
router.register(rf'{endpoint}/segment', views.SegmentViewSet, basename='segment')



urlpatterns = [
    path('', include(router.urls)),

    *documentation,

    # Automatically generated views
    # *utils.get_model_urls('litteraturlabbet', f'{endpoint}', exclude=['page', 'work', 'work_authors', 'author', 'cluster', ),
]