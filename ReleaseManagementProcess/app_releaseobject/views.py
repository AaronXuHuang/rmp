
from platform import release
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from app_jira import views as Jiraviews
from app_octopus import views as Octoviews
from app_releaseobject.models import ReleaseObject, ReleaseProcess
from threading import Thread
import json
import time

BUX_QA = 'BUX_QA'
BUX_PRF = 'BUX_PRF'
ERROR = 'error'
ERROR_NO_RELEASE_OBJECT_FOUND = 'no corresponding release object found'

# Create your views here.
def test(request):
    fix_version = request.GET.get('fixversion')
    orgunit = request.GET.get('orgunit')

    return HttpResponse('test')


def LoadReleaseObject(request):


    return render(request, 'releaseobject.html')


def CreateReleaseObject(request):
    fix_version = request.GET.get('fixversion')
    orgunit = request.GET.get('orgunit')

    # fetch jira issues according to the fix version
    release_object = {fix_version: {}}
    issues = Jiraviews.FetchJiraIssues(orgunit, fix_version)
    release_object = ConstructROComponent(orgunit, fix_version, issues, release_object)
    release_object = ConstructROIssue(fix_version, issues, release_object)
    # get octopus space id
    octo_space_id = Octoviews.GetOrgunitSpaceId(orgunit)
    # get octopus project id
    octo_project_id_map = ConstructROProjectMap(release_object, fix_version)
    # fetch octopus project environments (run for the first component)
    envs_map = ConstructROEnvMap(octo_space_id, octo_project_id_map)
    release_object = ConstructRO(release_object, fix_version, octo_space_id, octo_project_id_map, envs_map)

    SaveReleaseObject(orgunit, fix_version, release_object)
 
    return JsonResponse(release_object)


def GetReleaseObject(request):
    fix_version = request.GET.get('fixversion')
    orgunit = request.GET.get('orgunit')

    release_object_info = {'information': {}}

    release_object_count_query = ReleaseObject.objects.filter(orgunit=orgunit, fixversion=fix_version)
    count = release_object_count_query.count()
    if count != 0:
        release_object_query = ReleaseObject.objects.filter(orgunit=orgunit, fixversion=fix_version, version=count).values()

        # append more information
        release_object = release_object_query[0]['releaseobject']
        release_object_info['information']['fixversion'] = fix_version
        release_object_info['information']['version'] = release_object_query[0]['version']
        release_object_info['information']['stage'] = release_object_query[0]['stage']
        release_object_info['information']['creator'] = release_object_query[0]['creator']
        release_object_info['information']['created time'] = release_object_query[0]['created']
        release_object_info['information']['release'] = release_object_query[0]['released']
        release_object_info['information']['orgunit'] = release_object_query[0]['orgunit']
        release_object_info['information']['space'] = Octoviews.SpaceMap(orgunit)
        release_object_info[fix_version] = json.loads(release_object)[fix_version]

        return JsonResponse(release_object_info)

    return JsonResponse({ERROR: ERROR_NO_RELEASE_OBJECT_FOUND})


def GetReleaseObjectFixVersion(request):
    orgunit = request.GET.get('orgunit')

    fix_versions_list = list(ReleaseObject.objects.filter(orgunit=orgunit).values('fixversion').order_by('-id'))
    fix_versions = ConstructROFixVersion(fix_versions_list)
    return JsonResponse(fix_versions)


def ConstructROComponent(orgunit, fix_version, issues, release_object):
    components_sort = []

    for issue in issues['issues']:
        for component in issue['components']:
            if component not in components_sort:
                components_sort.append(component)
    components_sort.sort()
    for component in components_sort:
        release_object[fix_version][component] = {
            'tier': 'n/a', # get tier from perforce or github
            'latest': '',
            'releaseversion': '',
            'releaseassembled': '',
            'environments': {},
            'issues': {}
        }
    
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
            release_object[fix_version][component]['issues'][issue_key] = {
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


def ConstructROEnvMap(octo_space_id, octo_project_id_map):
    envs = {}
    project_name = list(octo_project_id_map)[0]

    channel_envs = Octoviews.FetchProjectChannelEnvironments(
        octo_space_id,
        octo_project_id_map[project_name])
    default_channel = channel_envs['default']

    for env in channel_envs['channels'][default_channel]:
        envs[env['Id']] = env['Name']
    
    return envs


def FilterRelease(octo_project_id_map, project_name, octo_space_id, release_object, fix_version):
    # fetch octopus projcet release
    project_id = octo_project_id_map[project_name]
    releases_filtered = {'releases': {}}

    releases = Octoviews.FetchProjectReleases(octo_space_id, project_id)
    
    releases_filtered['latest'] = releases['latest']
    for release_name, release in releases['releases'].items(): 
        for jira_issue in release_object[fix_version][project_name]['issues']:
            if release['jiraissue'] == jira_issue:
                releases_filtered['releases'][release_name] = release

    return releases_filtered
    

def ConstrucRelease(releases_filtered, release_object, fix_version, project_name, release_version, release_assembled, env_states):
    latest_version = ''
    project = release_object[fix_version][project_name]
    project['releaseversion'] = release_version
    project['releaseassembled'] = release_assembled
    project['environments'] = env_states

    for release_name, release in releases_filtered['releases'].items():
        for key, jira_issue in project['issues'].items():
            if release['jiraissue'] == key:
                jira_issue['releases'][release_name] = release
                if not latest_version:
                    project['latest'] = releases_filtered['latest']

    return release_object


def ConstructRO(release_object, fix_version, octo_space_id, octo_project_id_map, envs_map):
    for project_name in release_object[fix_version]:
        releases_filtered = FilterRelease(
            octo_project_id_map,
            project_name,
            octo_space_id,
            release_object,
            fix_version)

        # fetch octopus projcet release deployment
        releases_filtered, tasks = Octoviews.FetchProjectReleaseDeployments(octo_space_id, releases_filtered)
        releases_filtered = ConstructROEnvName(releases_filtered, envs_map)

        releases_filtered = Octoviews.FetchProjectReleaseDeploymentStates(releases_filtered, tasks)

        release_version, release_assembled = ConstructROReleaseVersion(releases_filtered)

        env_states = ConstructROReleaseEnvironmentState(
            releases_filtered,
            envs_map,
            release_version)

        release_object = ConstrucRelease(
            releases_filtered,
            release_object,
            fix_version,
            project_name,
            release_version,
            release_assembled,
            env_states)

    return release_object


def ConstructROEnvName(releases_filtered, envs_map):
    for release in releases_filtered['releases'].values():
        for deployment in release['deployments'].values():
            env_id = deployment['environmentid']
            deployment['environmentname'] = envs_map[env_id]

    return releases_filtered


def ConstructROReleaseVersion(releases_filtered):
    release_version = ''
    release_assembled = ''
    last_assembled = ''
                
    for release in releases_filtered['releases'].values():
        version = release['version']
        assembled = release['assembled']
        for deployment in release['deployments'].values():
            env_name = deployment['environmentname']
            state = deployment['state']
            if env_name == BUX_QA and state == 'Success' and assembled > last_assembled:
                release_version = version
                last_assembled = assembled
                release_assembled = ConvertTimeZone(assembled)

    return release_version, release_assembled


def ConstructROFixVersion(fix_versions_list):
    fix_versions = {'fix_versions': []}

    for fix_version in fix_versions_list:
        fix_versions['fix_versions'].append(
            fix_version['fixversion']
        )
    return fix_versions


def ConstructROReleaseEnvironmentState(releases_filtered, envs_map, release_version):
    env_states = {}

    for env in envs_map:
        env_states[envs_map[env]] = 'none'

    for release in releases_filtered['releases'].values():
        if release['version'] == release_version:
            for  deployment in release['deployments'].values():
                env_states[deployment['environmentname']] = deployment['state']

    return env_states


def ConvertTimeZone(assembled):
    index = assembled.index('.')
    assembled = assembled[0:index]
    format = "%Y-%m-%dT%H:%M:%S"

    assembled = datetime.strptime(assembled, format) + timedelta(hours=-7)
    assembled = assembled.strftime(format)

    return assembled


def SaveReleaseObject(orgunit, fix_version, release_object):
    ReleaseObject.objects.filter(orgunit=orgunit, fixversion=fix_version).delete()
    ReleaseObject.objects.create(
        fixversion = fix_version,
        releaseobject = json.dumps(release_object),
        version = '1',
        orgunit = orgunit,
        stage = 'create release object',
        creator = '',
        created = datetime.utcnow())


def RunReleaseProcess(request):
    orgunit = request.GET.get('orgunit')
    fix_version = request.GET.get('fixversion')
    env = request.GET.get('env')
    state = request.GET.get('state')

    if orgunit == 'BUX':
        print('thread run_rp_bux')
        RP_InitState(orgunit, fix_version, state)
        run_rp_bux = Thread(target=RunReleaseProcess_BUX, args=(fix_version, env))
        run_rp_bux.start()

    return JsonResponse({'result': 'ok'})

def RunReleaseProcess_BUX(fix_version, env):
    orgunit = 'BUX'

    if env  == 'PIE':
        sub_env = 'PIE'
        RP_Deploy(orgunit, fix_version, env, sub_env)
        RP_Test(orgunit, fix_version, sub_env)
    if env  == 'STG':
        sub_envs = ['STG2', 'STG1']
        for sub_env in sub_envs:
            RP_F5(orgunit, fix_version, env, sub_env, 'disable', 'prt')
            RP_F5(orgunit, fix_version, env, sub_env, 'disable', 'nonprt')
            RP_IISReset(orgunit, fix_version, env, sub_env)
            RP_Deploy(orgunit, fix_version, env, sub_env)
            RP_F5(orgunit, fix_version, env, sub_env, 'enable', 'nonprt')
            RP_F5(orgunit, fix_version, env, sub_env, 'enable', 'prt')
        RP_Test(orgunit, fix_version, env)
    if env  == 'PROD':
        sub_envs = ['DC2', 'DC1']
        for sub_env in sub_envs:
            RP_F5(orgunit, fix_version, env, sub_env, 'disable', 'prt')
            RP_F5(orgunit, fix_version, env, sub_env, 'drain', 'prt')
            RP_F5(orgunit, fix_version, env, sub_env, 'disable', 'nonprt')
            RP_F5(orgunit, fix_version, env, sub_env, 'drain', 'nonprt')
            RP_IISReset(orgunit, fix_version, env, sub_env)
            RP_Deploy(orgunit, fix_version, env, sub_env)
            RP_F5(orgunit, fix_version, env, sub_env, 'enable', 'nonprt')
            RP_F5(orgunit, fix_version, env, sub_env, 'enable', 'prt')
        RP_Test(orgunit, fix_version, env)

    print('RunReleaseProcess_BUX done')


def RP_InitState(orgunit, fix_version, state):
    if state == 'start':
        if orgunit == 'BUX':
            file_path = './app_releaseobject/config/release_process_tracker/BUX.json'
        temp_file = open(file_path)
        tracker = json.load(temp_file)
        temp_file.close()
        ReleaseProcess.objects.update_or_create(orgunit=orgunit, fixversion=fix_version, defaults={'tracker':json.dumps(tracker)})


def RP_UpdateState(orgunit, fix_version, env, id, text, time_item, state):
    format = "%Y-%m-%dT%H:%M:%S"
    time = datetime.utcnow() + timedelta(hours=-7)
    time = time.strftime(format)

    object = ReleaseProcess.objects.filter(orgunit=orgunit, fixversion=fix_version).values()
    tracker = json.loads(object[0]['tracker'])
    tracker[orgunit][env][id]['text'] = text
    tracker[orgunit][env][id][time_item] = time
    tracker[orgunit][env][id]['status'] = state
    ReleaseProcess.objects.update_or_create(orgunit=orgunit, fixversion=fix_version, defaults={'tracker':json.dumps(tracker)})


def RP_GetState(orgunit, fix_version):
    object = ReleaseProcess.objects.filter(orgunit=orgunit, fixversion=fix_version).values()
    tracker = json.loads(object[0]['tracker'])

    return tracker


def RP_Deploy(orgunit, fix_version, env, sub_env):
    RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-deploy', 'Deploying', 'start', 'running')
    # todo
    time.sleep(30)
    RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-deploy', 'Deployed', 'complete', 'done')

    print('RP_Deploy')


def RP_Test(orgunit, fix_version, env):
    RP_UpdateState(orgunit, fix_version, env, env.lower() + '-test', env + ' testing', 'start', 'running')
    print('RP_Test')


def RP_F5(orgunit, fix_version, env, sub_env, action, tier):
    if action == 'disable':
        RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-disabled-' + tier, 'Disabling ' + tier, 'start', 'running')
        # todo
        time.sleep(10)
        RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-disabled-' + tier, 'Disabled ' + tier, 'complete', 'done')
    elif action == 'enable':
        RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-enabled-' + tier, 'Enabling ' + tier, 'start', 'running')
        # todo
        time.sleep(10)
        RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-enabled-' + tier, 'Enabled ' + tier, 'complete', 'done')
    elif action == 'drain':
        RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-drain-' + tier, 'Draining ' + tier, 'start', 'running')
        # todo
        time.sleep(10)
        RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-drain-' + tier, 'Drained ' + tier, 'complete', 'done')

    print('RP_F5')


def RP_IISReset(orgunit, fix_version, env, sub_env):
    RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-iisreset', 'IIS reseting', 'start', 'running')
    # todo
    time.sleep(30)
    RP_UpdateState(orgunit, fix_version, env, sub_env.lower() + '-iisreset', 'IIS reseted', 'complete', 'done')
    print('RP_IISReset')


def GetReleaseProcessState(request):
    orgunit = request.GET.get('orgunit')
    fix_version = request.GET.get('fixversion')

    tracker = RP_GetState(orgunit, fix_version)
    return JsonResponse(tracker)

def UpdateReleaseProcessTest(request):
    orgunit = request.GET.get('orgunit')
    fix_version = request.GET.get('fixversion')
    env = request.GET.get('env')

    RP_UpdateState(orgunit, fix_version, env, env.lower() + '-test', env + ' tested', 'complete', 'done')

    return JsonResponse({'result': 'ok'})