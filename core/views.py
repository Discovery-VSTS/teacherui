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
import time


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
            print("team list", team_list)
            
    r = requests.get(CM_BASE_URL.format('code-score/gpa/', '?github_repo=%s&instance_id=%s&user_email=%s'
                                        % (REPO_NAME, TEAM_ID, MEMBER_EMAIL)))

    if r.status_code == 200:
        gpa = r.json()
    else:
        gpa = {}

    r = requests.get(BASE_URL_CODEMETRICS.format('repo-stats/commit-stats/',
                                                 '?instance_name=%s&repo_name=%s' % (TEAM_NAME, REPO_NAME)))

    # Add all members into the list

    line_chart_data_add = dict()
    line_chart_data_delete = dict()
    line_chart_data_edit = dict()

    for member in team_list:
        line_chart_data_delete[member['name']] = []
        line_chart_data_edit[member['name']] = []
        line_chart_data_add[member['name']] = []

    if r.status_code == 200:
        commit_stats = r.json()
        print("Commit stats", commit_stats)

        sorted_time = []
        for epoch in commit_stats.keys():
            sorted_time.append(int(epoch))

        sorted_time = sorted(sorted_time)

        date_sorted_time = []

        i = 0
        for epoch in sorted_time:
            date_sorted_time.append(time.strftime('%Y-%m-%d', time.localtime(epoch)))
            commit_data = commit_stats[str(epoch)]
            print("Commit data", commit_data)
            for commit in commit_data:
                data = commit['commit']
                author = data['author']
                name = author['name']
                email = author['email']
                changes = data['changes']
                add = changes['add']
                delete = changes['delete']
                edit = changes['edit']

                # Map to the same user
                if email == 'zcabrga@ucl.ac.uk' or email == 'gascons1995@gmail.com':
                    if 'Ricard Gascons Gascon' in line_chart_data_add:
                        if len(line_chart_data_add['Ricard Gascons Gascon']) == 0:
                            line_chart_data_add['Ricard Gascons Gascon'] = [add]
                        else:
                            line_chart_data_add['Ricard Gascons Gascon'][len(line_chart_data_add['Ricard Gascons Gascon'])-1] += add
                    else:
                        line_chart_data_add['Ricard Gascons Gascon'] = [add]

                    if 'Ricard Gascons Gascon' in line_chart_data_delete:
                        if len(line_chart_data_delete['Ricard Gascons Gascon']) == 0:
                            line_chart_data_delete['Ricard Gascons Gascon'] = [delete]
                        else:
                            line_chart_data_delete['Ricard Gascons Gascon'][len(line_chart_data_delete['Ricard Gascons Gascon'])-1] += delete
                    else:
                        line_chart_data_delete['Ricard Gascons Gascon'] = [delete]

                    if 'Ricard Gascons Gascon' in line_chart_data_edit:
                        if len(line_chart_data_edit['Ricard Gascons Gascon']) == 0:
                            line_chart_data_edit['Ricard Gascons Gascon'] = [edit]
                        else:
                            line_chart_data_edit['Ricard Gascons Gascon'][len(line_chart_data_edit['Ricard Gascons Gascon'])-1] += edit
                    else:
                        line_chart_data_edit['Ricard Gascons Gascon'] = [edit]
                else:
                    print("name={}".format(name))
                    if name in line_chart_data_add:
                        if len(line_chart_data_add[name]) == 0:
                            line_chart_data_add[name] = [add]
                        else:
                            line_chart_data_add[name][len(line_chart_data_add[name])-1] += add
                    else:
                        line_chart_data_add[name] = [add]

                    if name in line_chart_data_delete:
                        if len(line_chart_data_delete[name]) == 0:
                            line_chart_data_delete[name] = [delete]
                        else:
                            line_chart_data_delete[name][len(line_chart_data_delete[name])-1] += delete
                    else:
                        line_chart_data_delete[name] = [delete]

                    if name in line_chart_data_edit:
                        if len(line_chart_data_edit[name]) == 0:
                            line_chart_data_edit[name] = [edit]
                        else:
                            line_chart_data_edit[name][len(line_chart_data_edit[name])-1] += edit
                    else:
                        line_chart_data_edit[name] = [edit]
            i += 1
            # Go through to see if everyone has the same length
            members = line_chart_data_delete.keys()
            for member in members:
                if len(line_chart_data_delete[member]) < i:
                    line_chart_data_delete[member].append(0)
                if len(line_chart_data_add[member]) < i:
                    line_chart_data_add[member].append(0)
                if len(line_chart_data_edit[member]) < i:
                    line_chart_data_edit[member].append(0)

            print("i={}".format(i))
            print("DELETE ", line_chart_data_delete)
            print("ADD ", line_chart_data_add)
            print("EDIT ", line_chart_data_edit)
            print("\n")

    else:
        commit_stats = {}

    return HttpResponse(template.render(Context(
        {
            'add_data': json.dumps(line_chart_data_add),
            'delete_data': json.dumps(line_chart_data_delete),
            'edit_data': json.dumps(line_chart_data_edit),
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
        }
    )))

