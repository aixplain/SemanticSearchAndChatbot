import json
import logging
import os
import requests
from ingestor_api import upload_file
from drive_downloader import download_files_from_drive_folder_link
from urls_air import CREATE_CORPUS_URL, RESET_CORPUS_URL
from auth import fetch_client_credentials_jwt
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent
load_dotenv(os.path.join(BASE_DIR, "secrets.env"), override=True)
CUSTOMER_ID = os.getenv("CUSTOMER_ID")
API_KEY = os.getenv("API_KEY")
CORPUS_ID = os.getenv("CORPUS_ID")

def index_using_drive_link(drive_link, corpus_id=CORPUS_ID):
    files_orig = download_files_from_drive_folder_link(drive_link)

    drive_file_url_template = "https://drive.google.com/file/d/{file_id}/view"
    responses = []
    for fileID, filepath  in files_orig.items():
        file_url = drive_file_url_template.format(file_id=fileID)
        metadata = {"uri": file_url, "filename": filepath.split("/")[-1]}
        response = upload_file(filepath, corpus_id=corpus_id, metadata=metadata, return_doc = True)
        if response.status_code == 200:
            response = response.json()
        responses.append(response)

    with open("responses_indexing.json", "w") as f:
        json.dump(responses, f, indent=4)

    return responses



def _get_create_corpus_json(corpus_name, corpus_description=""):
    """ Returns a create corpus json. """
    corpus = {}
    corpus["name"] = corpus_name
    corpus["description"] = corpus_description

    return json.dumps({"corpus":corpus})

def create_corpus(corpus_name, corpus_description):
    jwt_token = fetch_client_credentials_jwt()
    post_headers = {
        "customer-id": f"{CUSTOMER_ID}",
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.post(
        CREATE_CORPUS_URL,
        data=_get_create_corpus_json(corpus_name, corpus_description),
        verify=True,
        headers=post_headers)

    if response.status_code != 200:
        logging.error("Create Corpus failed with code %d, reason %s, text %s",
                       response.status_code,
                       response.reason,
                       response.text)
        return response, False
    return response, True


def _get_reset_corpus_json():
    """ Returns a reset corpus json. """
    corpus = {}
    corpus["customer_id"] = CUSTOMER_ID
    corpus["corpus_id"] = CORPUS_ID

    return json.dumps(corpus)

def reset_corpus():
    """Reset a corpus.
    Args:
        customer_id: Unique customer ID in vectara platform.
        corpus_id: Corpus ID in vectara platform.
        admin_address: Address of the admin server. e.g., api.vectara.io
        jwt_token: A valid Auth token.

    Returns:
        (response, True) in case of success and returns (error, False) in case of failure.
    """

    jwt_token = fetch_client_credentials_jwt()
    post_headers = {
        "customer-id": f"{CUSTOMER_ID}",
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.post(
        RESET_CORPUS_URL,
        data=_get_reset_corpus_json(),
        verify=True,
        headers=post_headers)

    if response.status_code != 200:
        logging.error("Reset Corpus failed with code %d, reason %s, text %s",
                       response.status_code,
                       response.reason,
                       response.text)
        return response, False
    return response, True