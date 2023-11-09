import streamlit as st
import os
from ingestor_api import upload_file
from corpora_utils import reset_corpus, index_using_drive_link

st.set_page_config(page_title="RAG DEMO")

if "collections" not in st.session_state:
    st.session_state["collections"] = set()
    st.session_state["collection_ids"] = {}

if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

st.header("Document Management Dashboard")

st.subheader("Reset Corpus/ Database")
st.warning("This action will clear all files inside the corpus")
clear = st.button("Clear")
if clear:
    response, success = reset_corpus()
    if success:
        st.success("Corpus emptied")


st.subheader("Upload files from a Google Drive folder")
with st.form(key='Drive ingestion',clear_on_submit=False):
    ingest_drive_link = st.text_input("Enter drive folder link", value="")
    ingestButton = st.form_submit_button(label = 'Ingest')

if ingestButton:
    responses = index_using_drive_link(ingest_drive_link)


st.subheader("Upload Files Directly")
st.write("Upload files here")
uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)

os.makedirs("uploaded_files", exist_ok=True)

# save files locally
for file in uploaded_files:
    if file.name not in st.session_state["uploaded_files"]:
        st.session_state["uploaded_files"].append(file.name)# = file.getvalue()
        file_path = os.path.join("./uploaded_files", file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
        response = upload_file(file_path)
        if response.status_code == 200:
            response = response.json()
            st.write("Indexed", file.name)
