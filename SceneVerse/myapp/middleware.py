from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Register

class SessionProtectionMiddleware:
    """
    Protect pages from unauthorized access.
    Only allow access if user is logged in.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pages to protect
        protected_paths = [
            '/creators/',
            '/artists/',
            '/artprofile',
            '/my_projects/',
            '/castingcalls/',
            '/my_castingcalls/',
            '/myapplications/',
            '/view_my_posts/',
            '/applications/',
            '/findprojects/',
            '/admindashboard/',
            '/admin_users/',
            '/manageprojects/',
            '/project/',
            '/blockproject/',
            '/unblockproject/',
            '/casting/',
            '/manageapplication/',
            '/editavatar/',
            '/projectlike/',
            '/projectcomment/',
        ]

        creator_pages = ['/applications/', '/creators/', '/my_castingcalls/',
                         '/my_projects/', '/manageprojects/','/blockproject/',
                         '/unblockproject/', '/admindashboard/', '/casting/', '/my_projects/',
                         '/manageapplication/', '/project/', '/admin_users/']
        if any(request.path.startswith(path) for path in creator_pages):
            if request.session.get('aid'):
                return redirect('/artists/')

        artist_pages = ['/artists/', '/artprofile/', '/findprojects/', '/manageprojects/','/blockproject/',
                         '/unblockproject/', '/admindashboard/', '/artprofile/', '/editavatar/', '/castingcalls/',
                        '/myapplications/', '/findprojects/',
                        '/view_my_posts/', '/admin_users/']
        if any(request.path.startswith(path) for path in artist_pages):
            if request.session.get('cid'):
                return redirect('/creators/')

        if any(request.path.startswith(path) for path in protected_paths):
            if not (request.session.get('cid') or
                    request.session.get('aid') or
                    request.session.get('admin')):
                return redirect('/login/')

        auth_pages = ['/login/', '/register/']
        if any(request.path.startswith(path) for path in auth_pages):
            if request.session.get('cid'):
                return redirect('/creators/')
            if request.session.get('aid'):
                return redirect('/artists/')
            if request.session.get('admin'):
                return redirect('/admindashboard/')

        response = self.get_response(request)
        return response

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check sessions for logged in user
        uid = request.session.get('cid') or request.session.get('aid') or request.session.get('admin')
        
        if uid:
            # Update last activity
            # We use filter().update() to avoid overhead of get() + save() and signals
            Register.objects.filter(id=uid).update(last_activity=timezone.now())
            
        return response