from unicodedata import name
from app_rmpadmin.models import Partner, Tier
from bs4 import BeautifulSoup
from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from urllib.parse import urlparse
import base64
import boto3
import configparser
import json
import os
import re
import requests
import time
import xml.etree.ElementTree as ET

# Create your views here.
region = 'us-west-2'
outputformat = 'json'
awsconfigfile = '\\.aws\\credentials'
sslverification = True
idpentryurl = 'https://sts.wip.greendotcorp.com/adfs/ls/idpinitiatedsignon.aspx?loginToRp=urn:amazon:webservices'
username = "svc_teamcity@nextestate.com"
password = "2utreraC"
role_arn = "arn:aws:iam::805088162977:role/bos-ssp-adfs-teamcity"
principal_arn = "arn:aws:iam::805088162977:saml-provider/sts.wip.greendotcorp.com"
duration = 7200
default_profile = "default"
rmp_profile = "rmp"
sleep_time = 0.5
accountMap = {
    "sbx": "sbx",
    "dev": "dev",
    "int": "int",
    "qa": "qa",
    "prf": "prf",
    "pie": "pie",
    "stg": "stg",
    "stgb": "stg",
    "stin": "stg",
    "pdin": "prod",
    "pdgb": "prod",
    "prod": "prod"
}
accountIdMap = {
    "sbx": "257873977405",
    "dev": "159865129828",
    "int": "908441563114",
    "qa": "372834007176",
    "prf": "716308132724",
    "pie": "500545396857",
    "stg": "223040669651",
    "prod": "262683030539"
}

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def test(request):
    aws_assume_role_with_saml()
    aws_assume_role('dev')
    filter_values = construct_filter_values(['green'], ['running'], ['*'], ['*'], ['CORE', 'FR'])
    response = aws_instance_filter(filter_values)
    fmt_response = json.dumps(response, cls=ComplexEncoder)
    instances = format_instances(json.loads(fmt_response))
    return HttpResponse(json.dumps(instances))

    return render(request, 'AWS.html')


def ListInstance(request):

    return render(request, 'AWS.html')
    

def update_credentials(token, profile):
    home = os.path.expanduser ('~')
    filename = home + awsconfigfile

    config = configparser.RawConfigParser()
    config.read(filename)

    awsprofile = profile
    if not config.has_section(awsprofile):
        config.add_section(awsprofile)

    config.set(awsprofile, 'output', outputformat)
    config.set(awsprofile, 'region', region)
    config.set(awsprofile, 'aws_access_key_id', token['Credentials']['AccessKeyId'])
    config.set(awsprofile, 'aws_secret_access_key', token['Credentials']['SecretAccessKey'])
    config.set(awsprofile, 'aws_session_token', token['Credentials']['SessionToken'])
    if profile == default_profile:
        config.set(awsprofile, 'aws_security_token', token['Credentials']['SessionToken'])

    with open(filename, 'w+') as configfile:
        config.write(configfile)

    time.sleep(sleep_time)
    

def aws_assume_role_with_saml():
    session = requests.Session()
    formresponse = session.get(idpentryurl, verify=sslverification)
    idpauthformsubmiturl = formresponse.url
    formsoup = BeautifulSoup(formresponse.text, features="lxml")
    payload = {}

    for inputtag in formsoup.find_all(re.compile('(INPUT|input)')):
        name = inputtag.get('name','')
        value = inputtag.get('value','')
        if "user" in name.lower():
            payload[name] = username
        elif "email" in name.lower():
            payload[name] = username
        elif "pass" in name.lower():
            payload[name] = password
        else:
            payload[name] = value

    for inputtag in formsoup.find_all(re.compile('(FORM|form)')):
        action = inputtag.get('action')
        loginid = inputtag.get('id')
        if (action and loginid == "loginForm"):
            parsedurl = urlparse(idpentryurl)
            idpauthformsubmiturl = parsedurl.scheme + "://" + parsedurl.netloc + action

    response = session.post(idpauthformsubmiturl, data=payload, verify=sslverification)

    soup = BeautifulSoup(response.text, features="lxml")
    assertion = ""
    for inputtag in soup.find_all('input'):
        if(inputtag.get('name') == 'SAMLResponse'):
            assertion = inputtag.get('value')

    if (assertion == ''):
        error_msg = "Response did not contain a valid SAML assertion/nYou probably specified an incorrect username and/or password or your account is locked out"
        return error_msg

    awsroles = []
    root = ET.fromstring(base64.b64decode(assertion))
    for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        if (saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
            for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                awsroles.append(saml2attributevalue.text)

    client = boto3.client('sts')
    token = client.assume_role_with_saml(
        RoleArn=role_arn,
        PrincipalArn=principal_arn,
        SAMLAssertion=assertion,
        DurationSeconds=duration)

    update_credentials(token, default_profile)


def aws_assume_role(env):
    boto3.setup_default_session(profile_name=default_profile)
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn = 'arn:aws:iam::' + accountIdMap[accountMap[env]] + ':role/bos-' + accountMap[env] + '-deploy-devops',
        RoleSessionName = 'qa'
    )
    update_credentials(response, rmp_profile)


def aws_instance_filter(filter_values):
    filter_vars = [
        {
            'Name': 'tag:Colorstack',
            'Values': filter_values['colorstack']
        },
        {
            'Name': 'tag:Tier',
            'Values': filter_values['tier']
        },
        {
            'Name': 'tag:Partner',
            'Values': filter_values['partner']
        },
        {
            # pending | running | shutting-down | terminated | stopping | stopped
            'Name': 'instance-state-name',
            'Values': filter_values['instance_state_name']
        },
        {
            'Name': 'network-interface.addresses.private-ip-address',
            'Values': filter_values['private_ip_address']
        }
    ]

    boto3.setup_default_session(profile_name=rmp_profile)
    client = boto3.client('ec2')
    response = client.describe_instances(
        Filters = filter_vars
    )
    print(response)
    return response


def construct_filter_values(colorstacks, instance_states, ipaddresses, partners, tiers):
    filter_values = {
        'colorstack': colorstacks,
        'instance_state_name': instance_states,
        'private_ip_address': ipaddresses,
        'partner': partners,
        'tier': tiers
    }

    return filter_values


def FilterInstance(request):
    environments = request.GET.get('environments').split(',')
    colorstacks = request.GET.get('colorstacks').split(',')
    instance_states = request.GET.get('instance_states').split(',')
    ip_addresses = request.GET.get('ip_addresses').split(',')
    partners = request.GET.get('partners').upper().split(',')
    tiers = request.GET.get('tiers').upper().split(',')
    
    # if no ip address set the value as *
    if not ip_addresses[0]:
        ip_addresses[0] = '*'
    else:
        for index in range(len(ip_addresses)):
            ip_addresses[index] = ip_addresses[index].strip()
            
    print(ip_addresses)
    # partner: BAAS, GBR, Intuit
    cvt_partners = []
    for partner in partners:
        if partner == 'INTUIT':
            cvt_partners.append('Intuit')
        else:
            cvt_partners.append(partner)

    instances = {}

    for env in environments:
        aws_assume_role_with_saml()
        aws_assume_role(env)
        filter_values = construct_filter_values(colorstacks, instance_states, ip_addresses, cvt_partners, tiers)
        response = aws_instance_filter(filter_values)
        fmt_response = json.dumps(response, cls=ComplexEncoder)
        instances[env] = format_instances(json.loads(fmt_response))
    return HttpResponse(json.dumps(instances))


def format_instances(instances):
    fmt_instance = {}
    fmt_instances = []

    for reservation in instances['Reservations']:
        instance_id = reservation['Instances'][0]['InstanceId']
        launch_time = reservation['Instances'][0]['LaunchTime']
        private_ipaddress = reservation['Instances'][0]['PrivateIpAddress']
        running_state = reservation['Instances'][0]['State']['Name']

        fmt_instance = {
            'InstanceId': instance_id,
            'LaunchTime': launch_time,
            'PrivateIpAddress': private_ipaddress,
            'State': running_state
            }
        for tag in reservation['Instances'][0]['Tags']:
            if tag['Key'] == 'Partner':
                partner = tag['Value']
                fmt_instance['Partner'] = partner
            if tag['Key'] == 'Environment':
                environment = tag['Value']
                fmt_instance['Environment'] = environment
            if tag['Key'] == 'Name':
                name = tag['Value']
                fmt_instance['Name'] = name
            if tag['Key'] == 'Colorstack':
                colorstack = tag['Value']
                fmt_instance['Colorstack'] = colorstack
            if tag['Key'] == 'Tier':
                tier = tag['Value']
                fmt_instance['Tier'] = tier

        host_name = name[name.index('-') + 1: -1] + instance_id[-5:]
        fmt_instance['HostName'] = host_name

        fmt_instances.append(fmt_instance)

    return fmt_instances


def GetInitData(request):
    orgunit = request.GET.get("orgunit")
    init_data = {
        "partners": "",
        "tiers": ""
    }

    partners = list(Partner.objects.filter(orgunit__name=orgunit).values('name'))
    tiers = list(Tier.objects.filter(orgunit__name=orgunit).values('name'))
    init_data['partners'] = partners
    init_data['tiers'] = tiers

    return HttpResponse(json.dumps(init_data))