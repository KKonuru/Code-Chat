import streamlit as st
import os
from main import codeChat
# Page title and instructions
st.title('Code Chat')
st.write('Welcome to Code Chat! This is a simple chatbot that can help you with your coding questions. Provide a link to your code repository and ask your question. The chatbot will try to help you with your query.')

# Sidebar to create new chats
st.sidebar.title("Repository Information")

# Folder selection
folder_input = st.text_input("Enter folder path", "")

def validate_folder_path(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return False
    return True
def draw_directory_tree():
    fileNames = st.session_state.chatbot.getFileNames()
    st.sidebar.write("Files in the directory:")
    for file in fileNames:
        st.sidebar.write(file)

if "folder_path" not in st.session_state:
    st.session_state.folder_path = None
# Save the folder path in a variable if provided
if folder_input and validate_folder_path(folder_input) and st.session_state.folder_path != folder_input:
    st.session_state.folder_path = folder_input
    st.sidebar.write(f"Selected folder path: {st.session_state.folder_path}")
    with st.spinner('Loading Codebase...'):
            chatbot = codeChat(folder_input)
    st.session_state.chatbot = chatbot
    draw_directory_tree()
elif folder_input and validate_folder_path(folder_input):
    st.sidebar.write(f"Selected folder path: {st.session_state.folder_path}")
    draw_directory_tree()
elif folder_input and not validate_folder_path(folder_input):
    st.sidebar.write("Invalid folder path. Please enter a valid folder path.")
    st.session_state.chatbot = None
else:
    st.sidebar.write("No folder selected yet.")



def response_generator(input_text):
    #Only if st.session_state.chatbot is defined
    if "chatbot" in st.session_state:
        response = st.session_state.chatbot.llmResponse(input_text)
    else:
        response = "The chatbot is not initialized yet. Please select a folder path."
    return response

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
        # Here you can integrate your RAG system for generating responses
        response = st.write_stream(response_generator(prompt))
    st.session_state.messages.append({"role": "assistant", "content": response})
