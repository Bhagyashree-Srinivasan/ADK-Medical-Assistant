from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
from .prompt import MEDICAL_TEMPLATE_PROMPT

def find_mcp_server_path():
    """Find the mcp-server directory by searching upward from current file."""
    current_path = Path(__file__).resolve()
    
    # Search upward until we find a directory containing 'mcp-server'
    for parent in current_path.parents:
        mcp_server_path = parent / "mcp_server" / "server.py"
        if mcp_server_path.exists():
            return str(mcp_server_path)
    
    raise FileNotFoundError("Could not find mcp_server/server.py")

# IMPORTANT: Dynamically find the absolute path to your server.py script
PATH_TO_MCP_SERVER_SCRIPT = find_mcp_server_path()



# Create MCP toolset
mcp_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command="python3",
                args=[PATH_TO_MCP_SERVER_SCRIPT],
            )
    )

MedicalTemplate = LlmAgent(
    name="MedicalTemplate",
    model="gemini-2.0-flash", # This agent primarily uses the tool, but its LLM decides when to use it
    description="Agent to fill the medical form template using audio transcript.",
    instruction= MEDICAL_TEMPLATE_PROMPT,  # The prompt that guides the agent's behavior
    tools=[mcp_toolset]  # Add the MCP toolset to access file operations
    #state_variables=["audio_file_path"],  # The agent will use this variable to access the audio file path
    #{audio_file_path} is a placeholder that will be replaced by the actual audio file path in state.
    #tools=[audio_diarization_tool],  # Register the tool to perform audio diarization and transcription
)