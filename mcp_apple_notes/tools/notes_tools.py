from typing import List, Dict, Any, Optional
from ..applescript.create_note import CreateNoteOperations
from ..applescript.list_folders import ListFoldersOperations
from ..applescript.create_folder import CreateFolderOperations
from ..applescript.read_note import ReadNoteOperations
from ..applescript.folder_utils import FolderPathUtils
from ..applescript.folder_details import FolderDetailsOperations
from ..applescript.rename_folder import RenameFolderOperations
from ..applescript.move_folder import MoveFolderOperations
from ..applescript.folder_structure import FolderStructureOperations
from ..applescript.notes_structure import NotesStructureOperations
from ..applescript.update_note import UpdateNoteOperations
from ..applescript.delete_note import DeleteNoteOperations
from ..applescript.move_note import MoveNoteOperations
from ..applescript.validation_utils import ValidationUtils
from ..applescript.note_id_utils import NoteIDUtils

class NotesTools:
    """Tools for Apple Notes operations."""
    
    def _validate_folder_path(self, folder_path: str) -> str:
        """Validate and clean folder path.
        
        Args:
            folder_path: The folder path to validate
            
        Returns:
            Cleaned folder path
            
        Raises:
            ValueError: If path is invalid
        """
        return ValidationUtils.validate_folder_path(folder_path)
    
    async def _check_path_exists(self, folder_path: str) -> bool:
        """Check if a folder path exists.
        
        Args:
            folder_path: The folder path to check
            
        Returns:
            True if path exists, False otherwise
        """
        return await ValidationUtils.check_path_exists(folder_path)
    

    async def create_note(self, name: str, body: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Create a new note with specified name, body, and folder path.
        
        This unified method handles both simple folders and nested paths.
        The folder path must exist before creating the note.
        Special characters in name and body are automatically escaped for AppleScript compatibility.
        
        Args:
            name: Name of the note (cannot be empty or contain only whitespace)
            body: Content of the note (supports all characters including quotes and backslashes)
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
    
    async def read_note(self, note_name: str, folder_path: str = "Notes") -> List[Dict[str, str]]:
        """Read notes with the given name in the specified folder path.
        
        This unified method handles both simple folders and nested paths.
        Returns all notes with the specified name if multiple exist.
        
        Args:
            note_name: Name of the note to read
            folder_path: Folder path (e.g., "Work" or "Work/Projects/2024"). Defaults to "Notes".
            
        Returns:
            List of notes with the specified name
            
        Raises:
            ValueError: If note name is empty or invalid
            RuntimeError: If folder path doesn't exist or note not found
        """
        # Use the robust note ID system to get the note ID first
        try:
            note_id_result = await NoteIDUtils.get_note_id_by_name_with_duplicate_check(note_name, folder_path)
            
            if note_id_result['status'] == 'single':
                # Get the note by ID
                note_result = await NoteIDUtils.get_note_by_id(note_id_result['note_id'], folder_path)
                return [note_result]
            elif note_id_result['status'] == 'multiple':
                # Return information about all duplicate notes
                return [{
                    'status': 'multiple',
                    'message': note_id_result['message'],
                    'duplicate_count': note_id_result['duplicate_count'],
                    'notes': note_id_result['notes']
                }]
            else:
                raise RuntimeError(f"Unexpected result: {note_id_result}")
                
        except Exception as e:
            # Fallback to the original method if the new system fails
            return await ReadNoteOperations.read_note(note_name, folder_path)
    
    async def get_folder_details(self, folder_name: str) -> Dict[str, Any]:
        """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
        return await FolderDetailsOperations.get_folder_details(folder_name)
    
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
    
    async def update_note(self, note_name: str, folder_path: str = "Notes", 
                         new_name: Optional[str] = None, new_body: Optional[str] = None) -> Dict[str, str]:
        """Update an existing note's name and/or content.
        
        This unified method handles both simple folders and nested paths.
        At least one of new_name or new_body must be provided.
        
        Args:
            note_name: Current name of the note to update
            folder_path: Folder path where the note is located (default: "Notes")
            new_name: New name for the note (optional)
            new_body: New content for the note (optional)
            
        Returns:
            Updated note metadata
            
        Raises:
            ValueError: If note name is empty or invalid, or if no updates provided
            RuntimeError: If folder path doesn't exist or note not found
        """
        # Use the robust note ID system to get the note ID first
        try:
            note_id_result = await NoteIDUtils.get_note_id_by_name_with_duplicate_check(note_name, folder_path)
            
            if note_id_result['status'] == 'single':
                # Use the note ID to update the note directly
                return await UpdateNoteOperations.update_note_by_id(note_id_result['note_id'], folder_path, new_name, new_body)
            elif note_id_result['status'] == 'multiple':
                # Return information about duplicate notes
                return {
                    'status': 'error',
                    'message': note_id_result['message'],
                    'duplicate_count': note_id_result['duplicate_count'],
                    'notes': note_id_result['notes']
                }
            else:
                raise RuntimeError(f"Unexpected result: {note_id_result}")
                
        except Exception as e:
            # Fallback to the original method if the new system fails
            return await UpdateNoteOperations.update_note(note_name, folder_path, new_name, new_body)
    
    async def delete_note(self, note_name: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Delete a note from Apple Notes.
        
        This unified method handles both simple folders and nested paths.
        
        Args:
            note_name: Name of the note to delete
            folder_path: Folder path where the note is located (default: "Notes")
            
        Returns:
            Deletion result with status and details
            
        Raises:
            ValueError: If note name is empty or invalid
            RuntimeError: If folder path doesn't exist, note not found, or duplicate names exist
        """
        # Use the robust note ID system to get the note ID first
        try:
            note_id_result = await NoteIDUtils.get_note_id_by_name_with_duplicate_check(note_name, folder_path)
            
            if note_id_result['status'] == 'single':
                # Get the note by ID and then delete it
                note_result = await NoteIDUtils.get_note_by_id(note_id_result['note_id'], folder_path)
                # TODO: Implement delete by ID in DeleteNoteOperations
                return await DeleteNoteOperations.delete_note(note_name, folder_path)
            elif note_id_result['status'] == 'multiple':
                # Return information about duplicate notes
                return {
                    'status': 'error',
                    'message': note_id_result['message'],
                    'duplicate_count': note_id_result['duplicate_count'],
                    'notes': note_id_result['notes']
                }
            else:
                raise RuntimeError(f"Unexpected result: {note_id_result}")
                
        except Exception as e:
            # Fallback to the original method if the new system fails
            return await DeleteNoteOperations.delete_note(note_name, folder_path)

    async def move_note(self, note_name: str, source_folder_path: str, target_folder_path: str) -> Dict[str, Any]:
        """Move a note from one folder to another.
        
        This unified method handles both simple folders and nested paths.
        
        Args:
            note_name: Name of the note to move
            source_folder_path: Current folder path where the note is located
            target_folder_path: Target folder path where to move the note
            
        Returns:
            Move operation result with status and details
            
        Raises:
            ValueError: If note name is empty or invalid, or if source/target paths are identical
            RuntimeError: If source/target paths don't exist, note not found, or move operation fails
        """
        # Use the robust note ID system to get the note ID first
        try:
            note_id_result = await NoteIDUtils.get_note_id_by_name_with_duplicate_check(note_name, source_folder_path)
            
            if note_id_result['status'] == 'single':
                # Get the note by ID and then move it
                note_result = await NoteIDUtils.get_note_by_id(note_id_result['note_id'], source_folder_path)
                # TODO: Implement move by ID in MoveNoteOperations
                return await MoveNoteOperations.move_note(note_name, source_folder_path, target_folder_path)
            elif note_id_result['status'] == 'multiple':
                # Return information about duplicate notes
                return {
                    'status': 'error',
                    'message': note_id_result['message'],
                    'duplicate_count': note_id_result['duplicate_count'],
                    'notes': note_id_result['notes']
                }
            else:
                raise RuntimeError(f"Unexpected result: {note_id_result}")
                
        except Exception as e:
            # Fallback to the original method if the new system fails
            return await MoveNoteOperations.move_note(note_name, source_folder_path, target_folder_path)

