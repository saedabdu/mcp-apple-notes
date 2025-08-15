from typing import List, Dict, Any, Optional
from ..applescript.create_note import CreateNoteOperations
from ..applescript.create_folder import CreateFolderOperations
from ..applescript.read_note import ReadNoteOperations
from ..applescript.read_folder import ReadFolderOperations

from ..applescript.rename_folder import RenameFolderOperations
from ..applescript.move_folder import MoveFolderOperations
from ..applescript.folder_structure import FolderStructureOperations
from ..applescript.notes_structure import NotesStructureOperations
from ..applescript.update_note import UpdateNoteOperations
from ..applescript.delete_note import DeleteNoteOperations

from ..applescript.note_id_utils import NoteIDUtils
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
    

    
    async def read_note(self, note_id: str, note_name: str) -> Dict[str, str]:
        """Read a note by its primary key ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, note name)
        2. AppleScript verifies ID and name match the same note
        3. Performs the read operation if verification passes
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1308")
            note_name: Name of the note to verify and read
            
        Returns:
            Note data with content, metadata, and verification info
            
        Raises:
            ValueError: If note ID or name is empty or invalid
            RuntimeError: If note not found, name doesn't match, or read fails
        """
        return await ReadNoteOperations.read_note_by_id_and_name(note_id, note_name)
    
    async def read_folder(self, folder_id: str, folder_name: str) -> Dict[str, Any]:
        """Read a folder by its primary key ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, folder name)
        2. AppleScript verifies ID and name match the same folder
        3. Performs the read operation if verification passes
        
        Args:
            folder_id: Primary key ID of the folder (e.g., "p2330")
            folder_name: Name of the folder to verify and read
            
        Returns:
            Folder data with metadata, child folders, and notes
            
        Raises:
            ValueError: If folder ID or name is empty or invalid
            RuntimeError: If folder not found, name doesn't match, or read fails
        """
        return await ReadFolderOperations.read_folder_by_id_and_name(folder_id, folder_name)
    

    
    async def rename_folder(self, folder_id: str, current_name: str, new_name: str) -> Dict[str, Any]:
        """Rename a folder in Apple Notes by ID with enhanced name verification.
        
        This method performs double verification:
        1. Validates the provided current name
        2. Gets the actual folder name by ID and verifies it matches
        
        Args:
            folder_id: Primary key ID of the folder to rename (e.g., "p2330")
            current_name: Current name of the folder to verify and rename
            new_name: New name for the folder
        """
        return await RenameFolderOperations.rename_folder_by_id(folder_id, current_name, new_name)
    
    async def move_folder(self, folder_id: str, folder_name: str, target_path: str = "") -> Dict[str, Any]:
        """Move a folder from one location to another in Apple Notes by ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, folder name, target path)
        2. AppleScript verifies ID and name match the same folder
        3. Performs the move operation if verification passes
        
        Args:
            folder_id: Primary key ID of the folder to move (e.g., "p2330")
            folder_name: Name of the folder to verify and move
            target_path: Target path where to move the folder (empty for root level)
        """
        return await MoveFolderOperations.move_folder_by_id(folder_id, folder_name, target_path)
    
    async def list_folder_with_structure(self) -> str:
        """List the complete folder structure with hierarchical tree format."""
        return await FolderStructureOperations.get_filtered_folders_structure()
    
    async def list_notes_with_structure(self) -> str:
        """List the complete folder structure with notes included in hierarchical tree format."""
        return await NotesStructureOperations.get_filtered_notes_structure()
    

    
    async def update_note(self, note_id: str, note_name: str, combined_content: str) -> Dict[str, str]:
        """Update an existing note by its primary key ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, note name, content)
        2. AppleScript verifies ID and name match the same note
        3. Performs the update if verification passes
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1234")
            note_name: Current name of the note to verify and update
            combined_content: Complete HTML content combining title and body (e.g., '<h1>Title</h1><p>Content</p>')
            
        Returns:
            Updated note metadata with primary key ID
            
        Raises:
            ValueError: If note ID or name is empty or invalid
            RuntimeError: If note not found, name doesn't match, or update fails
        """
        return await UpdateNoteOperations.update_note_by_id_and_name(note_id, note_name, combined_content)
    


    async def delete_note(self, note_id: str, note_name: str) -> Dict[str, str]:
        """Delete a note by its primary key ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, note name)
        2. AppleScript verifies ID and name match the same note
        3. Performs the deletion if verification passes
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1308")
            note_name: Name of the note to verify and delete
            
        Returns:
            Deletion result with status and details
            
        Raises:
            ValueError: If note ID or name is empty or invalid
            RuntimeError: If note not found, name doesn't match, or deletion fails
        """
        return await DeleteNoteOperations.delete_note_by_id_and_name(note_id, note_name)



    async def list_all_notes(self) -> List[Dict[str, str]]:
        """Get a list of all notes across all folders with their IDs and names.
        
        Returns:
            List of dictionaries with note_id, name, and folder info
        """
        # Import the list notes operations
        from ..applescript.list_notes import ListNotesOperations
        return await ListNotesOperations.list_all_notes()

    async def move_note(self, note_id: str, note_name: str, target_folder_path: str) -> Dict[str, str]:
        """Move a note from source folder to target folder by ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, note name, target path)
        2. AppleScript verifies ID and name match the same note
        3. Performs the move operation if verification passes
        
        Args:
            note_id: Primary key ID of the note to move (e.g., "p1308")
            note_name: Name of the note to verify and move
            target_folder_path: Target folder path where to move the note
            
        Returns:
            Move result with status and details
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If note not found, name doesn't match, or move fails
        """
        return await MoveNoteOperations.move_note_by_id_and_name(note_id, note_name, target_folder_path)

    async def delete_folder(self, folder_id: str, folder_name: str) -> Dict[str, Any]:
        """Delete a folder in Apple Notes by ID with AppleScript verification.
        
        This method relies on AppleScript's built-in verification:
        1. Validates input parameters (ID, folder name)
        2. AppleScript verifies ID and name match the same folder
        3. Performs the deletion if verification passes
        
        Args:
            folder_id: Primary key ID of the folder to delete (e.g., "p2330")
            folder_name: Name of the folder to verify and delete
        """
        # Import the delete folder operations
        from ..applescript.delete_folder import DeleteFolderOperations
        return await DeleteFolderOperations.delete_folder_by_id_and_name(folder_id, folder_name)

    async def search_notes(self, keywords: List[str]) -> List[Dict[str, str]]:
        """Search for notes containing the specified keywords.
        
        This method searches through all notes in Apple Notes to find those
        containing any of the specified keywords in their content.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of dictionaries with note_id, name, folder, and matched_keyword
            
        Raises:
            ValueError: If keywords list is empty or invalid
            RuntimeError: If search operation fails
        """
        # Import the search notes operations
        from ..applescript.search_notes import SearchNotesOperations
        return await SearchNotesOperations.search_notes(keywords)
