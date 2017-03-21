from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import UserForm

import requests
import json
import logging


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


def convert_to_line_graph_data_structure(distribution_json, member_dict_ids):
    print("Convert line graph")
    print(distribution_json)
    dates = []
    # Store member with its distribution
    member = dict()
    for data in distribution_json:
        week = data['week']
        print("Week:", week)

        points = data['given_points']
        print("Points", points)

        dates.append(week)
        for point_dist in points:
            to_member = point_dist['to_member']
            print("To_member:", to_member)
            point = point_dist['points']
            print("point:", point)
            name = member_dict_ids[to_member]

            try:
                if name in member.keys():
                    member[name].append(point)
                else:
                    member[name] = [point]

            except KeyError as e:
                logging.warn(e)

            except Exception as e:
                logging.error(e)

    return dates, member


def resolve_member_ids(member_ids, instance_id):
    try:
        decoding_dict = dict()
        members = member_ids[instance_id]['members']

        print("Member details", members)

        for member in members:
            ins_id = member['identifier']
            name = member['name']
            decoding_dict[ins_id] = name

        return decoding_dict
    except KeyError as e:
        logging.error(e)
        return {}

    except Exception as e:
        logging.error(e)


@login_required
def tab_100_points(request):
    template = get_template('tabs/tab_100_points.html')
    BASE_URL = 'https://discovery-100p.azurewebsites.net/{}{}'

    r = requests.get(BASE_URL.format('v1/teams/all/', ''))
    instance_list = r.json()

    print("instance_list", instance_list)

    TEAM = request.GET.get('team', '')
    r = requests.get(BASE_URL.format('v1/team/points/', '?instance_id=%s' % TEAM))
    total_points_team = r.json()

    member_decoding_dict = resolve_member_ids(instance_list, TEAM)

    print("Decoding dict", member_decoding_dict)

    # Get history of point distribution
    params = {'instance_id': TEAM}
    point_distribution_r = requests.get(BASE_URL.format('v1/points/distribution/history', ''), params=params)
    point_distribution_data = point_distribution_r.json()

    dates, members = convert_to_line_graph_data_structure(point_distribution_data, member_decoding_dict)

    # Add in elements for point distribution

    piechart_labels = []
    piechart_datasets = []

    for name, point in total_points_team.items():
        piechart_labels.append(name.strip())
        piechart_datasets.append(point)

    print(piechart_datasets)
    print(piechart_labels)

    return HttpResponse(template.render(Context(
        {
            'dates': json.dumps({'dates': dates}),
            'line_chart_data': json.dumps({'line_chart_data': members}),
            'members': piechart_labels,
            'labels': json.dumps({"labels": piechart_labels}),
            'datasets': json.dumps({"datasets": piechart_datasets}),
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
    MEMBER_NAME = request.GET.get('member_name', '')
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

    r = requests.get(BASE_URL_CODEMETRICS.format('repo-stats/commit-stats/',
                                                 '?instance_name=%s&repo_name=%s' % (TEAM_NAME, REPO_NAME)))

    if r.status_code == 200:
        commit_stats = r.json()
    else:
        commit_stats = {}

    r = requests.get(BASE_URL_CODEMETRICS.format('code-score/test_coverage/',
                                                 '?instance_id=%s&github_repo=%s&user_email=%s'
                                                 % (TEAM_ID, REPO_NAME, MEMBER_EMAIL)))

    if r.status_code == 200:
        test_coverage = r.json()
    else:
        test_coverage = {}

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
            'member_name': MEMBER_NAME,
            'member_email': MEMBER_EMAIL,
            'gpa_object': gpa,
            'commit_stats': json.dumps(commit_stats),
            'test_coverage': json.dumps(test_coverage),
        }
    )))

