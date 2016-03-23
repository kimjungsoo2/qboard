import datetime
import json
import sys
import traceback
from operator import itemgetter
from urllib import urlencode
from urllib2 import Request, urlopen, URLError

from django.db import models

from testboard.models import Test, Person, FixVersion, IssueLink, CR, Execution, Project

__author__ = 'jukim'


class JIRAREST(object):
    # This class handles with requesting end point API of JIRA to
    # retrieve data from JIRA system.
    # It functionality extends to save retrieved data to internal DB (mongoDB).

    def __init__(self, api):
        self.endpoint = api
        self.result = ''
        self.JSESSIONID = '200EB7B78E4F94FAF04CA8A445618F92'
        self.atlassian_token = 'AG87-S37R-QM8W-6VWE|e79bf6a10719a691b0a21e38ab7675abd9b4b5a6|lin'

    def query(self, payload, start_at):
        """

        :param start_at:
        :param payload:
        :rtype: object
        """
        request = Request(self.endpoint + '?' + urlencode(payload))
        # request.add_header('Authorization', 'Basic ' + self.token)
        request.add_header('Cookie',
                           'JSESSIONID=' + self.JSESSIONID + '; atlassian.xsrf.token=' + self.atlassian_token)

        print '\nEncoded URL:', request.get_full_url()

        if start_at == -1:
            print "\nGetting total number of JIRA query..."
        else:
            print "\nStarted polling records from JIRA starting at", start_at, "..."

        try:
            response = urlopen(request)
            self.result = response.read()
            response.close

            if start_at == -1:
                print "Finished getting the total!\n"
            else:
                print "Finished polling data from JIRA!\n"

            # print self.result

            if len(self.result) > 0:
                return json.loads(self.result)
            else:
                return {}
        except URLError, e:
            print 'No results. Got an error code:', e
            pass

    @staticmethod
    def save_exec_db(result):
        count = 1
        total = len(result['executions'])

        for execution in result['executions']:
            try:
                exe, created = Execution.objects.get_or_create(execId=execution['id'])

                assignee, created = Person.objects.get_or_create(email_address=execution['assigneeUserName'])
                assignee.display_name = execution['assigneeDisplay']
                assignee.save()
                exe.assignee = assignee

                exe.components = execution['comment']

                if execution['creationDate']:
                    exe.creationDate = restruct_time(execution['creationDate'])

                exe.cycleId = execution['cycleId']
                exe.cycleName = execution['cycleName']

                tester, created = Person.objects.get_or_create(email_address=execution['executedByUserName'])
                tester.display_name = execution['executedByDisplay']
                tester.save()
                exe.executedBy = tester

                if execution['executedOn']:
                    exe.executedOn = restruct_time(execution['executedOn'])

                # get associated defects
                for defect in execution['executionDefects']:
                    # capture Project object
                    p, created = Project.objects.get_or_create(key=execution['projectKey'])
                    p.save()

                    d, created = CR.objects.get_or_create(key=defect['defectKey'])
                    d.status = defect['defectStatus']
                    d.summary = defect['defectSummary']

                    # save captured project
                    d.project = p
                    d.save()

                    if defect['defectKey'] not in exe.executionDefects:
                        exe.executionDefects.append(defect['defectKey'])
                    else:
                        index = exe.executionDefects.index(defect['defectKey'])
                        exe.executionDefects[index] = defect['defectKey']

                # exe.testcase = execution['issueKey'] - don't save test case string, instead, trying to
                # link to embedded test object
                exe.status = execution['status']['name']
                exe.versionName = execution['versionName']

                # map test case
                tc, created = Test.objects.get_or_create(key=execution['issueKey'])
                tc.jiraid = execution['issueId']  # we need to capture jiraid of Test
                tc.summary = execution['issueSummary']
                tc.save()

                # link test object
                exe.testcase = tc
                exe.tckey = tc.key

                exe.save()
            except Exception as e:
                print execution
                print e, traceback.print_exc()
                exit(0)

            sys.stdout.write('\r')
            sys.stdout.write("Saving Execution Results to MongoDB..." + "{0:.0f}".format(float(count * 100 / total)) +
                             "% - " + str(count) + '/' + str(total))
            sys.stdout.flush()
            count += 1

        print "\ncomplete"

    @staticmethod
    def save_cr_db(result):
        crlist = ('Story', 'Production Bug', 'Defect', 'Task', 'Sub-Task', 'Epic')
        count = 1
        total = len(result['issues'])

        for issue in result['issues']:
            fields = issue['fields']

            # save to mongoDB
            try:
                if 'issuetype' in fields.keys():
                    if fields['issuetype']['name'] in crlist:
                        # first get object by jiraid, if exists, compare key. if different, delete old record
                        try:
                            obj = CR.objects.get(jiraid=issue['id'])

                            # delete old object because key has changed.  we cannot simply update key because
                            # it is primary key for the record
                            # after delete the old object, create new object with new key value
                            if obj.key != issue['key']:
                                obj.delete()
                                obj, created = CR.objects.get_or_create(key=issue['key'])
                        except models.ObjectDoesNotExist:
                            # create new object with new key value
                            obj, created = CR.objects.get_or_create(key=issue['key'])
                    elif fields['issuetype']['name'] == 'Test':
                        obj, created = Test.objects.get_or_create(key=issue['key'])
                    else:
                        obj = None

                if obj:
                    obj.keynum = int(''.join(c for c in issue['key'] if c.isdigit())) # capture key number only
                    obj.jiraid = issue['id']  # we need to capture jiraid of CR

                    if fields['issuetype']['name'] in crlist:
                        if fields['assignee']:
                            a, created = Person.objects.get_or_create(email_address=fields['assignee']['emailAddress'])
                            a.display_name = fields['assignee']['displayName']
                            a.save()
                            obj.assignee = a
                        else:
                            obj.assignee = None

                        obj.status = fields['status']['name']

                        if 'components' in fields.keys():
                            obj.components = fields['components']

                    if fields['issuetype']['name'] == 'Test':
                        if fields['customfield_11217']:
                            obj.exectype = fields['customfield_11217']['value']
                        else:
                            obj.exectype = ''

                        if fields['customfield_12212']:
                            obj.funnel = fields['customfield_12212']['value']
                        else:
                            obj.funnel = ''

                        obj.updated = fields['updated']

                    c, created = Person.objects.get_or_create(email_address=fields['creator']['emailAddress'])
                    c.display_name = fields['creator']['displayName']
                    c.save()
                    obj.creator = c

                    for ver in fields['fixVersions']:
                        f, created = FixVersion.objects.get_or_create(name=ver['name'])

                        if 'releaseDate' in ver.keys():
                            f.release_date = ver['releaseDate']

                        f.save()

                        if f not in obj.fix_versions:
                            obj.fix_versions.append(f)

                    # filter fix versions not archived, then if it has more than 1 dictionary,
                    # sort by release data and get the recent release date.  Otherwise, fitered dictionary
                    # could be BACKLOG with no releaseDate specified.  Therefore, just get the dict.
                    if len(fields['fixVersions']) > 1:
                        # filtered_dict = list(filter(lambda d: d['archived'] in [False], fields['fixVersions']))
                        filtered_dict = list(filter(lambda d: d['name'] not in ['BACKLOG'], fields['fixVersions']))

                        if len(filtered_dict) > 0:
                            if len(filtered_dict) > 1:
                                sorted_dict = sorted(filtered_dict, key=itemgetter('releaseDate'))
                                obj.target = sorted_dict.pop()['name']
                            else:
                                obj.target = filtered_dict.pop()['name']
                    elif len(fields['fixVersions']) > 0:
                        obj.target = fields['fixVersions'][0]['name']

                    # issue type
                    obj.issuetype = fields['issuetype']['name']

                    # capture project name and save project model
                    p, created = Project.objects.get_or_create(key=fields['project']['key'])
                    p.name = fields['project']['name']
                    p.save()
                    obj.project = p

                    for issuelink in fields['issuelinks']:
                        if 'inwardIssue' in issuelink.keys():
                            inward, created = IssueLink.objects.get_or_create(key=issuelink['inwardIssue']['key'])
                            inward.issuetype = issuelink['inwardIssue']['fields']['issuetype']['name']

                            if 'priority' in issuelink['inwardIssue']['fields']:
                                inward.priority = issuelink['inwardIssue']['fields']['priority']['name']

                            inward.status = issuelink['inwardIssue']['fields']['status']['name']
                            inward.summary = issuelink['inwardIssue']['fields']['summary']

                            # retrieve target version of the linked issue
                            try:
                                cr_detail = CR.objects.get(key=inward.key)
                                inward.target = cr_detail.target
                            except models.ObjectDoesNotExist:
                                pass

                            inward.save()

                            if inward not in obj.issuelinks:
                                obj.issuelinks.append(inward)
                            else:
                                # if issuelink exists in the Listfield
                                # simply update it
                                index = obj.issuelinks.index(inward)
                                obj.issuelinks[index] = inward

                            # add tests
                            if obj.issuetype in crlist:
                                if inward.issuetype == 'Test':
                                    try:
                                        test = Test.objects.get(key=inward.key)

                                    except models.ObjectDoesNotExist:
                                        test = None

                                    if test:
                                        if test not in obj.tests:
                                            obj.tests.append(test)
                                        else:
                                            # update
                                            index = obj.tests.index(test)
                                            obj.tests[index] = test

                            # link to associated story
                            elif obj.issuetype == 'Test':
                                if inward.issuetype in crlist:
                                    try:
                                        cr = CR.objects.get(key=inward.key)

                                    except models.ObjectDoesNotExist:
                                        cr = None

                                    if cr:
                                        if obj not in cr.tests:
                                            cr.tests.append(obj)
                                        else:
                                            # update
                                            index = cr.tests.index(obj)
                                            cr.tests[index] = obj

                                            # save story
                                            cr.save()

                        if 'outwardIssue' in issuelink.keys():
                            outward, created = IssueLink.objects.get_or_create(key=issuelink['outwardIssue']['key'])
                            outward.issuetype = issuelink['outwardIssue']['fields']['issuetype']['name']

                            if 'priority' in issuelink['outwardIssue']['fields'].keys():
                                outward.priority = issuelink['outwardIssue']['fields']['priority']['name']

                            outward.status = issuelink['outwardIssue']['fields']['status']['name']
                            outward.summary = issuelink['outwardIssue']['fields']['summary']

                            # retrieve target version of the linked issue
                            try:
                                cr_detail = CR.objects.get(key=outward.key)
                                outward.target = cr_detail.target
                            except models.ObjectDoesNotExist:
                                pass

                            outward.save()

                            if outward not in obj.issuelinks:
                                obj.issuelinks.append(outward)
                            else:
                                # if issuelink exists in the Listfield
                                # simply update it
                                index = obj.issuelinks.index(outward)
                                obj.issuelinks[index] = outward

                            # add tests
                            if obj.issuetype in crlist:
                                if outward.issuetype == 'Test':
                                    try:
                                        test = Test.objects.get(key=outward.key)
                                    except models.ObjectDoesNotExist:
                                        test = None

                                    if test:
                                        if test not in obj.tests:
                                            obj.tests.append(test)
                                        else:
                                            index = obj.tests.index(test)
                                            obj.tests[index] = test
                            elif obj.issuetype == 'Test':
                                # link to associated story
                                if outward.issuetype in crlist:
                                    try:
                                        cr = CR.objects.get(key=outward.key)

                                    except models.ObjectDoesNotExist:
                                        cr = None

                                    if cr:
                                        if obj not in cr.tests:
                                            cr.tests.append(obj)
                                        else:
                                            index = cr.tests.index(obj)
                                            cr.tests[index] = obj

                                            # save story
                                            cr.save()

                    if fields['resolution']:
                        obj.resolution = fields['resolution']['name']
                    else:
                        obj.resolution = ''

                    if 'summary' in fields.keys():
                        obj.summary = fields['summary']

                    if ('priority' in fields.keys()) and fields['priority']:
                        obj.priority = fields['priority']['name']

                    # if current object is Epic, save epic name
                    if 'customfield_10912' in fields.keys():
                        obj.epicname = fields['customfield_10912']

                    else:
                        # for regular CR, link Epic CR
                        if 'customfield_10911' in fields.keys():
                            try:
                                epic = CR.objects.get(key=fields['customfield_10911'])
                                obj.epicname = epic.epicname
                                obj.epicsummary = epic.summary
                            except models.ObjectDoesNotExist:
                                pass

                    obj.save()
            except Exception as e:
                print '\n', issue['id'], issue['key']
                print e, traceback.print_exc()
                exit(0)

            sys.stdout.write('\r')
            sys.stdout.write("Saving CR(s) to MongoDB..." + "{0:.0f}".format(float(count * 100 / total)) + "% - " +
                             str(count) + '/' + str(total))
            sys.stdout.flush()
            count += 1

        print "\ncomplete"


def restruct_time(str_time):
    struct_time = datetime.datetime.strptime(str_time, "%d/%b/%y")
    formated_time = datetime.datetime.strftime(struct_time, "%Y-%m-%d %H:%M:%S")
    return formated_time
