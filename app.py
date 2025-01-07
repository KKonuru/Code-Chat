import streamlit as st
import os
from Agent import CodingAgent
import subprocess


#On change function that adjusts the temperature when the slider is changed
def tempChange():
    if "chatbot" in st.session_state:
        st.session_state.chatbot.setAgentTemp(st.session_state.agent_temp)
        st.session_state.chatbot.setCodeLLMTemp(st.session_state.code_llm_temp)


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

#Check if the user input folder is a valid path and is a directory
def validateFolderPath(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return False
    return True

#Pages title
st.title('Code Chat')
st.write('Welcome to Code Chat! This is a simple chatbot that can help you with your coding questions. Provide a link to your code repository and ask your question. The chatbot will answer your questions using access to the codebase.')

on = st.toggle("Activate Chatbot Agent Mode")
if on:
    st.write("Chatbot Agent Mode is ON. You can ask questions about the codebase. You can also ask programming related questions and get youtube links to helpful videos.")
else:
    st.write("Chatbot Agent Mode is OFF. You are interacting with the RAG application. You can ask questions about the codebase and general programming questions.")
# Sidebar to create new chats
st.sidebar.title("About Code Chat")
st.sidebar.write("You can interact with either the multi-tool agent or the RAG application. The rag application can answer questions on the codebase and general programming questions. The multi-tool agent can do the functions of the rag application and also answer questions on programming and provide youtube links and wikipedia summaries.")
st.sidebar.write("Check out the repository for more information on the project [here](https://github.com/KKonuru/Code-Chat).")
st.sidebar.title("Settings")
st.sidebar.write("You can change the settings of the chatbot here.")

agent_temp = st.sidebar.slider("Agent LLM Temperature", 0.0, 1.0, 0.05,on_change=tempChange)
st.session_state.agent_temp = agent_temp
code_llm_temp = st.sidebar.slider("Code LLM Temperature", 0.0, 1.0, 0.85,on_change=tempChange)
st.session_state.code_llm_temp = code_llm_temp
st.sidebar.title("Repository Information")

# Folder inputs
folder_input = st.text_input("Enter folder path", "")


#Save the folder path to check if it has been changed
if "folder_path" not in st.session_state:
    st.session_state.folder_path = None

# Save the folder path in a variable if provided
if folder_input and validateFolderPath(folder_input) and st.session_state.folder_path != folder_input:
    st.session_state.folder_path = folder_input
    st.sidebar.write(f"Selected folder path: {st.session_state.folder_path}")
    with st.spinner('Loading Codebase...'):
            chatbot = CodingAgent(st.session_state.folder_path,st.session_state.agent_temp,st.session_state.code_llm_temp)             
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

def ragResponse(input_text):
    if "chatbot" in st.session_state:
        response = st.session_state.chatbot.getRagApp().llmResponse(input_text)
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
        if on:
            response = responseGenerator(prompt)  # Get the response
            st.markdown(response)
        else: 
            response = ragResponse(prompt)
            response = st.write_stream(response)
        st.session_state.messages.append({"role": "assistant", "content": response})  # Save it

