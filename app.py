import streamlit as st
import os
import numpy as np
import pandas as pd
st.title('Code Chat')
st.write('Welcome to Code Chat! This is a simple chatbot that can help you with your coding questions. Provide a link to your code repository and ask your question. The chatbot will try to help you with your query.')

#Sidebar to create new chats
st.sidebar.title("New Chat")
st.sidebar.write("Create a new chat with the chatbot")
st.sidebar.write("Provide a link to your code repository and ask your question")


uploaded_files = st.file_uploader(
    "Choose code files", accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    

#Here invoke rag app to get response
def response_generator(input_text):
    response = input_text
    for word in response.split():
        yield word + " "

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask away!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt))
    st.session_state.messages.append({"role": "assistant", "content": response})
