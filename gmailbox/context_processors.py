from .views import _load_creds_from_session

def oauth_authenticated(request):
    creds = _load_creds_from_session(request)
    return {'is_oauth_authenticated': creds is not None}