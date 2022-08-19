from app_octopus.models import OctoSpace
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests

# Create your views here.
OCTOPUS_USER='svc_mcp'
OCTOPUS_PWD='Wa7rUxeD'
OCTOPUS_SERVER='https://octopus.nextestate.com'
OCTOPUS_API_KEY='API-BDUFSI5UEGU3SOTLCH6IBDXFW'

def UpdateSpace(request):
    
    spaces = FetchSpace()
    OctoSpace.objects.all().delete()
    SaveSpace(spaces)
    return JsonResponse(spaces)


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


def SaveSpace(spaces):
    bulk_data = []

    for space in spaces['spaces']:
        bulk_data.append(OctoSpace(id=space['id'], name=space['name']))
    OctoSpace.objects.bulk_create(bulk_data)


def FetchEnvironment(request, orgunit):
    
    return HttpResponse()


def FetchDeployment(request, orgunit, issue):
    
    return HttpResponse()