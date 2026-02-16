from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('main_home/', views.main_home, name='main_home'),
    path('logout/', views.logout_view, name='logout'),
    path('upload_page/', views.upload_view, name='upload_page'),
    path('download/<int:analysis_id>/', views.download_optimized_resume, name='download_resume')
]

