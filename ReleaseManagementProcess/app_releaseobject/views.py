import json
from platform import release
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from app_jira import views as Jiraviews
from app_octopus import views as Octoviews
from app_jira.models import JiraProject, JiraFixVersion

# Create your views here.
def CreateRO(request):
    fix_version = request.GET.get('fixversion')
    orgunit = request.GET.get('orgunit')

    # fetch jira issues according to the fix version
    release_object = {fix_version: {}}
    issues = Jiraviews.FetchJiraIssues(orgunit, fix_version)
    release_object = ConstructROComponent(fix_version, issues, release_object)
    release_object = ConstructROIssue(fix_version, issues, release_object)
    # get octopus space id
    octo_space_id = Octoviews.GetOrgunitSpaceId(orgunit)
    # get octopus project id
    octo_project_id_map = ConstructROProjectMap(release_object, fix_version)
    # fetch octopus project environments (run for the first component)
    environments = ConstructROEnvironmentMap(octo_space_id, octo_project_id_map)
    release_object = ConstructRO(release_object, fix_version, octo_space_id, octo_project_id_map)
 
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
            release_object[fix_version][component][issue_key] = {
                'issuetype': issue_type,
                'releases': {}}
    
    return release_object


def ConstructROProjectMap(release_object, fix_version):
    octo_project_id_map = {}
    project_names = []

    for component in release_object[fix_version]:
        project_names.append(component)
    octo_projects= Octoviews.GetProjectId(project_names)
    for octo_project in octo_projects:
        octo_project_id_map[octo_project['name']] = octo_project['id']

    return octo_project_id_map


def ConstructROEnvironmentMap(octo_space_id, octo_project_id_map):
    environments = {}
    project_name = list(octo_project_id_map)[0]

    channel_environments = Octoviews.FetchProjectChannelEnvironments(
        octo_space_id,
        octo_project_id_map[project_name])
    default_channel = channel_environments['default']

    for environment in channel_environments['channels'][default_channel]:
        environments[environment['Id']] = environment['Name']
    
    return environments


def FilterRelease(octo_project_id_map, project_name, octo_space_id, release_object, fix_version):
    # fetch octopus projcet release
    project_id = octo_project_id_map[project_name]
    releases_filtered = {'releases': {}}

    releases = Octoviews.FetchProjectReleases(octo_space_id, project_id)
    
    for release in releases['releases']:
        for jira_issue in release_object[fix_version][project_name]:
            if releases['releases'][release]['jiraissue'] == jira_issue:
                releases_filtered['releases'][release] = releases['releases'][release]
    
    return releases_filtered
    

def ConstrucRelease(releases_filtered, release_object, fix_version, project_name):
    for release in releases_filtered['releases']:
        for jira_issue in release_object[fix_version][project_name]:
            if releases_filtered['releases'][release]['jiraissue'] == jira_issue:
                release_object[fix_version][project_name][jira_issue]['releases'][release] = releases_filtered['releases'][release]

    return release_object


def ConstructRO(release_object, fix_version, octo_space_id, octo_project_id_map):
    for project_name in release_object[fix_version]:
        releases_filtered = FilterRelease(octo_project_id_map, project_name, octo_space_id, release_object, fix_version)

        # fetch octopus projcet release deployment
        releases_filtered, tasks = Octoviews.FetchProjectReleaseDeployments(octo_space_id, releases_filtered)

        # not necessary to check deployments state
        # because if the deployment failed, the jira issue can not be finished
        # fetch octopus projcet release deployment state
        releases_filtered = Octoviews.FetchProjectReleaseDeploymentStates(releases_filtered, tasks)

        release_object = ConstrucRelease(releases_filtered, release_object, fix_version, project_name)

    return release_object