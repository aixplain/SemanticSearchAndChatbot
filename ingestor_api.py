import requests
import json
import os
from urls_air import UPLOAD_URL, QUERY_URL
from pathlib import Path

from dotenv import load_dotenv
BASE_DIR = Path(__file__).parent
load_dotenv(os.path.join(BASE_DIR, "secrets.env"), override=True)

CUSTOMER_ID = os.getenv("CUSTOMER_ID")
API_KEY = os.getenv("API_KEY")
CORPUS_ID = os.getenv("CORPUS_ID")

def upload_file(file_path, corpus_id=CORPUS_ID, metadata=None, return_doc: bool = True):
    params = {
        "c": CUSTOMER_ID,
        "o": corpus_id,
    }
    optional_params = {
        "d": return_doc,
    }

    file_name = file_path.split("/")[-1]
    files = {
        "file": (file_name, open(file_path, "rb")),
    }
    if metadata is not None:
        files["doc_metadata"] = (None, json.dumps(metadata), "application/json")

    headers = {
        "x-api-key": API_KEY
    }
    response = requests.post(UPLOAD_URL, params=params, data=optional_params, files=files, headers=headers)
    # Check the response status code
    if response.status_code == 200:
        print("File uploaded and indexed successfully.")
        # with open("response.json", "w") as f:
        #     json.dump(response,f)
    else:
        print(f"Error {response.status_code}: {response.text}")
    return response


def query(query: str, num_results=10, int_lambda=0.025):
    api_key_header = {
        "customer-id": CUSTOMER_ID,
        "x-api-key": API_KEY
    }
    data_dict = {
        "query": [
                    {
                        "query": query,
                        "start": 0,
                        "num_results": num_results,
                        "contextConfig": {
                            "charsBefore": 0,
                            "charsAfter": 0,
                            "sentencesBefore": 4,
                            "sentencesAfter": 4,
                            "startTag": "\n", #"%START_SNIPPET%",
                            "endTag": "\n", #"%END_SNIPPET%"
                        },
                        "corpus_key": [
                            {
                                "customer_id": CUSTOMER_ID,
                                "corpus_id": CORPUS_ID,
                                # "semantics": 0,
                                "metadataFilter": "",
                                "lexicalInterpolationConfig": {
                                    "lambda": int_lambda
                                },
                                "dim": []
                            }
                        ],
                        "summary": [
                            {
                            "maxSummarizedResults": 5,
                            "responseLang": "eng",
                            "summarizerPromptName": "vectara-summary-ext-v1.2.0" #summarizer name
                            }
                        ]
                    }
            ]
        }
    payload = json.dumps(data_dict)
    response = requests.post(
        QUERY_URL,
        data=payload,
        verify=True,
        headers=api_key_header)
    return response
