from typing import List, Dict, Any, Optional
from ..applescript.list_notes import ListNotesOperations
from ..applescript.create_note import CreateNoteOperations
from ..applescript.list_folders import ListFoldersOperations
from ..applescript.list_notes_by_folder import ListNotesByFolderOperations
from ..applescript.create_folder import CreateFolderOperations
from ..applescript.read_note import ReadNoteOperations

class NotesTools:
    """Tools for Apple Notes operations."""
    
    async def list_notes(self) -> List[Dict[str, Any]]:
        """List all notes."""
        return await ListNotesOperations.list_all_notes()
    
    async def list_folders(self) -> List[str]:
        """List all folders."""
        return await ListFoldersOperations.list_all_folders()
    
    async def create_note(self, name: str, body: str, folder_name: str = "Notes") -> Dict[str, str]:
        """Create a new note."""
        return await CreateNoteOperations.create_note(name, body, folder_name)
    
    async def list_notes_by_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        """List all notes from a specific folder."""
        return await ListNotesByFolderOperations.list_notes_by_folder(folder_name)
    
    async def create_folder(self, folder_name: str) -> Dict[str, str]:
        """Create a new folder."""
        return await CreateFolderOperations.create_folder(folder_name)
    
    async def read_note_by_name(self, note_name: str, folder_name: str = None) -> Dict[str, str]:
        """Read a note's content by name and optional folder."""
        return await ReadNoteOperations.read_note_by_name(note_name, folder_name)

