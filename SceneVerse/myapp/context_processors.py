from myapp.models import Register, ArtistDetails

def sidebar_user_info(request):
    user_info = {
        'sidebar_name': 'My Account',
        'sidebar_avatar': None,
        'sidebar_role': None
    }
    
    # Try custom session login first (cid, aid, or admin custom roles)
    user_id = request.session.get('cid') or request.session.get('aid') or request.session.get('admin')
    if user_id:
        try:
            reg = Register.objects.get(id=user_id)
            user_info['sidebar_name'] = f"{reg.first_name} {reg.last_name}"
            user_info['sidebar_role'] = reg.role
            
            # Retrieve profile image from ArtistDetails (shared across creators/artists)
            details = ArtistDetails.objects.filter(added_by=reg).first()
            if details and details.avatarphoto:
                user_info['sidebar_avatar'] = details.avatarphoto.url
        except Register.DoesNotExist:
            pass
            
    # Fallback to Django Authentication user (like Django admin login without custom session)
    elif getattr(request, 'user', None) and request.user.is_authenticated:
        user_info['sidebar_name'] = request.user.get_full_name() or request.user.username
        if hasattr(request.user, 'profile_image') and request.user.profile_image:
            user_info['sidebar_avatar'] = request.user.profile_image.url
            
    return user_info
