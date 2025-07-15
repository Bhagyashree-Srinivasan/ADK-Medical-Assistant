# ADK Medical Assistant

A comprehensive medical consultation assistant built with Google's ADK (Agent Development Kit) that processes audio recordings of medical consultations to generate structured medical documentation.

## 🏥 Overview

The ADK Medical Assistant is an AI-powered system designed to streamline medical documentation workflows. It takes audio recordings of doctor-patient consultations and automatically generates:

- **Transcripts** - Accurate transcriptions of the consultation
- **Medical Templates** - Structured medical forms filled with extracted information
- **Assessment Plans** - Treatment and follow-up recommendations
- **Medical Summaries** - Concise summaries of the consultation
- **Critic Reviews** - Quality assessments to improve patient care

## 🚀 Features

### Core Functionality
- **Audio Processing**: Supports MP3 and WAV audio formats
- **AI Transcription**: Powered by Google's Gemini 2.5 Flash model
- **Parallel Processing**: Multiple agents work simultaneously on different tasks
- **Structured Output**: Generates standardized medical documentation
- **Quality Assurance**: Built-in validation and review mechanisms

### User Interface
- **Streamlit Web App**: Clean, intuitive web interface
- **File Upload**: Drag-and-drop audio file upload
- **Real-time Chat**: Interactive conversation with the medical assistant
- **Session Management**: Persistent conversation sessions

### Technical Features
- **MCP Protocol**: Model Context Protocol for tool integration
- **Modular Design**: Separate agents for different medical tasks
- **Error Handling**: Comprehensive logging and error management
- **Extensible**: Easy to add new agents and capabilities

## 🏗️ Architecture

ADK-Medical-Assistant/
├── .gitignore
├── MedicalAgent/                  # Main application source code
│   ├── __init__.py
│   ├── mcp_server/                # Server component (e.g., Flask/Django)
│   │   ├── __init__.py
│   │   ├── app.py                 # Main server file
│   │   ├── routes.py              # API or web routes
│   │   ├── models.py              # Database models
│   │   ├── static/                # For CSS, JavaScript, images
│   │   │   └── css/
│   │   │       └── style.css
│   │   ├── templates/             # HTML templates
│   │   │   └── index.html
│   │   ├── processing_files/      # Ignored directory for runtime files
│   │   └── processing_files_sample1/ # Ignored directory for sample files
│   └── core/                      # Core logic, helpers, etc.
│       ├── __init__.py
│       └── utils.py
├── data/                          # For raw data, CSVs, etc.
│   └── medical_records.csv
├── docs/                          # Project documentation
│   ├── conf.py
│   └── index.rst
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   └── test_app.py
├── medenv/                        # Python virtual environment (ignored)
│   ├── bin/
│   ├── include/
│   └── lib/
├── README.md                      # Project description
└── requirements.txt               # Project dependencies

## 📋 Prerequisites

- Python 3.12+
- Google Cloud API access with billing account. 

## 🛠️ Installation

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set up environment variables:** Update the `.env` file within the root agent folder (MedicalAgent):
    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    ```

## 🚦 Usage

### Starting the System

1.  **Launch the adk server first and split terminal and launch the streamlit app (Launch the command from root folder):**
    ```bash
    adk api_server
    streamlit run streamlit-app.py
    ```
2.  **Access the agent trace and flow use ADK web, ensure you already have an audio file under uploads (to be done manually). (Launch the command from root folder):** 
```bash
adk web 
```

### Processing Audio Files

1.  **Upload Audio:**
    -   Click "Choose an audio file" in the web interface
    -   Select an MP3 or WAV file of a medical consultation
    -   Click "Upload"
2.  **Start Processing:**
    -   Create a new session in the sidebar
    -   The system will automatically begin processing the uploaded audio
    -   Watch as different agents work on transcription and document generation
3.  **Review Results:**
    -   Generated documents are saved in `MedicalAgent/mcp_server/processing_files/{filename}/`
    -   Each consultation gets its own folder with all generated documents

### Note - 

**To avoid MCP timeout errors**:
Modify the timeout seconds from 5 to 300 code within venv/lib/google/adk/tools/mcp_session_manager.py with the one below - 

      transports = await self._exit_stack.enter_async_context(client)
      # The streamable http client returns a GetSessionCallback in addition to the read/write MemoryObjectStreams
      # needed to build the ClientSession, we limit then to the two first values to be compatible with all clients.
      if isinstance(self._connection_params, StdioConnectionParams):
        session = await self._exit_stack.enter_async_context(
            ClientSession(
                *transports[:2],
                read_timeout_seconds=timedelta(
                    seconds=**300** #self._connection_params.timeout
                ),
            )
        )
