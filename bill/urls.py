from django.urls import path
from . import views

app_name = 'bill'

urlpatterns = [
    # Authentication routes
    # path('', views.login, name='login'),  # Default page is now login
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),

    # Main application routes
    path('index/', views.index, name='index'),  # Main page after login
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='profile_update'),
    # path('profile/delete/', views.delete_profile, name='profile_delete'),
    path('ai_chat/', views.ai_chat, name='ai_chat'),
    path('virtual_world/',views.virtual_world, name='virtual_world'),
    path('status/', views.status, name='status'),
    path('money/', views.money, name='money'),
    path('day_goal/', views.day_goal, name='day_goal'),

    # Bill management routes
    # Outcome (expenses) routes
    path('outcome/list/', views.outcome_list, name='outcome_list'),
    path('outcome/add/', views.outcome_add, name='outcome_add'),
    path('outcome/<int:nid>/edit/', views.outcome_edit, name='outcome_edit'),
    path('outcome/<int:nid>/delete/', views.outcome_delete, name='outcome_delete'),

    # Income routes
    path('income/list/', views.income_list, name='income_list'),
    path('income/add/', views.income_add, name='income_add'),
    path('income/<int:nid>/edit/', views.income_edit, name='income_edit'),
    path('income/<int:nid>/delete/', views.income_delete, name='income_delete'),

    # Analysis routes
    path('analysis/', views.analysis, name='analysis'),
    path('analysis/bar/', views.bar, name='bar'),
    path('analysis/pie/', views.pie, name='pie'),
    path('<slug:year_month>/text/', views.text, name='text'),

# Main application routes
    path('index/', views.redirect_to_funds_index, name='index'),  # Redirect to funds index
]