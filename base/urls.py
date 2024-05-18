from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.CoinListView.as_view(), name='list'),
    path('update_is_caught/', views.UpdateIsCaughtView.as_view(), name='update_is_caught'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name="logout"),
    path('coin/<int:pk>/', views.CoinDetailView.as_view(), name='coin'),
    path('blogposts/', views.BlogPostListView.as_view(), name='blogpost_list'),
    path('blogpost/<int:pk>/', views.BlogPostDetailView.as_view(), name='blogpost'),
    path('currency-conversion/', views.CurrencyConversionProxyView.as_view(), name='currency_conversion'),
]  