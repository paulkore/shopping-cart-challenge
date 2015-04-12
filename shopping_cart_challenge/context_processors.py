# This is a template for a default request processor to be applied to all request

def default_processor(request):

    default_context = {
        'ignore_this_property': 'abc'
    }

    return default_context