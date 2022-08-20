from app_octopus.models import OctoProject, OctoSpace
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests

# Create your views here.
# svc_mcp api key
OCTOPUS_API_KEY='API-BDUFSI5UEGU3SOTLCH6IBDXFW'
OCTOPUS_SERVER='https://octopus.nextestate.com'

def UpdateSpace(request):
    
    spaces = FetchSpace()
    OctoSpace.objects.all().delete()
    SaveSpace(spaces)
    return JsonResponse(spaces)


def UpdateProject(request):
    # Spaces-2: TPG, Spaces-22: RushCard, Spaces-22: RE
    exclude_items = ['Spaces-2', 'Spaces-22', 'Spaces-62']
    space_ids = list(OctoSpace.objects.values_list('id', flat=True))
    for item in exclude_items:
        space_ids.remove(item)
    
    projects = FetchProject(space_ids)
    OctoProject.objects.all().delete()
    SaveProject(projects)
    return JsonResponse(projects)


def FetchSpace():
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


def FetchProject(space_ids):
    projects = {
        'projects': [],
    }

    for space_id in space_ids:
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


def SaveSpace(spaces):
    bulk_data = []

    for space in spaces['spaces']:
        bulk_data.append(OctoSpace(
            id=space['id'], 
            name=space['name']))
    OctoSpace.objects.bulk_create(bulk_data)


def SaveProject(projects):
    bulk_data = []

    for project in projects['projects']:
        bulk_data.append(OctoProject(
            id=project['id'], 
            name=project['name'], 
            projectgroupid=project['projectgroupid'],
            spaceid=project['spaceid']))
    OctoProject.objects.bulk_create(bulk_data)


def FetchEnvironment(request, orgunit):
    
    return HttpResponse()


def FetchDeployment(request, orgunit, issue):
    
    return HttpResponse()