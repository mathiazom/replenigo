from os import environ
from oauthlib.oauth2 import BackendApplicationClient
import urllib.parse
from requests_oauthlib import OAuth2Session

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

CLIENTID = environ['CLIENTID']
SECRET = environ['SECRET']

# Create authenticated session
oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(CLIENTID))
session = OAuth2Session(client=oauth2_client)
session.fetch_token(
    token_url='https://auth.sbanken.no/identityserver/connect/token',
    client_id=urllib.parse.quote(CLIENTID),
    client_secret=urllib.parse.quote(SECRET)
)
