import requests
import requests.auth
import requests.exceptions


class OAUTHCLIENT(object):

    def __init__(self, env):

        if env == 'stg':
            self.client_id = '1665defd303a41e6b8dcc9c29a88dd23'
            self.client_secret = '75126a4b66e74d4da9bdf3a84d876046'
        else:
            self.client_id = 'prosperPublicSite'
            self.client_secret = 'xYuklmasdklop'

        self.host = ''

        if env == 'qa32':
            self.host = 'http://qajb101.p2pcredit.local/security/oauth/token'
        elif env == 'stg':
            self.host = 'http://stage-api-proxy-A.vip.c1.stg/security/oauth/token'
        elif env == 'qa20':
            self.host = 'http://np97.c1.dev/security/oauth/token'

    def get_token(self):
        client_auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        post_data = {
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(
                self.host,
                auth=client_auth,
                data=post_data
            )

            token_json = response.json()

            return token_json
        except requests.exceptions.RequestException as e:
            return e
