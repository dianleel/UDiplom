# repo/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.NewsListView.as_view(), name='news'),
    path('works/', views.WorksListView.as_view(), name='works'),
    path('my-activity/', views.MyActivityView.as_view(), name='my_activity'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    # Профиль
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),

    # Работы
    path('work/create/', views.WorkCreateView.as_view(), name='create_work'),
    path('work/<int:pk>/edit/', views.WorkUpdateView.as_view(), name='edit_work'),
    path('work/<int:pk>/delete/', views.WorkDeleteView.as_view(), name='delete_work'),

    # Новости
    path('news/create/', views.NewsCreateView.as_view(), name='create_news'),
    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='edit_news'),
    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='delete_news'),
]