from oauthlib.oauth2 import BackendApplicationClient
import urllib.parse
from requests_oauthlib import OAuth2Session


def create_auth_session(client_id: str, client_secret: str):
    oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(client_id))
    session = OAuth2Session(client=oauth2_client)
    session.fetch_token(
        token_url='https://auth.sbanken.no/identityserver/connect/token',
        client_id=urllib.parse.quote(client_id),
        client_secret=urllib.parse.quote(client_secret)
    )
    return session
