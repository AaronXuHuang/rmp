from platform import release
from unicodedata import name
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from app_jira.models import JiraFixVersion, JiraProject
import json
import requests

# Create your views here.
JIRA_USER = 'svc_mcp'
JIRA_PWD = 'Wa7rUxeD'
JIRA_SERVER = 'https://pd.nextestate.com'


def test(request):
    project = request.GET.get('project')
    fix_version = request.GET.get('fix_version')

    issues = FetchJiraIssues(project, fix_version)
    # not database operation
    return JsonResponse(issues)


def SyncJiraProjects(request):
    projects = FetchJiraProjects()
    JiraProject.objects.all().delete()
    SaveJiraProjects(projects)

    return JsonResponse(projects)


def SyncJiraFixVersions(request):
    project = request.GET.get('project')

    fix_versions = FetchJiraFixVersions(project)
    JiraFixVersion.objects.filter(project=project).delete()
    SaveJiraFixVersion(fix_versions)

    return JsonResponse(fix_versions)


def GetJiraIssues(request):
    project = request.GET.get('project')
    fix_version = request.GET.get('fixversion')

    issues = FetchJiraIssues(project, fix_version)
    # not database operation
    return JsonResponse(issues)


def GetJiraFixVersions(request):
    project = request.GET.get('project')
    released = request.GET.get('released')

    SyncJiraFixVersions(request)
    
    print(released)
    if released == 'false':
        fix_versions = ReadJiraFixVersions(project, released)
    else:
        fix_versions = ReadJiraFixVersions(project, 'all')

    return JsonResponse(fix_versions)


def FetchJiraProjects():
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


def FetchJiraFixVersions(project):
    # https://pd.nextestate.com/rest/api/2/project/12500/version?maxResults=1048576

    fix_versions = {
        'fix_versions': []
    }
    project_id = JiraProject.objects.get(key=project).id
    url = JIRA_SERVER + "/rest/api/2/project/" + str(project_id) + '/version?maxResults=1048576'

    items = requests.get(url=url, auth=(JIRA_USER, JIRA_PWD), verify=False).json()
    for item in items['values']:
        if 'description' in item:
            fix_versions['fix_versions'].append({
                'id': item['id'],
                'name': item['name'],
                'description': item['description'],
                'released': item['released'],
                'projectid': project_id,
                'project': project
                })
        else:
            fix_versions['fix_versions'].append({
                'id': item['id'],
                'name': item['name'],
                'description': "N/A",
                'released': item['released'],
                'projectid': project_id,
                'project': project
                })

    return fix_versions


def FetchJiraIssues(project, fix_version):
    # https://pd.nextestate.com/rest/api/2/search?jql=fixVersion=M113.22.08.11%20and%20project=BUX&maxResults=2500&fields=key,customfield_12429,issuetype

    issues = {'issues': []}
    search = "search?jql="
    fix_version = "fixVersion=" + fix_version
    connector = "%20and%20"
    project = "project=" + project
    _and_ = "&"
    max_result = "maxResults=2500"
    fileds = "fields=key,customfield_12429,issuetype"
    jql_string = search + fix_version + connector + project + _and_ + max_result + _and_ + fileds
    url = JIRA_SERVER + "/rest/api/2/" + jql_string
    
    items = requests.get(url=url, auth=(JIRA_USER, JIRA_PWD), verify=False).json()
    for item in items['issues']:
        issue_key = item['key']
        issue_type = item['fields']['issuetype']['name']
        if issue_type == 'Server Config':
            continue
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
    
    return issues


def ProjectKey(project):
      return project['key']


def SaveJiraProjects(projects):
    bulk_data = []

    for project in projects['projects']:
        bulk_data.append(JiraProject(id=project['id'], name=project['name'], key=project['key']))
    JiraProject.objects.bulk_create(bulk_data)


def SaveJiraFixVersion(fix_versions):
    bulk_data = []

    for fix_version in fix_versions['fix_versions']:
        bulk_data.append(JiraFixVersion(
            id = fix_version['id'],
            name = fix_version['name'],
            description = fix_version['description'],
            released = fix_version['released'],
            projectid = fix_version['projectid'],
            project = fix_version['project']))
    JiraFixVersion.objects.bulk_create(bulk_data)


def ReadJiraFixVersions(project, released):
    if released == 'all':
        fix_versions_list = list(JiraFixVersion.objects.filter(project=project).values().order_by('-id'))
    else:
        fix_versions_list =  list(JiraFixVersion.objects.filter(project=project, released=released.lower()).values().order_by('-id'))

    fix_versions = ConstructFixVersion(fix_versions_list)

    return fix_versions


def ConstructFixVersion(fix_versions_list):
    fix_versions = {'fix_versions': []}

    for fix_version in fix_versions_list:
        fix_versions['fix_versions'].append({
            'id': fix_version['id'],
            'name': fix_version['name'],
            'description': fix_version['description'],
            'released': fix_version['released'],
            'projectid': fix_version['projectid'],
            'project': fix_version['project']
            })

    return fix_versions