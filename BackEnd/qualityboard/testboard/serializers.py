from rest_framework import serializers
from models import Test, Person, IssueLink, FixVersion, CR, Execution, Project

__author__ = 'jukim'


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('display_name', 'email_address')


class FixVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FixVersion
        fields = ('name', 'release_date')


class IssueLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueLink
        fields = ('issuetype', 'key', 'priority', 'status', 'summary', 'target')


class TestSerializer(serializers.ModelSerializer):
    creator = PersonSerializer()
    issuelinks = serializers.ListField(child=IssueLinkSerializer())
    fix_versions = serializers.ListField(child=FixVersionSerializer())

    class Meta:
        model = Test
        fields = ('creator', 'exectype', 'fix_versions', 'funnel', 'jiraid', 'issuetype', 'issuelinks',
                  'key', 'summary', 'updated', 'target', 'result')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('key', 'name')


class ExecutionSerializer(serializers.HyperlinkedModelSerializer):
    assignee = PersonSerializer()
    executedBy = PersonSerializer()
    testcase = TestSerializer()

    class Meta:
        model = Execution
        fields = (
            'assignee',
            'comment',
            'creationDate',
            'cycleId',
            'executionDefects',
            'cycleName',
            'executedBy',
            'executedOn',
            'execId',
            'status',
            'versionName',
            'testcase',
            'tckey'
        )


class CRSerializer(serializers.HyperlinkedModelSerializer):
    assignee = PersonSerializer()
    fix_versions = serializers.ListField(child=FixVersionSerializer())
    issuelinks = serializers.ListField(child=IssueLinkSerializer())
    creator = PersonSerializer()
    tests = serializers.ListField(child=TestSerializer())
    project = ProjectSerializer()

    class Meta:
        model = CR
        fields = (
            'epicname',
            'epicsummary',
            'assignee',
            'components',
            'creator',
            'fix_versions',
            'issuetype',
            'issuelinks',
            'resolution',
            'status',
            'summary',
            'jiraid',
            'key',
            'target',
            'tests',
            'defects',
            'project',
            'keynum',
            'priority'
        )
