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

├── MedicalAgent/ # Main agent system

│ ├── mcp\_server/ # MCP (Model Context Protocol) server

│ │ ├── server.py # Core MCP server implementation

│ │ ├── prompt.py # Transcription prompts

│ │ ├── upload/ # Audio file storage

│ │ └── processing\_files/ # Generated documents storage

│ │ └── {audio\_name}/ # Per-consultation folders

│ │ ├── Transcript.txt

│ │ ├── MedicalTemplate.txt

│ │ ├── AssessmentPlan.txt

│ │ ├── CriticReview.txt

│ │ └── MedicalSummary.txt

│ ├── sub\_agents/ # Specialized processing agents

│ │ ├── AudioProcessor/ # Audio transcription

│ │ └── parallel\_processing\_agent/ # Parallel document generation

│ │ └── parallel\_steps/

│ │ ├── AssessmentPlanner/ # Treatment planning

│ │ ├── Critic/ # Quality review

│ │ └── medical\_template\_agent/

│ │ └── sequence\_steps/

│ │ ├── MedicalTemplate/ # Form filling

│ │ └── TemplateValidator/ # Validation

│ └── utils/ # Utilities and patches

│ └── custom\_adk\_patches.py # Custom ADK extensions

├── streamlit-app.py # Web interface

├── requirements.txt # Python dependencies

└── README.md # This file

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
