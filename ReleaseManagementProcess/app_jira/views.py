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

    projects = GetJiraProject()
    PurgeTable(JiraProject)
    SaveProjects(projects)

    return JsonResponse(projects)


def GetJiraProject():
    # https://pd.nextestate.com/rest/api/2/project

    projects = {
        'projects': []
        }
    url = jira_server + "/rest/api/2/project/"

    items = requests.get(url=url, auth=(jira_user, jira_pwd), verify=False).json()
    for item in items:
        project = {
            'id': item['id'],
            'key': item['key'],
            'name': item['name']
        }
        projects['projects'].append(project)

    return projects


def PurgeTable(model):
    model.objects.all().delete()


def SaveProjects(projects):
    bulk_data = []

    for project in projects['projects']:
        bulk_data.append(JiraProject(id=project['id'], name=project['name'], key=project['key']))
    JiraProject.objects.bulk_create(bulk_data)


def GetJiraFixVersion(request):
    # https://pd.nextestate.com/rest/api/2/project/12500/version?maxResults=1048576

    fix_versions = {
        'fixversions': []
    }
    project = request.GET.get('project')
    projectid = JiraProject.objects.get(key=project).id
    url = jira_server + "/rest/api/2/project/" + str(projectid) + '/version?maxResults=1048576'

    items = requests.get(url=url, auth=(jira_user, jira_pwd), verify=False).json()
    for item in items['values']:
        if 'description' in item:
            fix_versions['fixversions'].append({
                'name': item['name'],
                'description': item['description']
                })
        else:
            fix_versions['fixversions'].append({
                'name': item['name'],
                'description': ""
                })

    return JsonResponse(fix_versions)

def FetchIssue(request, orgunit, milestone):
    
    return HttpResponse()