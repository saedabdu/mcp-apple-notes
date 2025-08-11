from typing import List, Dict, Any, Optional
from ..applescript.list_notes import ListNotesOperations
from ..applescript.create_note import CreateNoteOperations
from ..applescript.list_folders import ListFoldersOperations
from ..applescript.list_notes_by_folder import ListNotesByFolderOperations
from ..applescript.create_folder import CreateFolderOperations
from ..applescript.read_note import ReadNoteOperations
from ..applescript.folder_utils import FolderPathUtils
from ..applescript.folder_details import FolderDetailsOperations
from ..applescript.folder_structure import FolderStructureOperations

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
    
    async def list_notes(self) -> List[Dict[str, Any]]:
        """List all notes."""
        return await ListNotesOperations.list_all_notes()
    
    async def create_note(self, name: str, body: str, folder_name: str = "Notes") -> Dict[str, str]:
        """Create a new note (backward compatibility)."""
        return await CreateNoteOperations.create_note(name, body, folder_name)
    
    async def create_note_in_path(self, name: str, body: str, folder_path: str) -> Dict[str, str]:
        """Create a new note in a nested folder path."""
        return await CreateNoteOperations.create_note_in_path(name, body, folder_path)
    
    async def list_notes_by_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        """List all notes from a specific folder (backward compatibility)."""
        return await ListNotesByFolderOperations.list_notes_by_folder(folder_name)
    
    async def list_notes_by_folder_path(self, folder_path: str) -> List[Dict[str, Any]]:
        """List all notes from a specific folder path."""
        return await ListNotesByFolderOperations.list_notes_by_folder_path(folder_path)
    
    async def create_folder(self, folder_name: str, folder_path: str = "") -> Dict[str, Any]:
        """Create a folder in Apple Notes.
        
        Args:
            folder_name: Name of the folder to create
            folder_path: Optional path where to create the folder. If empty, creates at root level.
        """
        # Use the enhanced CreateFolderOperations that handles all logic internally
        return await CreateFolderOperations.create_folder(folder_name, folder_path)
    
    async def read_note_by_name(self, note_name: str, folder_name: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder (backward compatibility)."""
        return await ReadNoteOperations.read_note_by_name(note_name, folder_name)
    
    async def read_note_by_name_in_path(self, note_name: str, folder_path: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder path."""
        return await ReadNoteOperations.read_note_by_name_in_path(note_name, folder_path)
    

    
    async def get_folder_details(self, folder_name: str) -> Dict[str, Any]:
        """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
        return await FolderDetailsOperations.get_folder_details(folder_name)
    
    async def get_folder_hierarchy_details(self, folder_name: str) -> Dict[str, Any]:
        """Get folder details with a more robust hierarchical structure."""
        return await FolderDetailsOperations.get_folder_hierarchy_details(folder_name)

    async def list_folder_structure(self) -> str:
        """List the complete folder structure with hierarchical tree format."""
        return await FolderStructureOperations.get_filtered_folders_structure()

