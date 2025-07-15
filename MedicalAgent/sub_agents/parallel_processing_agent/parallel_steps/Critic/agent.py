from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
from .prompt import CRITIC_PROMPT

# IMPORTANT: Dynamically compute the absolute path to your server.py script
PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent.parent.parent.parent.parent / "mcp_server" / "server.py").resolve())

# Create MCP toolset
mcp_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command="python3",
                args=[PATH_TO_MCP_SERVER_SCRIPT],
            )
    )

Critic = LlmAgent(
    name="Critic",
    model="gemini-2.0-flash", # This agent primarily uses the tool, but its LLM decides when to use it
    description="Agent that provides the doctor with criticism to improve their patient care capabilities.",
    instruction= CRITIC_PROMPT,  # The prompt that guides the agent's behavior
    tools=[mcp_toolset]  # Add the MCP toolset to access file operations
    #state_variables=["audio_file_path"],  # The agent will use this variable to access the audio file path
    #{audio_file_path} is a placeholder that will be replaced by the actual audio file path in state.
    #tools=[audio_diarization_tool],  # Register the tool to perform audio diarization and transcription
)