import asyncio
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from .tools.notes_tools import NotesTools

# Initialize FastMCP server
mcp = FastMCP(name="mcp-apple-notes")

# Initialize tools
notes_tools = NotesTools()



@mcp.tool()
async def create_note(
    ctx: Context,
    name: str = Field(..., description="Note title wrapped in <h1> tags (e.g., '<h1>My Note Title</h1>')"),
    body: str = Field(
        ...,
        description="Note body content with appropriate HTML formatting (e.g., '<p>Content here</p>'). For proper spacing between two sections, use <br>."
    ),
    folder_path: str = Field(default="Notes", description="Target folder path (e.g., 'Work' or 'Work/Projects/2024'). Defaults to 'Notes'")
) -> str:
    """Create a new note with specified name and content.
    
    🎨 **Supported HTML:** <h1-h6>, <b><i><u>, <p><div><br>, <ul><ol><li>, <table>, <a>
    ✅ **Best Practices:** Use semantic HTML, add <br> tags for spacing, avoid CSS styles
    📁 **Folders:** Root level or nested paths (up to 5 levels deep)
    ⚠️ **Limitations:** No special chars in name, no complex CSS/JS
    
    💡 **Example:**
    name: "<h1>Project Report</h1>"
    body: "<p>Status: <b>In Progress</b></p><br><ul><li>Task 1</li></ul>"
    
    Args:
        name: Note title wrapped in <h1> tags
        body: Note body content with HTML formatting
        folder_path: Target folder path (default: "Notes")
    """
    try:
        # Import validation utils for title validation
        from .applescript.validation_utils import ValidationUtils
        
        # Validate the title content in the name parameter
        ValidationUtils.validate_html_title_content(name)
        
        # Combine name (title) and body into complete HTML content with <br> spacing
        combined_content = name + "<br>" + body
        note = await notes_tools.create_note("note", combined_content, folder_path)
        return str(note)
    except ValueError as e:
        # Handle validation errors with clear messages
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        await ctx.error(f"Error creating note: {str(e)}")
        raise

@mcp.tool()
async def create_folder(
    ctx: Context, 
    folder_name: str = Field(..., description="Name of the folder to create (1-128 chars, no < > : \" | ? *)"),
    folder_path: str = Field(default="", description="Optional nested path (e.g., 'Work/Projects'). If empty, creates at root level. Max 5 levels deep.")
) -> str:
    """Create a folder in Apple Notes.
    
    📁 **Features:**
    - Creates folders at root level or nested paths (up to 5 levels deep)
    - Unicode and emoji support for international characters
    - Duplicate name detection and comprehensive validation
    
    ⚠️ **Validation:**
    - Max 128 characters, no special chars: < > : " | ? *
    - Parent paths must exist, prevents duplicates
    
    Args:
        folder_name: Name of the folder to create
        folder_path: Optional path where to create the folder (empty for root level)
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
async def read_note(
    ctx: Context,
    note_id: str = Field(..., description="Primary key ID of the note to read (e.g., 'p1308')"),
    folder_path: str = Field(default="Notes", description="Folder path where the note should be located for verification (default: 'Notes')")
) -> str:
    """Read a note by its primary key ID with folder path verification.
    
    🔍 **Security Features:**
    - Verifies note exists in specified folder path
    - Uses primary key ID for precise identification
    - Returns full note content with metadata
    
    📄 **Output:**
    - Note name, ID, folder, creation/modification dates
    - Full note content (title + body)
    - Status and read method information
    
    Args:
        note_id: Primary key ID of the note to read
        folder_path: Folder path for verification (default: "Notes")
    """
    try:
        note_data = await notes_tools.read_note(note_id, folder_path)
        
        # Format the response
        result = f"Note Content:\n"
        result += f"Note Name: {note_data.get('name', 'N/A')}\n"
        result += f"Note ID: {note_data.get('note_id', 'N/A')}\n"
        result += f"Folder: {note_data.get('folder', 'N/A')}\n"
        result += f"Creation Date: {note_data.get('creation_date', 'N/A')}\n"
        result += f"Modification Date: {note_data.get('modification_date', 'N/A')}\n"
        result += f"Status: {note_data.get('status', 'N/A')}\n"
        result += f"Read Method: {note_data.get('read_method', 'by_id')}\n\n"
        result += f"Full Content:\n{note_data.get('body', 'No content available')}\n"
        
        return result
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        error_msg = f"Note not found or path error: {str(e)}"
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        await ctx.error(f"Error reading note: {str(e)}")
        raise

@mcp.tool()
async def update_note(
    ctx: Context,
    note_id: str = Field(..., description="Primary key ID of the note to update (e.g., 'p1234')"),
    new_name: str = Field(..., description="New note title wrapped in <h1> tags (e.g., '<h1>Updated Title</h1>')"),
    new_body: str = Field(..., description="New note body content with appropriate HTML formatting (e.g., '<p>Updated content</p>') For proper spacing between two sections, use <br>.")
) -> str:
    """Update an existing note by its primary key ID.
    
    📋 **Required:** Both new_name and new_body parameters
    🎨 **Supported HTML:** <h1-h6>, <b><i><u>, <p><div><br>, <ul><ol><li>, <table>, <a>
    ✅ **Best Practices:** Use semantic HTML, add <br> tags for spacing, avoid CSS styles
    
    💡 **Example:**
    note_id: "p1234"
    new_name: "<h1>Updated Report</h1>"
    new_body: "<p>Status: <b>Complete</b></p><br><ul><li>Done</li></ul>"
    
    Args:
        note_id: Primary key ID of the note to update
        new_name: New note title wrapped in <h1> tags
        new_body: New note body content with HTML formatting
    """
    try:
        # Import validation utils for title validation
        from .applescript.validation_utils import ValidationUtils
        
        # Validate the title content in the new_name parameter
        ValidationUtils.validate_html_title_content(new_name)
        
        # Combine new_name (title) and new_body into complete HTML content with <br> spacing
        combined_content = new_name + "<br>" + new_body
        updated_note = await notes_tools.update_note(note_id, combined_content)
        
        # Format the response with primary key ID
        result = f"Note Update Result:\n"
        result += f"Note Name: {updated_note.get('name', 'N/A')}\n"
        result += f"Note ID: {updated_note.get('note_id', 'N/A')}\n"
        result += f"Creation Date: {updated_note.get('creation_date', 'N/A')}\n"
        result += f"Modification Date: {updated_note.get('modification_date', 'N/A')}\n"
        result += f"Status: {updated_note.get('status', 'N/A')}\n"
        
        return result
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        error_msg = f"Note not found or path error: {str(e)}"
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        await ctx.error(f"Error updating note: {str(e)}")
        raise





@mcp.tool()
async def rename_folder(
    ctx: Context, 
    folder_path: str = Field(..., description="Path where the folder is located (e.g., 'Work/Projects'). Use empty string for root level."),
    current_name: str = Field(..., description="Current name of the folder to rename"),
    new_name: str = Field(..., description="New name for the folder (1-128 chars, no < > : \" | ? *)")
) -> str:
    """Rename a folder in Apple Notes with comprehensive validation.
    
    📁 **Features:**
    - Renames folders at root level and nested paths (up to 5 levels deep)
    - Comprehensive validation and duplicate detection
    - Unicode and emoji support for folder names
    
    ⚠️ **Validation:**
    - Max 128 characters, no special chars: < > : " | ? *
    - Prevents duplicate names, validates path existence
    - New name cannot be same as current name
    
    Args:
        folder_path: Path where the folder is located (empty for root level)
        current_name: Current name of the folder to rename
        new_name: New name for the folder
    """
    try:
        rename_result = await notes_tools.rename_folder(folder_path, current_name, new_name)
        
        # Format the response
        result = f"Folder Rename Result:\n"
        result += f"Path: {rename_result.get('folder_path', 'N/A')}\n"
        result += f"Old Name: {rename_result.get('current_name', 'N/A')}\n"
        result += f"New Name: {rename_result.get('new_name', 'N/A')}\n"
        result += f"Status: {rename_result.get('status', 'N/A')}\n"
        result += f"Message: {rename_result.get('message', 'N/A')}\n"
        
        return result
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
        error_msg = f"Unexpected error renaming folder '{current_name}' to '{new_name}': {str(e)}"
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def move_folder(
    ctx: Context, 
    source_path: str = Field(..., description="Current path where the folder is located (e.g., 'Work/Projects'). Use empty string for root level."),
    folder_name: str = Field(..., description="Name of the folder to move"),
    target_path: str = Field(default="", description="Target path where to move the folder (e.g., 'Archive'). If empty, moves to root level.")
) -> str:
    """Move a folder from one location to another in Apple Notes.
    
    📁 **Features:**
    - Moves folders between root level and nested paths (up to 5 levels deep)
    - Comprehensive validation and duplicate detection
    - Unicode and emoji support for folder names
    
    ⚠️ **Validation:**
    - Validates source and target paths exist
    - Prevents duplicate names in target location
    - Enforces 5-level nesting depth limit
    
    Args:
        source_path: Current path where the folder is located
        folder_name: Name of the folder to move
        target_path: Target path where to move the folder (empty for root level)
    """
    try:
        move_result = await notes_tools.move_folder(source_path, folder_name, target_path)
        
        # Format the response
        result = f"Folder Move Result:\n"
        result += f"Folder Name: {move_result.get('folder_name', 'N/A')}\n"
        result += f"Source Path: {move_result.get('source_path', 'N/A')}\n"
        result += f"Target Path: {move_result.get('target_path', 'N/A')}\n"
        result += f"Status: {move_result.get('status', 'N/A')}\n"
        result += f"Message: {move_result.get('message', 'N/A')}\n"
        
        return result
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
        error_msg = f"Unexpected error moving folder '{folder_name}' from '{source_path}' to '{target_path}': {str(e)}"
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def list_folder_with_structure(ctx: Context) -> str:
    """List the complete folder structure with hierarchical tree format.
    
    📁 **Features:**
    - Shows all folders in hierarchical tree format
    - Displays folder nesting levels with visual indicators
    - Works with root level and nested folder structures
    
    📊 **Output Format:**
    - Tree structure with ├── and └── indicators
    - Clear hierarchy visualization
    - Folder names with proper indentation
    
    Returns:
        Hierarchical tree structure of all folders in Apple Notes
    """
    try:
        folder_structure = await notes_tools.list_folder_with_structure()
        
        if not folder_structure:
            return "No folders found in Apple Notes"
        
        # Return filtered AppleScript result
        return f"Apple Notes Folder Structure:\n\n{folder_structure}"
    except Exception as e:
        await ctx.error(f"Error listing folder structure: {str(e)}")
        raise

@mcp.tool()
async def delete_note(
    ctx: Context,
    note_id: str = Field(..., description="Primary key ID of the note to delete (e.g., 'p1308')"),
    folder_path: str = Field(default="Notes", description="Folder path where the note should be located for verification (default: 'Notes')")
) -> str:
    """Delete a note by its primary key ID with folder path verification.
    
    🗑️ **Security Features:**
    - Verifies note exists in specified folder path
    - Uses primary key ID for precise identification
    - Provides detailed error messages for troubleshooting
    
    📄 **Output:**
    - Note name, ID, folder, creation/modification dates
    - Deletion status and method information
    
    Args:
        note_id: Primary key ID of the note to delete
        folder_path: Folder path for verification (default: "Notes")
    """
    try:
        deleted_note = await notes_tools.delete_note(note_id, folder_path)
        
        # Format the response
        result = f"Note Deletion Result:\n"
        result += f"Note Name: {deleted_note.get('name', 'N/A')}\n"
        result += f"Note ID: {deleted_note.get('note_id', 'N/A')}\n"
        result += f"Folder: {deleted_note.get('folder', 'N/A')}\n"
        result += f"Creation Date: {deleted_note.get('creation_date', 'N/A')}\n"
        result += f"Modification Date: {deleted_note.get('modification_date', 'N/A')}\n"
        result += f"Status: {deleted_note.get('status', 'N/A')}\n"
        result += f"Deletion Method: by_id\n"
        
        return result
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        error_msg = f"Note not found or path error: {str(e)}"
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        await ctx.error(f"Error deleting note: {str(e)}")
        raise



@mcp.tool()
async def list_notes_with_structure(ctx: Context) -> str:
    """List the complete folder structure with notes included in hierarchical tree format.
    
    📁 **Features:**
    - Shows all folders and notes in hierarchical tree format
    - Displays folder nesting levels with visual indicators
    - Lists notes within each folder
    - Works with root level and nested folder structures
    
    📊 **Output Format:**
    - Tree structure with ├── and └── indicators
    - Folder names with proper indentation
    - Notes listed under their respective folders
    
    Returns:
        Hierarchical tree structure of all folders and notes in Apple Notes
    """
    try:
        notes_structure = await notes_tools.list_notes_with_structure()
        
        if not notes_structure:
            return "No folders or notes found in Apple Notes"
        
        # Return filtered AppleScript result
        return f"Apple Notes Structure with Notes:\n\n{notes_structure}"
    except Exception as e:
        await ctx.error(f"Error listing notes structure: {str(e)}")
        raise

@mcp.tool()
async def list_notes(
    ctx: Context, 
    folder_path: str = Field(default="Notes", description="Folder path to list notes from (e.g., 'Work' or 'Work/Projects/2024'). Defaults to 'Notes'")
) -> str:
    """List notes with their names and IDs from a specific folder path.
    
    📝 **Features:**
    - Lists all notes in the specified folder
    - Shows note names and IDs
    - Works with root level and nested folder paths
    - Handles empty folders gracefully
    
    📊 **Output Format:**
    - Numbered list of notes
    - Note names with emoji indicators
    - Note IDs for reference
    
    Args:
        folder_path: Folder path to list notes from (default: "Notes")
    """
    try:
        notes_list = await notes_tools.list_notes(folder_path)
        
        if not notes_list:
            return f"No notes found in folder: {folder_path}"
        
        # Format the response
        result = f"Notes in '{folder_path}' ({len(notes_list)} total):\n\n"
        
        for i, note in enumerate(notes_list, 1):
            result += f"{i:3d}. {note.get('name', 'N/A')}\n"
            result += f"     ID: {note.get('note_id', 'N/A')}\n"
            result += "\n"
        
        return result
        
    except ValueError as e:
        error_msg = f"Invalid folder path: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        error_msg = f"Folder not found: {str(e)}"
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        await ctx.error(f"Error listing notes: {str(e)}")
        raise

@mcp.tool()
async def list_all_notes(ctx: Context) -> str:
    """List all notes across all folders with their names and IDs.
    
    📝 **Features:**
    - Lists ALL notes from ALL folders in Apple Notes
    - Shows note names, IDs, and folder locations
    - Includes notes from Recently Deleted folder
    - Provides comprehensive system overview
    
    📊 **Output Format:**
    - Numbered list of all notes
    - Note names with emoji indicators
    - Note IDs for reference
    - Folder location for each note
    
    Returns:
        Complete list of all notes across all folders in Apple Notes
    """
    try:
        notes_list = await notes_tools.list_all_notes()
        
        if not notes_list:
            return "No notes found in Apple Notes"
        
        # Format the response
        result = f"All Notes ({len(notes_list)} total):\n\n"
        
        for i, note in enumerate(notes_list, 1):
            result += f"{i:3d}. {note.get('name', 'N/A')}\n"
            result += f"     ID: {note.get('note_id', 'N/A')}\n"
            result += f"     Folder: {note.get('folder', 'N/A')}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        await ctx.error(f"Error listing all notes: {str(e)}")
        raise

@mcp.tool()
async def move_note(
    ctx: Context,
    note_id: str = Field(..., description="Primary key ID of the note to move (e.g., 'p1308')"),
    source_folder_path: str = Field(..., description="Current folder path where the note is located (e.g., 'Work' or 'Work/Projects/2024')"),
    target_folder_path: str = Field(..., description="Target folder path where to move the note (e.g., 'Archive' or 'Work/Completed')")
) -> str:
    """Move a note from one folder to another in Apple Notes.
    
    🔄 **Validation Sequence:**
    1. ✅ Validate note ID is not empty
    2. ✅ Check source and target paths are different
    3. ✅ Verify note exists in source folder
    4. ✅ Verify target folder path exists
    5. ✅ Perform move operation
    
    📁 **Features:**
    - Moves notes between root folders and nested paths (up to 5 levels deep)
    - Comprehensive validation and error handling
    - Supports all folder path types (root, simple, nested)
    - Maintains note content and metadata during move
    
    ⚠️ **Requirements:**
    - Note must exist in source folder
    - Target folder path must exist
    - Source and target paths must be different
    
    Args:
        note_id: Primary key ID of the note to move
        source_folder_path: Current folder path where note is located
        target_folder_path: Target folder path where to move the note
    """
    try:
        move_result = await notes_tools.move_note(note_id, source_folder_path, target_folder_path)
        
        # Format the response
        result = f"Note Move Result:\n"
        result += f"Note Name: {move_result.get('name', 'N/A')}\n"
        result += f"Note ID: {move_result.get('note_id', 'N/A')}\n"
        result += f"Source Folder: {move_result.get('source_folder', 'N/A')}\n"
        result += f"Target Folder: {move_result.get('target_folder', 'N/A')}\n"
        result += f"Status: {move_result.get('status', 'N/A')}\n"
        result += f"Message: {move_result.get('message', 'N/A')}\n"
        
        return result
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
        error_msg = f"Unexpected error moving note '{note_id}' from '{source_folder_path}' to '{target_folder_path}': {str(e)}"
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def list_folder_contents(
    ctx: Context, 
    folder_path: str = Field(default="Notes", description="Folder path to list contents from (default: 'Notes')")
) -> str:
    """List both notes and direct child folders in a specified folder path.
    
    📁 **Features:**
    - Lists notes (with IDs) and direct child folders
    - Works with root level and nested folder paths
    - Provides counts and structured output
    
    📊 **Output Format:**
    - Summary counts for notes and folders
    - Numbered lists with emoji indicators
    - Clear separation between notes and folders
    
    Args:
        folder_path: Folder path to list contents from (default: "Notes")
    """
    try:
        folder_contents = await notes_tools.list_folder_contents(folder_path)
        
        # Format the response
        result = f"Folder Contents: '{folder_path}'\n\n"
        result += f"Summary:\n"
        result += f"   Notes: {folder_contents.get('notes_count', 0)}\n"
        result += f"   Folders: {folder_contents.get('folders_count', 0)}\n\n"
        
        # List notes
        notes = folder_contents.get('notes', [])
        if notes:
            result += f"Notes ({len(notes)}):\n"
            for i, note in enumerate(notes, 1):
                result += f"   {i:2d}. {note.get('name', 'N/A')}\n"
                result += f"       ID: {note.get('note_id', 'N/A')}\n"
            result += "\n"
        
        # List folders
        folders = folder_contents.get('folders', [])
        if folders:
            result += f"Direct Child Folders ({len(folders)}):\n"
            for i, folder in enumerate(folders, 1):
                result += f"   {i:2d}. {folder.get('name', 'N/A')}\n"
            result += "\n"
        
        if not notes and not folders:
            result += "This folder is empty (no notes or folders).\n"
        
        return result
        
    except ValueError as e:
        error_msg = f"Invalid folder path: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        error_msg = f"Folder not found: {str(e)}"
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        await ctx.error(f"Error listing folder contents: {str(e)}")
        raise

# Run the server
if __name__ == "__main__":
    mcp.run()
