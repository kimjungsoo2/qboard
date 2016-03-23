from urllib2 import Request, urlopen, URLError
from urllib import urlencode

payload = {
    'zqlQuery': 'project = BOR',
    'maxRecords': 1
}

endpoint = 'https://jira.prosper.com/rest/zapi/latest/zql/executeSearch'
request = Request(endpoint + '?' + urlencode(payload))


# request = Request('https://jira.prosper.com/rest/zapi/latest/zql/executeSearch')
# request.add_data(json.dumps(payload))
request.add_header('Authorization', 'Basic cWFfYXV0b190ZXN0QHByb3NwZXIuY29tOldlbGNvbWUx')

try:
    response = urlopen(request)
    kittens = response.read()
    print kittens
except URLError, e:
    print 'No kittez. Got an error code:', e