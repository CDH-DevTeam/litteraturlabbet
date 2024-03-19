from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("litteraturlabbet")
documentation = utils.build_app_api_documentation("litteraturlabbet", endpoint)


router = routers.DefaultRouter()
router.register(rf'{endpoint}/page', views.PageViewSet, basename='page')
router.register(rf'{endpoint}/work/19th_century', views.Work19thCenturyViewSet, basename='19th century work')
router.register(rf'{endpoint}/work', views.WorkPageViewSet, basename='work')
router.register(rf'{endpoint}/author', views.AuthorViewSet, basename='author')
router.register(rf'{endpoint}/cluster', views.ClusterViewSet, basename='cluster')
router.register(rf'{endpoint}/segment', views.SegmentViewSet, basename='segment')
router.register(rf'{endpoint}/graphic', views.GraphicViewSet, basename='graphics')
router.register(rf'{endpoint}/nearest_neighbours', views.NearestNeighboursViewSet, basename='nearest neighbours')
router.register(rf'{endpoint}/image_cloud_cluster', views.ClusterMetaViewSet, basename='image cloud cluster')
router.register(rf'{endpoint}/author_exchange_info', views.AuthorExchangeSegmentsView, basename='author-exchange full information')
router.register(rf'{endpoint}/phrase_search', views.PhraseSearchView, basename='phrase search')

urlpatterns = [
    path('', include(router.urls)),

    *documentation,
    path(rf'{endpoint}/author_exchange/', views.AuthorExchangeView.as_view())
    # Automatically generated views
    # *utils.get_model_urls('litteraturlabbet', f'{endpoint}', exclude=['page', 'work', 'work_authors', 'author', 'cluster', ),
]