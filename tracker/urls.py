from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app URLs (require authentication)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('habits/', views.all_habits, name='all_habits'),
    path('habits/create/', views.habit_create, name='habit_create'),
    path('habits/<int:habit_id>/delete/', views.habit_delete, name='habit_delete'),
    path('habits/<int:habit_id>/log/', views.log_entry, name='log_entry'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
] 