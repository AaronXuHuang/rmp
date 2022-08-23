from app_octopus.models import OctoEnvironment, OctoProject, OctoSpace
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create your views here.
# svc_mcp api key
OCTOPUS_API_KEY='API-BDUFSI5UEGU3SOTLCH6IBDXFW'
OCTOPUS_SERVER='https://octopus.nextestate.com'
HEADERS = {'X-Octopus-ApiKey': OCTOPUS_API_KEY}

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


def GetDeploymentStatus(request):
    orgunit = request.GET.get('orgunit')
    jira_issues = request.GET.get('issues')

    return JsonResponse('')


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

    default_channel = CheckDefaultChannel(channels)
    channel_environments['default'] = default_channel

    return channel_environments


def CheckDefaultChannel(channels):
    # check if channel is default channel
    # https://octopus.nextestate.com/api/channels/Channels-902

    default_channel = ''

    for channel in channels:
        url = OCTOPUS_SERVER + "/api/channels/" + channel
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


def FetchDeployments(request, orgunit, issue):
    
    return HttpResponse()



# project releases
# https://octopus/api/Spaces-1/projects/Projects-682/releases

# project release deployments
# https://octopus/api/Spaces-1/releases/Releases-150307/deployments


