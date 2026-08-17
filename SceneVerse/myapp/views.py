from django.shortcuts import render, redirect
import re
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import *
from datetime import date
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch, Count
from .models import Register, Project, ProjectLike, ProjectComment, ApplicationAttachment
from django.db.models import Q
from django.utils.decorators import decorator_from_middleware
from myapp.middleware import SessionProtectionMiddleware




def index(request):
    if request.session.get('cid'):
        return redirect('/creators/')

    if request.session.get('aid'):
        return redirect('/artists/')

    return render(request, "index.html")

def reg(request):
    if request.session.get('cid'):
        return redirect('/creators/')

    if request.session.get('aid'):
        return redirect('/artists/')

    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        creator_role = request.POST.get('creator-role')
        artist_role = request.POST.get('artist-role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("/register/")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("/register/")

        if not re.search(r"[A-Z]", password):
            messages.error(request, "Password must contain at least 1 uppercase letter.")
            return redirect("/register/")

        if not re.search(r"[a-z]", password):
            messages.error(request, "Password must contain at least 1 lowercase letter.")
            return redirect("/register/")

        if not re.search(r"[0-9]", password):
            messages.error(request, "Password must contain at least 1 number.")
            return redirect("/register/")

        if not re.search(r"[@$!%*#?&]", password):
            messages.error(request, "Password must contain at least 1 special character (@$!%*#?&).")
            return redirect("/register/")

        if Register.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("/register/")

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store data in session
        request.session['signup_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'role': role,
            'creator_role': creator_role,
            'artist_role': artist_role,
            'password': password
        }
        request.session['signup_otp'] = otp
        
        # Send OTP
        subject = 'Your Verification Code - SceneVerse'
        message = f'Your verification code is: {otp}'
        email_from = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@sceneverse.com'
        recipient_list = [email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, f"OTP sent to {email}. Check your console/email.")
            return redirect('/verify_otp/')
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")
            return redirect("/register/")

    return render(request, "register.html")

def verify_otp(request):
    if 'signup_otp' not in request.session:
        messages.error(request, "Session expired. Please register again.")
        return redirect('/register/')
        
    if request.method == 'POST':
        entered_otp = request.POST.get('otp1') + request.POST.get('otp2') + request.POST.get('otp3') + request.POST.get('otp4') + request.POST.get('otp5') + request.POST.get('otp6')
        
        if entered_otp == request.session.get('signup_otp'):
            data = request.session.get('signup_data')
            
            # Create User
            reg = Register(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                role=data['role'],
                creator_role=data.get('creator_role'),
                artist_role=data.get('artist_role'),
                password=data['password']
            )
            reg.save()
            
            # Clear session data
            del request.session['signup_otp']
            del request.session['signup_data']
            
            messages.success(request, "Registration successful! Please login.")
            return redirect('/login/')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'verify_otp.html', {'hide_sidebar': True})

def cancel_signup(request):
    if 'signup_otp' in request.session:
        del request.session['signup_otp']
    if 'signup_data' in request.session:
        del request.session['signup_data']
    messages.info(request, "Registration cancelled.")
    return redirect('/register/')

@never_cache
def resend_otp(request):
    if 'signup_otp' not in request.session or 'signup_data' not in request.session:
        messages.error(request, "Session expired. Please register again.")
        return redirect('/register/')
        
    data = request.session.get('signup_data')
    email = data['email']
    
    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    request.session['signup_otp'] = otp
    
    subject = 'Your New Registration OTP - SceneVerse'
    message = f'Your new registration verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, f"A new OTP has been sent to {email}.")
    except Exception as e:
        messages.error(request, f"Error sending email: {e}")
        
    return redirect('/verify_otp/')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not Register.objects.filter(email=email).exists():
            messages.error(request, "Email not found.")
            return redirect('/forgot_password/')
        
        otp = str(random.randint(100000, 999999))
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        
        subject = 'Password Reset OTP - SceneVerse'
        message = f'Your password reset code is: {otp}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, f"OTP sent to {email}.")
            return redirect('/verify_reset_otp/')
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")
            return redirect('/forgot_password/')
            
            return redirect('/forgot_password/')
            
    return render(request, 'forgot_password.html', {'hide_sidebar': True})

def verify_reset_otp(request):
    if 'reset_otp' not in request.session:
        messages.error(request, "Session expired.")
        return redirect('/forgot_password/')
        
    if request.method == 'POST':
        entered_otp = "".join([request.POST.get(f'otp{i}') for i in range(1, 7)])
        
        if entered_otp == request.session.get('reset_otp'):
            request.session['otp_verified'] = True
            return redirect('/new_password/')
        else:
            messages.error(request, "Invalid OTP.")
            
    return render(request, 'verify_reset_otp.html', {'hide_sidebar': True})

@never_cache
def resend_reset_otp(request):
    if 'reset_otp' not in request.session or 'reset_email' not in request.session:
        messages.error(request, "Session expired.")
        return redirect('/forgot_password/')
        
    email = request.session.get('reset_email')
    
    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    request.session['reset_otp'] = otp
    
    subject = 'Your New Password Reset OTP - SceneVerse'
    message = f'Your new password reset code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, f"A new OTP has been sent to {email}.")
    except Exception as e:
        messages.error(request, f"Error sending email: {e}")
        
    return redirect('/verify_reset_otp/')

def new_password(request):
    if not request.session.get('otp_verified'):
        return redirect('/forgot_password/')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/new_password/')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("/new_password/")

        if not re.search(r"[A-Z]", password):
            messages.error(request, "Password must contain at least 1 uppercase letter.")
            return redirect("/new_password/")

        if not re.search(r"[a-z]", password):
            messages.error(request, "Password must contain at least 1 lowercase letter.")
            return redirect("/new_password/")

        if not re.search(r"[0-9]", password):
            messages.error(request, "Password must contain at least 1 number.")
            return redirect("/new_password/")

        if not re.search(r"[@$!%*#?&]", password):
            messages.error(request, "Password must contain at least 1 special character (@$!%*#?&).")
            return redirect("/new_password/")
            
        email = request.session.get('reset_email')
        Register.objects.filter(email=email).update(password=password)
        
        # Cleanup session
        del request.session['reset_email']
        del request.session['reset_otp']
        del request.session['otp_verified']
        
        messages.success(request, "Password reset successful. Please login.")
        return redirect('/login/')
        
        messages.success(request, "Password reset successful. Please login.")
        return redirect('/login/')
        
    return render(request, 'new_password.html', {'hide_sidebar': True})



@csrf_exempt
@never_cache
def login(request):
    msg=False

    if request.session.get('cid'):
        return redirect('/creators/')

    if request.session.get('aid'):
        return redirect('/artists/')

    if request.session.get('admin'):
        return redirect('/admin_users/')

    if request.method=="POST":
        e=request.POST.get("email")
        p=request.POST.get("password")
        if not e or not p:
            messages.error(request, "Email and password are required.")
            return redirect("/login/")

        log=Register.objects.filter(email=e,password=p)
        if log:
            for i in log:
                r=i.rights
                rol=i.role
                if r == "Blocked" or r == "blocked":
                    messages.error(request, "your account was blocked by admin contact them")
                    return redirect("/login/")
                elif r == "Deactivated" or r == "deactivated":
                    messages.error(request, "your account has been deactivated contact admin")
                    return redirect("/login/")
                elif r == "Admin":
                    request.session['admin'] = i.id
                    messages.success(request, "Welcome, Admin!")
                    return redirect("/admin_users/")
                elif rol=="creator":
                    request.session['cid']=i.id
                    request.session['role'] = 'creator'
                    messages.success(request, f"Welcome back, {i.first_name}!")
                    return redirect("/creators/")
                elif rol=="artist":
                    request.session['aid']=i.id
                    request.session['role'] = 'artist'
                    messages.success(request, f"Welcome back, {i.first_name}!")
                    return redirect("/artists/")
        else:
            messages.error(request, "Invalid email or password")
            msg=True
            return redirect("/login/")

    return render(request, "login.html",context={'msg':msg})

@never_cache
def creators(request):
    if not request.session.get('cid'):
        return redirect('/login/')
    if not request.session.get('role'):
        request.session['role'] = 'creator'
    cid = request.session.get('cid')
    logcreator=Register.objects.filter(id=cid)
    proj=Project.objects.filter(added_by=cid)
    recent_projects = Project.objects.filter(added_by=cid).order_by('-created_at')[:3]
    deadline = CastingCall.objects.filter(added_by=cid).order_by('deadline')[:3]
    
    # Real-time Stats
    active_projects_count = Project.objects.filter(added_by=cid).count()
    applications_count = Applications.objects.filter(casting_id__added_by=cid).count()
    unread_messages_count = get_unread_msg_count(cid)
    
    context = {
        'proj': proj,
        '3proj': recent_projects,
        'logcreator': logcreator,
        'deadline': deadline,
        'stats': {
            'active_projects': active_projects_count,
            'applications': applications_count,
            'unread_messages': unread_messages_count,
            'profile_views': 1200  # Placeholder until we add view tracking
        }
    }
    return render(request, template_name="creators/creators.html", context=context)

@never_cache
def artists(request):
    if not request.session.get('aid'):
        return redirect('/login/')
    if not request.session.get('role'):
        request.session['role'] = 'artist'
    aid = request.session['aid']
    crt = Register.objects.get(id=aid)
    det = CastingCall.objects.filter(deadline__gt=date.today())
    count=len(det)
    try:
        details=ArtistDetails.objects.get(added_by=crt)
    except:
        details=[]
    if request.method == 'POST':
        caption = request.POST.get('caption')
        media_files = request.FILES.getlist('media')
        
        # Create post if there is content
        if caption or media_files:
            po = Post.objects.create(added_by=crt, caption=caption)
            
            import json
            trim_data = request.POST.get('trim_data', '{}')
            try:
                trim_metadata = json.loads(trim_data)
            except:
                trim_metadata = {}

            for file in media_files:
                # Check mime type to determine if it's image or video
                content_type = file.content_type
                if content_type.startswith('image'):
                    PhotoPost.objects.create(image=file, post=po)
                elif content_type.startswith('video'):
                    # Get metadata for this file
                    meta = trim_metadata.get(file.name, {})
                    start = meta.get('start', 0.0)
                    end = meta.get('end', None)
                    VideoPost.objects.create(video=file, post=po, start_time=start, end_time=end)
                    
        messages.success(request, 'Post created successfully!')
        return redirect('/artists/')

    # Fetch Feed Posts - Exclude deactivated users
    all_posts = Post.objects.exclude(added_by=crt).exclude(added_by__rights='Deactivated').order_by('-created_at')
    posts_with_media = []
    for post in all_posts:
        # Attach author details
        try:
            post.added_by.details = ArtistDetails.objects.filter(added_by=post.added_by).first()
        except:
            post.added_by.details = None
            
        # Fetch top-level comments using the join-fix logic if needed, 
        # or standard logic (assuming caching fixed the render issue)
        comments_qs = ArtistComment.objects.filter(post=post, parent=None).order_by('created_at')
        comments_list = []
        for comment in comments_qs:
             # Pre-fetch replies to avoid template complexity
             comment.replies_list = comment.replies.all().order_by('created_at')
             comments_list.append(comment)

        photos = list(post.photopost_set.all())
        videos = list(post.videopost_set.all())
        post.all_media = photos + videos
        
        posts_with_media.append({'post': post, 'com': comments_list})

    # Fetch User Likes
    artist_likes = ArtistLike.objects.filter(liked_by=crt).values_list("post_id", flat=True)

    # Fetch Recommended Projects - Exclude deactivated users
    recommended_projects = CastingCall.objects.filter(deadline__gt=date.today()).exclude(added_by__rights='Deactivated').order_by('-created_at')[:5]

    unread_count = get_unread_msg_count(aid)

    # Stats for Artist
    applications_sent = Applications.objects.filter(added_by=crt).count()
    shortlisted_count = Applications.objects.filter(added_by=crt, application_status='Short Listed').count()

    context = {
        'details': details,
        'crt': crt,
        'count': count,
        'det': det, # Keeping original for backward compat if needed
        'all_artist_posts': posts_with_media,
        'creator_likes': list(artist_likes), # Reusing same name as findartists for template compatibility
        'recommended_projects': recommended_projects,
        'logartist': [crt], # For template compatibility where it loops or expects list
        'unread_count': unread_count,
        'stats': {
            'applications_sent': applications_sent,
            'shortlisted': shortlisted_count,
        }
    }
    return render(request, "artists/artists.html", context)



def manageusers(request):
    if not request.session.get('admin'):
        return redirect('/login/')
    
    search = request.GET.get('search', '').strip()
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    us = Register.objects.exclude(rights='Admin')

    if search:
        us = us.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) | 
            Q(email__icontains=search)
        )
    
    if role:
        us = us.filter(role=role)
    
    if status:
        if status == 'active':
            us = us.filter(rights='user')
        elif status == 'banned':
            us = us.filter(rights='Blocked')

    stats = {
        'total': Register.objects.exclude(rights='Admin').count(),
        'creators': Register.objects.filter(role='creator').count(),
        'artists': Register.objects.filter(role='artist').count(),
        'admins': Register.objects.filter(rights='Admin').count(),
    }
    
    return render(request, template_name="admin/admin_users.html",context={'us':us, 'stats': stats})

def blockuser(request,id):
    Register.objects.filter(id=id).update(rights='Blocked')
    return redirect("/admin_users/")
def unblockuser(request,id):
    Register.objects.filter(id=id).update(rights='user')
    return redirect("/admin_users/")

def project(request):
    cid=request.session['cid']
    crt=Register.objects.get(id=cid)
    if request.method == 'POST':
        project_title = request.POST.get('project_title', '').strip()
        project_type = request.POST.get('project_type', '').strip()
        project_description = request.POST.get('project_description', '').strip()
        genre = request.POST.get('genre', '').strip()
        project_status = request.POST.get('project_status', '').strip()
        
        if not project_title or not genre:
            messages.error(request, 'Project Title and Genre are required.')
            return redirect('/my_projects/')
        
        # File Handling
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        media = request.FILES.get('media')
        
        if media:
            if media.content_type.startswith('image'):
                image = media
            elif media.content_type.startswith('video'):
                video = media
        
        # Trimming Data
        import json
        trim_data = request.POST.get('trim_data', '{}')
        try:
            trim_metadata = json.loads(trim_data)
        except:
            trim_metadata = {}
            
        video_start = 0.0
        video_end = None
        
        if video:
            meta = trim_metadata.get(video.name, {})
            video_start = meta.get('start', 0.0)
            video_end = meta.get('end', None)

        pro = Project(
            added_by=crt,
            project_title=project_title, 
            project_type=project_type,
            project_description=project_description,
            genre=genre,
            project_status=project_status,
            image=image,
            video=video,
            video_start=video_start,
            video_end=video_end
        )
        pro.save()
        messages.success(request, 'Project created successfully!')
        return redirect('/my_projects/')
    return render(request, "creators/creators.html")

def manageprojects(request):
    if not request.session.get('admin'):
        return redirect('/login/')
    
    search = request.GET.get('search', '').strip()
    p_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    proj = Project.objects.all().order_by('-created_at')

    if search:
        proj = proj.filter(
            Q(project_title__icontains=search) |
            Q(added_by__first_name__icontains=search) |
            Q(added_by__last_name__icontains=search)
        )
    
    if p_type:
        proj = proj.filter(project_type=p_type)
    
    if status:
        proj = proj.filter(project_status=status)

    stats = {
        'total': Project.objects.count(),
        'feature': Project.objects.filter(project_type='feature-film').count(),
        'short': Project.objects.filter(project_type='short-film').count(),
        'active': Project.objects.exclude(project_status='Completed').count(),
        'blocked': Project.objects.filter(rights='Blocked').count(),
    }
    
    return render(request, template_name="admin/manage_projects.html",context={'proj':proj, 'stats': stats})

def manage_castingcalls(request):
    if not request.session.get('admin'):
        return redirect('/login/')
    
    search = request.GET.get('search', '').strip()
    p_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    calls = CastingCall.objects.all().order_by('-created_at')

    if search:
        calls = calls.filter(
            Q(project_title__project_title__icontains=search) |
            Q(added_by__first_name__icontains=search) |
            Q(added_by__last_name__icontains=search)
        )
    
    if p_type:
        calls = calls.filter(project_title__project_type=p_type)
    
    if status:
        # New Project status filters
        if status in ['Pre-Production', 'Production', 'Post-Production', 'Casting', 'Released']:
            calls = calls.filter(project_title__project_status=status)
        else:
            # Fallback for old active/expired if still needed by URL but not in UI
            today = date.today()
            if status == 'active':
                calls = calls.filter(deadline__gt=today)
            elif status == 'expired':
                calls = calls.filter(deadline__lte=today)

    today = date.today()
    stats = {
        'total': CastingCall.objects.count(),
        'active': CastingCall.objects.filter(deadline__gt=today).count(),
        'expired': CastingCall.objects.filter(deadline__lte=today).count(),
        'new_today': CastingCall.objects.filter(created_at__date=today).count(),
        'feature': CastingCall.objects.filter(project_title__project_type='feature-film').count(),
        'short': CastingCall.objects.filter(project_title__project_type='short-film').count(),
    }
    
    return render(request, 'admin/manage_castingcalls.html', {'calls': calls, 'stats': stats})

def admin_delete_casting(request, id):
    if not request.session.get('admin'):
        return redirect('/login/')
    call = CastingCall.objects.get(id=id)
    call.delete()
    return redirect('/manage_admin/manage_casting/')

def manage_artistposts(request):
    if not request.session.get('admin'):
        return redirect('/login/')
    
    search = request.GET.get('search', '').strip()
    media_type = request.GET.get('type', '')

    posts = Post.objects.all().order_by('-created_at')

    if search:
        posts = posts.filter(
            Q(caption__icontains=search) |
            Q(added_by__first_name__icontains=search) |
            Q(added_by__last_name__icontains=search)
        )
    
    if media_type:
        if media_type == 'photo':
            posts = posts.filter(photopost__isnull=False).distinct()
        elif media_type == 'video':
            posts = posts.filter(videopost__isnull=False).distinct()

    today = date.today()
    stats = {
        'total': Post.objects.count(),
        'photos': PhotoPost.objects.count(),
        'videos': VideoPost.objects.count(),
        'total_likes': ArtistLike.objects.count(),
        'total_comments': ArtistComment.objects.count(),
        'new_today': Post.objects.filter(created_at__date=today).count(),
    }
    
    return render(request, 'admin/manage_posts.html', {'posts': posts, 'stats': stats})

def admin_delete_post(request, id):
    if not request.session.get('admin'):
        return redirect('/login/')
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('/manage_admin/manage_posts/')

def manage_allcomments(request):
    if not request.session.get('admin'):
        return redirect('/login/')
    
    search = request.GET.get('search', '').strip()
    c_type = request.GET.get('type', '')

    p_comments = ProjectComment.objects.all().order_by('-created_at')
    a_comments = ArtistComment.objects.all().order_by('-created_at')

    if search:
        p_comments = p_comments.filter(
            Q(comment__icontains=search) |
            Q(added_by__first_name__icontains=search) |
            Q(added_by__last_name__icontains=search)
        )
        a_comments = a_comments.filter(
            Q(comment__icontains=search) |
            Q(commented_by__first_name__icontains=search) |
            Q(commented_by__last_name__icontains=search)
        )
    
    if c_type:
        if c_type == 'project':
            a_comments = ArtistComment.objects.none()
        elif c_type == 'post':
            p_comments = ProjectComment.objects.none()

    today = date.today()
    stats = {
        'total': ProjectComment.objects.count() + ArtistComment.objects.count(),
        'project': ProjectComment.objects.count(),
        'post': ArtistComment.objects.count(),
        'project_today': ProjectComment.objects.filter(created_at__date=today).count(),
        'post_today': ArtistComment.objects.filter(created_at__date=today).count(),
    }
    
    return render(request, 'admin/manage_comments.html', {
        'p_comments': p_comments,
        'a_comments': a_comments,
        'stats': stats
    })

def admin_delete_comment(request, id, type):
    if not request.session.get('admin'):
        return redirect('/login/')
    if type == 'project':
        ProjectComment.objects.get(id=id).delete()
    else:
        ArtistComment.objects.get(id=id).delete()
    return redirect('/manage_admin/manage_comments/')

def blockproject(request,id):
    Project.objects.filter(id=id).update(rights='Blocked')
    return redirect("/manageprojects/")
def unblockproject(request,id):
    Project.objects.filter(id=id).update(rights='project')
    return redirect("/manageprojects/")

@never_cache
def admindashboard(request):
    if not request.session.get('admin'):
        return redirect('/login/')

    stats = {
        'total_users': Register.objects.exclude(rights='Admin').count(),
        'total_projects': Project.objects.count(),
        'total_casting': CastingCall.objects.count(),
        'total_posts': Post.objects.count(),
        'total_comments': ProjectComment.objects.count() + ArtistComment.objects.count(),
        'total_apps': Applications.objects.count(),
    }

    return render(request, 'admin/admin_dashboard.html', {'stats': stats})

def admin_delete_project(request, id):
    if not request.session.get('admin'):
        return redirect('/login/')
    project = get_object_or_404(Project, id=id)
    project.delete()
    return redirect('/manageprojects/')

def post_casting_call(request):
    cid = request.session['cid']
    creator = Register.objects.get(id=cid)
    if request.method == 'POST':
        role_title = request.POST.get('role_title', '').strip()
        associated_project_id = request.POST.get('associated_project')
        role_category = request.POST.get('role_category', '').strip()
        role_requirements =  request.POST.get('role_requirements', '').strip()
        required_gender = request.POST.get('required_gender', '').strip()
        age_range = request.POST.get('age_range', '').strip()
        role_description = request.POST.get('role_description', '').strip()
        compensation = request.POST.get('compensation', '').strip()
        deadline = request.POST.get('deadline')
        
        if not role_title or not compensation or not role_description or not role_requirements:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('/my_castingcalls/')
            
        pro=Project.objects.get(id=associated_project_id)
        casting_call = CastingCall(added_by=creator,project_title=pro,role_title=role_title,
                                   role_category=role_category,role_requirements=role_requirements,required_gender=required_gender,age_range=age_range,
                                   role_description=role_description,compensation=compensation,deadline=deadline)
        casting_call.save()
        messages.success(request, 'Casting call posted successfully!')
        return redirect('/my_castingcalls/')
    return render(request, "creators/creators.html")


def my_projects(request):
    cid = request.session.get('cid')
    if not cid:
        return redirect('login')
        
    # Enforce Creator Role for this view
    request.session['role'] = 'creator'

    try:
        logcreator = Register.objects.get(id=cid)
    except Register.DoesNotExist:
        return redirect('logout')

    # Get filter parameters
    project_type = request.GET.get('project_type')
    project_status = request.GET.get('project_status')
    search_query = request.GET.get('search', '').strip()

    # Start with basic filter
    projects_qs = Project.objects.filter(added_by=cid)

    # Apply additional filters if present
    if project_type and project_type != 'all':
        projects_qs = projects_qs.filter(project_type=project_type)
    if project_status and project_status != 'all':
        projects_qs = projects_qs.filter(project_status=project_status)
    if search_query:
        projects_qs = projects_qs.filter(project_title__icontains=search_query)

    # 1. Fetch ALL comments - Exclude deactivated users
    all_comments_qs = ProjectComment.objects.exclude(added_by__rights='Deactivated').select_related('added_by').prefetch_related('added_by__artistdetails_set').order_by('created_at')

    # 2. Attach these comments to the Projects
    proj = projects_qs.order_by('-created_at').prefetch_related(
        Prefetch('projectcomment_set', queryset=all_comments_qs, to_attr='all_comments')
    )

    creator_likes = ProjectLike.objects.filter(liked_by=logcreator).values_list('project_id', flat=True)

    # Prepare filter lists for the template to avoid spacing issues with auto-formatter
    type_filters = [
        {'value': 'all', 'label': 'All Types', 'selected': not project_type or project_type == 'all'},
        {'value': 'feature-film', 'label': 'Feature Film', 'selected': project_type == 'feature-film'},
        {'value': 'short-film', 'label': 'Short Film', 'selected': project_type == 'short-film'},
        {'value': 'documentary', 'label': 'Documentary', 'selected': project_type == 'documentary'},
        {'value': 'series', 'label': 'Web Series', 'selected': project_type == 'series'},
    ]

    status_filters = [
        {'value': 'all', 'label': 'All Statuses', 'selected': not project_status or project_status == 'all'},
        {'value': 'Pre-Production', 'label': 'Pre-Production', 'selected': project_status == 'Pre-Production'},
        {'value': 'Production', 'label': 'Production', 'selected': project_status == 'Production'},
        {'value': 'Post-Production', 'label': 'Post-Production', 'selected': project_status == 'Post-Production'},
        {'value': 'Casting', 'label': 'Casting', 'selected': project_status == 'Casting'},
        {'value': 'Released', 'label': 'Released', 'selected': project_status == 'Released'},
    ]

    context = {
        'proj': proj,
        'logcreator': logcreator,
        'likes': set(creator_likes),
        'type_filters': type_filters,
        'status_filters': status_filters,
        'search_query': search_query or '',
        'is_filtered': (project_type and project_type != 'all') or (project_status and project_status != 'all') or search_query,
    }

    return render(request, "creators/my_projects.html", context)

def my_castingcalls(request):
    cid = request.session.get('cid')
    if not cid:
        return redirect('login')
        
    logcreator = Register.objects.get(id=cid)
    proj = Project.objects.filter(added_by=cid)
    
    # Get filter parameters
    project_type = request.GET.get('project_type')
    project_status = request.GET.get('project_status')
    search_query = request.GET.get('search', '').strip()
    
    # Base query for casting calls
    casting_calls = CastingCall.objects.filter(added_by=cid).annotate(
        application_count=Count('applications')
    )
    
    # Apply filters
    if project_type and project_type != 'all':
        casting_calls = casting_calls.filter(project_title__project_type=project_type)
    if project_status and project_status != 'all':
        casting_calls = casting_calls.filter(project_title__project_status=project_status)
    if search_query:
        casting_calls = casting_calls.filter(
            Q(role_title__icontains=search_query) |
            Q(project_title__project_title__icontains=search_query)
        )
        
    # Prepare filter lists
    type_filters = [
        {'value': 'all', 'label': 'All Types', 'selected': not project_type or project_type == 'all'},
        {'value': 'feature-film', 'label': 'Feature Film', 'selected': project_type == 'feature-film'},
        {'value': 'short-film', 'label': 'Short Film', 'selected': project_type == 'short-film'},
        {'value': 'documentary', 'label': 'Documentary', 'selected': project_type == 'documentary'},
        {'value': 'series', 'label': 'Web Series', 'selected': project_type == 'series'},
    ]

    status_filters = [
        {'value': 'all', 'label': 'All Statuses', 'selected': not project_status or project_status == 'all'},
        {'value': 'Pre-Production', 'label': 'Pre-Production', 'selected': project_status == 'Pre-Production'},
        {'value': 'Production', 'label': 'Production', 'selected': project_status == 'Production'},
        {'value': 'Post-Production', 'label': 'Post-Production', 'selected': project_status == 'Post-Production'},
        {'value': 'Casting', 'label': 'Casting', 'selected': project_status == 'Casting'},
        {'value': 'Released', 'label': 'Released', 'selected': project_status == 'Released'},
    ]

    context = {
        'casting_calls': casting_calls,
        'proj': proj,
        'logcreator': logcreator,
        'type_filters': type_filters,
        'status_filters': status_filters,
        'search_query': search_query or '',
        'is_filtered': (project_type and project_type != 'all') or (project_status and project_status != 'all') or search_query
    }
    
    return render(request, "creators/my_castingcalls.html", context)


from django.shortcuts import redirect



def editavatar(request):
    if request.method == 'POST':
        aid = request.session.get('aid')  # Use .get() for safer access
        if not aid:
            return redirect('/login/')
        try:
            crt = Register.objects.get(id=aid)
        except Register.DoesNotExist:
            return redirect('/login/')
        image = request.FILES.get('image')
        if image:
            try:
                details = ArtistDetails.objects.get(added_by=crt)
                details.avatarphoto = image
                details.save()
            except ArtistDetails.DoesNotExist:
                ArtistDetails.objects.create(added_by=crt,avatarphoto=image)
    return redirect('/artprofile/')

def editcover(request):
    if request.method == 'POST':
        aid = request.session.get('aid')  # Use .get() for safer access
        if not aid:
            return redirect('/login/')
        try:
            crt = Register.objects.get(id=aid)
        except Register.DoesNotExist:
            return redirect('/login/')
        image = request.FILES.get('imagecover')
        if image:
            try:
                details = ArtistDetails.objects.get(added_by=crt)
                details.coverphoto = image
                details.save()
            except ArtistDetails.DoesNotExist:
                ArtistDetails.objects.create(added_by=crt, coverphoto=image)
    return redirect('/artprofile/')

def artprofile(request):
    aid = request.session['aid']
    crt = Register.objects.get(id=aid)
    castcount = CastingCall.objects.filter(deadline__gt=date.today())
    count=len(castcount)
    try:
        details=ArtistDetails.objects.get(added_by=crt)
    except:
        details=[]
    posts = Post.objects.filter(added_by=crt).order_by('-created_at')
    posts_with_data = []
    for post in posts:
        # Attach details just in case, though it's the current user
        post.added_by.details = details
        
        # Fetch comments and their replies - Exclude deactivated users
        comments_qs = ArtistComment.objects.filter(post=post, parent=None).exclude(commented_by__rights='Deactivated').order_by('created_at')
        comments_list = []
        for comment in comments_qs:
            # We must iterate and essentially 'cache' the replies on the object
            # Because if we just pass the queryset, the template re-evaluates it and custom attrs are lost
            comment.replies_list = comment.replies.all().order_by('created_at')
            comments_list.append(comment)
        
        # Fetch media
        photos = list(post.photopost_set.all())
        videos = list(post.videopost_set.all())
        post.all_media = photos + videos
        
        posts_with_data.append({'post': post, 'com': comments_list})

    # Fetch likes for the current user (crt)
    user_likes = ArtistLike.objects.filter(liked_by=crt).values_list("post_id", flat=True)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        title = request.POST.get('title')
        about = request.POST.get('about')
        gender = request.POST.get('gender')
        location = request.POST.get('location')
        skillsinput = request.POST.get('skillsinput')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        personalwebsite = request.POST.get('personalwebsite')
        instagram = request.POST.get('instagram')
        email_changed = (email != crt.email)
        phone_changed = (phone != (details.phone if details else ""))

        if email_changed and Register.objects.filter(email=email).exclude(id=aid).exists():
            messages.error(request, 'Email already exists.')
            return redirect('/artprofile/')
        
        if phone_changed and phone and ArtistDetails.objects.filter(phone=phone).exclude(added_by_id=aid).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('/artprofile/')

        if email_changed or phone_changed:
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['profile_otp'] = otp
            request.session['pending_profile_type'] = 'artist'
            request.session['pending_profile_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'title': title,
                'location': location,
                'skillsinput': skillsinput,
                'about': about,
                'gender': gender,
                'phone': phone,
                'personalwebsite': personalwebsite,
                'instagram': instagram
            }
            
            # Send OTP to CURRENT email
            subject = 'Verify Your Profile Change - SceneVerse'
            message = f'Your verification code to change your email or phone number is: {otp}. If you did not request this, please contact support immediately.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [crt.email]
            
            try:
                send_mail(subject, message, email_from, recipient_list)
                messages.success(request, f"Verification code sent to {crt.email}.")
                return redirect('/verify_profile_otp/')
            except Exception as e:
                messages.error(request, f"Error sending verification email: {e}")
                return redirect('/artprofile/')
        else:
            if details:
                ArtistDetails.objects.filter(added_by=crt).update(title=title,
                                location=location, skillsinput=skillsinput, about=about, gender=gender,
                                phone=phone, personalwebsite=personalwebsite, instagram=instagram)
            else:
                ArtistDetails.objects.create(added_by=crt, title=title,
                                        location=location, skillsinput=skillsinput, about=about,gender=gender,
                                       phone=phone, personalwebsite=personalwebsite, instagram=instagram)
            Register.objects.filter(id=aid).update(first_name=first_name,last_name=last_name,email=email)
            messages.success(request, 'Profile updated successfully!')
            return redirect('/artprofile/')
    
    unread_count = get_unread_msg_count(aid)

    context = {
        'details': details,
        'crt': crt,
        'count': count,
        'all_artist_posts': posts_with_data,  # Matching variable name for template reuse
        'creator_likes': list(user_likes),    # Matching variable name for template reuse
        'unread_count': unread_count,
        'post_count': posts.count(),
    }
    return render(request, "artists/artprofile.html", context)

def castingcalls(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')
        
    reg = Register.objects.get(id=aid)
    artd = ArtistDetails.objects.get(added_by=aid)
    
    # Base Query - Exclude deactivated users
    details = CastingCall.objects.filter(
        deadline__gt=date.today()
    ).exclude(
        added_by__rights='Deactivated'
    ).select_related('added_by', 'project_title').order_by('-created_at')

    # 1. Filter by Project Type
    project_type = request.GET.get('project_type')
    if project_type:
        details = details.filter(project_title__project_type=project_type)

    # 2. Filter by Project Status
    project_status = request.GET.get('project_status')
    if project_status:
        details = details.filter(project_title__project_status=project_status)

    # 3. Search by Role, Project Title, or Creator Name
    search_query = request.GET.get('search', '').strip()
    if search_query:
        details = details.filter(
            Q(role_title__icontains=search_query) |
            Q(project_title__project_title__icontains=search_query) |
            Q(added_by__first_name__icontains=search_query) |
            Q(added_by__last_name__icontains=search_query)
        )

    # Filter Options (Synchronized with New Project Form)
    PROJECT_TYPES = [
        ('feature-film', 'Feature Film'),
        ('short-film', 'Short Film'),
        ('documentary', 'Documentary'),
        ('series', 'Web Series'),
    ]

    STATUS_CHOICES = [
        ('Pre-Production', 'Pre-Production'),
        ('Production', 'Production'),
        ('Post-Production', 'Post-Production'),
        ('Casting', 'Casting'),
        ('Released', 'Released'),
    ]

    type_filters = [{'value': t[0], 'label': t[1], 'selected': t[0] == project_type} for t in PROJECT_TYPES]
    status_filters = [{'value': s[0], 'label': s[1], 'selected': s[0] == project_status} for s in STATUS_CHOICES]
    is_filtered = bool(project_type or project_status or search_query)

    applied_ids = Applications.objects.filter(details_of=artd).values_list('casting_id_id', flat=True)

    if request.method == 'POST':

        message = request.POST.get('message')
        casting_id = request.POST.get('casting_id')
        cast=CastingCall.objects.get(id=casting_id)
        applications_form = Applications(
            casting_id=cast, 
            added_by=reg, 
            details_of=artd, 
            message=message
        )
        applications_form.save()
        
        # Handle multiple file uploads
        media_files = request.FILES.getlist('media_files')
        for file in media_files:
            # Determine file type
            file_type = 'unknown'
            if file.content_type.startswith('image'):
                file_type = 'image'
            elif file.content_type.startswith('video'):
                file_type = 'video'
                
            ApplicationAttachment.objects.create(
                application=applications_form,
                file=file,
                file_type=file_type
            )

        applied_ids = Applications.objects.filter(details_of=artd).values_list('casting_id_id', flat=True)


    return render(
        request, 
        "artists/casting_calls.html",
        {
            'reg': reg,
            'details': details,
            'artd': artd,
            'count': details.count(),
            'applied_ids': list(applied_ids),
            'type_filters': type_filters,
            'status_filters': status_filters,
            'is_filtered': is_filtered,
            'search_query': search_query or ''
        }
    )

def applications(request):
    cid = request.session['cid']
    crt = Register.objects.get(id=cid)
    
    # Optimized query to fetch all non-rejected applications for this creator's casting calls
    apps_qs = Applications.objects.filter(
        casting_id__added_by=crt
    ).exclude(
        application_status="Rejected"
    ).select_related(
        'added_by', 
        'casting_id', 
        'casting_id__project_title', # Fetch project as well
        'details_of'
    ).prefetch_related('attachments')

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'oldest':
        apps_qs = apps_qs.order_by('created_at')
    else:
        apps_qs = apps_qs.order_by('-created_at')

    # Filter by Project (Casting Call ID)
    project_id = request.GET.get('project_id')
    if project_id and project_id != 'All Projects':
        apps_qs = apps_qs.filter(casting_id__id=project_id)

    # Filter by Status
    status_filter = request.GET.getlist('status')
    if status_filter:
        apps_qs = apps_qs.filter(application_status__in=status_filter)

    # Flatten data for template to avoid lookup issues
    data = []
    import json
    for app in apps_qs:
        attachments = []
        for att in app.attachments.all():
            attachments.append({
                'url': att.file.url,
                'type': att.file_type
            })
            
        data.append({
            'app': app,
            'role': app.casting_id.role_title,
            'project': app.casting_id.project_title.project_title,
            'attachments_json': json.dumps(attachments)
        })
    
    # Casting Calls for Dropdown
    creator_casting_calls = CastingCall.objects.filter(added_by=crt)
    
    # Pre-calculate selection to avoid template syntax issues with auto-formatters
    selected_proj_int = int(project_id) if project_id and project_id.isdigit() else None
    for cc in creator_casting_calls:
        cc.is_selected = (cc.id == selected_proj_int)

    return render(request, "creators/applications_v2.html", {
        'crt': crt,
        'applications': data,
        'creator_casting_calls': creator_casting_calls,
        'selected_project': selected_proj_int,
        'selected_status': status_filter,
        'pending_checked': 'Pending' in status_filter,
        'shortlisted_checked': 'Short Listed' in status_filter,
        'reviewed_checked': 'Reviewed' in status_filter,
        'sort_by': sort_by,
    })

def manageapplication(request):
    if request.method == 'POST':
        mid = request.POST.get('mid')
        b=request.POST.get('button')
        if b == 'reject':
            Applications.objects.filter(id=mid).update(application_status='Rejected')
        elif b == 'shortlist':
            Applications.objects.filter(id=mid).update(application_status='Short Listed')
        elif b == 'review':
            Applications.objects.filter(id=mid).update(application_status='Reviewed')

    return redirect("/applications/")

def myapplications(request):
    aid = request.session.get('aid')
    artist = Register.objects.get(id=aid)
    artist_details = ArtistDetails.objects.get(added_by=aid)
    applications = Applications.objects.filter(added_by=artist).order_by('-created_at').prefetch_related('attachments')
    count = CastingCall.objects.filter(deadline__gt=date.today()).count()

    import json
    import json
    apps_data = []
    for app in applications:
        attachments = []
        for att in app.attachments.all():
            attachments.append({
                'url': att.file.url,
                'type': att.file_type
            })
        
        # Attach JSON directly to the object to avoid template changes
        app.attachments_json = json.dumps(attachments)
        apps_data.append(app)

    return render(
        request,
        "artists/my_applications.html",
        {
            'crt': artist,
            'details': artist_details,
            'applications': apps_data,
            'count': count
        }
    )

def findprojects(request):
    aid = request.session.get('aid')
    if not aid:
         return redirect('login') 
         
    artist = Register.objects.get(id=aid)

    try:
        details = ArtistDetails.objects.get(added_by=aid)
    except:
        details = None

    projects = Project.objects.exclude(
        added_by=aid
    ).exclude(
        added_by__rights='Deactivated'
    ).select_related('added_by').prefetch_related('added_by__artistdetails_set').order_by('-created_at')

    # fetch comments & likes
    # Optimized fetching: Get all top-level comments with their replies pre-fetched
    comments_qs = ProjectComment.objects.filter(parent=None).prefetch_related('replies').order_by('created_at')
    
    # We need to map comments to projects to avoid N+1 in template or complex logic
    # But since the template iterates projects -> comments, we should prefetch comments on projects
    
    # 1. Fetch ALL comments (Artists + Creators) - Exclude deactivated users
    all_comments_qs = ProjectComment.objects.exclude(added_by__rights='Deactivated').select_related('added_by').prefetch_related('added_by__artistdetails_set').order_by('created_at')

    # 2. Attach these comments to the Projects
    # Filter by Project Type
    project_type = request.GET.get('project_type')
    if project_type:
        projects = projects.filter(project_type=project_type)

    # Filter by Status
    project_status = request.GET.get('project_status')
    if project_status:
        projects = projects.filter(project_status=project_status)

    # Search by Title or Creator Name
    search_query = request.GET.get('search', '').strip()
    if search_query:
        projects = projects.filter(
            Q(project_title__icontains=search_query) |
            Q(added_by__first_name__icontains=search_query) |
            Q(added_by__last_name__icontains=search_query)
        )

    # Note: This attaches ALL comments. Filtering for top-level happens in template or we can refine here.
    projects = projects.prefetch_related(
        Prefetch('projectcomment_set', queryset=all_comments_qs, to_attr='all_comments')
    )

    likes = ProjectLike.objects.filter(liked_by=artist).values_list("project_id", flat=True)

    castcount = CastingCall.objects.filter(deadline__gt=date.today()).count()

    # Filter Options (Synchronized with New Project Form)
    PROJECT_TYPES = [
        ('feature-film', 'Feature Film'),
        ('short-film', 'Short Film'),
        ('documentary', 'Documentary'),
        ('series', 'Web Series'),
    ]

    STATUS_CHOICES = [
        ('Pre-Production', 'Pre-Production'),
        ('Production', 'Production'),
        ('Post-Production', 'Post-Production'),
        ('Casting', 'Casting'),
        ('Released', 'Released'),
    ]

    type_filters = [{'value': t[0], 'label': t[1], 'selected': t[0] == project_type} for t in PROJECT_TYPES]
    status_filters = [{'value': s[0], 'label': s[1], 'selected': s[0] == project_status} for s in STATUS_CHOICES]
    is_filtered = bool(project_type or project_status or search_query)

    return render(
        request,
        "artists/find_projects.html",
        {
            'crt': artist,
            'details': details,
            'projects': projects,
            # 'comments': comments, # Removed as we attached to projects
            'likes': likes,
            'count': castcount,
            'logartist': artist, # For template compatibility
            'type_filters': type_filters,
            'status_filters': status_filters,
            'is_filtered': is_filtered,
            'search_query': search_query,
        }
    )


def project_like(request):
    if request.method == "POST":
        # Get session data
        aid = request.session.get('aid')
        cid = request.session.get('cid')
        role = request.session.get('role')

        # Robustly determine user based on active role
        user_id = None
        if role == 'creator' and cid:
            user_id = cid
        elif role == 'artist' and aid:
            user_id = aid
        else:
            # Fallback: Prefer Artist if generic (legacy behavior) but check both
            user_id = aid if aid else cid

        if not user_id:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)

        try:
            user = Register.objects.get(id=user_id)
            project_id = request.POST.get('project_id')
            
            if not project_id:
                  return JsonResponse({'success': False, 'error': 'No project ID provided'}, status=400)
            
            project = Project.objects.get(id=project_id)
            
            existing = ProjectLike.objects.filter(project=project, liked_by=user)
            is_liked = False

            if existing.exists():
                existing.delete()
                is_liked = False
            else:
                ProjectLike.objects.create(project=project, liked_by=user)
                is_liked = True

            new_like_count = ProjectLike.objects.filter(project=project).count()

            return JsonResponse({
                'success': True,
                'is_liked': is_liked,
                'count': new_like_count,
                'project_id': project_id
            })
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def project_comment(request):
    if request.method == "POST":
        aid = request.session.get('aid')
        cid = request.session.get('cid')
        
        user_id = aid if aid else cid
        if not user_id:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)

        try:
            user = Register.objects.get(id=user_id)
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, id=project_id)
        except (Register.DoesNotExist, Project.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid ID'}, status=404)

        comment_text = request.POST.get('comment', '').strip()
        if not comment_text:
             return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = ProjectComment.objects.get(id=parent_id)
            except ProjectComment.DoesNotExist:
                pass

        save_comment = ProjectComment(
            project=project,
            added_by=user,
            comment=comment_text,
            parent=parent
        )
        save_comment.save()

        comment_time_formatted = timezone.localtime(save_comment.created_at).strftime("%b %d, %Y %H:%M") # actually timesince in template usually
        
        # Prepare HTML for response
        # Determine Profile Link
        if user.role == 'creator':
             profile_url = f"/view_creator_profile/{user.id}/"
             if user.id == cid: profile_url = "/creator_profile/" # self
        else:
             profile_url = f"/view_artist_profile/{user.id}/"
             if user.id == aid: profile_url = "/artprofile/" # self

        # Determine Avatar
        avatar_url = "https://ui-avatars.com/api/?name=" + user.first_name + "+" + user.last_name + "&background=random"
        try:
            if user.role == 'artist':
                details = ArtistDetails.objects.get(added_by=user)
                if details.avatarphoto:
                    avatar_url = details.avatarphoto.url
            # For creators, maybe they don't have avatar model yet? Using default/ui-avatar for now or if you have CreatorDetails
        except:
            pass

        # Reply/Edit/Delete Buttons logic
        # Since this response is for the user who JUST posted, they OWN the comment.
        # So we include Edit/Delete buttons.
        
        action_buttons = f"""
            <div class="d-flex gap-2 align-items-center mt-1">
                 <button class="btn btn-link btn-sm p-0 text-decoration-none text-muted reply-btn" data-comment-id="{save_comment.id}">Reply</button>
                 <button class="btn btn-link btn-sm p-0 text-decoration-none text-muted edit-btn" data-comment-id="{save_comment.id}" data-comment-text="{comment_text}">Edit</button>
                 <button class="btn btn-link btn-sm p-0 text-decoration-none text-danger delete-btn" data-comment-id="{save_comment.id}">Delete</button>
            </div>
        """

        container_class = "comment-box bg-opacity-75 d-flex align-items-start" if parent else "comment-box d-flex align-items-start"
        
        # We need to structure it exactly as the template expects for consistency
        # Assuming template uses:
        
        comment_html = f"""
        <div class="mb-2">
            <div class="{container_class}">
                <a href="{profile_url}">
                    <img src="{avatar_url}" class="rounded-circle me-2" width="40" height="40" style="object-fit:cover;">
                </a>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between">
                        <a href="{profile_url}" class="fw-bold text-decoration-none text-white">
                            {user.first_name} {user.last_name}
                        </a>
                        <small class="text-muted">Just now</small>
                    </div>
                    <p class="mb-1">{comment_text}</p>
                    {action_buttons}
                </div>
            </div>
            <!-- Container for nested replies if top-level -->
            {'' if parent else f'<div class="ms-4 border-start ps-3"><form method="POST" action="/projectcomment/" class="reply-form d-none mt-2" id="reply-form-{save_comment.id}"><input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get("csrftoken")}"><input type="hidden" name="project_id" value="{project.id}"><input type="hidden" name="parent_id" value="{save_comment.id}"><div class="input-group input-group-sm"><input type="text" name="comment" class="form-control" placeholder="Write a reply..."><button class="btn btn-secondary" type="submit">Reply</button></div></form></div>'}
        </div>
        """
        
        # If it's a reply, we just return the inner box content usually, but the JS expects full HTML to append. 
        # For a reply, the template structure is a bit simpler (no outer mb-2 wrapper needed strictly, but let's keep consistent)
        
        if parent:
             comment_html = f"""
            <div class="{container_class}">
                <a href="{profile_url}">
                    <img src="{avatar_url}" class="rounded-circle me-2" width="30" height="30" style="object-fit:cover;">
                </a>
                <div class="flex-grow-1">
                    <a href="{profile_url}" class="fw-bold text-decoration-none text-white small">
                        {user.first_name} {user.last_name}
                    </a>
                    <p class="small mb-0 comment-text">{comment_text}</p>
                    {action_buttons}
                </div>
            </div>
            """

        return JsonResponse({
            'success': True,
            'project_id': project_id,
            'comment_html': comment_html,
            'parent_id': parent_id
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def edit_project_comment(request, comment_id):
    if request.method == "POST":
        uid = request.session.get('cid') or request.session.get('aid')
        if not uid:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
            
        comment = get_object_or_404(ProjectComment, id=comment_id)
        
        if comment.added_by.id != int(uid):
             return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
             
        new_text = request.POST.get('comment', '').strip()
        if not new_text:
             return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

        if new_text:
            comment.comment = new_text
            comment.save()
            return JsonResponse({'success': True, 'comment': new_text})
            
    return JsonResponse({'success': False}, status=400)


def view_my_posts(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('/login/')
    artist = Register.objects.get(id=aid)

    try:
        details = ArtistDetails.objects.get(added_by=artist)
    except:
        details = None
    posts = Post.objects.filter(added_by=artist).order_by('-created_at')
    comments = ArtistComment.objects.all()
    likes = ArtistLike.objects.filter(liked_by=artist).values_list("post_id", flat=True)
    castcount = CastingCall.objects.filter(deadline__gt=date.today()).count()
    posts_with_media = []
    for post in posts:
        # Combine the media querysets into a single list
        photos = list(post.photopost_set.all())
        videos = list(post.videopost_set.all())

        # Attach the combined list to the post object
        post.all_media = photos + videos
        posts_with_media.append(post)
    return render(
        request,
        "artists/view_my_posts.html",
        {
            'crt': artist,
            'details': details,
            'posts': posts_with_media,
            'comments': comments,
            'likes': likes,
            'count': castcount
        }
    )

def artist_like(request):
    if request.method == "POST":
        aid = request.session.get('aid')
        try:
            artist = Register.objects.get(id=aid)
        except Register.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        post_id = request.POST.get('post_id')
        try:
            post = get_object_or_404(Post, id=post_id)
        except Exception:
             return JsonResponse({'error': 'Post not found'}, status=404)

        existing = ArtistLike.objects.filter(post=post, liked_by=artist)
        is_liked = False

        if existing.exists():
            existing.delete()
            is_liked = False
        else:
            ArtistLike.objects.create(post=post, liked_by=artist)
            is_liked = True

        new_like_count = ArtistLike.objects.filter(post=post).count()

        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'count': new_like_count,
            'post_id': post_id
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def artist_comment(request):
    if request.method == "POST":
        aid = request.session.get('aid')
        if not aid:
             return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
        try:
            artist = Register.objects.get(id=aid)
        except Register.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment', '').strip()
        if not comment_text:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
        parent_id = request.POST.get('parent_id')

        try:
            post = get_object_or_404(Post, id=post_id)
        except Exception:
            return JsonResponse({'error': 'Post not found'}, status=404)

        parent = None
        if parent_id:
            try:
                parent = ArtistComment.objects.get(id=parent_id)
            except ArtistComment.DoesNotExist:
                pass

        # Create the comment object
        new_comment = ArtistComment.objects.create(
            post=post,
            commented_by=artist,
            comment=comment_text,
            parent=parent
        )

        comment_time_formatted = timezone.localtime(new_comment.created_at).strftime("%b %d, %Y %H:%M")
        
        # Prepare avatar HTML
        try:
            details = ArtistDetails.objects.filter(added_by=artist).first()
            if details and details.avatarphoto:
                avatar_url = details.avatarphoto.url
            else:
                avatar_url = f"https://ui-avatars.com/api/?name={artist.first_name}"
        except:
             avatar_url = f"https://ui-avatars.com/api/?name={artist.first_name}"
        
        is_reply = parent is not None

        if is_reply:
             # Reply HTML
             comment_html = f"""
                <div class="comment-box d-flex align-items-start mt-2" id="comment-{new_comment.id}">
                    <img src="{avatar_url}" class="rounded-circle me-2" width="25" height="25" style="object-fit:cover;">
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start">
                             <div>
                                <span class="comment-author text-info small d-block font-weight-bold">
                                    {artist.first_name} {artist.last_name}
                                </span>
                                <span class="text-white-50 comment-text">{new_comment.comment}</span>
                            </div>
                             <div class="dropdown">
                                <button class="btn btn-link btn-sm text-muted p-0" data-bs-toggle="dropdown">
                                    <i class="bi bi-three-dots-vertical"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                                    <li><a class="dropdown-item btn-edit-comment" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                                    <li><a class="dropdown-item btn-delete-comment text-danger" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-trash me-2"></i>Delete</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            """
        else:
            # Top-level HTML
             comment_html = f"""
                <div class="comment-group mb-3">
                    <div class="comment-box d-flex align-items-start" id="comment-{new_comment.id}">
                         <a href="#">
                            <img src="{avatar_url}" class="rounded-circle me-2" width="30" height="30" style="object-fit:cover;">
                        </a>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                     <span class="comment-author text-primary small d-block font-weight-bold">
                                        {artist.first_name} {artist.last_name}
                                    </span>
                                    <span class="text-white-50 comment-text">{new_comment.comment}</span>
                                     <div class="mt-1">
                                        <a href="#" class="btn-reply-comment text-muted small text-decoration-none" data-comment-id="{new_comment.id}">
                                            <i class="bi bi-reply me-1"></i>Reply
                                        </a>
                                    </div>
                                </div>
                                <div class="dropdown">
                                    <button class="btn btn-link btn-sm text-muted p-0" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots-vertical"></i>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                                        <li><a class="dropdown-item btn-edit-comment" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                                        <li><a class="dropdown-item btn-delete-comment text-danger" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-trash me-2"></i>Delete</a></li>
                                    </ul>
                                </div>
                            </div>
                            
                            <!-- Reply Form -->
                            <div class="reply-form-container mt-2" id="reply-form-{new_comment.id}" style="display: none;">
                                <form method="POST" action="/artistcomment/" class="text-end">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                                    <input type="hidden" name="post_id" value="{post_id}">
                                    <input type="hidden" name="parent_id" value="{new_comment.id}">
                                    <textarea name="comment" class="form-control form-control-sm mb-2" rows="1" placeholder="Write a reply..." required></textarea>
                                    <div class="d-flex justify-content-end gap-2">
                                        <button type="button" class="btn btn-sm btn-outline-secondary btn-cancel-reply" data-comment-id="{new_comment.id}">Cancel</button>
                                        <button type="submit" class="btn btn-sm btn-primary px-3">Reply</button>
                                    </div>
                                </form>
                            </div>
                            
                            <!-- Replies Container -->
                            <div class="replies-container ms-4 border-start ps-3 mt-2" id="replies-{new_comment.id}"></div>
                        </div>
                    </div>
                </div>
            """

        return JsonResponse({
            'success': True,
            'post_id': post_id,
            'comment_id': new_comment.id,
            'parent_id': parent_id if parent_id else None,
            'comment_html': comment_html
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@never_cache
def logout(request):
    next_url = request.GET.get('next', "/login/")
    request.session.flush()
    response = redirect(next_url)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response



@never_cache
def findartists(request):
    if not request.session.get('cid'):
        return redirect('/login/')

    cid = request.session.get('cid')
    creator = Register.objects.get(id=cid)

    all_posts = Post.objects.exclude(added_by__rights='Deactivated').order_by('-created_at')
    
    # Search Filter
    query = request.GET.get('q', '').strip()
    if query:
        all_posts = all_posts.filter(
            Q(added_by__first_name__icontains=query) | 
            Q(added_by__last_name__icontains=query) |
            Q(caption__icontains=query)
        )

    posts_with_media = []
    for post in all_posts:
        try:
            post.added_by.details = ArtistDetails.objects.get(added_by=post.added_by)
        except ArtistDetails.DoesNotExist:
            post.added_by.details = None
        comment=ArtistComment.objects.filter(post=post, parent=None).order_by('created_at')
        photos = list(post.photopost_set.all())
        videos = list(post.videopost_set.all())
        post.all_media = photos + videos
        posts_with_media.append({'post':post,'com':comment})

    creator_likes = ArtistLike.objects.filter(liked_by=creator).values_list("post_id", flat=True)
    logcreator = Register.objects.filter(id=cid)
    proj = Project.objects.filter(added_by=cid)

    return render(
        request,
        "creators/find_artists.html",
        {
            'logcreator': logcreator,
            'projects': proj,
            'all_artist_posts': posts_with_media,
            'creator_likes': list(creator_likes),
        }
    )


def creator_artist_like(request):
    if request.method == "POST":
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        
        if not cid and not aid:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)

        user = None
        if cid:
            try:
                user = Register.objects.get(id=cid)
            except Register.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
        elif aid:
            try:
                user = Register.objects.get(id=aid)
            except Register.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

        post_id = request.POST.get('post_id')
        try:
            post = get_object_or_404(Post, id=post_id)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)

        existing = ArtistLike.objects.filter(post=post, liked_by=user)
        is_liked = False

        if existing.exists():
            existing.delete()
            is_liked = False
        else:
            ArtistLike.objects.create(post=post, liked_by=user)
            is_liked = True

        new_like_count = ArtistLike.objects.filter(post=post).count()

        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'count': new_like_count,
            'post_id': post_id
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def creator_artist_comment(request):
    if request.method == "POST":
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        
        if not cid and not aid:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)

        user = None
        if cid:
            try:
                user = Register.objects.get(id=cid)
            except Register.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
        elif aid:
            try:
                user = Register.objects.get(id=aid)
            except Register.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment', '').strip()
        if not comment_text:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
        parent_id = request.POST.get('parent_id')

        try:
            post = get_object_or_404(Post, id=post_id)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)

        parent = None
        if parent_id:
            try:
                parent = ArtistComment.objects.get(id=parent_id)
            except ArtistComment.DoesNotExist:
                pass

        new_comment = ArtistComment.objects.create(
            post=post,
            commented_by=user,
            comment=comment_text,
            parent=parent
        )

        # Prepare avatar HTML to match template logic
        details = user.artistdetails_set.first()
        if details and details.avatarphoto:
            avatar_url = details.avatarphoto.url
        else:
            avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}"

        is_reply = parent is not None

        # Determine Profile URL based on Role and Session
        profile_url = "#"
        if cid and user.id == cid:
            profile_url = "/creator_profile/"
        elif aid and user.id == aid:
            profile_url = "/artprofile/"
        elif user.role == 'creator':
            profile_url = f"/view_creator_profile/{user.id}/"
        else:
            profile_url = f"/view_artist_profile/{user.id}/"

        # Generate HTML based on whether it's a reply or top-level comment
        if is_reply:
            # Reply HTML - simpler structure
            comment_html = f"""
                <div class="comment-box d-flex align-items-start mt-2" id="comment-{new_comment.id}">
                    <img src="{avatar_url}" class="rounded-circle me-2" width="25" height="25" style="object-fit:cover;">
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <a href="{profile_url}" class="comment-author text-info small d-block font-weight-bold text-decoration-none">
                                    {user.first_name} {user.last_name}
                                </a>
                                <span class="text-white-50 comment-text">
                                    {new_comment.comment}
                                </span>
                            </div>
                            <div class="dropdown">
                                <button class="btn btn-link btn-sm text-muted p-0" data-bs-toggle="dropdown">
                                    <i class="bi bi-three-dots-vertical"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                                    <li><a class="dropdown-item btn-edit-comment" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                                    <li><a class="dropdown-item btn-delete-comment text-danger" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-trash me-2"></i>Delete</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            """
        else:
            # Top-level comment HTML - includes reply form and container
            comment_html = f"""
                <div class="comment-group mb-3">
                    <div class="comment-box d-flex align-items-start" id="comment-{new_comment.id}">
                        <a href="{profile_url}">
                            <img src="{avatar_url}" class="rounded-circle me-2" width="30" height="30" style="object-fit:cover;">
                        </a>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <a href="{profile_url}" class="comment-author text-primary small d-block font-weight-bold text-decoration-none">
                                        {user.first_name} {user.last_name}
                                    </a>
                                    <span class="text-white-50 comment-text">{new_comment.comment}</span>
                                    <div class="mt-1">
                                        <a href="#" class="btn-reply-comment text-muted small text-decoration-none" data-comment-id="{new_comment.id}">
                                            <i class="bi bi-reply me-1"></i>Reply
                                        </a>
                                    </div>
                                </div>
                                <div class="dropdown">
                                    <button class="btn btn-link btn-sm text-muted p-0" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots-vertical"></i>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                                        <li><a class="dropdown-item btn-edit-comment" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                                        <li><a class="dropdown-item btn-delete-comment text-danger" href="#" data-comment-id="{new_comment.id}"><i class="bi bi-trash me-2"></i>Delete</a></li>
                                    </ul>
                                </div>
                            </div>

                            <div class="reply-form-container mt-2" id="reply-form-{new_comment.id}" style="display: none;">
                                <form method="POST" action="/comment_artist_post/" class="text-end">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">
                                    <input type="hidden" name="post_id" value="{post_id}">
                                    <input type="hidden" name="parent_id" value="{new_comment.id}">
                                    <textarea name="comment" class="form-control form-control-sm mb-2" rows="1" placeholder="Write a reply..." required></textarea>
                                    <div class="d-flex justify-content-end gap-2">
                                        <button type="button" class="btn btn-sm btn-outline-secondary btn-cancel-reply" data-comment-id="{new_comment.id}">Cancel</button>
                                        <button type="submit" class="btn btn-sm btn-primary px-3">Reply</button>
                                    </div>
                                </form>
                            </div>

                            <div class="replies-container ms-4 border-start ps-3 mt-2" id="replies-{new_comment.id}">
                            </div>
                        </div>
                    </div>
                </div>
            """

        return JsonResponse({
            'success': True,
            'post_id': post_id,
            'comment_id': new_comment.id,
            'parent_id': parent_id if parent_id else None,
            'comment_html': comment_html
        })

def edit_artist_comment(request, comment_id):
    if request.method == "POST":
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        current_user_id = cid or aid

        if not current_user_id:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
        
        comment = get_object_or_404(ArtistComment, id=comment_id)
        if str(comment.commented_by.id) != str(current_user_id):
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        new_text = request.POST.get('comment', '').strip()
        if not new_text:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
        
        if new_text:
            comment.comment = new_text
            comment.save()
            return JsonResponse({'success': True, 'new_text': new_text})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def delete_artist_comment(request, comment_id):
    if request.method == "POST":
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        current_user_id = cid or aid

        if not current_user_id:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
        
        comment = get_object_or_404(ArtistComment, id=comment_id)
        post_owner_id = comment.post.added_by.id
        
        # Allow deletion if current user is the comment author OR the post owner
        if str(comment.commented_by.id) != str(current_user_id) and str(post_owner_id) != str(current_user_id):
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        comment.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@never_cache
def creator_profile(request):
    if not request.session.get('cid'):
        return redirect('/login/')

    cid = request.session.get('cid')
    crt = Register.objects.get(id=cid)
    proj = Project.objects.filter(added_by=cid)
    recent_projects = Project.objects.filter(added_by=cid).order_by('-created_at')[:3]
    deadline = CastingCall.objects.filter(added_by=cid).order_by('deadline')[:3]

    details = ArtistDetails.objects.filter(added_by=crt).first()

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        about = request.POST.get('about')
        location = request.POST.get('location')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        personalwebsite = request.POST.get('personalwebsite')
        instagram = request.POST.get('instagram')
        avatarphoto = request.FILES.get('avatarphoto')

        email_changed = (email != crt.email)
        phone_changed = (phone != (details.phone if details else ""))

        if email_changed and Register.objects.filter(email=email).exclude(id=cid).exists():
            messages.error(request, 'Email already exists.')
            return redirect('/creator_profile/')
        
        if phone_changed and phone and ArtistDetails.objects.filter(phone=phone).exclude(added_by_id=cid).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('/creator_profile/')

        if email_changed or phone_changed:
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['profile_otp'] = otp
            request.session['pending_profile_type'] = 'creator'
            request.session['pending_profile_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'about': about,
                'location': location,
                'phone': phone,
                'personalwebsite': personalwebsite,
                'instagram': instagram
            }
            # Handle Avatar (cannot easily put file in session, usually store temporarily or skip)
            # For now, let's skip avatar update if OTP is needed, or just let users re-upload
            # Actually, I can save the file name or something, but it's simpler to skip files for OTP updates
            
            # Send OTP to CURRENT email
            subject = 'Verify Your Profile Change - SceneVerse'
            message = f'Your verification code to change your email or phone number is: {otp}. If you did not request this, please contact support immediately.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [crt.email]
            
            try:
                send_mail(subject, message, email_from, recipient_list)
                messages.success(request, f"Verification code sent to {crt.email}.")
                return redirect('/verify_profile_otp/')
            except Exception as e:
                messages.error(request, f"Error sending verification email: {e}")
                return redirect('/creator_profile/')
        else:
            if details:
                details.location = location
                details.about = about
                details.phone = phone
                details.personalwebsite = personalwebsite
                details.instagram = instagram
                if avatarphoto:
                    details.avatarphoto = avatarphoto
                details.save()
            else:
                ArtistDetails.objects.create(
                    added_by=crt,
                    location=location,
                    about=about,
                    phone=phone,
                    personalwebsite=personalwebsite,
                    instagram=instagram,
                    avatarphoto=avatarphoto
                )

            Register.objects.filter(id=cid).update(first_name=first_name, last_name=last_name, email=email)
            messages.success(request, 'Profile updated successfully!')
            return redirect('/creator_profile/')

    # Stats
    total_projects = Project.objects.filter(added_by=cid).count()
    total_casting_calls = CastingCall.objects.filter(added_by=cid).count()
    # Mocking applications count for now as it needs a complex query
    total_applications = Applications.objects.filter(casting_id__added_by=crt).count()

    context = {
        'crt': crt,
        'proj': proj,
        '3proj': recent_projects,
        'deadline': deadline,
        'details': details,
        'stats': {
            'projects': total_projects,
            'casting_calls': total_casting_calls,
            'applications': total_applications,
        }
    }

    return render(request, "creators/creator_profile.html", context)



def project_creator_comment(request):
    if request.method == "POST":
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        user_id = cid or aid

        if not user_id:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
        
        user = None
        if cid:
            try: user = Register.objects.get(id=cid)
            except: pass
        elif aid:
            try: user = Register.objects.get(id=aid)
            except: pass
            
        if not user:
             return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

        project_id = request.POST.get('project_id')
        parent_id = request.POST.get('parent_id')
        comment_text = request.POST.get('comment', '').strip()

        if not comment_text:
             return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

        project = get_object_or_404(Project, id=project_id)

        parent_obj = None
        if parent_id:
            parent_obj = get_object_or_404(ProjectComment, id=parent_id)

        # Save to Database
        new_comment = ProjectComment.objects.create(
            project=project,
            added_by=user,
            comment=comment_text,
            parent=parent_obj
        )

        # Prepare avatar and profile URL
        # Logic for the person icon/color
        avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=random"
        details = None
        try:
            details = ArtistDetails.objects.filter(added_by=user).first()
            if details and details.avatarphoto:
                avatar_url = details.avatarphoto.url
        except: pass

        # Profile URL Logic
        profile_url = "#"
        if user.role == 'creator':
             profile_url = f"/view_creator_profile/{user.id}/"
             if str(user.id) == str(cid): profile_url = "/creator_profile/"
        else:
             profile_url = f"/view_artist_profile/{user.id}/"
             if str(user.id) == str(aid): profile_url = "/artprofile/"


        # Build the HTML String (Matching my_projects.html structure)
        is_reply = parent_id is not None
        
        if is_reply:
            # Reply HTML (Structure: comment-box bg-opacity-75 inside ms-4)
            comment_html = f"""
            <div class="comment-box bg-opacity-75 d-flex align-items-start" id="comment-{new_comment.id}">
                <a href="{profile_url}">
                    <img src="{avatar_url}" class="rounded-circle me-2" width="30" height="30" style="object-fit:cover;">
                </a>
                <div class="flex-grow-1">
                    <a href="{profile_url}" class="fw-bold text-decoration-none text-white small">
                        {user.first_name} {user.last_name}
                    </a>
                    <p class="small mb-0 comment-text">{new_comment.comment}</p>
                    <div class="d-flex gap-2 align-items-center mt-1">
                        <button class="btn btn-link btn-sm p-0 text-decoration-none text-muted edit-btn"
                            data-comment-id="{new_comment.id}"
                            data-comment-text="{new_comment.comment}"
                            style="font-size: 0.75rem;">Edit</button>
                        <button class="btn btn-link btn-sm p-0 text-decoration-none text-danger delete-btn"
                            data-comment-id="{new_comment.id}"
                            style="font-size: 0.75rem;">Delete</button>
                    </div>
                </div>
            </div>
            """
        else:
            # Top-level HTML (Structure: mb-2 > comment-box > replies container > hidden form)
            comment_html = f"""
            <div class="mb-2">
                <div class="comment-box d-flex align-items-start" id="comment-{new_comment.id}">
                    <a href="{profile_url}">
                        <img src="{avatar_url}" class="rounded-circle me-2" width="40" height="40" style="object-fit:cover;">
                    </a>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between">
                            <a href="{profile_url}" class="fw-bold text-decoration-none text-white">
                                {user.first_name} {user.last_name}
                            </a>
                            <small class="text-muted">just now</small>
                        </div>
                        <p class="mb-1">{new_comment.comment}</p>
                        <div class="d-flex gap-2 align-items-center">
                            <button class="btn btn-link btn-sm p-0 text-decoration-none text-muted reply-btn"
                                data-comment-id="{new_comment.id}">Reply</button>
                            <button class="btn btn-link btn-sm p-0 text-decoration-none text-muted edit-btn"
                                data-comment-id="{new_comment.id}"
                                data-comment-text="{new_comment.comment}">Edit</button>
                            <button class="btn btn-link btn-sm p-0 text-decoration-none text-danger delete-btn"
                                data-comment-id="{new_comment.id}">Delete</button>
                        </div>
                    </div>
                </div>

                <!-- Replies Container -->
                <div class="ms-4 border-start ps-3">
                    <!-- Replies will be inserted here -->
                    
                    <!-- Reply Form (Hidden) -->
                    <form method="POST" action="/project_creator_comment/"
                        class="reply-form d-none mt-2" id="reply-form-{new_comment.id}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE')}">
                        <input type="hidden" name="project_id" value="{project.id}">
                        <input type="hidden" name="parent_id" value="{new_comment.id}">
                        <div class="input-group input-group-sm">
                            <input type="text" name="comment" class="form-control"
                                placeholder="Write a reply...">
                            <button class="btn btn-secondary" type="submit">Reply</button>
                        </div>
                    </form>
                </div>
            </div>
            """

        return JsonResponse({
            'success': True,
            'comment_html': comment_html,
            'parent_id': parent_id
        })


    return JsonResponse({'success': False}, status=400)



def delete_project_comment(request, comment_id):
    if request.method == "POST":
        uid = request.session.get('cid') or request.session.get('aid')
        if not uid:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
            
        comment = get_object_or_404(ProjectComment, id=comment_id)
        
        # Check permissions
        if comment.added_by.id != int(uid):
             return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
             
        comment.delete()
        return JsonResponse({'success': True})
            
    return JsonResponse({'success': False}, status=400)


def edit_project_comment(request, comment_id):
    if request.method == "POST":
        uid = request.session.get('cid') or request.session.get('aid')
        if not uid:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
            
        comment = get_object_or_404(ProjectComment, id=comment_id)
        
        # Check permissions (must be comment owner)
        if comment.added_by.id != int(uid):
             return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
             
        new_text = request.POST.get('comment', '').strip()
        if not new_text:
             return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

        comment.comment = new_text
        comment.save()
        return JsonResponse({'success': True, 'comment': new_text})
            
    return JsonResponse({'success': False}, status=400)


def delete_project_comment(request, comment_id):
    if request.method == "POST":
        uid = request.session.get('cid') or request.session.get('aid')
        if not uid:
            return JsonResponse({'success': False, 'error': 'Not logged in'}, status=401)
            
        comment = get_object_or_404(ProjectComment, id=comment_id)
        
        # Check permissions (must be comment owner)
        if comment.added_by.id != int(uid):
             return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
             
        comment.delete()
        return JsonResponse({'success': True})
            
    return JsonResponse({'success': False}, status=400)


def view_creator_profile(request, id):
    """Public profile for creators."""
    try:
        creator = Register.objects.get(id=id)
        if creator.role != 'creator' or creator.rights == 'Deactivated':
             return redirect('/findprojects/')
    except Register.DoesNotExist:
        return redirect('/findprojects/')

    # Identify Viewer
    cid = request.session.get('cid')
    aid = request.session.get('aid')
    admin_id = request.session.get('admin')
    viewer_id = cid or aid or admin_id
    viewer = None
    if viewer_id:
        try:
            viewer = Register.objects.get(id=viewer_id)
        except Register.DoesNotExist:
            pass

    # Fetch Public Data
    projects = Project.objects.filter(added_by=creator).order_by('-created_at')
    casting_calls = CastingCall.objects.filter(added_by=creator).order_by('-created_at')
    details = ArtistDetails.objects.filter(added_by=creator).first()

    # Fetch Comments & Likes
    # 1. Likes
    liked_projects = []
    if viewer:
        liked_projects = ProjectLike.objects.filter(liked_by=viewer, project__in=projects).values_list('project_id', flat=True)

    # 2. Comments (Prefetch)
    # Re-using the logic from findprojects to attach comments efficiently
    all_comments_qs = ProjectComment.objects.filter(project__in=projects).exclude(added_by__rights='Deactivated').select_related('added_by').prefetch_related('added_by__artistdetails_set').order_by('created_at')
    
    # We want top-level comments with their replies.
    # Actually, the template usually iterates top-level and then has nested replies.
    # Let's attach top-level comments to each project.
    
    from django.db.models import Prefetch
    projects = projects.prefetch_related(
        Prefetch(
            'projectcomment_set',
            queryset=ProjectComment.objects.filter(parent=None).exclude(added_by__rights='Deactivated').prefetch_related('replies', 'replies__added_by', 'replies__added_by__artistdetails_set').select_related('added_by').order_by('created_at'),
            to_attr='top_level_comments'
        )
    )

    # Pre-formatted HTML for total template robustness
    cre_about = details.about if details and details.about else "Professional creative lead."
    cre_loc = details.location if details else ""
    cre_insta = details.instagram.strip().lstrip('@') if details and details.instagram else ""
    cre_web = details.personalwebsite if details else ""
    cre_email = creator.email

    # HTML Links handled here to avoid formatter splitting tags in template
    cre_email_html = f'<a href="mailto:{cre_email}">{cre_email}</a>'
    cre_insta_html = f'<a href="https://instagram.com/{cre_insta}" target="_blank">@{cre_insta}</a>' if cre_insta else ""
    cre_web_html = f'<a href="{cre_web}" target="_blank">Website</a>' if cre_web else ""

    context = {
        'creator': creator,
        'projects': projects,
        'casting_calls': casting_calls,
        'details': details,
        'cre_about': cre_about,
        'cre_loc': cre_loc,
        'cre_email_html': cre_email_html,
        'cre_insta_html': cre_insta_html,
        'cre_web_html': cre_web_html,
        'liked_projects': list(liked_projects),
        'viewer': viewer, # To check if logged in
        'loguser': viewer, # Consistent naming if needed
    }
    return render(request, 'creators/view_creator_profile.html', context)

@never_cache
def view_artist_profile(request, id):
    cid = request.session.get('cid')
    aid = request.session.get('aid')
    admin_id = request.session.get('admin')
    
    if not cid and not aid and not admin_id:
        return redirect('/login/')
    
    try:
        artist = Register.objects.get(id=id)
        if artist.rights == 'Deactivated':
            if cid:
                return redirect('/findartists/')
            else:
                return redirect('/artprofile/')
    except Register.DoesNotExist:
        if cid:
            return redirect('/findartists/')
        else:
            return redirect('/artprofile/')
    
    details = ArtistDetails.objects.filter(added_by=artist).first()
    
    skills_list = []
    if details and details.skillsinput:
        skills_list = [s.strip() for s in details.skillsinput.split(',') if s.strip()]
    
    # Fetch their posts
    all_posts = Post.objects.filter(added_by=artist).order_by('-created_at')
    posts_with_media = []
    for post in all_posts:
        # Load comments for this post
        comments = ArtistComment.objects.filter(post=post, parent=None).exclude(commented_by__rights='Deactivated').order_by('created_at')
        
        photos = list(post.photopost_set.all())
        videos = list(post.videopost_set.all())
        post.all_media = photos + videos
        posts_with_media.append({'post': post, 'com': comments})
    
    viewer = None
    creator_likes = []
    
    if cid:
        viewer = Register.objects.get(id=cid)
        creator_likes = ArtistLike.objects.filter(liked_by=viewer).values_list("post_id", flat=True)
    elif aid:
        viewer = Register.objects.get(id=aid)
        creator_likes = ArtistLike.objects.filter(liked_by=viewer).values_list("post_id", flat=True)

    context = {
        'artist': artist,
        'details': details,
        'skills_list': skills_list,
        'all_artist_posts': posts_with_media,
        'creator_likes': list(creator_likes),
    }
    
    if cid:
        context['logcreator'] = [viewer]
    elif aid:
        context['logartist'] = viewer

    return render(request, "creators/view_artist_profile.html", context)


# ==========================================
# Chat Functionality Views
# ==========================================

from django.db.models import Q
from django.utils.timezone import now
import json

def get_logged_in_user(request):
    """Helper to get the logged-in Register object based on session."""
    uid = request.session.get('cid') or request.session.get('aid') or request.session.get('admin')
    if uid:
        return Register.objects.filter(id=uid).first()
    return None

@decorator_from_middleware(SessionProtectionMiddleware)
def chat_home(request):
    user = get_logged_in_user(request)
    if not user:
        return redirect('/login/')
    
    return render(request, 'chat.html', {'user': user})

def get_unread_msg_count(user_id):
    """Helper to get total unread messages for a user."""
    return ChatMessage.objects.filter(thread__participants=user_id, is_read=False).exclude(sender=user_id).values('thread').distinct().count()

def get_global_unread_count(request):
    """API to get global unread count for badges."""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'count': 0})
    
    count = get_unread_msg_count(user.id)
    return JsonResponse({'count': count})

def get_user_threads(request):
    """API to get thread list for sidebar polling."""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'threads': []})

    threads = user.chat_threads.all().order_by('-updated_at')
    time_threshold = timezone.now() - timezone.timedelta(minutes=5)
    
    threads_data = []
    for thread in threads:
        other_user = thread.participants.exclude(id=user.id).first()
        if other_user:
            is_online = other_user.last_activity and other_user.last_activity > time_threshold
            # Fetch the last message that is NOT deleted for the current user
            last_msg = thread.messages.filter(is_deleted=False).exclude(
                Q(sender=user, deleted_by_sender=True) |
                ~Q(sender=user) & Q(deleted_by_recipient=True)
            ).order_by('-timestamp').first()
            
            # Count unread messages from the other user, excluding deleted ones
            unread_count = thread.messages.filter(
                sender=other_user, 
                is_read=False,
                is_deleted=False,
                deleted_by_recipient=False
            ).count()
            
            # Check typing status for sidebar
            is_typing = False
            typing_obj = ChatTyping.objects.filter(thread=thread, user=other_user).first()
            if typing_obj and (timezone.now() - typing_obj.timestamp).total_seconds() < 5:
                is_typing = True

            threads_data.append({
                'id': thread.id,
                'other_user_name': f"{other_user.first_name} {other_user.last_name}",
                'other_user_id': other_user.id,
                'other_user_role': other_user.role,
                'is_online': is_online,
                'is_typing': is_typing,
                'unread_count': unread_count,
                'last_message': last_msg.message if last_msg else "No messages yet",
                'last_msg_is_me': (last_msg.sender.id == user.id) if last_msg else False,
                'last_msg_is_read': last_msg.is_read if last_msg else False,
                'timestamp': last_msg.timestamp.isoformat() if last_msg else thread.updated_at.isoformat()
            })
            
    return JsonResponse({'threads': threads_data})

def search_users(request):
    """API to search users by email or name."""
    query = request.GET.get('q', '').strip()
    user = get_logged_in_user(request)
    if not user or not query:
        return JsonResponse({'users': []})

    # Search users excluding self, admins, and deactivated users
    users = Register.objects.filter(
        Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ).exclude(id=user.id).exclude(rights__iexact='Admin').exclude(rights='Deactivated')[:10]

    results = []
    for u in users:
        # Try to find avatar or use UI-avatars
        avatar = ""
        details = ArtistDetails.objects.filter(added_by=u).first()
        if details and details.avatarphoto:
            avatar = details.avatarphoto.url
        else:
            avatar = f"https://ui-avatars.com/api/?name={u.first_name}+{u.last_name}"

        results.append({
            'id': u.id,
            'name': f"{u.first_name} {u.last_name}",
            'email': u.email,
            'role': u.role.capitalize(),
            'avatar': avatar,
            # Link to profile based on role
            'profile_url': f"/view_creator_profile/{u.id}/" if u.role == 'creator' else f"/view_artist_profile/{u.id}/"
        })

    return JsonResponse({'users': results})

def get_chat_thread(request, user_id):
    """API to get or create a thread with a specific user."""
    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    try:
        other_user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Check if a thread already exists with these two
    threads = ChatThread.objects.filter(participants=me).filter(participants=other_user)
    if threads.exists():
        thread = threads.first()
    else:
        thread = ChatThread.objects.create()
        thread.participants.add(me, other_user)
    
    return JsonResponse({'thread_id': thread.id})

def send_message(request):
    """API to send a message."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    try:
        data = json.loads(request.body)
        thread_id = data.get('thread_id')
        text = data.get('message')
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not thread_id or not text:
        return JsonResponse({'error': 'Missing data'}, status=400)

    try:
        thread = ChatThread.objects.get(id=thread_id, participants=me)
    except ChatThread.DoesNotExist:
        return JsonResponse({'error': 'Thread not found'}, status=404)

    msg = ChatMessage.objects.create(thread=thread, sender=me, message=text)
    
    # Update thread timestamp
    thread.updated_at = now()
    thread.save()

    return JsonResponse({
        'status': 'ok', 
        'message': {
            'text': msg.message,
            'sender_id': msg.sender.id,
            'timestamp': msg.timestamp.isoformat(),
            'msg_id': msg.id
        }
    })

    return JsonResponse({'messages': msgs_data})

def get_messages(request, thread_id):
    """API to fetch messages for a thread."""
    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    try:
        thread = ChatThread.objects.get(id=thread_id, participants=me)
    except ChatThread.DoesNotExist:
        return JsonResponse({'error': 'Thread not found'}, status=404)
        
    # Check other user status
    other_user = thread.participants.exclude(id=me.id).first()
    is_online = False
    if other_user and other_user.last_activity:
        threshold = timezone.now() - timezone.timedelta(minutes=5)
        if other_user.last_activity > threshold:
            is_online = True

    first_unread_id = None
    if other_user:
        unread_qs = thread.messages.filter(sender=other_user, is_read=False).order_by('timestamp')
        first_unread = unread_qs.first()
        if first_unread:
            first_unread_id = first_unread.id
        unread_qs.update(is_read=True)

    # Retrieve messages, filtering out those deleted for the current user
    messages_qs = thread.messages.order_by('timestamp')
    
    msgs_data = []
    for m in messages_qs:
        # Skip if deleted for ME specifically (either I sent it and clicked "delete for me", 
        # or I received it and clicked "delete for me")
        if m.sender.id == me.id:
            if m.deleted_by_sender: continue
        else:
            if m.deleted_by_recipient: continue

        msgs_data.append({
            'id': m.id,
            'text': m.message,
            'sender_id': m.sender.id,
            'is_me': m.sender.id == me.id,
            'timestamp': m.timestamp.isoformat(),
            'is_edited': m.is_edited,
            'is_deleted': m.is_deleted, 
            'can_edit': (timezone.now() - m.timestamp).total_seconds() < 900,  # 15 minutes
            'can_delete_for_everyone': (timezone.now() - m.timestamp).total_seconds() < 3600, # 1 hour
            'is_read': m.is_read
        })

    # Check typing status
    is_typing = False
    if other_user:
        typing_obj = ChatTyping.objects.filter(thread=thread, user=other_user).first()
        if typing_obj:
            # Considered typing if updated within last 5 seconds
            if (timezone.now() - typing_obj.timestamp).total_seconds() < 5:
                is_typing = True

    return JsonResponse({'messages': msgs_data, 'is_online': is_online, 'first_unread_id': first_unread_id, 'is_typing': is_typing})

def delete_message(request):
    """API to delete a message - supports 'for_me' and 'for_everyone'"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    try:
        data = json.loads(request.body)
        msg_id = data.get('msg_id')
        delete_type = data.get('delete_type', 'for_me')  # Default to 'for_me' for safety

        # Find the message and ensure the user is part of the thread
        msg = get_object_or_404(ChatMessage, id=msg_id)
        if msg.sender.id != me.id and not msg.thread.participants.filter(id=me.id).exists():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        if delete_type == 'for_me':
            # Soft delete - only hide from the person who clicked it
            if msg.sender.id == me.id:
                msg.deleted_by_sender = True
            else:
                msg.deleted_by_recipient = True
            msg.save()
            return JsonResponse({'status': 'ok', 'type': 'for_me'})

        elif delete_type == 'for_everyone':
            # Hard delete - both users stop seeing it, with 1-hour limit. ONLY for SENDER.
            if msg.sender.id != me.id:
                return JsonResponse({'error': 'Only the sender can delete for everyone.'}, status=403)
                
            age_seconds = (timezone.now() - msg.timestamp).total_seconds()
            if age_seconds > 3600:  # 1 hour
                return JsonResponse({'error': 'Time expired. You can only delete for everyone within 1 hour of sending.'}, status=400)
            
            msg.is_deleted = True
            msg.message = 'This message was deleted.'
            msg.save()
            return JsonResponse({'status': 'ok', 'type': 'for_everyone'})

        return JsonResponse({'error': 'Invalid delete_type'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def edit_message(request):
    """API to edit a message."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
        
    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)
        
    try:
        data = json.loads(request.body)
        msg_id = data.get('msg_id')
        new_text = data.get('text')
        
        msg = ChatMessage.objects.get(id=msg_id, sender=me)
        
        # Check 15 minute limit
        if (timezone.now() - msg.timestamp).total_seconds() > 900:
             return JsonResponse({'error': 'Edit time expired'}, status=400)
             
        msg.message = new_text
        msg.is_edited = True
        msg.save()
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def update_typing_status(request):
    """API to update typing status."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
        
    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)
        
    try:
        data = json.loads(request.body)
        thread_id = data.get('thread_id')
        is_typing = data.get('is_typing', False) 

        if not thread_id:
            return JsonResponse({'error': 'Missing thread_id'}, status=400)

        thread = ChatThread.objects.get(id=thread_id, participants=me)
        
        if is_typing:
            ChatTyping.objects.update_or_create(thread=thread, user=me, defaults={'timestamp': timezone.now()})
        else:
            ChatTyping.objects.filter(thread=thread, user=me).delete()
            
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
def edit_casting_call(request, id):
    cid = request.session.get('cid')
    if not cid:
        return redirect('/login/')
    
    casting = get_object_or_404(CastingCall, id=id, added_by=cid)
    projects = Project.objects.filter(added_by=cid)
    
    if request.method == 'POST':
        role_title = request.POST.get('role_title', '').strip()
        project_id = request.POST.get('associated_project')
        role_category = request.POST.get('role_category', '').strip()
        required_gender = request.POST.get('required_gender', '').strip()
        age_range = request.POST.get('age_range', '').strip()
        compensation = request.POST.get('compensation', '').strip()
        role_description = request.POST.get('role_description', '').strip()
        deadline = request.POST.get('deadline')
        
        if not role_title or not compensation or not role_description:
            messages.error(request, 'Please fill in all required fields.')
            return redirect(f'/creators/casting/{id}/')

        casting.role_title = role_title
        casting.project_title = get_object_or_404(Project, id=project_id)
        casting.role_category = role_category
        casting.required_gender = required_gender
        casting.age_range = age_range
        casting.compensation = compensation
        casting.role_description = role_description
        casting.deadline = deadline
        
        casting.save()
        messages.success(request, 'Casting call updated successfully!')
        return redirect('/my_castingcalls/')
        
    return render(request, 'creators/edit_casting_call.html', {
        'casting': casting,
        'projects': projects
    })

def delete_casting_call(request, id):
    cid = request.session.get('cid')
    if not cid:
        return redirect('/login/')
        
    casting = get_object_or_404(CastingCall, id=id, added_by=cid)
    
    if request.method == 'POST':
        casting.delete()
        messages.success(request, 'Casting call deleted.')
        
        
    return redirect('/my_castingcalls/')


def edit_project(request, id):
    cid = request.session.get('cid')
    if not cid:
        return redirect('/login/')
    
    project = get_object_or_404(Project, id=id, added_by=cid)
    
    if request.method == 'POST':
        project_title = request.POST.get('project_title', '').strip()
        project_type = request.POST.get('project_type', '').strip()
        project_description = request.POST.get('project_description', '').strip()
        genre = request.POST.get('genre', '').strip()
        project_status = request.POST.get('project_status', '').strip()
        
        if not project_title or not genre:
            messages.error(request, 'Project Title and Genre are required.')
            return redirect(f'/creators/projects/{id}/')

        project.project_title = project_title
        project.project_type = project_type
        project.project_description = project_description
        project.genre = genre
        project.project_status = project_status
        
        # File Handling
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        media = request.FILES.get('media')
        
        if media:
            if media.content_type.startswith('image'):
                image = media
            elif media.content_type.startswith('video'):
                video = media

        if image:
            project.image = image
            
        if video:
            project.video = video
            
            # Trimming Data for new video
            import json
            trim_data = request.POST.get('trim_data', '{}')
            try:
                trim_metadata = json.loads(trim_data)
            except:
                trim_metadata = {}
                
            meta = trim_metadata.get(video.name, {})
            project.video_start = meta.get('start', 0.0)
            project.video_end = meta.get('end', None)
        
        project.save()
        messages.success(request, 'Project updated successfully!')
        return redirect('/my_projects/')
        
    return render(request, 'creators/edit_project.html', {'project': project})

def delete_project(request, id):
    cid = request.session.get('cid')
    if not cid:
        return redirect('/login/')
        
    project = get_object_or_404(Project, id=id, added_by=cid)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project and associated casting calls deleted.')
        
    return redirect('/creators/')

@never_cache
def settings_page(request):
    if not request.session.get('cid') and not request.session.get('aid'):
        return redirect('/login/')
    return render(request, 'settings.html', {'hide_sidebar': False})

@csrf_exempt
def deactivate_account(request):
    if request.method == 'POST':
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        user_id = cid if cid else aid
        if not user_id:
            return redirect('/login/')
            
        Register.objects.filter(id=user_id).update(rights='Deactivated')
        for key in ['cid', 'aid', 'admin', 'role']:
            request.session.pop(key, None)
        return redirect('/login/')
    return redirect('/settings/')

@csrf_exempt
def delete_account(request):
    if request.method == 'POST':
        cid = request.session.get('cid')
        aid = request.session.get('aid')
        user_id = cid if cid else aid
        if not user_id:
            return redirect('/login/')
            
        user = Register.objects.get(id=user_id)
        # Generate OTP for deletion
        otp = str(random.randint(100000, 999999))
        request.session['delete_account_otp'] = otp
        request.session['delete_account_user_id'] = user_id
        
        # Send OTP to user's email
        subject = 'Delete Your SceneVerse Account'
        message = f'Your account deletion verification code is: {otp}\nIf you did not request this, please ignore this email.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, f"A verification code has been sent to {user.email}.")
            return redirect('/verify_delete_otp/')
        except Exception as e:
            messages.error(request, "Error sending verification email. Please try again.")
            return redirect('/settings/')
            
    return redirect('/settings/')

@never_cache
def verify_delete_otp(request):
    if 'delete_account_otp' not in request.session:
        messages.error(request, "Session expired or invalid request.")
        return redirect('/settings/')
        
    if request.method == 'POST':
        entered_otp = "".join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])
        
        if entered_otp == request.session.get('delete_account_otp'):
            # Clear the OTP but keep the confirmation flag
            request.session['delete_account_verified'] = True
            return render(request, 'verify_delete_otp.html', {'show_final_modal': True})
        else:
            messages.error(request, "Invalid verification code.")
            
    return render(request, 'verify_delete_otp.html')

@never_cache
def resend_delete_otp(request):
    if 'delete_account_otp' not in request.session:
        messages.error(request, "Session expired. Please try again.")
        return redirect('/settings/')
        
    user_id = request.session.get('delete_account_user_id')
    user = Register.objects.get(id=user_id)
    
    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    request.session['delete_account_otp'] = otp
    
    # Send OTP
    subject = 'Your New Deletion Code - SceneVerse'
    message = f'Your new verification code for account deletion is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, f"A new verification code has been sent to {user.email}.")
        return redirect('/verify_delete_otp/')
    except Exception as e:
        messages.error(request, "Error sending email. Please try again.")
        return redirect('/verify_delete_otp/')

@never_cache
def confirm_delete(request):
    if request.method == 'POST' and request.session.get('delete_account_verified'):
        user_id = request.session.get('delete_account_user_id')
        if not user_id:
            return redirect('/login/')
            
        Register.objects.filter(id=user_id).delete()
        for key in ['cid', 'aid', 'admin', 'role', 'delete_account_otp', 'delete_account_user_id', 'delete_account_verified']:
            request.session.pop(key, None)
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('/login/')
        
    messages.error(request, "Invalid request.")
    return redirect('/settings/')

@never_cache
def user_contact(request):
    cid = request.session.get('cid')
    aid = request.session.get('aid')
    user_id = cid if cid else aid
    if not user_id:
        return redirect('/login/')
        
    # Fetch the first Admin user to show their contact info
    admin = Register.objects.filter(rights='Admin').first()
            
    return render(request, 'user_contact.html', {'admin': admin})


@never_cache
def verify_profile_otp(request):
    if 'profile_otp' not in request.session:
        messages.error(request, "Session expired or invalid request.")
        return redirect('/settings/')
        
    if request.method == 'POST':
        entered_otp = "".join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])
        
        if entered_otp == request.session.get('profile_otp'):
            data = request.session.get('pending_profile_data')
            p_type = request.session.get('pending_profile_type')
            
            uid = request.session.get('cid') if p_type == 'creator' else request.session.get('aid')
            user = Register.objects.get(id=uid)
            
            # Update Register Info
            Register.objects.filter(id=uid).update(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
            
            # Update Details
            if p_type == 'artist':
                ArtistDetails.objects.filter(added_by=user).update(
                    title=data['title'],
                    location=data['location'],
                    skillsinput=data['skillsinput'],
                    about=data['about'],
                    gender=data['gender'],
                    phone=data['phone'],
                    personalwebsite=data['personalwebsite'],
                    instagram=data['instagram']
                )
            else: # creator
                ArtistDetails.objects.filter(added_by=user).update(
                    location=data['location'],
                    about=data['about'],
                    phone=data['phone'],
                    personalwebsite=data['personalwebsite'],
                    instagram=data['instagram']
                )
            
            # Cleanup session
            del request.session['profile_otp']
            del request.session['pending_profile_data']
            del request.session['pending_profile_type']
            
            messages.success(request, "Profile updated successfully!")
            return redirect('/creator_profile/' if p_type == 'creator' else '/artprofile/')
        else:
            messages.error(request, "Invalid verification code.")
            
    p_type = request.session.get('pending_profile_type')
    return render(request, 'verify_profile_otp.html', {'p_type': p_type})

@never_cache
def resend_profile_otp(request):
    if 'profile_otp' not in request.session or 'pending_profile_type' not in request.session:
        messages.error(request, "Session expired. Please update your profile again.")
        return redirect('/settings/')
    
    p_type = request.session.get('pending_profile_type')
    uid = request.session.get('cid') if p_type == 'creator' else request.session.get('aid')
    user = Register.objects.get(id=uid)
    
    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    request.session['profile_otp'] = otp
    
    # Send OTP to CURRENT email
    subject = 'Your New Verification Code - SceneVerse'
    message = f'Your new verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, f"A new verification code has been sent to {user.email}.")
    except Exception as e:
        messages.error(request, f"Error sending verification email: {e}")
        
    return redirect('/verify_profile_otp/')


def clear_chat(request):
    """API to clear chat for the current user."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    me = get_logged_in_user(request)
    if not me:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    try:
        data = json.loads(request.body)
        thread_id = data.get('thread_id')
        
        thread = get_object_or_404(ChatThread, id=thread_id, participants=me)
        messages = thread.messages.all()

        for msg in messages:
            if msg.sender.id == me.id:
                msg.deleted_by_sender = True
            else:
                msg.deleted_by_recipient = True
            msg.save()

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def delete_artist_post(request, post_id):
    """API to delete an artist post."""
    aid = request.session.get('aid')
    if not aid:
        return redirect('/login/')
        
    post = get_object_or_404(Post, id=post_id, added_by=aid)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        
    return redirect('/artprofile/')


def edit_artist_post(request, post_id):
    """View to edit an artist post caption."""
    aid = request.session.get('aid')
    if not aid:
        return redirect('/login/')
        
    post = get_object_or_404(Post, id=post_id, added_by=aid)
    crt = Register.objects.get(id=aid)

    if request.method == 'POST':
        caption = request.POST.get('caption')
        post.caption = caption
        post.save()
        messages.success(request, 'Post updated successfully.')
        return redirect('/artprofile/')

    return render(request, 'artists/edit_artist_post.html', {'post': post, 'crt': crt})


def change_password(request):
    """View to change user password after verifying old password."""
    cid = request.session.get('cid')
    aid = request.session.get('aid')
    user_id = cid if cid else aid
    
    if not user_id:
        return redirect('/login/')
        
    if request.method == 'POST':
        old_p = request.POST.get('old_password')
        new_p = request.POST.get('new_password', '').strip()
        conf_p = request.POST.get('confirm_password', '').strip()
        
        # Validation pattern (8-16 chars, mix of A-z, 0-9 & symbols)
        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-]).{8,16}$"
        
        user = Register.objects.get(id=user_id)
        
        if not new_p:
            messages.error(request, "New password cannot be blank.")
        elif not re.match(password_regex, new_p):
            messages.error(request, "New password must be 8-16 characters and include uppercase, lowercase, numbers, and special characters.")
        elif new_p != conf_p:
            messages.error(request, "New passwords do not match.")
        elif user.password != old_p:
            messages.error(request, "Incorrect old password.")
        else:
            user.password = new_p
            user.save()
            messages.success(request, "Password updated successfully!")
            
    return redirect('/settings/')

