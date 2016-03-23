# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from testboard.models import Test, IssueLink, Person, FixVersion, CR, Execution, Project
from testboard.oauthclient import OAUTHCLIENT
import requests
import requests.exceptions
from serializers import TestSerializer, IssueLinkSerializer, PersonSerializer, FixVersionSerializer, \
    CRSerializer, ExecutionSerializer, ProjectSerializer
from datetime import datetime, timedelta


@api_view(['GET'])
def test_all(request, format=None):
    """
    Get all tests.
    """
    if request.method == 'GET':
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def cr_all(request, format=None):
    """
    Get all stories
    """
    if request.method == 'GET':
        cr = CR.objects.all()
        # return Response(len(cr))

        serializer = CRSerializer(cr, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def cr_detail(request, key, format=None):
    """
    Get CR detail
    """
    if request.method == 'GET':
        cr = CR.objects.filter(key=key)
        serializer = CRSerializer(cr, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def test_list(request, target, format=None):
    """
    List tests for the requested target.
    """
    if request.method == 'GET':
        tests = Test.objects.filter(target=target)
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def test_detail(request, key, format=None):
    """
    Get test detail
    """
    if request.method == 'GET':
        test = Test.objects.filter(key=key)
        serializer = TestSerializer(test, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def cr_list(request, target, project, format=None):
    """
    List stories for the requested target.
    """
    if request.method == 'GET':
        cr = CR.objects.filter(target=target, key__startswith=project + '-').order_by('keynum')
        serializer = CRSerializer(cr, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def person_all(request, format=None):
    """
    Get all persons
    """
    if request.method == 'GET':
        creators = Person.objects.all()
        serializer = PersonSerializer(creators, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def fix_version_all(request, format=None):
    """
    Get all fix versions
    """
    if request.method == 'GET':
        # fixversions = FixVersion.objects.all().order_by('-release_date')
        fixversions = FixVersion.objects.filter(release_date__gte=datetime.now() - timedelta(1)).order_by('-release_date')
        serializer = FixVersionSerializer(fixversions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def fix_version_tribe(request, tribe, format=None):
    """
    Get fix versions by Project
    :param request:
    :param format:
    :return:
    """
    if request.method == 'GET':
        if tribe == 'Hotfix':
            fixversions = FixVersion.objects.filter(name__endswith=tribe).order_by('-release_date')
        else:
            fixversions = FixVersion.objects.filter(name__startswith=tribe).order_by('-release_date')

        serializer = FixVersionSerializer(fixversions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def issuelinks_all(request, format=None):
    """
    Get all issue links
    """
    if request.method == 'GET':
        issuelinks = IssueLink.objects.all()
        serializer = IssueLinkSerializer(issuelinks, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def execution_list(request, version, project, format=None):
    """
    List executions for the requested versionName
    """
    if request.method == 'GET':
        executions = Execution.objects.filter(versionName=version, tckey__startswith=project).order_by('execId')
        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def execution_all(request, format=None):
    """
    Get All execution records
    """
    if request.method == 'GET':
        executions = Execution.objects.all()
        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def project_all(request, format=None):
    """
    Get All project names
    :param request:
    :param format:
    :return:
    """
    if request.method == 'GET':
        projects = Project.objects.all().order_by('key')
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def request_verification_bypass(request, env, email):
    """
    request email verification by-pass
    :param email:
    :param env:
    :param request:
    :return:
    """
    if request.method == 'POST':
        oauth_client = OAUTHCLIENT(env)
        token = oauth_client.get_token()
        content = {'message': email + " has been requested for By-pass to " + env}

        if 'access_token' in token:
            if env == 'qa32':
                host = 'http://qajb101.p2pcredit.local/users/email/'
            elif env == 'stg':
                host = 'http://stage-api-proxy-A.vip.c1.stg/users/email/'
            elif env == 'qa20':
                host = 'http://np97.c1.dev/users/email/'

            # create header with access token
            headers = {'Authorization': token['token_type'] + ' ' + token['access_token']}

            # request email verification by-pass with access-token
            response = requests.get(
                    host + email,
                    headers=headers
            )

            response_json = response.json()

            # build response message
            if response_json['email_exists']:
                if response_json['activation_key'] == "":
                    content['result'] = "VERIFIED"
                    content['message'] = email + " is auto-verified on " + env
                else:
                    content['result'] = "NOT VERIFIED"
                    content['message'] = email + " is not verified yet on " + env + \
                                         ". Please verify your email by clicking 'Verify Email' link."
            else:
                content['result'] = "USER NOT FOUND"
                content['message'] = email + " is not found on " + env

            response_status = status.HTTP_200_OK
            content['response'] = response_json
        else:
            content['result'] = str(token)
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            content['response'] = 'No token generated'

        return Response(content, status=response_status)
