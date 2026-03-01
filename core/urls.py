from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('main_home/', views.main_home, name='main_home'),
    path('logout/', views.logout_view, name='logout'),
    path('upload_page/', views.upload_view, name='upload_page'),
    path('download/<int:analysis_id>/', views.download_resume, name='download_resume'),
    path('api/fix-resume/', views.fix_resume_api, name='fix_resume_api'),
    
    path("template-preview/", views.template_preview_page, name="template_preview"),
    path("resume-preview/", views.resume_preview, name="resume_preview"),
    path("select-template/", views.select_template, name="select_template"),

]

