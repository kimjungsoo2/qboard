import getopt
import os
import sys

__author__ = 'jukim'


def cal_repeat(total, offset):
    if total % offset > 0:
        return (total / offset) + 1
    else:
        return total / offset


def main(argv):
    query = ''
    days = ''
    offset = 1000  # this is offset limit to be used to make a chunk of size of data to poll.

    try:
        opts, args = getopt.getopt(argv, "j:z:d:")
    except getopt.GetoptError:
        print 'import.py -z <query string> : import test executions from Zephyr'
        print 'import.py -j <query string> : import JIRA tickets'
        print 'import.py -d <number of days> : import JIRA and Zephyr data for the last number of days'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-z':
            query = arg
        elif opt == '-j':
            query = arg
        elif opt == '-d':
            days = arg

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qualityboard.settings')

    from testboard.jira_service import JIRAREST, Execution
    from django.core.wsgi import get_wsgi_application

    get_wsgi_application()

    # ================================
    # query executions
    # exe = Execution.objects.filter(execId='237722')

    # for e in exe:
    #    print e.execId, e.testcase
    #    e.delete()  # delete the record
    # exit(0)
    # ================================

    # pull text execution records
    if opt == '-z' or opt == '-d':
        rest = JIRAREST(
                api='https://jira.prosper.com/rest/zapi/latest/zql/executeSearch'
        )

        if opt == '-d':
            query = 'executionDate >= -' + days + 'd OR creationDate >= -' + days + 'd'

        payload = {
            'zqlQuery': query,
            'maxRecords': -1
        }

        # get total number of queried issues
        content = rest.query(payload, -1)

        if 'totalCount' in content:
            print "Total number of records to poll:", content['totalCount']

            # query the records in a chunk of 1000 - jql limits to 1000 records return
            for r in range(cal_repeat(content['totalCount'], offset)):
                payload = {
                    'zqlQuery': query,
                    'maxRecords': offset,
                    'offset': r * offset
                }

                content = rest.query(payload, r * offset)

                # ----------------------------------------
                # Verification
                # ----------------------------------------
                # index = 1
                # for e in content['executions']:
                #    print index, e['issueKey'], e['id'], e['cycleName']
                #    index += 1

                rest.save_exec_db(content)
        else:
            print "Zero records";

    if opt == '-j' or opt == '-d':
        rest = JIRAREST(
                api="https://jira.prosper.com/rest/api/2/search"
        )

        if opt == '-d':
            query = 'created >= -' + days + 'd OR updated >= -' + days + 'd'

        payload = {
            'jql': query,
            'maxResults': -1
        }

        # get total number of quried issues
        content = rest.query(payload, -1)
        print "Total number of records to poll:", content['total']

        # query the records in a chunk of 1000 - jql limits to 1000 records return
        for r in range(cal_repeat(content['total'], offset)):
            payload = {
                'jql': query,
                'maxResults': offset,
                'startAt': r * offset
            }

            content = rest.query(payload, r * offset)

            # ----------------------------------------
            # Verification
            # ----------------------------------------
            # index = 1
            # for issue in content['issues']:
            #    print index, issue['key']
            #    index += 1

            rest.save_cr_db(content)


if __name__ == '__main__':
    if len(sys.argv[1:]) > 0:
        main(sys.argv[1:])
    else:
        print 'import.py -z <query string> : import test executions from Zephyr'
        print 'import.py -j <query string> : import JIRA tickets'
        print 'import.py -d <number of days> : import JIRA and Zephyr data for the last number of days'
