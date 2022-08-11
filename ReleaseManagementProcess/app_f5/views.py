from asyncio.windows_events import NULL
import json
from time import sleep
from tkinter.tix import Form
from unicodedata import name
from django import forms
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from f5.bigip import ManagementRoot
from app_f5.models import F5Pools
from app_f5.forms import PoolForm

# Create your views here.

USERNAME = "admin"
PASSWORD = "$hinRyuk3n!"


def test(request):

    return render(request, 'test.html')


def nopage(request):
    
    return render(request, 'nopage.html')


def UpdatePoolNames(request):
    server_name = "gdcf501"
    pools = []
    pools_name = []

    mgmt = GetMgmt(server_name, USERNAME, PASSWORD)
    pools = GetPools(mgmt)
    SavePool(pools)

    for pool in pools:
        pools_name.append(pool.name)

    return JsonResponse(pools_name, safe=False, status=200)


def GetF5State(request):
    if request.method == "GET":
        form_pool = PoolForm(initial={'name':'','project':'','server':'','environment':'1'})
        pool_list = list(F5Pools.objects.all())
        return render(request, 'F5.html', {'form_pool': form_pool, 'pool_list': pool_list})

    form_pool = PoolForm(data=request.POST)
    if form_pool.is_valid():
        print(form_pool.cleaned_data)
    else:
        print(form_pool.errors)

    AddPool(request)
    pool_list = list(F5Pools.objects.all())
    return redirect('/f5/state/')


def AddPool(request):
    pool_name = request.POST.get('name')
    project = request.POST.get('project')
    environment = request.POST.get('environment')
    server = request.POST.get('server')

    exists = F5Pools.objects.filter(name=pool_name, project=project, server=server).exists()
    if not exists:
        F5Pools.objects.create(name=pool_name, project=project, server=server, environment=environment )


def GetMgmt(server_name):
    # return mgmt object
    try:
        mgmt = ManagementRoot(server_name, USERNAME, PASSWORD)
    except:
        return "mgmt error"
    return mgmt


def GetPools(mgmt):
    # return pool object list
    try:
        pools = mgmt.tm.ltm.pools.get_collection()
    except:
        return "pool error"
    return pools


def GetPool(mgmt, pool_name):
    # return pool object
    try:
        pool = mgmt.tm.ltm.pools.pool.load(name=pool_name, partition='Common')
    except:
        return "pool error"
    return pool


def GetPoolState(request):
    server_name = request.GET.get('server_name')
    pool_name = request.GET.get('pool_name')

    pool_state = {
        "curconn": "Error",
        "maxconn": "Error",
        "totconn": "Error",
        "state": "Error"}

    mgmt = GetMgmt(server_name)
    if mgmt == "mgmt error":
        return HttpResponse(json.dumps(mgmt), status=500)

    pool = GetPool(mgmt, pool_name)
    if pool == "pool error":
        return HttpResponse(json.dumps(pool), status=500)

    pool_stats = pool.stats.load()
    key_name = list(pool_stats.raw["entries"].keys())[0]
    pool_state["curconn"] = pool_stats.raw["entries"][key_name]["nestedStats"]["entries"]["serverside.curConns"]["value"]
    pool_state["maxconn"] = pool_stats.raw["entries"][key_name]["nestedStats"]["entries"]["serverside.maxConns"]["value"]
    pool_state["totconn"] = pool_stats.raw["entries"][key_name]["nestedStats"]["entries"]["serverside.totConns"]["value"]
    pool_state["state"] = pool_stats.raw["entries"][key_name]["nestedStats"]["entries"]["status.availabilityState"]["description"]

    #return pool_status
    return HttpResponse(json.dumps(pool_state))


def GetMembers(pool):
    # return member object
    members = []

    for member in pool.members_s.get_collection():
        members.append(member)
    return members


def GetMemberState(request):
    server_name = request.GET.get('server_name')
    pool_name = request.GET.get('pool_name')

    members_state = []

    mgmt = GetMgmt(server_name)
    if mgmt == "mgmt error":
        return HttpResponse(json.dumps(mgmt), status=500)

    pool = GetPool(mgmt, pool_name)
    if pool == "pool error":
        return HttpResponse(json.dumps(pool), status=500)
        
    members = GetMembers(pool)
    for member in members:
        member_state = {
            "pool": "",
            "name": "",
            "curconn": "",
            "maxconn": "",
            "totconn": "",
            "state": ""
        }
        
        member_stats = member.stats.load()
        key_name = list(member_stats.raw["entries"].keys())[0]
        entries = member_stats.raw["entries"][key_name]["nestedStats"]["entries"]

        member_state["pool"] = pool_name
        member_state["name"] = member.name
        member_state["curconn"] = entries["serverside.curConns"]["value"]
        member_state["maxconn"] = entries["serverside.maxConns"]["value"]
        member_state["totconn"] = entries["serverside.totConns"]["value"]
        member_state["state"] = entries["status.availabilityState"]["description"]
        members_state.append(member_state)

    return HttpResponse(json.dumps(members_state))


def SavePool(pools):
    bulk_data = []

    pools_name = list(F5Pools.objects.values_list("name", flat=True))
    for pool in pools:
        if pool.name not in pools_name:
            bulk_data.append(F5Pools(name=pool.name, project=""))
    if (len(bulk_data) != 0):
        F5Pools.objects.bulk_create(bulk_data)


def RemovePool(request):
    server_name = request.GET.get('server_name')
    pool_name = request.GET.get('pool_name')

    result = F5Pools.objects.filter(name=pool_name, server=server_name).delete()
    if result:
        return HttpResponse(json.dumps(result), status=200)
    return HttpResponse(state=500)


def PoolAction(request):
    server_name = request.GET.get('server_name')
    pool_name = request.GET.get('pool_name')
    action = request.GET.get('action')

    mgmt = GetMgmt(server_name)
    if mgmt == "mgmt error":
        return HttpResponse(json.dumps(mgmt), status=500)

    pool = GetPool(mgmt, pool_name)
    if pool == "pool error":
        return HttpResponse(json.dumps(pool), status=500)

    members = GetMembers(pool)
    if (action == "enable"):
        action_state = "user-up"
        action_session = "user-enabled"
    elif(action == "forceoffline"):
        action_state = "user-down"
        action_session = "user-disabled"

    for member in members:
        member.modify(state=action_state)
        member.modify(session=action_session)

    return HttpResponse()