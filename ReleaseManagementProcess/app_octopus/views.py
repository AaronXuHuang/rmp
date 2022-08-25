from asyncio.windows_events import NULL
import json
from app_octopus.models import OctoEnvironment, OctoProject, OctoSpace
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create your views here.
# svc_mcp api key
OCTOPUS_API_KEY='API-BDUFSI5UEGU3SOTLCH6IBDXFW'
OCTOPUS_SERVER='https://octopus.nextestate.com'
HEADERS = {'X-Octopus-ApiKey': OCTOPUS_API_KEY}
WORKER = 10

def test(request):
    # test begin
    # fetch project channel environments map and default channel
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id
    project_name = request.GET.get('project')
    project_id = OctoProject.objects.get(name=project_name).id

    channel_environments = FetchProjectChannelEnvironments(space_id, project_id)

    return JsonResponse(channel_environments)
    # test end


def SyncOctoSpaces(request):
    spaces = FetchSpaces()
    OctoSpace.objects.all().delete()
    SaveSpaces(spaces)

    return JsonResponse(spaces)


def SyncOctoProjects(request):
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id
    
    projects = FetchProjects(space_id)
    OctoProject.objects.filter(spaceid=space_id).delete()
    SaveProjects(projects)

    return JsonResponse(projects)


def SyncOctoEnvironments(request):
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id

    environments = FetchEnvironments(space_id)
    OctoEnvironment.objects.filter(spaceid=space_id).delete()
    SaveEnvironments(environments)

    return JsonResponse(environments)


def GetOctoProjectChannelEnvironments(request):
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id
    project_name = request.GET.get('project')
    project_id = OctoProject.objects.get(name=project_name).id

    channel_environments = FetchProjectChannelEnvironments(space_id, project_id)

    return JsonResponse(channel_environments)


def GetOctoProjectReleases(request):
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id
    project_name = request.GET.get('project')
    project_id = OctoProject.objects.get(name=project_name).id

    releases = FetchProjectReleases(space_id, project_id)

    return JsonResponse(releases)


def GetOctoProjectReleaseDeployments(request):
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id
    project_name = request.GET.get('project')
    project_id = OctoProject.objects.get(name=project_name).id

    releases = FetchProjectReleases(space_id, project_id)
    releases, tasks = FetchProjectReleaseDeployments(space_id, releases)

    return JsonResponse(releases)


def GetOctoProjectReleaseDeploymentStates(request):
    space_name = request.GET.get('space')
    space_id = OctoSpace.objects.get(name=space_name).id
    project_name = request.GET.get('project')
    project_id = OctoProject.objects.get(name=project_name).id

    releases = FetchProjectReleases(space_id, project_id)
    releases, tasks = FetchProjectReleaseDeployments(space_id, releases)
    releases = FetchProjectReleaseDeploymentStates(releases, tasks)

    return JsonResponse(releases)


def FetchSpaces():
    # https://octopus.nextestate.com/api/Spaces

    spaces = {
        'spaces': []
        }

    url = OCTOPUS_SERVER + "/api/Spaces"
    items = requests.get(url=url, headers=HEADERS, verify=False, allow_redirects=True).json()
    for item in items['Items']:
        spaces['spaces'].append({
            'id': item['Id'],
            'name': item['Name']
        })

    return spaces


def FetchProjects(space_id):
    # https://octopus.nextestate.com/api/Spaces-42/projects?skip=0&take=2147483647

    projects = {
        'projects': [],
    }

    url = OCTOPUS_SERVER + "/api/" + space_id + "/projects?skip=0&take=2147483647"
    items = requests.get(url=url, headers=HEADERS, verify=False, allow_redirects=True).json()
    for item in items['Items']:
        projects['projects'].append({
            'id': item['Id'],
            'name': item['Name'],
            'projectgroupid': item['ProjectGroupId'],
            'spaceid': item['SpaceId']
        })

    return projects


def FetchEnvironments(space_id):
    # https://octopus.nextestate.com/api/Spaces-42/environments?skip=0&take=2147483647

    environments = {
        'environments': [],
    }

    url = OCTOPUS_SERVER + "/api/" + space_id + "/environments?skip=0&take=2147483647"
    items = requests.get(url=url, headers=HEADERS, verify=False, allow_redirects=True).json()
    for item in items['Items']:
        environments['environments'].append({
            'id': item['Id'],
            'name': item['Name'],
            'spaceid': item['SpaceId']
        })

    return environments


def FetchProjectChannelEnvironments(space_id, project_id):
    # project channel/environment map
    # https://octopus.nextestate.com/api/Spaces-1/progression/Projects-682

    channel_environments = {
        'default': '',
        'channels': []
    }
    channels = []

    url = OCTOPUS_SERVER + "/api/" + space_id + "/progression/" + project_id
    items = requests.get(url=url, headers=HEADERS, verify=False, allow_redirects=True).json()
    channel_environments['channels'] = items['ChannelEnvironments']
    for item in items['ChannelEnvironments']:
        channels.append(item)

    default_channel = CheckDefaultChannel(space_id, channels)
    channel_environments['default'] = default_channel

    return channel_environments


def FetchProjectReleases(space_id, project_id):
    # project releases
    # https://octopus.nextestate.com/api/Spaces-1/projects/Projects-682/releases

    releases = {
        'releases': {}
        }

    url = OCTOPUS_SERVER + "/api/" + space_id + "/projects/" + project_id + "/releases?skip=0&take=2147483647"
    items = requests.get(url=url, headers=HEADERS, verify=False, allow_redirects=True).json()
    for item in items['Items']:
        release_note = item['ReleaseNotes']
        if release_note is None:
            continue
        jira_issue_begin = release_note.index('[')
        jira_issue_end = release_note.index(']')
        jira_issue = release_note[jira_issue_begin + 1: jira_issue_end]

        release = {
            'version': item['Version'],
            'channelid': item['ChannelId'],
            'jiraissue': jira_issue,
            'deployments': {}
        }
        releases['releases'][item['Id']] = release

    return releases


def FetchProjectReleaseDeployments(space_id, releases):
    # project release deployments
    # https://octopus.nextestate.com/api/Spaces-1/releases/Releases-150307/deployments?skip=0&take=2147483647

    urls = []
    futures = []
    tasks = {}
    session = FuturesSession(max_workers=WORKER)

    for release in releases['releases']:
        urls.append(OCTOPUS_SERVER + "/api/" + space_id + "/releases/" + release + "/deployments?skip=0&take=2147483647")

    for url in urls:
        futures.append(session.get(url=url, headers=HEADERS, verify=False, allow_redirects=True))

    for future in as_completed(futures):
        deployments = {}
        items = json.loads(future.result().text)
        for item in items['Items']:
            task = item['TaskId']
            deployment = {
                'environmentid': item['EnvironmentId'],
                'taskid': task,
                'state': ''
            }
            tasks[task] = {
                'releaseid': item['ReleaseId'],
                'deploymentid': item['Id']
            }
            deployments[item['Id']] = deployment
        releases['releases'][item['ReleaseId']]['deployments'] = deployments

    return releases, tasks


def FetchProjectReleaseDeploymentStates(releases, tasks):
    # project release deployment states (deployment result: Success/Failed)
    # https://octopus.nextestate.com/api/tasks/ServerTasks-645703

    urls = []
    futures = []
    session = FuturesSession(max_workers=WORKER)

    for task in tasks:
        urls.append(OCTOPUS_SERVER + "/api/tasks/" + task)
    
    for url in urls:
        futures.append(session.get(url=url, headers=HEADERS, verify=False, allow_redirects=True))

    for future in as_completed(futures):
        items = json.loads(future.result().text)
        task_id = items['Id']
        deployment_id = items['Arguments']['DeploymentId']
        state = items['State']
        release_id = tasks[task_id]['releaseid']
        releases['releases'][release_id]['deployments'][deployment_id]['state'] = state

    return releases


def CheckDefaultChannel(space_id, channels):
    # check if channel is default channel
    # https://octopus.nextestate.com/api/channels/Channels-902

    default_channel = ''

    for channel in channels:
        url = OCTOPUS_SERVER + "/api/"  + space_id + "/channels/" + channel
        item = requests.get(url=url, headers=HEADERS, verify=False, allow_redirects=True).json()
        if item['IsDefault']:
            default_channel = channel
            break

    return default_channel


def SaveSpaces(spaces):
    bulk_data = []

    for space in spaces['spaces']:
        bulk_data.append(OctoSpace(
            id=space['id'], 
            name=space['name']))
    OctoSpace.objects.bulk_create(bulk_data)


def SaveProjects(projects):
    bulk_data = []

    for project in projects['projects']:
        bulk_data.append(OctoProject(
            id=project['id'], 
            name=project['name'], 
            projectgroupid=project['projectgroupid'],
            spaceid=project['spaceid']))
    OctoProject.objects.bulk_create(bulk_data)


def SaveEnvironments(environments):
    bulk_data = []

    for environment in environments['environments']:
        bulk_data.append(OctoEnvironment(
            id=environment['id'], 
            name=environment['name'], 
            spaceid=environment['spaceid']))
    OctoEnvironment.objects.bulk_create(bulk_data)


def GetOrgunitSpaceId(orgunit):
    # Should move the lists to config file
    default_space = ['LEGACY', 'BUX', 'FW', 'GSS', 'GBOS']
    azure_space = ['CBS', 'GWA', 'FX']

    if orgunit.upper() in default_space:
        space_name = 'Default'
    elif orgunit.upper() in azure_space:
        space_name = 'Azure'

    space_id = OctoSpace.objects.get(name=space_name).id

    return space_id


def GetProjectId(project_names):
    project_id = list(OctoProject.objects.filter(name__in=project_names).values())

    return project_id