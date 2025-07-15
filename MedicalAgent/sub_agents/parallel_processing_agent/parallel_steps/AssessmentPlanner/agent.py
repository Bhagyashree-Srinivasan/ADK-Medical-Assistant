from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
from .prompt import PLAN_PROMPT

# IMPORTANT: Dynamically compute the absolute path to your server.py script
PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent.parent.parent.parent.parent / "mcp_server" / "server.py").resolve())

# Create MCP toolset
mcp_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command="python3",
                args=[PATH_TO_MCP_SERVER_SCRIPT],
            )
    )

AssessmentPlanner = LlmAgent(
    name="AssessmentPlanner",
    model="gemini-2.0-flash", # This agent primarily uses the tool, but its LLM decides when to use it
    description="Generates the next plan of treatment/ follow-up for the patient",
    instruction= PLAN_PROMPT,  # The prompt that guides the agent's behavior
    tools=[mcp_toolset]  # Add the MCP toolset to access file operations
)