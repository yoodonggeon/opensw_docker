# backend/lotto/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'lotto'

urlpatterns = [
    path('', views.index, name='index'),
    path('buy/', views.buy_ticket, name='buy_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    
    # 인증 관련 URL
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='lotto:index'), name='logout'),

    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/draw/', views.draw_lotto, name='draw_lotto'),
]
