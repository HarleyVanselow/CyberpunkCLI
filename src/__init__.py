import json
import os
from apiclient import discovery
from google.oauth2 import service_account
SERVICE = None
SHEET_ID = ''
with open('credentials.json') as creds:
        creds = json.load(creds)
        SHEET_ID = creds['sheet_id']
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    secret_file = os.path.join(os.getcwd(), 'client_secret.json')
    credentials = service_account.Credentials.from_service_account_file(
        secret_file, scopes=scopes)
    SERVICE = discovery.build('sheets', 'v4', credentials=credentials)
except Exception as e:
    print(e)