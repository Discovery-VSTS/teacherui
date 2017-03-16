from django.http import HttpResponse
from django.template.loader import get_template


def login(request):
    template = get_template('login/login.html')
    return HttpResponse(template.render())


def index(request):
    html = get_template('base.html')
    return HttpResponse(html.render())


def tab_100_points(request):
    template = get_template('tabs/tab_100_points.html')
    return HttpResponse(template.render())


def tab_codemetrics(request):
    template = get_template('tabs/tab_codemetrics.html')
    return HttpResponse(template.render())

