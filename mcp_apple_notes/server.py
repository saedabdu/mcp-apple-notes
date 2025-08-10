import asyncio
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import Context, FastMCP

from .tools.notes_tools import NotesTools

# Initialize FastMCP server
mcp = FastMCP(name="mcp-apple-notes")

# Initialize tools
notes_tools = NotesTools()

@mcp.tool()
async def list_notes(ctx: Context) -> str:
    """List all Apple Notes with metadata."""
    try:
        notes = await notes_tools.list_notes()
        return str(notes)
    except Exception as e:
        await ctx.error(f"Error listing notes: {str(e)}")
        raise

@mcp.tool()
async def list_folders(ctx: Context) -> str:
    """List all Apple Notes folders."""
    try:
        folders = await notes_tools.list_folders()
        return str(folders)
    except Exception as e:
        await ctx.error(f"Error listing folders: {str(e)}")
        raise

@mcp.tool()
async def create_note(ctx: Context, name: str, body: str, folder_name: str = "Notes") -> str:
    """Create a new Apple Note with specified name, body, and folder."""
    try:
        note = await notes_tools.create_note(name, body, folder_name)
        return str(note)
    except Exception as e:
        await ctx.error(f"Error creating note: {str(e)}")
        raise

@mcp.tool()
async def list_notes_by_folder(ctx: Context, folder_name: str) -> str:
    """List all notes from a specific folder."""
    try:
        notes = await notes_tools.list_notes_by_folder(folder_name)
        return str(notes)
    except Exception as e:
        await ctx.error(f"Error listing notes by folder: {str(e)}")
        raise

@mcp.tool()
async def create_folder(ctx: Context, folder_name: str) -> str:
    """Create a new Apple Notes folder."""
    try:
        folder = await notes_tools.create_folder(folder_name)
        return str(folder)
    except Exception as e:
        await ctx.error(f"Error creating folder: {str(e)}")
        raise

@mcp.tool()
async def read_note_by_name(ctx: Context, note_name: str, folder_name: str = None) -> str:
    """Read a note's content by name and optional folder."""
    try:
        note = await notes_tools.read_note_by_name(note_name, folder_name)
        return str(note)
    except Exception as e:
        await ctx.error(f"Error reading note: {str(e)}")
        raise

# Run the server
if __name__ == "__main__":
    mcp.run()
