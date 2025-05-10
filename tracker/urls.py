from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('all-habits/', views.all_habits, name='all_habits'),
    path('habits/create/', views.habit_create, name='habit_create'),
    path('habits/<int:habit_id>/delete/', views.habit_delete, name='habit_delete'),
    path('habits/<int:habit_id>/log/', views.log_entry, name='log_entry'),
    path('habits/<int:habit_id>/progress/', views.habit_progress_panel, name='habit_progress_panel'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_progress, name='day_progress'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
] 