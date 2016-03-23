from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField


class Person(models.Model):
    display_name = models.CharField(max_length=255)
    email_address = models.EmailField()


class FixVersion(models.Model):
    name = models.CharField(max_length=255, null=True)
    release_date = models.DateTimeField(null=True)


class IssueLink(models.Model):
    issuetype = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    summary = models.TextField()
    target = models.CharField(max_length=255)


class Project(models.Model):
    key = models.CharField(max_length=255)
    name = models.CharField(max_length=255)


# Create your models here.
class Test(models.Model):
    creator = EmbeddedModelField('Person', null=True)
    exectype = models.CharField(max_length=255)
    fix_versions = ListField(EmbeddedModelField('FixVersion'))
    funnel = models.TextField()
    jiraid = models.IntegerField(null=True)
    issuelinks = ListField(EmbeddedModelField('IssueLink'))
    issuetype = models.CharField(max_length=255)
    key = models.CharField(max_length=255, primary_key=True)
    summary = models.TextField()
    updated = models.DateTimeField(null=True)
    target = models.CharField(max_length=255)
    result = models.CharField(max_length=255)


class CR(models.Model):
    assignee = EmbeddedModelField('Person', null=True)
    components = ListField()
    creator = EmbeddedModelField('Person', null=True)
    fix_versions = ListField(EmbeddedModelField('FixVersion'))
    issuetype = models.CharField(max_length=255)
    issuelinks = ListField(EmbeddedModelField('IssueLink'))
    resolution = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    summary = models.TextField(null=True)
    jiraid = models.IntegerField(null=True)
    key = models.CharField(max_length=255, primary_key=True)
    keynum = models.IntegerField(null=True)
    # target = ListField() - changed to CharField: keep only one target
    target = models.CharField(max_length=255)
    tests = ListField(EmbeddedModelField('Test'))
    defects = ListField(EmbeddedModelField('CR'))
    project = EmbeddedModelField('Project', null=True)
    epicname = models.CharField(max_length=255, null=True)
    epicsummary = models.TextField(null=True)
    # epic = EmbeddedModelField('CR', null=True)
    priority = models.CharField(max_length=255, null=True)


class Execution(models.Model):
    assignee = EmbeddedModelField('Person', null=True)
    comment = models.TextField()
    creationDate = models.DateTimeField(null=True)
    cycleId = models.FloatField(null=True)
    cycleName = models.CharField(max_length=255)
    executedBy = EmbeddedModelField('Person', null=True)
    executedOn = models.DateTimeField(null=True)
    executionDefects = ListField()
    execId = models.FloatField(primary_key=True)
    testcase = EmbeddedModelField('Test', null=True)
    tckey = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    versionName = models.CharField(max_length=255)
