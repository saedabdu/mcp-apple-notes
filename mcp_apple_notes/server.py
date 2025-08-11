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
async def create_folder(ctx: Context, folder_name: str, folder_path: str = "") -> str:
    """Create a folder in Apple Notes.
    
    Args:
        folder_name: Name of the folder to create
        folder_path: Optional path where to create the folder (e.g., "Work/Projects"). If empty, creates at root level.
    """
    try:
        folder = await notes_tools.create_folder(folder_name, folder_path)
        return str(folder)
    except ValueError as e:
        # Handle validation errors with clear messages
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        # Handle AppleScript errors with helpful context
        error_msg = str(e)
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error creating folder '{folder_name}' in path '{folder_path}': {str(e)}"
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def read_note_by_name(ctx: Context, note_name: str, folder_name: str) -> str:
    """Read all notes with the given name in the specified folder."""
    try:
        notes = await notes_tools.read_note_by_name(note_name, folder_name)
        
        if not notes:
            return f"No notes found with name '{note_name}' in folder '{folder_name}'"
        
        if len(notes) == 1:
            return f"Found 1 note:\n{str(notes[0])}"
        else:
            result = f"Found {len(notes)} notes with name '{note_name}' in folder '{folder_name}':\n"
            for i, note in enumerate(notes, 1):
                result += f"\n--- Note {i} ---\n"
                result += f"Creation Date: {note['creation_date']}\n"
                result += f"Modification Date: {note['modification_date']}\n"
                result += f"Content:\n{note['body']}\n"
            return result
            
    except Exception as e:
        await ctx.error(f"Error reading note: {str(e)}")
        raise

@mcp.tool()
async def create_note_in_path(ctx: Context, name: str, body: str, folder_path: str) -> str:
    """Create a new note in a nested folder path."""
    try:
        note = await notes_tools.create_note_in_path(name, body, folder_path)
        return str(note)
    except Exception as e:
        await ctx.error(f"Error creating note in path: {str(e)}")
        raise

@mcp.tool()
async def list_notes_by_folder_path(ctx: Context, folder_path: str) -> str:
    """List all notes from a specific folder path."""
    try:
        notes = await notes_tools.list_notes_by_folder_path(folder_path)
        return str(notes)
    except Exception as e:
        await ctx.error(f"Error listing notes by folder path: {str(e)}")
        raise

@mcp.tool()
async def read_note_by_name_in_path(ctx: Context, note_name: str, folder_path: str) -> str:
    """Read all notes with the given name in the specified folder path."""
    try:
        notes = await notes_tools.read_note_by_name_in_path(note_name, folder_path)
        
        if not notes:
            return f"No notes found with name '{note_name}' in folder path '{folder_path}'"
        
        if len(notes) == 1:
            return f"Found 1 note:\n{str(notes[0])}"
        else:
            result = f"Found {len(notes)} notes with name '{note_name}' in folder path '{folder_path}':\n"
            for i, note in enumerate(notes, 1):
                result += f"\n--- Note {i} ---\n"
                result += f"Creation Date: {note['creation_date']}\n"
                result += f"Modification Date: {note['modification_date']}\n"
                result += f"Content:\n{note['body']}\n"
            return result
            
    except Exception as e:
        await ctx.error(f"Error reading note by path: {str(e)}")
        raise



@mcp.tool()
async def get_folder_details(ctx: Context, folder_name: str) -> str:
    """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
    try:
        folder_details = await notes_tools.get_folder_details(folder_name)
        
        # Format the response in a readable way
        result = f"📁 Folder Details: {folder_name}\n"
        result += f"📂 Path: {folder_details.get('path', 'N/A')}\n"
        result += f"📝 Total Notes: {folder_details.get('total_notes', 0)}\n"
        result += f"📁 Total Subfolders: {folder_details.get('total_subfolders', 0)}\n\n"
        
        # Add notes information
        notes = folder_details.get('notes', [])
        if notes:
            result += "📝 Notes:\n"
            for i, note in enumerate(notes, 1):
                result += f"  {i}. {note.get('name', 'N/A')}\n"
                result += f"     Created: {note.get('creation_date', 'N/A')}\n"
                result += f"     Modified: {note.get('modification_date', 'N/A')}\n"
                if note.get('body'):
                    result += f"     Content: {note.get('body', '')[:100]}...\n"
                result += "\n"
        else:
            result += "📝 Notes: None\n\n"
        
        # Add subfolders information
        subfolders = folder_details.get('subfolders', [])
        if subfolders:
            result += "📁 Subfolders:\n"
            for i, subfolder in enumerate(subfolders, 1):
                result += f"  {i}. {subfolder.get('name', 'N/A')} (Path: {subfolder.get('path', 'N/A')})\n"
                result += f"     Notes: {subfolder.get('total_notes', 0)}, Subfolders: {subfolder.get('total_subfolders', 0)}\n\n"
        else:
            result += "📁 Subfolders: None\n\n"
        
        return result
    except Exception as e:
        await ctx.error(f"Error getting folder details: {str(e)}")
        raise

@mcp.tool()
async def get_folder_hierarchy_details(ctx: Context, folder_name: str) -> str:
    """Get folder details with a more robust hierarchical structure."""
    try:
        folder_details = await notes_tools.get_folder_hierarchy_details(folder_name)
        
        # Format the response in a readable way
        result = f"📁 Folder Hierarchy Details: {folder_name}\n"
        result += f"📂 Path: {folder_details.get('path', 'N/A')}\n"
        result += f"📝 Notes Count: {folder_details.get('notes_count', 0)}\n"
        result += f"📁 Subfolders Count: {folder_details.get('subfolders_count', 0)}\n\n"
        
        # Add notes information
        notes = folder_details.get('notes', [])
        if notes:
            result += "📝 Notes:\n"
            for i, note in enumerate(notes, 1):
                result += f"  {i}. {note.get('name', 'N/A')}\n"
                result += f"     Created: {note.get('creation_date', 'N/A')}\n"
                result += f"     Modified: {note.get('modification_date', 'N/A')}\n\n"
        else:
            result += "📝 Notes: None\n\n"
        
        # Add subfolders information
        subfolders = folder_details.get('subfolders', [])
        if subfolders:
            result += "📁 Subfolders:\n"
            for i, subfolder in enumerate(subfolders, 1):
                result += f"  {i}. {subfolder.get('name', 'N/A')} (Path: {subfolder.get('path', 'N/A')})\n"
                result += f"     Notes: {subfolder.get('notes_count', 0)}, Subfolders: {subfolder.get('subfolders_count', 0)}\n\n"
        else:
            result += "📁 Subfolders: None\n\n"
        
        return result
    except Exception as e:
        await ctx.error(f"Error getting folder hierarchy details: {str(e)}")
        raise

@mcp.tool()
async def list_folder_structure(ctx: Context) -> str:
    """List the complete folder structure with hierarchical tree format."""
    try:
        folder_structure = await notes_tools.list_folder_structure()
        
        if not folder_structure:
            return "No folders found in Apple Notes"
        
        # Return filtered AppleScript result
        return f"📁 Apple Notes Folder Structure:\n\n{folder_structure}"
    except Exception as e:
        await ctx.error(f"Error listing folder structure: {str(e)}")
        raise

# Run the server
if __name__ == "__main__":
    mcp.run()
