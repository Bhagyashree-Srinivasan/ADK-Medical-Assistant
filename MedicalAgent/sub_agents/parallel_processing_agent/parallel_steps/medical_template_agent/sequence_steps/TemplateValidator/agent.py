from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
from .prompt import TEMPLATE_VALIDATION_PROMPT

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

TemplateValidator = LlmAgent(
    name="TemplateValidator",
    model="gemini-2.0-flash",
    description="This agent cross checks the filled medical form and validates the information using the audio transcript.",
    instruction=TEMPLATE_VALIDATION_PROMPT,
    tools=[mcp_toolset]
)