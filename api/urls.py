from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout_view'),
    path('auction_list/', views.auction_list, name='auction_list'),
    path('auction/<int:pk>/', views.auction_detail, name='auction_detail'),
    path('transaction/<int:pk>/', views.transaction_detail, name='transaction_detail'),
]