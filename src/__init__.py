import json
import os
from apiclient import discovery
from google.oauth2 import service_account
import os
SHEET_ID = os.getenv('SHEET_ID')
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
account = json.loads(os.getenv('SHEET_ACCOUNT'))
credentials = service_account.Credentials.from_service_account_info(
    account, scopes=scopes)
SERVICE = discovery.build('sheets', 'v4', credentials=credentials)
TABLE = {}