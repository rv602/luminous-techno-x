import os
import time
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# Google Sheets API scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Firebase Realtime Database URL and API key
FIREBASE_URL = os.getenv("FIREBASE_URL")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Authenticate and get Google Sheets credentials
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# Function to update Google Sheets
def update_google_sheet(spreadsheet_id, range_name, new_values):
    creds = authenticate()
    url_update = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}?valueInputOption=USER_ENTERED'
    body = {
        "range": range_name,
        "majorDimension": "ROWS",
        "values": new_values
    }
    
    update_response = requests.put(url_update, json=body, headers={'Authorization': f'Bearer {creds.token}'})
    
    if update_response.status_code == 200:
        print("Data updated successfully:", update_response.json())
    else:
        print("Failed to update data:", update_response.content)

# Function to fetch data from Firebase
def fetch_firebase_data():
    response = requests.get(FIREBASE_URL)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data
        else:
            print("Firebase data is empty.")
            return None
    else:
        print(f"Failed to fetch data from Firebase. Status code: {response.status_code}")
        return None

# Main loop to check for changes and update Google Sheets
def main():
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    RANGE_NAME = 'Sheet1!A2:D10'
    
    last_data = None  # To store the last fetched data

    while True:
        current_data = fetch_firebase_data()

        if current_data is None:
            print("No data to update. Skipping iteration...")
        elif current_data != last_data:
            print("Data has changed. Updating Google Sheets...")
            # Transform current_data to match the structure expected by Google Sheets
            try:
                new_values = [[row['column1'], row['column2'], row['column3']] for row in current_data]
                update_google_sheet(SPREADSHEET_ID, RANGE_NAME, new_values)
                last_data = current_data  # Update last_data to current_data
            except KeyError as e:
                print(f"Error in data format: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        time.sleep(3)  # Sleep for 3 seconds before checking again

if __name__ == "__main__":
    main()