from django.template.defaulttags import register

# register custom filters here...

@register.filter
def sample_filter(value):
    return '[' + str(value) + ']'
