from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import google.auth.exceptions
import os

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'creds/service_account.json'
PARENT_FOLDER_ID = "1W71Ty5GPkeeFm01kkRpJAsYiGzgxiqs2"

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_photo(file_path):
    try:
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)


        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [PARENT_FOLDER_ID]
        }

        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=file_path,
            fields="id"  # Only requesting the file ID in response
        ).execute()

        file_id = file.get('id')

        # Set the permissions to make it shareable
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()

        # Generate the direct link to the file
        file_link = f"https://drive.google.com/uc?id={file_id}&export=download"

        return file_link

    except google.auth.exceptions.GoogleAuthError as auth_error:
        print("Authentication Error:", auth_error)
    except HttpError as http_error:
        print("An error occurred with the API:", http_error)
    except FileNotFoundError:
        print("The file was not found. Please check the file path.")
    except Exception as e:
        print("An unexpected error occurred:", e)
# # Upload the file and print the shareable link
# shareable_link = upload_photo("logic.py")
# print("Shareable link:", shareable_link)
