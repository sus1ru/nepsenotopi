from rest_framework.routers import DefaultRouter

from nepse.views import (
    CompanyViewSet,
    InstrumentTypeViewSet,
    SecurityLogViewSet,
    SecurityViewSet,
    SectorViewSet,
    ShareGroupViewSet,
)

router = DefaultRouter()
router.register('sectors', SectorViewSet, basename='sector')
router.register('share-groups', ShareGroupViewSet, basename='share-group')
router.register('securities', SecurityViewSet, basename='security')
router.register('instrument-types', InstrumentTypeViewSet, basename='instrument-type')
router.register('companies', CompanyViewSet, basename='company')
router.register('security-logs', SecurityLogViewSet, basename='security-log')

urlpatterns = router.urls
