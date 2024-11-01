# carts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')

app_name = 'carts'

urlpatterns = [
    path('', include(router.urls)),
]