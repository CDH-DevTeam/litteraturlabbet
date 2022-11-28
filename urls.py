from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("litteraturlabbet")
documentation = utils.build_app_api_documentation("litteraturlabbet", endpoint)


router = routers.DefaultRouter()
router.register(rf'{endpoint}/page', views.PageViewSet, basename='page')
router.register(rf'{endpoint}/texts', views.WorkPageViewSet, basename='texts')


urlpatterns = [
    path('', include(router.urls)),

    *documentation,

    # Automatically generated views
    *utils.get_model_urls('litteraturlabbet', f'{endpoint}', exclude=['page', 'work', 'work_authors']),
]