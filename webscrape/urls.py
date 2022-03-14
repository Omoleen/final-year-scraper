from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.button, name='search-page'),
    path('search/', views.searchresult, name='search'),
    path('account/', views.account, name='account'),
    path('login/', views.loginpage, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('delete/<int:id>', views.delete),
    path('savedproducts/', views.savedproductspage, name='saved_products'),
    path('trendingproducts/', views.trendingproducts, name='trending_products'),
    # path('delete/<int:id>', views.delete)
]
