from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    home,
    register_view,
    login_view,
    logout_view,
    get_cart,
    add_to_cart,
    create_order,
    cart_view,
    contact_view,
    ProductViewSet,
)

# API router
router = DefaultRouter()
router.register(r'products', ProductViewSet)

# Główne ścieżki
urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_view, name='contact'),
    path('cart/', cart_view, name='cart'),  # 🔹 koszyk użytkownika

    # API endpoints
    path('api/', include(router.urls)),
    path('api/cart/', get_cart, name="get_cart"),
    path('api/cart/add/', add_to_cart, name="add_to_cart"),
    path('api/order/create/', create_order, name="create_order"),
]

# Pliki statyczne (media)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
