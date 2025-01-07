import streamlit as st
import os
from Agent import CodingAgent
import subprocess

#Pages title
st.title('Code Chat')
st.write('Welcome to Code Chat! This is a simple chatbot that can help you with your coding questions. Provide a link to your code repository and ask your question. The chatbot will answer your questions using access to the codebase.')

# Sidebar to create new chats
st.sidebar.title("Repository Information")

# Folder inputs
folder_input = st.text_input("Enter folder path", "")

#Check if the user input folder is a valid path and is a directory
def validateFolderPath(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return False
    return True

#Lists all the file names that are stored in the vector database
#Some files are exlcuded based on the file type
def displayFiles():
    fileNames = st.session_state.chatbot.getRagApp().getFileNames()
    st.sidebar.write("Files in the directory:")
    
    for file in fileNames:
        st.sidebar.write(file)

#Function for button on click 
def openInVscode():
    if st.session_state.folder_path:
        # Run the VSCode command using subprocess
        try:
            subprocess.run(["code", st.session_state.folder_path], check=True)
            st.success(f"Opening folder '{st.session_state.folder_path}' in VSCode!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error opening folder: {e}")
        except FileNotFoundError:
            st.error("VSCode is not installed or 'code' command is not in your PATH.")
    else:
        st.error("Please provide a valid folder path.")

#Save the folder path to check if it has been changed
if "folder_path" not in st.session_state:
    st.session_state.folder_path = None

# Save the folder path in a variable if provided
if folder_input and validateFolderPath(folder_input) and st.session_state.folder_path != folder_input:
    st.session_state.folder_path = folder_input
    st.sidebar.write(f"Selected folder path: {st.session_state.folder_path}")
    with st.spinner('Loading Codebase...'):
            chatbot = CodingAgent(st.session_state.folder_path)             
    st.session_state.chatbot = chatbot
    st.sidebar.button("Open in VSCode",on_click=openInVscode)
    displayFiles()
elif folder_input and validateFolderPath(folder_input):
    st.sidebar.write(f"Selected folder path: {st.session_state.folder_path}")
    st.sidebar.button("Open in VSCode",on_click=openInVscode)
    displayFiles()
elif folder_input and not validateFolderPath(folder_input):
    st.sidebar.write("Invalid folder path. Please enter a valid folder path.")
    st.session_state.chatbot = None
else:
    st.sidebar.write("No folder selected yet.")

#Returns the response from the chatbot
def responseGenerator(input_text):
    # Only if st.session_state.chatbot is defined
    if "chatbot" in st.session_state:
        response = st.session_state.chatbot.query(input_text)
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

    # Generate and display the assistant's response
    with st.chat_message("assistant"):
        response = responseGenerator(prompt)  # Get the response
        st.markdown(response)  # Display the response
        st.session_state.messages.append({"role": "assistant", "content": response})  # Save it

