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


def FetchSpaces():
    # https://octopus.nextestate.com/api/Spaces
    spaces = {
        'spaces': []
        }

    url = OCTOPUS_SERVER + "/api/Spaces"
    headers = {'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    items = requests.get(url=url, headers=headers, verify=False, allow_redirects=True).json()

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
    headers = {'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    items = requests.get(url=url, headers=headers, verify=False, allow_redirects=True).json()
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
    headers = {'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    items = requests.get(url=url, headers=headers, verify=False, allow_redirects=True).json()
    for item in items['Items']:
        environments['environments'].append({
            'id': item['Id'],
            'name': item['Name'],
            'spaceid': item['SpaceId']
        })

    return environments


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