from oauthlib.oauth2 import BackendApplicationClient
import urllib.parse
from requests_oauthlib import OAuth2Session
from config import CLIENT_ID, SECRET

# Create authenticated session
oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(CLIENT_ID))
session = OAuth2Session(client=oauth2_client)
session.fetch_token(
    token_url='https://auth.sbanken.no/identityserver/connect/token',
    client_id=urllib.parse.quote(CLIENT_ID),
    client_secret=urllib.parse.quote(SECRET)
)
