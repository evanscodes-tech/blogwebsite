from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verified
            user.save()
            
            # Generate email verification token
            token = default_token_generator.make_token(user)
            user.email_verification_token = token
            user.email_verification_sent_at = timezone.now()
            user.save()
            
            # Send verification email
            send_verification_email(request, user)
            
            messages.success(request, 'Please check your email to verify your account.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = user.email_verification_token
    
    verification_link = f"{request.scheme}://{request.get_host()}/users/verify-email/{uid}/{token}/"
    
    subject = 'Verify Your Email Address'
    message = f'''
    Hello {user.username},
    
    Please click the link below to verify your email address:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Thanks,
    The Blog Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Check if token is expired (24 hours)
        if (timezone.now() - user.email_verification_sent_at).days < 1:
            user.email_verified = True
            user.is_active = True
            user.email_verification_token = ''  # Clear token
            user.save()
            
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Verification link has expired.')
            return redirect('register')
    else:
        messages.error(request, 'Invalid verification link.')
        return redirect('register')

@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/profile_update.html', {'form': form})