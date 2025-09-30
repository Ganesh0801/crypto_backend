# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import WalletViewSet, TransactionViewSet, PriceTicker

# router = DefaultRouter()
# router.register('wallets', WalletViewSet, basename='wallet')
# router.register('transactions', TransactionViewSet, basename='transaction')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('prices/', PriceTicker.as_view(), name='price-ticker'),
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, TransactionViewSet, PriceTicker, RegisterUserView, MeView

router = DefaultRouter()
router.register('wallets', WalletViewSet, basename='wallet')
router.register('transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
    path('prices/', PriceTicker.as_view(), name='price-ticker'),
]
