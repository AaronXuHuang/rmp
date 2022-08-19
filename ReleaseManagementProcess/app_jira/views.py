from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from app_jira.models import JiraProject, JiraReleaseObject
import json
import requests

# Create your views here.
JIRA_USER = 'svc_mcp'
JIRA_PWD = 'Wa7rUxeD'
JIRA_SERVER = 'https://pd.nextestate.com'


def test(request):
    result = UpdateJiraProject()
    return JsonResponse(result)


def FetchJiraProject():
    # https://pd.nextestate.com/rest/api/2/project

    projects = {
        'projects': []
        }
    url = JIRA_SERVER + "/rest/api/2/project/"

    items = requests.get(url=url, auth=(JIRA_USER, JIRA_PWD), verify=False).json()
    for item in items:
        project = {
            'id': item['id'],
            'key': item['key'],
            'name': item['name']
        }
        projects['projects'].append(project)

    projects['projects'].sort(key=ProjectKey)
    return projects


def FetchJiraFixVersion(request):
    # https://pd.nextestate.com/rest/api/2/project/12500/version?maxResults=1048576

    project = request.GET.get('project')

    fix_versions = {
        'fix_versions': []
    }
    projectid = JiraProject.objects.get(key=project).id
    url = JIRA_SERVER + "/rest/api/2/project/" + str(projectid) + '/version?maxResults=1048576'

    items = requests.get(url=url, auth=(JIRA_USER, JIRA_PWD), verify=False).json()
    for item in items['values']:
        if 'description' in item:
            fix_versions['fix_versions'].append({
                'name': item['name'],
                'description': item['description']
                })
        else:
            fix_versions['fix_versions'].append({
                'name': item['name'],
                'description': ""
                })

    return JsonResponse(fix_versions)


def FetchJiraIssue(request):
    # https://pd.nextestate.com/rest/api/2/search?jql=fixVersion=M113.22.08.11%20and%20project=BUX&maxResults=2500&fields=key,customfield_12429,issuetype

    project = "project=" + request.GET.get('project')
    fix_version = "fixVersion=" + request.GET.get('fix_version')

    issues = {'issues': []}
    search = "search?jql="
    connector = "%20and%20"
    _and_ = "&"
    max_result = "maxResults=2500"
    fileds = "fields=key,customfield_12429,issuetype"
    jql_string = search + fix_version + connector + project + _and_ + max_result + _and_ + fileds
    url = JIRA_SERVER + "/rest/api/2/" + jql_string
    
    items = requests.get(url=url, auth=(JIRA_USER, JIRA_PWD), verify=False).json()
    for item in items['issues']:
        issue_key = item['key']
        issue_type = item['fields']['issuetype']['name']
        custom_field = item['fields']['customfield_12429']
        if issue_type != 'Release' and custom_field:
            components_ver_map = json.loads(custom_field)
            components = []
            for component in components_ver_map['componentVersionMap']:
                components.append(component)
            issues['issues'].append({
                'issue': issue_key,
                'issuetype': issue_type,
                'components': components})
    
    return JsonResponse(issues)


def UpdateJiraProject(request):

    projects = FetchJiraProject()
    JiraProject.objects.all().delete()
    SaveProject(projects)

    return JsonResponse(projects)


def ProjectKey(project):
      return project['key']


def SaveProject(projects):
    bulk_data = []

    for project in projects['projects']:
        bulk_data.append(JiraProject(id=project['id'], name=project['name'], key=project['key']))
    JiraProject.objects.bulk_create(bulk_data)