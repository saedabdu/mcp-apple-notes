from typing import Dict, List, Optional, Tuple
from .base_operations import BaseAppleScriptOperations

from .validation_utils import ValidationUtils

class NoteIDUtils(BaseAppleScriptOperations):
    """Utilities for note ID operations and duplicate handling."""
    
    @staticmethod
    async def get_all_notes_in_folder(folder_path: str = "Notes") -> List[Dict[str, str]]:
        """Get all notes in a folder with their IDs and names.
        
        Args:
            folder_path: Folder path to search in
            
        Returns:
            List of dictionaries with note_id, name, and folder info
            
        Raises:
            RuntimeError: If folder path doesn't exist
        """
        folder_path = folder_path.strip()
        
        if '/' not in folder_path:
            return await NoteIDUtils._get_all_notes_in_simple_folder(folder_path)
        else:
            return await NoteIDUtils._get_all_notes_in_nested_path(folder_path)
    
    @staticmethod
    async def _get_all_notes_in_simple_folder(folder_name: str) -> List[Dict[str, str]]:
        """Get all notes in a simple folder."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set noteList to {{}}
                
                repeat with theNote in notes of targetFolder
                    set noteInfo to {{id:(id of theNote as string), name:(name of theNote as string), folder:"{folder_name}"}}
                    copy noteInfo to end of noteList
                end repeat
                
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await NoteIDUtils.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get notes: {result[6:]}")
        
        return NoteIDUtils._parse_notes_list(result, folder_name)
    
    @staticmethod
    async def _get_all_notes_in_nested_path(folder_path: str) -> List[Dict[str, str]]:
        """Get all notes in a nested folder path."""
        # Validate that the folder path exists
        path_exists = await ValidationUtils.check_path_exists(folder_path)
        if not path_exists:
            raise RuntimeError(f"Folder path '{folder_path}' does not exist.")
        
        # Parse the path components
        path_components = ValidationUtils.parse_folder_path(folder_path)
        
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
                    set noteInfo to {{id:(id of theNote as string), name:(name of theNote as string), folder:"{folder_path}"}}
                    copy noteInfo to end of noteList
                end repeat
                
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await NoteIDUtils.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get notes: {result[6:]}")
        
        return NoteIDUtils._parse_notes_list(result, folder_path)
    
    @staticmethod
    def _parse_notes_list(result: str, folder_path: str) -> List[Dict[str, str]]:
        """Parse the AppleScript result and return list of notes."""
        try:
            notes = []
            # Parse the AppleScript result format: {id:noteId, name:noteName, folder:folderPath}, {id:noteId2, name:noteName2, folder:folderPath}
            
            # Split by }, { to get individual note entries
            note_entries = result.split('}, {')
            
            for entry in note_entries:
                # Clean up the entry
                entry = entry.strip()
                if entry.startswith('{'):
                    entry = entry[1:]
                if entry.endswith('}'):
                    entry = entry[:-1]
                
                # Parse individual note data
                note_info = {}
                
                # Extract ID
                id_start = entry.find('id:') + 3
                id_end = entry.find(', name:', id_start)
                if id_end == -1:
                    id_end = entry.find(', folder:', id_start)
                note_info['id'] = entry[id_start:id_end].strip()
                
                # Extract name
                name_start = entry.find('name:') + 5
                name_end = entry.find(', folder:', name_start)
                if name_end == -1:
                    name_end = len(entry)
                name = entry[name_start:name_end].strip()
                # Remove quotes if present
                if name.startswith('"') and name.endswith('"'):
                    name = name[1:-1]
                note_info['name'] = name
                
                # Use the provided folder_path instead of parsing from result
                note_info['folder'] = folder_path
                
                notes.append(note_info)
            
            return notes
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse notes list: {str(e)}")
    

    

    
    @staticmethod
    def extract_primary_key(full_note_id: str) -> str:
        """Extract just the primary key from a full Core Data ID.
        
        Args:
            full_note_id: Full Core Data ID like "x-coredata://UUID/ICNote/p123"
            
        Returns:
            Just the primary key part like "p123"
        """
        try:
            # Split by '/' and get the last part
            parts = full_note_id.split('/')
            if len(parts) > 0:
                return parts[-1]  # Gets "p123" part
            return full_note_id
        except:
            return full_note_id