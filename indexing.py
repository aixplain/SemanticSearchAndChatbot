import json
from ingestor_api import upload_file
from drive_downloader import download_files_from_drive_folder_link

drive_link = None # Your public drive link here

if drive_link:
    files_orig = download_files_from_drive_folder_link(drive_link)

    drive_file_url_template = "https://drive.google.com/file/d/{file_id}/view"
    responses = []
    for fileID, filepath  in files_orig.items():
        file_url = drive_file_url_template.format(file_id=fileID)
        metadata = {"uri": file_url, "filename": filepath.split("/")[-1]}
        response = upload_file(filepath, metadata=metadata, return_doc = True)
        if response.status_code == 200:
            response = response.json()
        responses.append(response)

    with open("responses_indexing.json", "w") as f:
        json.dump(responses, f, indent=4)
else:
    print("Please enter a public drive link!")