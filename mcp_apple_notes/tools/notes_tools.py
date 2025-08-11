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
    
    async def list_notes(self) -> List[Dict[str, Any]]:
        """List all notes."""
        return await ListNotesOperations.list_all_notes()
    
    async def list_folders(self) -> List[str]:
        """List all folder names (root and subfolders)."""
        return await ListFoldersOperations.list_folders()
    
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
    
    async def create_folder(self, folder_name: str) -> Dict[str, str]:
        """Create a new folder (backward compatibility)."""
        return await CreateFolderOperations.create_folder(folder_name)
    
    async def create_folder_with_path(self, folder_path: str) -> Dict[str, Any]:
        """Create a nested folder structure."""
        return await CreateFolderOperations.create_folder_with_path(folder_path)
    
    async def read_note_by_name(self, note_name: str, folder_name: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder (backward compatibility)."""
        return await ReadNoteOperations.read_note_by_name(note_name, folder_name)
    
    async def read_note_by_name_in_path(self, note_name: str, folder_path: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder path."""
        return await ReadNoteOperations.read_note_by_name_in_path(note_name, folder_path)
    
    async def resolve_folder_path(self, folder_path: str) -> Dict[str, Any]:
        """Resolve a folder path to get the target folder and its metadata."""
        return await FolderPathUtils.resolve_folder_path(folder_path)
    
    async def get_folder_details(self, folder_name: str) -> Dict[str, Any]:
        """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
        return await FolderDetailsOperations.get_folder_details(folder_name)
    
    async def get_folder_hierarchy_details(self, folder_name: str) -> Dict[str, Any]:
        """Get folder details with a more robust hierarchical structure."""
        return await FolderDetailsOperations.get_folder_hierarchy_details(folder_name)
    
    async def get_folders_structure(self) -> str:
        """Get complete folder structure - return raw AppleScript data."""
        # Return exactly what AppleScript gives us
        return await FolderStructureOperations.get_folders_structure()

