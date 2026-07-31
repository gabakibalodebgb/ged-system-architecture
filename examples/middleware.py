"""
Middleware pour capturer la requête courante (nécessaire pour les signals)
"""
from threading import local

_thread_locals = local()


def get_current_request():
    """Récupère la requête HTTP courante"""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Récupère l'utilisateur courant"""
    request = get_current_request()
    if request and hasattr(request, 'user'):
        return request.user
    return None


def get_client_ip():
    """Récupère l'IP du client"""
    request = get_current_request()
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    return None


class CurrentRequestMiddleware:
    """Middleware pour stocker la requête dans un thread local"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        
        # Nettoyer après la requête
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        
        return response