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

    # instance_id = request.GET.get('instance_id','')
    # github_repo = request.GET.get('github_repo','')
    # user_email = request.GET.get('user_email','')
    instance_id = "f352ef29-9321-4588-85ba-e35ca23db41f"
    github_repo = "100-point-discovery-backend"
    user_email = "zcabmdo%40ucl.ac.uk"
    r = requests.get(CM_BASE_URL.format('code-score/gpa/', '?github_repo=%s&instance_id=%s&user_email=%s'
                                        % github_repo, instance_id, user_email))
    gpa = r.json()

    return HttpResponse(template.render(Context(
        {
            'gpa': gpa
        }
    )))

