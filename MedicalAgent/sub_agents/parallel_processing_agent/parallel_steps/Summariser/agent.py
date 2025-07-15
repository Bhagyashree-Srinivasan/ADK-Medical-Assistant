from google.adk.agents import LlmAgent
from . import prompt
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path


PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent.parent.parent.parent.parent / "mcp_server" / "server.py").resolve())

# Create MCP toolset
mcp_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command="python3",
                args=[PATH_TO_MCP_SERVER_SCRIPT],
            )
    )

Summariser = LlmAgent(
    name="Summariser",
    model="gemini-2.0-flash", # This agent primarily uses the tool, but its LLM decides when to use it
    description="This agent generates patient summaries from the medical form template.",
    instruction= prompt.SUMMARY_PROMPT,  # The prompt that guides the agent's behavior
    tools = [mcp_toolset],  # The agent will use this variable to access the audio file path
    #{audio_file_path} is a placeholder that will be replaced by the actual audio file path in state.
    #tools=[audio_diarization_tool],  # Register the tool to perform audio diarization and transcription
 
)