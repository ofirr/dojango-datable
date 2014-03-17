
def getFullPath(request):
    """Get full URL path from the request
    """
    # When testing, there is no request.META['HTTP_HOST'] in Django test client
    host = request.META.get('HTTP_HOST', 'none')
    full_path = ('http', ('', 's')[request.is_secure()], \
                 '://', host, request.path)
    return ''.join(full_path)
