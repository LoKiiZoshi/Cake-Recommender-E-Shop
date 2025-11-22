from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import User
from .froms import UserRegistrationForm, UserProfileForm,ForgotPasswordEmailForm,OTPVerificationForm,NewPasswordForm
from .models import UserProfile
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from .models import PasswordResetOTP



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  # Redirect to home instead of login
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form}) 


@login_required
def profile(request):
    # Create profile if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(user = request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance = profile)
        if form.is_valid():
            form.save()
            messages.success(request,'Profile updated successfully!')
            return redirect('profile')
        else:
            form = UserProfile(isinstance = profile)
            return render(request,'accounts/profile.html',{'form': form})
    
    class LogoutGetAllowed(LogoutView):
        def get(self,request, *args,**kwargs):
            return self.post(request,*args,**kwargs)


# Custom view to handle google OAuth sucess
def google_login_sucesss(request):
    """Handle sucessful google OAuth login"""
    if request.user.is_authenticated:
        # Create user profile if it doesn't exist
        UserProfile.objects.get_or_create(user=request.user)
        messages.success(request,f'Welcome{request.user.first_name or request.user.username}')
        
        
        
        



def forgot_password_email(request):
    if request.method == 'POST':
        form = ForgotPasswordEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if user exists with this email
            try:
                user = User.objects.get(email=email)
                
                # Delete any existing OTP for this email
                PasswordResetOTP.objects.filter(email=email, is_used=False).delete()
                
                # Create new OTP
                otp_obj = PasswordResetOTP.objects.create(email=email)
                
                # Send OTP via email
                subject = 'Password Reset OTP - Smart Cake Shop'
                message = f'''
Hello,

You have requested to reset your password for Smart Cake Shop.

Your OTP is: {otp_obj.otp}

This OTP is valid for 10 minutes only.

If you didn't request this, please ignore this email.

Best regards,
Smart Cake Shop Team
                '''
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    
                    # Store email in session for next step
                    request.session['reset_email'] = email
                    messages.success(request, 'OTP has been sent to your email address.')
                    return redirect('verify_otp')
                    
                except Exception as e:
                    messages.error(request, 'Failed to send OTP. Please try again.')
                    
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = ForgotPasswordEmailForm()
    
    return render(request, 'accounts/forgot_password_email.html', {'form': form})

def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('forgot_password_email')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            
            try:
                otp_obj = PasswordResetOTP.objects.get(
                    email=email,
                    otp=entered_otp,
                    is_used=False
                )
                
                if otp_obj.is_valid():
                    # Mark OTP as used
                    otp_obj.is_used = True
                    otp_obj.save()
                    
                    # Store verification status in session
                    request.session['otp_verified'] = True
                    messages.success(request, 'OTP verified successfully!')
                    return redirect('reset_password')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return redirect('forgot_password_email')
                    
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'accounts/verify_otp.html', {
        'form': form,
        'email': email
    })

def resend_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Session expired'})
    
    try:
        # Delete existing OTP
        PasswordResetOTP.objects.filter(email=email, is_used=False).delete()
        
        # Create new OTP
        otp_obj = PasswordResetOTP.objects.create(email=email)
        
        # Send new OTP
        subject = 'Password Reset OTP - Smart Cake Shop'
        message = f'''
Hello,

Your new OTP for password reset is: {otp_obj.otp}

This OTP is valid for 10 minutes only.

Best regards,
Smart Cake Shop Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True, 'message': 'New OTP sent successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Failed to send OTP'})

def reset_password(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    
    if not email or not otp_verified:
        messages.error(request, 'Unauthorized access. Please start the process again.')
        return redirect('forgot_password_email')
    
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Clear session data
                request.session.pop('reset_email', None)
                request.session.pop('otp_verified', None)
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('password_reset_success')
                
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = NewPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})

def password_reset_success(request):
    return render(request, 'accounts/password_reset_success.html')


