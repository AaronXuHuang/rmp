from bs4 import BeautifulSoup
from datetime import date, datetime
from django.http import HttpResponse
from django.shortcuts import render
from urllib.parse import urlparse
import base64
import boto3
import configparser
import json
import os
import re
import requests
import xml.etree.ElementTree as ET

# Create your views here.

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def test(request):
    error_msg = aws_saml()
    if error_msg:
        return HttpResponse(error_msg)
    
    result = aws_credential('qa')
    print(result)
    return HttpResponse(result)

    instance_list = aws_cmd('qa')
    return HttpResponse(json.dumps(instance_list, cls=ComplexEncoder))

    return render(request, 'AWS.html')


def aws_saml():
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

    print(awsroles)

    client = boto3.client('sts')
    token = client.assume_role_with_saml(
        RoleArn=role_arn,
        PrincipalArn=principal_arn,
        SAMLAssertion=assertion,
        DurationSeconds=duration)

    home = os.path.expanduser ('~')
    filename = home + awsconfigfile

    config = configparser.RawConfigParser()
    config.read(filename)

    awsprofile = default_profile
    if not config.has_section(awsprofile):
        config.add_section(awsprofile)

    config.set(awsprofile, 'output', outputformat)
    config.set(awsprofile, 'region', region)
    config.set(awsprofile, 'aws_access_key_id', token['Credentials']['AccessKeyId'])
    config.set(awsprofile, 'aws_secret_access_key', token['Credentials']['SecretAccessKey'])
    config.set(awsprofile, 'aws_session_token', token['Credentials']['SessionToken'])
    config.set(awsprofile, 'aws_security_token', token['Credentials']['SessionToken'])

    with open(filename, 'w+') as configfile:
        config.write(configfile)

    return None


def aws_credential(env):
    credential = {}
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
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn = 'arn:aws:iam::' + accountIdMap[accountMap[env]] + ':role/bos-' + accountMap[env] + '-deploy-devops',
        RoleSessionName = env
    )

    credential['AccessKeyId'] = response['Credentials']['AccessKeyId']
    credential['SecretAccessKey'] = response['Credentials']['SecretAccessKey']
    credential['SessionToken'] = response['Credentials']['SessionToken']

    return credential


def set_windows_env_variable(credential):
    
    return False

def aws_cmd(env):
    client = boto3.client('ec2')
    response = client.describe_instances()
    return False