from typing import List, Dict, Any
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils
from .validation_utils import ValidationUtils
from .note_id_utils import NoteIDUtils

class ListNotesOperations(BaseAppleScriptOperations):
    """Operations for listing Apple Notes with their IDs."""
    
    @staticmethod
    def _validate_folder_path(folder_path: str) -> str:
        """Validate and clean folder path."""
        return ValidationUtils.validate_folder_path(folder_path)
    
    @staticmethod
    def _parse_notes_list(result: str, folder_path: str) -> List[Dict[str, str]]:
        """Parse AppleScript result into list of note dictionaries.
        
        Args:
            result: Raw AppleScript result
            folder_path: Folder path for context
            
        Returns:
            List of dictionaries with note_id, name, and folder info
        """
        notes = []
        
        if not result or result == "{}":
            return notes
        
        # AppleScript returns lists as comma-separated values
        # Format: id1, name1, id2, name2, id3, name3, ...
        try:
            # Split by comma and process pairs
            parts = [part.strip() for part in result.split(',') if part.strip()]
            
            # Process pairs (id, name)
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    full_note_id = parts[i].strip('"')
                    note_name = parts[i + 1].strip('"')
                    
                    # Extract just the primary key
                    short_id = NoteIDUtils.extract_primary_key(full_note_id)
                    
                    # Skip empty entries
                    if short_id and note_name:
                        notes.append({
                            'note_id': short_id,
                            'name': note_name,
                            'folder': folder_path
                        })
        
        except Exception as e:
            # If parsing fails, return empty list
            print(f"Warning: Failed to parse notes list: {e}")
            return []
        
        return notes
    
    @staticmethod
    def _parse_all_notes_list(result: str) -> List[Dict[str, str]]:
        """Parse AppleScript result for all notes list.
        
        Args:
            result: Raw AppleScript result
            
        Returns:
            List of dictionaries with note_id, name, and folder info
        """
        notes = []
        
        if not result or result == "{}":
            return notes
        
        # AppleScript returns lists as comma-separated values
        # Format: id1, name1, folder1, id2, name2, folder2, ...
        try:
            # Split by comma and process triplets
            parts = [part.strip() for part in result.split(',') if part.strip()]
            
            # Process triplets (id, name, folder)
            for i in range(0, len(parts), 3):
                if i + 2 < len(parts):
                    full_note_id = parts[i].strip('"')
                    note_name = parts[i + 1].strip('"')
                    folder_name = parts[i + 2].strip('"')
                    
                    # Extract just the primary key
                    short_id = NoteIDUtils.extract_primary_key(full_note_id)
                    
                    # Skip empty entries
                    if short_id and note_name and folder_name:
                        notes.append({
                            'note_id': short_id,
                            'name': note_name,
                            'folder': folder_name
                        })
        
        except Exception as e:
            # If parsing fails, return empty list
            print(f"Warning: Failed to parse all notes list: {e}")
            return []
        
        return notes
    
    @staticmethod
    async def list_notes(folder_path: str = "Notes") -> List[Dict[str, str]]:
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
        # Validate and clean folder path
        try:
            folder_path = ListNotesOperations._validate_folder_path(folder_path)
        except ValueError as e:
            raise ValueError(f"Invalid folder path: {str(e)}")
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            return await ListNotesOperations._list_notes_in_simple_folder(folder_path)
        else:
            return await ListNotesOperations._list_notes_in_nested_path(folder_path)
    
    @staticmethod
    async def _list_notes_in_simple_folder(folder_name: str) -> List[Dict[str, str]]:
        """Get all notes in a simple folder (no nested paths)."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set noteList to {{}}
                
                repeat with theNote in notes of targetFolder
                    set noteId to id of theNote as string
                    set noteName to name of theNote as string
                    copy noteId to end of noteList
                    copy noteName to end of noteList
                end repeat
                
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ListNotesOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get notes from folder '{folder_name}': {result[6:]}")
        
        return ListNotesOperations._parse_notes_list(result, folder_name)
    
    @staticmethod
    async def _list_notes_in_nested_path(folder_path: str) -> List[Dict[str, str]]:
        """Get all notes in a nested folder path."""
        # Validate that the folder path exists
        path_exists = await ValidationUtils.check_path_exists(folder_path)
        if not path_exists:
            raise RuntimeError(f"Folder path '{folder_path}' does not exist.")
        
        # Parse the path components
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        script = f'''
        tell application "Notes"
            try
                set currentFolder to missing value
                set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
                
                repeat with i from 1 to count of pathComponents
                    set componentName to item i of pathComponents
                    
                    if currentFolder is missing value then
                        -- Start from root folders
                        repeat with rootFolder in folders
                            if name of rootFolder is componentName then
                                set currentFolder to rootFolder
                                exit repeat
                            end if
                        end repeat
                    else
                        -- Navigate into subfolders
                        repeat with subFolder in folders of currentFolder
                            if name of subFolder is componentName then
                                set currentFolder to subFolder
                                exit repeat
                            end if
                        end repeat
                    end if
                end repeat
                
                if currentFolder is missing value then
                    return "error:Target folder not found"
                end if
                
                set noteList to {{}}
                
                repeat with theNote in notes of currentFolder
                    set noteId to id of theNote as string
                    set noteName to name of theNote as string
                    copy noteId to end of noteList
                    copy noteName to end of noteList
                end repeat
                
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ListNotesOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get notes from folder path '{folder_path}': {result[6:]}")
        
        return ListNotesOperations._parse_notes_list(result, folder_path)
    
    @staticmethod
    async def list_all_notes() -> List[Dict[str, str]]:
        """Get a list of all notes across all folders with their IDs and names.
        
        Returns:
            List of dictionaries with note_id, name, and folder info
        """
        script = '''
        tell application "Notes"
            try
                set allNotesList to {}
                
                -- Get all folders recursively
                set allFolders to {}
                
                -- Add root folders
                repeat with rootFolder in folders
                    set end of allFolders to rootFolder
                    
                    -- Add subfolders recursively
                    set subFolders to folders of rootFolder
                    repeat with subFolder in subFolders
                        set end of allFolders to subFolder
                    end repeat
                end repeat
                
                -- Get notes from each folder
                repeat with currentFolder in allFolders
                    set folderName to name of currentFolder
                    
                    repeat with theNote in notes of currentFolder
                        set noteId to id of theNote as string
                        set noteName to name of theNote as string
                        copy noteId to end of allNotesList
                        copy noteName to end of allNotesList
                        copy folderName to end of allNotesList
                    end repeat
                end repeat
                
                return allNotesList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ListNotesOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get all notes: {result[6:]}")
        
        return ListNotesOperations._parse_all_notes_list(result)
