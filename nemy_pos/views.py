from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token

@requires_csrf_token
def custom_404(request, exception=None):
    """
    Custom 404 error handler
    
    Args:
        request: The HTTP request object
        exception: The exception that triggered this handler
        
    Returns:
        Rendered 404 error page
    """
    return render(request, 'errors/404.html', status=404)

@requires_csrf_token
def custom_500(request):
    """
    Custom 500 error handler
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered 500 error page
    """
    return render(request, 'errors/500.html', status=500)

@requires_csrf_token
def custom_403(request, exception=None):
    """
    Custom 403 error handler
    
    Args:
        request: The HTTP request object
        exception: The exception that triggered this handler
        
    Returns:
        Rendered 403 error page
    """
    return render(request, 'errors/403.html', status=403) 