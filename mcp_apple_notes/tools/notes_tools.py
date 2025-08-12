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
        if not folder_path:
            return ""
        
        # Clean the path
        folder_path = folder_path.strip()
        
        # Remove leading/trailing slashes
        folder_path = folder_path.strip('/')
        
        # Check for invalid patterns
        if '//' in folder_path:
            raise ValueError("Folder path contains invalid double slashes")
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in folder_path:
                raise ValueError(f"Folder path contains invalid character '{char}'")
        
        return folder_path
    
    async def _check_path_exists(self, folder_path: str) -> bool:
        """Check if a folder path exists.
        
        Args:
            folder_path: The folder path to check
            
        Returns:
            True if path exists, False otherwise
        """
        try:
            # Use a simple AppleScript to check if folder exists
            from ..applescript.base_operations import BaseAppleScriptOperations
            
            path_components = self._validate_folder_path(folder_path).split('/')
            if not path_components or not path_components[0]:
                return False
            
            script = f'''
            tell application "Notes"
                try
                    set currentFolder to missing value
                    set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
                    
                    repeat with i from 1 to count of pathComponents
                        set componentName to item i of pathComponents
                        
                        if currentFolder is missing value then
                            -- Check root folders
                            set found to false
                            repeat with rootFolder in every folder
                                if name of rootFolder is componentName then
                                    set currentFolder to rootFolder
                                    set found to true
                                    exit repeat
                                end if
                            end repeat
                            if not found then
                                return "error:Folder not found"
                            end if
                        else
                            -- Check subfolders
                            set found to false
                            repeat with subFolder in every folder of currentFolder
                                if name of subFolder is componentName then
                                    set currentFolder to subFolder
                                    set found to true
                                    exit repeat
                                end if
                            end repeat
                            if not found then
                                return "error:Folder not found"
                            end if
                        end if
                    end repeat
                    
                    return "exists"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
            
            result = await BaseAppleScriptOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    

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

