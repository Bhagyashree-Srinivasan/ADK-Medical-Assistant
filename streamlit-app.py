"""
Handles the chat interface for uploading audio files and generating processed output files.

This module provides functionality for users to upload audio files through a chat-based interface.
It processes the uploaded audio files and generates corresponding output files based on the 
specified processing logic.

"""

import streamlit as st
import requests
import os
import uuid
import time
import json

#set page config
st.set_page_config(
    page_title="Medical Assistant Agent",
    page_icon="👩‍⚕️⚕️🩺",
    layout="centered"
)

#constants
API_BASE_URL = "http://127.0.0.1:8000"
APP_NAME = "MedicalAgent"


#Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"  # Generate a unique user ID

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

def handle_file_upload(uploaded_file):
    """Handles the file upload and saves it to the mcp_server/upload directory.
    
    Args:
        uploaded_file: The uploaded file from Streamlit's file uploader
        
    Returns:
        str: The filename of the uploaded audio file, or None if upload failed
    """
    if uploaded_file is not None:
        try:
            # Define the upload directory path
            upload_dir = os.path.join("MedicalAgent", "mcp_server", "upload")
            
            # Create the upload directory if it doesn't exist
            os.makedirs(upload_dir, exist_ok=True)
            
            # Get the file extension
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            # Validate file type
            if file_extension not in ['.mp3', '.wav']:
                st.error("Please upload only MP3 or WAV audio files.")
                return None
            
            # Create the file path (keeping original filename)
            file_path = os.path.join(upload_dir, uploaded_file.name)
            
            # Save the uploaded file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Audio file '{uploaded_file.name}' uploaded successfully!")
            
            # Store the filename in session state for automatic passing
            st.session_state.uploaded_filename = uploaded_file.name
            
            # Return just the filename
            return uploaded_file.name
            
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
            return None
    else:
        st.warning("⚠️ No file selected.")
        return None

def create_session():
    """
    Create a new session with the speaker agent.
    
    This function:
    1. Generates a unique session ID based on timestamp
    2. Sends a POST request to the ADK API to create a session
    3. Updates the session state variables if successful
    
    Returns:
        bool: True if session was created successfully, False otherwise
    
    API Endpoint:
        POST /apps/{app_name}/users/{user_id}/sessions/{session_id}
    """
    session_id = f"session-{int(time.time())}"
    response = requests.post(
        f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({})
    )
    
    if response.status_code == 200:
        st.session_state.session_id = session_id
        st.session_state.messages = []
        return True
    else:
        st.error(f"Failed to create session: {response.text}")
        return False

def send_message(message):
    """
    Send a message to the speaker agent and process the response.
    
    This function:
    1. Adds the user message to the chat history
    2. Sends the message to the ADK API
    3. Processes the response to extract text and audio information
    4. Updates the chat history with the assistant's response
    
    Args:
        message (str): The user's message to send to the agent
        
    Returns:
        bool: True if message was sent and processed successfully, False otherwise
    
    API Endpoint:
        POST /run
        
    Response Processing:
        - Parses the ADK event structure to extract text responses
        - Looks for text_to_speech function responses to find audio file paths
        - Adds both text and audio information to the chat history
    """
    if not st.session_state.session_id:
        st.error("No active session. Please create a session first.")
        return False
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Send message to API
    response = requests.post(
        f"{API_BASE_URL}/run",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        })
    )
    
    if response.status_code != 200:
        st.error(f"Error: {response.text}")
        return False
    
    # Process the response
    events = response.json()
    
    # Extract assistant's text response
    assistant_message = None
    audio_file_path = None
    
    for event in events:
        # Look for the final text response from the model
        if event.get("content", {}).get("role") == "model" and "text" in event.get("content", {}).get("parts", [{}])[0]:
            assistant_message = event["content"]["parts"][0]["text"]
    
    # Add assistant response to chat
    if assistant_message:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message, "audio_path": audio_file_path})
    
    return True

# Main UI Components
st.title("Chat with your Medical Assistant")

# Sidebar for session management
with st.sidebar:
    st.header("Session Management")
    
    if st.session_state.session_id:
        st.success(f"Active session: {st.session_state.session_id}")
        if st.button("➕ New Session"):
            create_session()
    else:
        st.warning("No active session")
        if st.button("➕ Create Session"):
            create_session()
    
    st.divider()
    st.caption("This app interacts with the Medical Agent via the ADK API Server.")
    st.caption("Make sure the ADK API Server is running on port 8000.")

# File upload section
st.subheader("📁 Upload Audio File")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose an audio file to process", 
        type=['mp3', 'wav'],
        help="Upload MP3 or WAV audio files for medical consultation processing"
    )

with col2:
    if uploaded_file:
        if st.button("🚀 Upload", type="primary", use_container_width=True):
            filename = handle_file_upload(uploaded_file)
            if filename:
                # Automatically send a message to process the uploaded file
                if st.session_state.session_id:
                    process_message = f"Please process the uploaded audio file: {filename}"
                    send_message(process_message)
                    st.rerun()
                else:
                    st.warning("Please create a session first to process the file.")
    else:
        st.button("🚀 Upload", disabled=True, use_container_width=True, help="Select a file first")

st.divider()

# Chat interface
st.subheader("Conversation")

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])

# Input for new messages
if st.session_state.session_id:  # Only show input if session exists
    user_input = st.chat_input("Type your message...")
    if user_input:
        send_message(user_input)
        st.rerun()  # Rerun to update the UI with new messages
else:
    st.info("👈 Create a session to start chatting")