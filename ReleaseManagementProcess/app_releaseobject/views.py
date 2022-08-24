import json
from platform import release
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from app_jira import views as Jiraviews
from app_octopus import views as Octoviews
from app_jira.models import JiraProject, JiraFixVersion

# Create your views here.
def CreateRO(request):
    fix_version = request.GET.get('fixversion')
    project = request.GET.get('project')

    release_object = {fix_version: {}}
    

    # fetch jira issues according to the fix version
    issues = Jiraviews.FetchJiraIssues(project, fix_version)
    release_object = ConstructROComponent(fix_version, issues, release_object)
    release_object = ConstructROIssue(fix_version, issues, release_object)

    # fetch octopus environments

    return JsonResponse(release_object)


def GetRO(request):
    
    return HttpResponse()


def ConstructROComponent(fix_version, issues, release_object):
    components_sort = []

    for issue in issues['issues']:
        for component in issue['components']:
            if component not in components_sort:
                components_sort.append(component)
    components_sort.sort()
    for component in components_sort:
        release_object[fix_version][component] = {}
    
    return release_object


def ConstructROIssue(fix_version, issues, release_object):
    for component in release_object[fix_version]:
        issues_sort = []
        for issue in issues['issues']:
            if component in issue['components']:
                issues_sort.append(issue['issue'] + '|' + issue['issuetype'])
        issues_sort.sort()
        for issue in issues_sort:
            index = issue.index('|')
            issue_key = issue[0: index]
            issue_type = issue[index + 1:]
            release_object[fix_version][component][issue_key] = {'issuetype': issue_type}
    
    return release_object


