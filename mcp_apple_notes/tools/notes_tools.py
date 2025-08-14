from typing import List, Dict, Any, Optional
from ..applescript.create_note import CreateNoteOperations
from ..applescript.create_folder import CreateFolderOperations
from ..applescript.read_note import ReadNoteOperations

from ..applescript.rename_folder import RenameFolderOperations
from ..applescript.move_folder import MoveFolderOperations
from ..applescript.folder_structure import FolderStructureOperations
from ..applescript.notes_structure import NotesStructureOperations
from ..applescript.update_note import UpdateNoteOperations
from ..applescript.delete_note import DeleteNoteOperations

from ..applescript.note_id_utils import NoteIDUtils
from ..applescript.list_notes import ListNotesOperations
from ..applescript.folder_contents import FolderContentsOperations
from ..applescript.move_note import MoveNoteOperations

class NotesTools:
    """Tools for Apple Notes operations."""
    
    async def create_note(self, name: str, body: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Create a new note with specified name, body, and folder path.
        
        This unified method handles both simple folders and nested paths.
        The folder path must exist before creating the note.
        Special characters in name and body are automatically escaped for AppleScript compatibility.
        
        Note: The body parameter should contain complete HTML content that combines
        both title and body content. This will be passed directly to Apple Notes.
        
        Args:
            name: Name of the note for Apple Notes internal reference (used for identification)
            body: Complete HTML content combining title and body (e.g., '<h1>Title</h1><p>Content</p>')
            folder_path: Folder path (e.g., "Work" or "Work/Projects/2024"). 
                        Must exist before creating note. Defaults to "Notes".
                        
        Raises:
            ValueError: If note name is empty, contains only whitespace, or contains invalid characters
            RuntimeError: If the specified folder path does not exist
        """
        return await CreateNoteOperations.create_note(name, body, folder_path)
    
    async def create_folder(self, folder_name: str, folder_path: str = "") -> Dict[str, Any]:
        """Create a folder in Apple Notes.
        
        Args:
            folder_name: Name of the folder to create
            folder_path: Optional path where to create the folder. If empty, creates at root level.
        """
        # Use the enhanced CreateFolderOperations that handles all logic internally
        return await CreateFolderOperations.create_folder(folder_name, folder_path)
    
    async def read_note(self, note_id: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Read a note by its primary key ID with folder path verification.
        
        This method verifies that the note with the given ID exists in the specified 
        folder path before reading, providing better error handling and security.
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1308")
            folder_path: Folder path where the note should be located (default: "Notes")
            
        Returns:
            Note data with content, metadata, and verification info
            
        Raises:
            ValueError: If note ID is empty or invalid
            RuntimeError: If folder path doesn't exist, note not found, or note not in specified folder
        """
        return await ReadNoteOperations.read_note_by_id(note_id, folder_path)
    

    
    async def rename_folder(self, folder_path: str, current_name: str, new_name: str) -> Dict[str, Any]:
        """Rename a folder in Apple Notes."""
        return await RenameFolderOperations.rename_folder(folder_path, current_name, new_name)
    
    async def move_folder(self, source_path: str, folder_name: str, target_path: str = "") -> Dict[str, Any]:
        """Move a folder from one location to another in Apple Notes.
        
        Args:
            source_path: The current path of the folder to move
            folder_name: The name of the folder to move
            target_path: The target path where to move the folder. If empty, moves to root level.
        """
        return await MoveFolderOperations.move_folder(source_path, folder_name, target_path)
    
    async def list_folder_with_structure(self) -> str:
        """List the complete folder structure with hierarchical tree format."""
        return await FolderStructureOperations.get_filtered_folders_structure()
    
    async def list_notes_with_structure(self) -> str:
        """List the complete folder structure with notes included in hierarchical tree format."""
        return await NotesStructureOperations.get_filtered_notes_structure()
    

    
    async def update_note(self, note_id: str, combined_content: str) -> Dict[str, str]:
        """Update an existing note by its primary key ID.
        
        This method updates a note directly using its primary key ID (e.g., "p1234").
        The combined_content should contain the complete HTML including title and body.
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1234")
            combined_content: Complete HTML content combining title and body (e.g., '<h1>Title</h1><p>Content</p>')
            
        Returns:
            Updated note metadata with primary key ID
            
        Raises:
            ValueError: If note ID is invalid
            RuntimeError: If note not found by ID
        """
        return await UpdateNoteOperations.update_note_by_id(note_id, None, combined_content)
    


    async def delete_note(self, note_id: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Delete a note by its primary key ID with folder path verification.
        
        This method verifies that the note with the given ID exists in the specified 
        folder path before deletion, providing better error handling and security.
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1308")
            folder_path: Folder path where the note should be located (default: "Notes")
            
        Returns:
            Deletion result with status and details
            
        Raises:
            ValueError: If note ID is empty or invalid
            RuntimeError: If folder path doesn't exist, note not found, or note not in specified folder
        """
        return await DeleteNoteOperations.delete_note_by_id(note_id, folder_path)



    async def list_notes(self, folder_path: str = "Notes") -> List[Dict[str, str]]:
        """Get a list of all notes in the specified folder path with their IDs and names.
        
        This unified method handles both simple folders and nested paths.
        
        Args:
            folder_path: Folder path (e.g., "Work" or "Work/Projects/2024"). Defaults to "Notes".
            
        Returns:
            List of dictionaries with note_id, name, and folder info
            
        Raises:
            ValueError: If folder path is invalid
            RuntimeError: If folder path doesn't exist
        """
        return await ListNotesOperations.list_notes(folder_path)
    
    async def list_all_notes(self) -> List[Dict[str, str]]:
        """Get a list of all notes across all folders with their IDs and names.
        
        Returns:
            List of dictionaries with note_id, name, and folder info
        """
        return await ListNotesOperations.list_all_notes()

    async def list_folder_contents(self, folder_path: str = "Notes") -> Dict[str, any]:
        """List both notes and direct child folders in the specified folder path.
        
        This method provides a comprehensive view of folder contents by listing
        both notes (with names and IDs) and direct child folders (with names).
        
        Args:
            folder_path: Folder path to list contents from (default: "Notes")
            
        Returns:
            Dictionary containing notes list and folders list
            
        Raises:
            ValueError: If folder path is invalid
            RuntimeError: If folder path doesn't exist
        """
        return await FolderContentsOperations.list_folder_contents(folder_path)

    async def move_note(self, note_id: str, source_folder_path: str, target_folder_path: str) -> Dict[str, str]:
        """Move a note from source folder to target folder.
        
        This method performs comprehensive validation before moving:
        1. Validate note ID is not empty
        2. Check source and target paths are different
        3. Verify note exists in source folder
        4. Verify target folder path exists
        5. Perform move operation
        
        Args:
            note_id: Primary key ID of the note to move (e.g., "p1308")
            source_folder_path: Current folder path where note is located
            target_folder_path: Target folder path where to move the note
            
        Returns:
            Move result with status and details
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If note not found, paths don't exist, or move fails
        """
        return await MoveNoteOperations.move_note(note_id, source_folder_path, target_folder_path)
