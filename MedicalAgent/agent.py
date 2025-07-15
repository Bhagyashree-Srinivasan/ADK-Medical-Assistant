from google.adk.agents import LlmAgent
from .sub_agents.AudioProcessor.agent import AudioProcessor
from .sub_agents.parallel_processing_agent.agent import parallel_processing_agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path


# IMPORTANT: Dynamically compute the absolute path to your server.py script
PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent / "mcp-server" / "server.py").resolve())

MedicalAgent = LlmAgent(
    name="medical_template_agent",
    description="Overall Coordinating Agent for Medical Audio Transcription, Generating Procesing Files and Communicating with the User.",
    model="gemini-2.0-flash",  # This agent primarily uses the tool, but its LLM decides when to use it
    sub_agents=[AudioProcessor, parallel_processing_agent],
    instruction="""You are a medical assistant agent. Your job is to transcribe medical telephone conversations,
    generate processing files and communicate with the user to fetch the audio file name and communicate with them to answer 
    questions using the processing files generated.

    1. Ask for the audio file name from the user.
    2. Once, you have the audio file name, use the AudioProcessor sub-agent to transcribe the audio file.
    3. After transcription, use the parallel_processing_agent to generate the processing files and ensure all the
    processing files are generated.
    4. Communicate with the user to answer questions using the processing files generated.

    """,
)

root_agent = MedicalAgent