from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import UserForm
import requests


def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['reg_username']
            pwd = form.cleaned_data['reg_password']
            if pwd != form.cleaned_data['reg_password_confirm']:
                return render(request, 'registration/info_msg.html',
                              {'message': 'The passwords don\'t match', 'title': 'Error'})
            email = form.cleaned_data['reg_email']
            user = User.objects.create_user(username, email, pwd)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            return render(request, 'registration/info_msg.html',
                          {'message': 'You\'ve registered correctly', 'title': 'Success', 'success': True})
    else:
        form = UserForm()
        return render(request, 'registration/register.html', {'form': form})


@login_required
def tab_100_points(request):
    template = get_template('tabs/tab_100_points.html')
    BASE_URL = 'http://discovery-100p.azurewebsites.net/{}{}'

    r = requests.get(BASE_URL.format('v1/teams/all/', ''))
    instance_list = r.json()

    TEAM = request.GET.get('team', '')
    r = requests.get(BASE_URL.format('v1/team/points/', '?instance_id=%s' % TEAM))
    total_points_team = r.json()
    return HttpResponse(template.render(Context(
        {
            'total_points_team': total_points_team,
            'instance_list': instance_list,
            'team_id': TEAM,
        }
    )))


@login_required
def tab_codemetrics(request):
    template = get_template('tabs/tab_codemetrics.html')

    CM_BASE_URL = 'https://discovery-codemetrics.azurewebsites.net/{}{}'
    BASE_URL_100P = 'http://discovery-100p.azurewebsites.net/{}{}'
    BASE_URL_CODEMETRICS = 'http://discovery-codemetrics.azurewebsites.net/{}{}'

    r = requests.get(BASE_URL_100P.format('v1/teams/all/', ''))
    instance_list = r.json()

    TEAM_ID = request.GET.get('team_id', '')
    REPO_ID = request.GET.get('repo_id', '')
    MEMBER_ID = request.GET.get('member_id', '')
    MEMBER_EMAIL = request.GET.get('member_email', '')
    TEAM_NAME = request.GET.get('team_name', '')
    REPO_NAME = request.GET.get('repo_name', '')

    r = requests.get(BASE_URL_CODEMETRICS.format('repo-stats/repos/',
                                                 '?instance_name=%s&instance_id=%s' % (TEAM_NAME, TEAM_ID)))
    if r.status_code == 200:
        repo_list = r.json()['repos']
    else:
        repo_list = []

    r = requests.get(BASE_URL_100P.format('v1/teams/all/', ''))
    teams = r.json()
    team_list = []
    for team_id, team in teams.items():
        if team_id == TEAM_ID:
            team_list = team['members']
            
    r = requests.get(CM_BASE_URL.format('code-score/gpa/', '?github_repo=%s&instance_id=%s&user_email=%s'
                                        % (REPO_NAME, TEAM_ID, MEMBER_EMAIL)))

    if r.status_code == 200:
        gpa = r.json()
    else:
        gpa = {}

    return HttpResponse(template.render(Context(
        {
            'instance_list': instance_list,
            'repo_list': repo_list,
            'team_list': team_list,
            'team_id': TEAM_ID,
            'team_name': TEAM_NAME,
            'repo_id': REPO_ID,
            'repo_name': REPO_NAME,
            'member_id': MEMBER_ID,
            'member_email': MEMBER_EMAIL,
            'gpa_object': gpa,
        }
    )))

