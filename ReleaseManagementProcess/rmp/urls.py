"""DevOpsTools URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_aws import views as AWSviews
from app_f5 import views as F5views
from app_jira import views as Jiraviews
from app_octopus import views as Octoviews
from app_releaseobject import views as ROviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nopage/', F5views.nopage),
    path('f5/test/', F5views.test),
    path('f5/state/', F5views.GetF5State),
    path('f5/pool/remove/', F5views.RemovePool),
    path('f5/pool/state/', F5views.GetPoolState),
    path('f5/pool/action/', F5views.PoolAction),
    path('f5/member/state/', F5views.GetMemberState),
    path('aws/test/', AWSviews.test),
    path('aws/instance/', AWSviews.ListInstance),
    path('aws/instance/filter/', AWSviews.FilterInstance),
    path('aws/instance/initdata/', AWSviews.GetInitData),
    path('jira/test/', Jiraviews.test),
    path('jira/project/sync/', Jiraviews.SyncJiraProjects),
    path('jira/fixversion/sync/', Jiraviews.SyncJiraFixVersions),
    path('jira/fixversion/get/', Jiraviews.GetJiraFixVersions),
    path('jira/issue/get/', Jiraviews.GetJiraIssues),
    path('octo/test/', Octoviews.test),
    path('octo/space/sync/', Octoviews.SyncOctoSpaces),
    path('octo/environment/sync/', Octoviews.SyncOctoEnvironments),
    path('octo/project/sync/', Octoviews.SyncOctoProjects),
    path('octo/channel/get/', Octoviews.GetOctoProjectChannelEnvironments),
    path('octo/release/get/', Octoviews.GetOctoProjectReleases),
    path('octo/deployment/get/', Octoviews.GetOctoProjectReleaseDeployments),
    path('octo/state/get/', Octoviews.GetOctoProjectReleaseDeploymentStates),
    path('releaseobject/test/', ROviews.test),
    path('releaseobject/', ROviews.LoadReleaseObject),
    path('releaseobject/create/', ROviews.CreateReleaseObject),
    path('releaseobject/get/', ROviews.GetLastReleaseObject)
]
