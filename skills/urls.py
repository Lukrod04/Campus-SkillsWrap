from django.urls import path
from . import views

urlpatterns = [
    path('sessions/<int:pk>/confirm/', views.confirm_session, name='confirm_session'),
    path('', views.skill_list, name='skill_list'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('skills/new/', views.skill_create, name='skill_create'),
    path('skills/<int:pk>/', views.skill_detail, name='skill_detail'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
    path('skills/<int:pk>/request/', views.request_session, name='request_session'),
    path('sessions/<int:pk>/complete/', views.complete_session, name='complete_session'),
]
