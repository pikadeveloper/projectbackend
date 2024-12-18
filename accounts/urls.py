from django.urls import path
from . import views

urlpatterns = [
    path('accounts/signup/', views.CreateUserView.as_view(), name='signup'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/users/', views.UserList.as_view(),name='Users'),
    path('accounts/user/<int:pk>', views.UserDetail.as_view(),name='User'),
    path('ofertas/', views.OfertaDeEmpleoList.as_view(), name='oferta-list'),
    path('ofertas/<int:pk>/', views.OfertaDeEmpleoDetail.as_view(), name='oferta-detail'),
    path('ofertas/empresa/<int:empresa_id>/', views.OfertaDeEmpleoEmpresa.as_view(), name='ofertas-empresa'),
    path('register/employer/', views.RegisterEmployerAPIView.as_view(), name='register-employer'),
    path('auth/login/', views.CreateTokenAPIView.as_view(), name='login'),
    path('empresa/', views.EmpresaCreateAPIView.as_view(), name='empresa-create'),
    path('empresa/detalle/', views.EmpresaDetailAPIView.as_view(), name='empresa-detail'),
]
