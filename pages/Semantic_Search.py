import streamlit as st
from ingestor_api import query
from utils import parse_search_response

st.set_page_config(page_title="RAG DEMO")

st.title("_RAG DEMO_")
st.subheader("Internal documents search and QA")

if "files" not in st.session_state:
    st.session_state["files"] = []

if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "collection_name" not in st.session_state:
    st.session_state["collection_name"]="Combined Documents"



st.subheader("Question Answering")
with st.form(key='Search Document',clear_on_submit=True):
    question = st.text_input("Enter your Query", placeholder="Type in your question...", label_visibility="collapsed")      
    limit = st.number_input("Number of relevant results",value=10)
    
    SearchButton = st.form_submit_button(label = 'Search')


if SearchButton:
    st.write(f"**Question:** {question}")
    response_search = query(question, num_results=limit)
    st.session_state["files"], summary = parse_search_response(response_search)
    st.session_state["responses"].append(response_search)

    st.write("Documents used for answering:")
    for i, file in enumerate(st.session_state["files"]):
        with st.expander(f"**Search result number {i+1}:**"):
            st.write(f"file: [{file['file_name']}]({file['file_url']})")
            # st.write(f"file_name: {file['file_name']}")
            st.write(f"{file['text']}")

    # response = answer_query(st.session_state["collection_name"], question)
    # answer=response.json()["message"]
    st.write(f"**Summary of the top results:** {summary}")
    st.write("Done!")
    