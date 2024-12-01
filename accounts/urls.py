from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.CreateUserView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('users/', views.UserList.as_view(),name='Users'),
    path('user/<int:pk>', views.UserDetail.as_view(),name='User')

]