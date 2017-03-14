from django.http import HttpResponse
from django.template.loader import get_template


def index(request):
    html = get_template('base.html')
    return HttpResponse(html.render())
