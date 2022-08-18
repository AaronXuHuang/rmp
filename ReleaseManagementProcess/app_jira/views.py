from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
import requests

from .models import JiraProject, JiraReleaseObject

# Create your views here.
jira_user = 'svc_mcp'
jira_pwd = 'Wa7rUxeD'
jira_server = 'https://pd.nextestate.com'


def test(request):
    result = UpdateJiraProject()
    return JsonResponse(result)


def UpdateJiraProject(request):
    # https://pd.nextestate.com/rest/api/2/project
    bulk_data = []
    projects = {'projects': []}
    url = jira_server + "/rest/api/2/project/"

    #ids_in_db = list(JiraProject.objects.values_list('id', flat=True))
    JiraProject.objects.all().delete()
    items = requests.get( url=url, auth=(jira_user, jira_pwd), verify=False).json()
    for item in items:
        project = {
            'id': item['id'],
            'key': item['key'],
            'name': item['name']
        }
        projects['projects'].append(project)

    for project in projects['projects']:
        bulk_data.append(JiraProject(id=project['id'], name=project['name'], key=project['key']))
    JiraProject.objects.bulk_create(bulk_data)

    return JsonResponse(projects)


def FetchIssue(request, orgunit, milestone):
    
    return HttpResponse()