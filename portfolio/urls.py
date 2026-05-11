from rest_framework.routers import DefaultRouter

from portfolio.views import (
    LatestPortfolioShareWaccViewSet,
    PortfolioShareViewSet,
    WatchlistViewSet,
)


router = DefaultRouter()
router.register('shares', PortfolioShareViewSet, basename='portfolio-share')
router.register('latest-wacc', LatestPortfolioShareWaccViewSet, basename='portfolio-latest-wacc')
router.register('watchlists', WatchlistViewSet, basename='watchlist')

urlpatterns = router.urls
