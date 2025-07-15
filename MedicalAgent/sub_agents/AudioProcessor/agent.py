from google.adk.agents import LlmAgent
#from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from ...utils.custom_adk_patches import CustomMCPToolset as MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
from pathlib import Path
from . import prompt

# IMPORTANT: Dynamically compute the absolute path to your server.py script
PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent.parent.parent / "mcp_server" / "server.py").resolve())

# Create MCP toolset
mcp_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command="python3",
                args=[PATH_TO_MCP_SERVER_SCRIPT],
            )
    )

AudioProcessor = LlmAgent(
    name="AudioProcessor",
    model="gemini-2.0-flash", # This agent primarily uses the tool, but its LLM decides when to use it
    description="This agent handles the transcription and diarization of audio.",
    instruction= """Check if you know the name of the audio file to transcribe, 
    if not request the filename from the user.
    Once you have the filename, fetch it's exact location using the get_audio_file tool.
    Then, use the transcribe_audio tool to transcribe the audio file and delegte back to the calling agent.""",
    tools=[mcp_toolset]  # Add the MCP toolset to the agent
)