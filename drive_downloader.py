# import the required libraries
import pickle
import os.path
import io
import shutil
import os

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


def get_google_creds():
    # Define the SCOPES. If modifying it,
    # delete the token.pickle file.
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = None
    # The file token.pickle stores the 
    # user's access and refresh tokens. It is
    # created automatically when the authorization 
    # flow completes for the first time.

    # Check if file token.pickle exists
    if os.path.exists('./token.pickle'):
        # Read the token from the file and 
        # store it in the variable creds
        with open('./token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials are available, 
    # request the user to log in.
    if not creds or not creds.valid:
        # If token is expired, it will be refreshed,
        # else, we will request a new one.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the access token in token.pickle 
        # file for future usage
        with open('./token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def download_file_with_id(drive, fId, fname):
    # File url format: https://drive.google.com/file/d/1KPLjYnsxKJpsAaGD00k5Is5qn_J2BKD7/view
    fileRequest = drive.files().get_media(fileId=fId)
    fh = io.BytesIO()
    try:
        downloader = MediaIoBaseDownload(fh, fileRequest)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        # fh.seek(0)
        # fhContents = fh.read()

        fh.seek(0)
        # Write the received data to the file
        save_path = os.path.join("./saved_drive_files")
        os.makedirs(save_path, exist_ok=True)
        save_file_path = os.path.join(save_path, fname)
        with open(save_file_path, 'wb') as f:
            shutil.copyfileobj(fh, f)

        print(f"File Downloaded in {save_path}")
        return save_file_path
    except HttpError as error:
        print(F'An error occurred: {error}')

def download_files_from_drive_folder_link(url):
    # https://drive.google.com/drive/folders/19JW-GAiIbVmpfOdXaaAaye3TEBIXENa16

    folderIDDriveLink = url.split("/")[-1]#'19JW-GAiIbVmpfOcXCAJye3TEBIXENa16'

    creds= get_google_creds()
    # Connect to the API service
    drive = build('drive', 'v3', credentials=creds)

    # request a list of first N files or 
    # folders with name and id from the API.
    folderId = drive.files().list(q = f"'{folderIDDriveLink}' in parents", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # Now, using the folder ID gotten above, we get all the files from
    # that particular folder

    filenames = []
    file_paths = []
    file_ids = []
    for f in range(0, len(folderIdResult)):
        fId = folderIdResult[f].get('id')
        fname = folderIdResult[f].get('name')
        filenames.append(fname)
        file_ids.append(fId)
        save_file_path = download_file_with_id(drive, fId, fname)
        file_paths.append(save_file_path)
    return dict(zip(file_ids, file_paths))

# filenames, file_ids=download_files_from_drive_folder_link("https://drive.google.com/drive/folders/19JW-GAiIbVmpfOcXCAJye3TEBIXENa16")

# print(filenames)
# print(file_ids)
