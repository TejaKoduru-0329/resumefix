from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('main_home/', views.main_home, name='main_home'),
    path('logout/', views.logout_view, name='logout'),
    path('upload_page/', views.upload_view, name='upload_page'),
    path('download/<int:analysis_id>/', views.download_resume, name='download_resume'),
    path('api/fix-resume/', views.fix_resume_api, name='fix_resume_api'),
    path('api/cover-letter/', views.generate_cover_letter_api, name='cover_letter_api'),
    path('download-cover-letter/', views.download_cover_letter, name='download_cover_letter'),
    path("template-preview/", views.template_preview_page, name="template_preview"),
    path("resume-preview/", views.resume_preview, name="resume_preview"),
    path("select-template/", views.select_template, name="select_template"),

    path('change-password/', views.change_password, name='change_password'),
    path('download-template/<int:analysis_id>/', views.download_from_template, name='download_from_template'),
]

