from django.http import HttpResponse
from django.template.loader import get_template


def index(request):
    html = get_template('base.html')
    return HttpResponse(html.render())


def tab_100_points(request):
    template = get_template('tabs/tab_100_points.html')
    return HttpResponse(template.render())


def tab_effort_analysis(request):
    template = get_template('tabs/tab_effort_analysis.html')
    return HttpResponse(template.render())


def tab_team_projects(request):
    template = get_template('tabs/tab_team_projects.html')
    return HttpResponse(template.render())
