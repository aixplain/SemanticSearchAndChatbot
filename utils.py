
def parse_search_response(response):
    response = response.json()
    results = response['responseSet'][0]
    files = []
    for i in range(len(results["response"])):
        chunk = results['response'][i]
        data = chunk["text"]
        doc_ind = chunk["documentIndex"]
        doc = results["document"][doc_ind]
        metadata = doc["metadata"]
        url = "Uploaded directly by user"
        for field in metadata:
            if field["name"]=="uri":
                url = field["value"]
                break
        file_name = doc["id"]
        files.append({"text": data, "file_url": url, "file_name": file_name})
    summary = results["summary"][0]["text"]
    if not summary:
        summary = results["summary"][0]["statusDetail"]
    return files, summary

def append_content(messages, files):
    search_prompts = f"""
            Use only the following content in the conversation ahead:
            **{{}}**
            """.format(files)
    new_system_message = [
        {
            "role": "system",
            "content": search_prompts
        }
    ]
    return messages.append(new_system_message)


def doc_directory(baselink, collection_name):
    return baselink+"/"+collection_name.replace(" ", "_")
