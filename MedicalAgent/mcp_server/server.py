import asyncio
import json
import logging
import os
import shutil
from pathlib import Path

import mcp.server.stdio
from dotenv import load_dotenv

# ADK Tool Imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Fetch the transcription prompt
from prompt import TRANSCRIPTION_PROMPT
from google.genai import types
from google import genai

load_dotenv()

# --- Logging Setup ---
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "mcp_server_activity.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="w"),
    ],
)


def get_audio_file(filename: str) -> dict:
    """Gets the specified audio file from the upload directory.
    
    Args:
        filename (str): The audio filename (e.g., "CAR0002.mp3")
    
    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              'audio_file_path' (str), and 'filename' (str) if successful.
    """
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), "upload")
        
        if not os.path.exists(upload_dir):
            return {
                "success": False,
                "message": "Upload directory not found",
                "audio_file_path": "",
                "filename": ""
            }

        file_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"Audio file '{filename}' not found in upload directory",
                "audio_file_path": "",
                "filename": ""
            }
        
        # Validate it's an audio file
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in ['.mp3', '.wav']:
            return {
                "success": False,
                "message": f"Invalid audio format: {file_extension}. Only .mp3 and .wav are supported.",
                "audio_file_path": "",
                "filename": ""
            }
        
        file_size = os.path.getsize(file_path)
        logging.info(f"Audio file found: {filename} ({file_size} bytes)")
        
        return {
            "success": True,
            "message": f"Audio file found: {filename}",
            "audio_file_path": file_path,
            "filename": filename
        }

    except Exception as e:
        logging.error(f"Error retrieving audio file: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error retrieving audio file: {e}",
            "audio_file_path": "",
            "filename": ""
        }


def transcribe_audio_file(audio_file_path: str) -> dict:
    """Transcribes an audio file and saves the transcript to processing_files directory.
    
    Args:
        audio_file_path (str): The path to the audio file to transcribe.
        
    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              and 'transcript_file_path' (str) if successful.
    """
    if not audio_file_path or not os.path.exists(audio_file_path):
        return {
            "success": False,
            "message": f"Audio file not found at path: {audio_file_path}",
            "transcript_file_path": ""
        }

    try:
        # Validate it's an audio file
        file_extension = Path(audio_file_path).suffix.lower()
        if file_extension not in ['.mp3', '.wav']:
            return {
                "success": False,
                "message": f"Unsupported audio format: {file_extension}. Only .mp3 and .wav are supported.",
                "transcript_file_path": ""
            }

        # Get audio filename (e.g., "CAR0002" from "CAR0002.mp3")
        audio_filename = Path(audio_file_path).stem

        # Create processing_files/CAR0002 directory if it doesn't exist
        processing_dir = os.path.join(os.path.dirname(__file__), "processing_files", audio_filename)
        os.makedirs(processing_dir, exist_ok=True)

        # Save as Transcript.txt
        transcript_file_path = os.path.join(processing_dir, "Transcript.txt")

        #Transcription Logic
        client = genai.Client()
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()

        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=[
                TRANSCRIPTION_PROMPT,
                types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type='audio/mp3',
                )
            ]
        )
        transcript = response.text
        
        # Save transcript to file
        with open(transcript_file_path, 'w', encoding='utf-8') as f:
            f.write(transcript)

        logging.info(f"Audio file transcribed: {audio_file_path} -> {transcript_file_path}")
        
        return {
            "success": True,
            "message": f"Audio transcribed successfully and saved to {audio_filename}/Transcript.txt",
            "transcript_file_path": transcript_file_path
        }

    except Exception as e:
        logging.error(f"Error transcribing audio file: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error transcribing audio file: {e}",
            "transcript_file_path": ""
        }


def save_processing_file(file_category: str, contents: str, audio_filename: str) -> dict:
    """Saves content to a specific file category in the processing directory.
    
    Args:
        file_category (str): The file category. Must be one of:
                            'CriticReview', 'MedicalTemplate', 'AssessmentPlan', 'MedicalSummary'
        contents (str): The content to save to the file.
        audio_filename (str): The audio filename (e.g., "CAR0002") to create the directory.
        
    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              and 'file_path' (str) if successful.
    """
    if not audio_filename or not audio_filename.strip():
        return {
            "success": False,
            "message": "Audio filename cannot be empty.",
            "file_path": ""
        }
    
    # Valid file categories
    valid_categories = ['CriticReview', 'MedicalTemplate', 'AssessmentPlan', 'MedicalSummary']
    
    if not file_category or file_category not in valid_categories:
        return {
            "success": False,
            "message": f"Invalid file category. Must be one of: {', '.join(valid_categories)}",
            "file_path": ""
        }

    if contents is None:
        contents = ""  # Allow empty content

    try:
        # Create processing_files/CAR0002 directory if it doesn't exist
        processing_dir = os.path.join(os.path.dirname(__file__), "processing_files", audio_filename.strip())
        os.makedirs(processing_dir, exist_ok=True)

        # Generate filename (e.g., AssessmentPlan.txt)
        filename = f"{file_category}.txt"
        file_path = os.path.join(processing_dir, filename)
        
        # Save content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contents)

        file_size = len(contents.encode('utf-8'))
        logging.info(f"{file_category} file saved: {audio_filename}/{filename} ({file_size} bytes)")
        
        return {
            "success": True,
            "message": f"{file_category} saved successfully to {audio_filename}/{filename} ({file_size} bytes)",
            "file_path": file_path
        }

    except Exception as e:
        logging.error(f"Error saving {file_category} file: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error saving {file_category} file: {e}",
            "file_path": ""
        }


def read_processing_file(file_category: str, audio_filename: str) -> dict:
    """Reads a specific file category from the processing directory.
    
    Args:
        file_category (str): The file category. Must be one of:
                            'CriticReview', 'MedicalTemplate', 'AssessmentPlan', 'MedicalSummary', 'Transcript'
        audio_filename (str): The audio filename (e.g., "CAR0002") to locate the directory.
        
    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              'file_path' (str), and 'content' (str) if successful.
    """
    if not audio_filename or not audio_filename.strip():
        return {
            "success": False,
            "message": "Audio filename cannot be empty.",
            "file_path": "",
            "content": ""
        }
    
    # Valid file categories (including Transcript)
    valid_categories = ['CriticReview', 'MedicalTemplate', 'AssessmentPlan', 'MedicalSummary', 'Transcript']
    
    if not file_category or file_category not in valid_categories:
        return {
            "success": False,
            "message": f"Invalid file category. Must be one of: {', '.join(valid_categories)}",
            "file_path": "",
            "content": ""
        }

    try:
        processing_dir = os.path.join(os.path.dirname(__file__), "processing_files", audio_filename.strip())
        
        if not os.path.exists(processing_dir):
            return {
                "success": False,
                "message": f"Processing directory not found: processing_files/{audio_filename}",
                "file_path": "",
                "content": ""
            }

        # Generate filename (e.g., AssessmentPlan.txt or Transcript.txt)
        filename = f"{file_category}.txt"
        file_path = os.path.join(processing_dir, filename)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"{file_category} file not found: {audio_filename}/{filename}",
                "file_path": "",
                "content": ""
            }
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_size = os.path.getsize(file_path)
        logging.info(f"{file_category} file read: {audio_filename}/{filename} ({file_size} bytes)")
        
        return {
            "success": True,
            "message": f"{file_category} file read successfully: {audio_filename}/{filename} ({file_size} bytes)",
            "file_path": file_path,
            "content": content
        }

    except UnicodeDecodeError as e:
        logging.error(f"Error reading {file_category} file (encoding issue): {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error reading {file_category} file - encoding issue: {e}",
            "file_path": "",
            "content": ""
        }
    except Exception as e:
        logging.error(f"Error reading {file_category} file: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error reading {file_category} file: {e}",
            "file_path": "",
            "content": ""
        }


# --- MCP Server Setup ---
logging.info(
    "Creating MCP Server instance for AUDIO AND FILE HANDLING..."
)  # Changed print to logging.info
app = Server("Audio Processing MCP Server")

# Wrap database utility functions as ADK FunctionTools
ADK_AUDIO_TOOLS = {
    #"upload_audio_file": FunctionTool(func=upload_audio_file),
    "get_audio_file": FunctionTool(func=get_audio_file),
    "transcribe_audio_file": FunctionTool(func=transcribe_audio_file),
    "read_processing_file": FunctionTool(func=read_processing_file),
    "save_processing_file": FunctionTool(func=save_processing_file),
}


@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes."""
    logging.info(
        "MCP Server: Received list_tools request."
    )  # Changed print to logging.info
    mcp_tools_list = []
    for tool_name, adk_tool_instance in ADK_AUDIO_TOOLS.items():
        if not adk_tool_instance.name:
            adk_tool_instance.name = tool_name

        mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_instance)
        logging.info(  # Changed print to logging.info
            f"MCP Server: Advertising tool: {mcp_tool_schema.name}, InputSchema: {mcp_tool_schema.inputSchema}"
        )
        mcp_tools_list.append(mcp_tool_schema)
    return mcp_tools_list


@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
    """MCP handler to execute a tool call requested by an MCP client."""
    logging.info(
        f"MCP Server: Received call_tool request for '{name}' with args: {arguments}"
    )  

    if name in ADK_AUDIO_TOOLS:
        adk_tool_instance = ADK_AUDIO_TOOLS[name]
        try:
            adk_tool_response = await adk_tool_instance.run_async(
                args=arguments,
                tool_context=None,  
            )
            logging.info( 
                f"MCP Server: ADK tool '{name}' executed. Response: {adk_tool_response}"
            )
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            logging.error(
                f"MCP Server: Error executing ADK tool '{name}': {e}", exc_info=True
            )  # Changed print to logging.error, added exc_info
            error_payload = {
                "success": False,
                "message": f"Failed to execute tool '{name}': {str(e)}",
            }
            error_text = json.dumps(error_payload)
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        logging.warning(
            f"MCP Server: Tool '{name}' not found/exposed by this server."
        ) 
        error_payload = {
            "success": False,
            "message": f"Tool '{name}' not implemented by this server.",
        }
        error_text = json.dumps(error_payload)
        return [mcp_types.TextContent(type="text", text=error_text)]


# --- MCP Server Runner ---
async def run_mcp_stdio_server():
    """Runs the MCP server, listening for connections over standard input/output."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logging.info(
            "MCP Stdio Server: Starting handshake with client..."
        )  
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        logging.info(
            "MCP Stdio Server: Run loop finished or client disconnected."
        )  


if __name__ == "__main__":
    logging.info(
        "Launching AUDIO PROCESSING MCP Server via stdio..."
    )  
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        logging.info(
            "\nMCP Server (stdio) stopped by user."
        )  
    except Exception as e:
        logging.critical(
            f"MCP Server (stdio) encountered an unhandled error: {e}", exc_info=True
        )  
    finally:
        logging.info(
            "MCP Server (stdio) process exiting."
        )



