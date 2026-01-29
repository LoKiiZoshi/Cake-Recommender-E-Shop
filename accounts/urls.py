from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views


from .views import LogoutView # or the correct path if in different file

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'), 
     
    
    
      # Google OAuth success handler
    path('google/success/', views.google_login_sucesss, name='google_login_success'), 
    
    
    # Include allauth URLs
    path('', include('allauth.urls')),
    
    
    
    
    # Password Reset URLs
    path('forgot-password/', views.forgot_password_email, name='forgot_password_email'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('password-reset-success/', views.password_reset_success, name='password_reset_success'),
    
    
    
]
 