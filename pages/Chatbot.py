import os
import openai
import streamlit as st
from datetime import date
from ingestor_api import query
from utils import parse_search_response
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
load_dotenv(os.path.join(BASE_DIR, "secrets.env"), override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="RAG DEMO")

st.title("_RAG DEMO_")
st.subheader("Internal process documents search and chat")

if "collection_name" not in st.session_state:
    st.session_state["collection_name"]="Combined Documents"

# chatbot
if "messages" not in st.session_state:
    st.session_state['today'] = date.today()
    system_prompt = f"""
        Reply back in the same language that you receive the query.
        For any question with adverbs of time, the reference would be the today's date.
        If you need a refrence for date, today's date is {st.session_state['today']}.
        Please do not continue any conversation about sensitive topics such as racism, flirting, hate speech, etc. No need to mention this at the begining of the conversation.
    """

    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "How can I help you?"}]
    st.session_state["airlin_avatar"] = "https://icones.pro/wp-content/uploads/2021/02/icone-utilisateur-rouge.png"
    st.session_state["user_avatar"] = "https://icones.pro/wp-content/uploads/2021/02/icone-utilisateur-rouge.png" 

for msg in st.session_state.messages:
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.chat_message(msg["role"], avatar=st.session_state["user_avatar"]).write(msg["content"])
        else:
            st.chat_message(msg["role"], avatar=st.session_state["airlin_avatar"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar=st.session_state["user_avatar"]).write(prompt)

    # search document based on user prompt
    reference_chunks_limit = 5
    response_search = query(prompt, num_results=reference_chunks_limit)
    relevant_chunks, _ = parse_search_response(response_search)
    chunks = ""
    for i, chunk in enumerate(relevant_chunks):
        chunks += f"Document {i+1}:\r\n\r\nfile_name:\r\n\r\n" + chunk["file_name"] + "\r\n\r\n" + "file_url:\r\n\r\n" + chunk["file_url"] + chunk["text"] + "\r\n\r\n"
    
    search_prompts = f"""
        Use only the following content in the conversation ahead:
        **{chunks}**
        Only if any of the documents above was used in your response, specify the file_name and file_url at the end of your response as reference in seprate lines with following format:
        Reference:\n
        file_name (file_url)
        if none of the documnets were used do not include the reference.
        do not show repeated reference if they are the same.
        """
    st.session_state.messages.append({"role": "system", "content": search_prompts})

    response = openai.ChatCompletion.create(model="gpt-4", messages=st.session_state.messages)
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.chat_message("assistant", avatar=st.session_state["airlin_avatar"]).write(msg.content)

    # Find the last 'system' role and remove to reduce the token size
    for i in reversed(range(len(st.session_state.messages))):
        if st.session_state.messages[i]["role"] == "system":
            del st.session_state.messages[i]
            break