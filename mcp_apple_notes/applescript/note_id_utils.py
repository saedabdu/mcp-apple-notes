from typing import Dict, List, Optional, Tuple
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils
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
    async def get_note_id_by_name_with_duplicate_check(note_name: str, folder_path: str = "Notes") -> Dict[str, any]:
        """Get note ID by name with comprehensive duplicate checking.
        
        This method:
        1. Fetches all notes in the folder
        2. Checks for duplicate names
        3. Returns the unique note ID if found
        
        Args:
            note_name: Name of the note to find
            folder_path: Folder path where to search
            
        Returns:
            Dict with note_id and metadata
            
        Raises:
            ValueError: If note name is invalid
            RuntimeError: If folder path doesn't exist, note not found, or duplicates exist
        """
        # Validate inputs
        try:
            note_name = ValidationUtils.validate_note_name(note_name)
        except ValueError as e:
            # If name is too long, try to find it with partial matching
            if "exceeds Apple Notes limit" in str(e):
                # Try with truncated name first
                truncated_name = ValidationUtils.truncate_note_name(note_name)
                try:
                    note_name = ValidationUtils.validate_note_name(truncated_name)
                except ValueError:
                    # If still too long, use the first 250 characters
                    note_name = note_name[:250]
            else:
                raise e
        
        # Get all notes in the folder
        all_notes = await NoteIDUtils.get_all_notes_in_folder(folder_path)
        
        # Find notes with matching name
        matching_notes = [note for note in all_notes if note['name'] == note_name]
        
        if len(matching_notes) == 0:
            raise RuntimeError(f"Note '{note_name}' not found in folder '{folder_path}'")
        elif len(matching_notes) == 1:
            # Single note found - return its ID
            note = matching_notes[0]
            return {
                'status': 'single',
                'note_id': note['id'],
                'name': note['name'],
                'folder': note['folder'],
                'duplicate_count': 1
            }
        else:
            # Multiple notes with same name found
            return {
                'status': 'multiple',
                'duplicate_count': len(matching_notes),
                'message': f"Found {len(matching_notes)} notes with the same name '{note_name}' in folder '{folder_path}'. Please specify which one to use.",
                'notes': matching_notes
            }
    
    @staticmethod
    async def get_note_by_id(note_id: str, folder_path: str = "Notes") -> Dict[str, any]:
        """Get note by ID.
        
        Args:
            note_id: ID of the note to retrieve
            folder_path: Folder path where the note is located
            
        Returns:
            Dict with note information
            
        Raises:
            RuntimeError: If note not found
        """
        folder_path = folder_path.strip()
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            return await NoteIDUtils._get_note_by_id_in_simple_folder(note_id, folder_path)
        else:
            # Nested path - validate path exists and get note
            return await NoteIDUtils._get_note_by_id_in_nested_path(note_id, folder_path)
    
    @staticmethod
    async def _get_note_by_id_in_simple_folder(note_id: str, folder_name: str) -> Dict[str, any]:
        """Get note by ID in a simple folder."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                repeat with theNote in notes of targetFolder
                    if (id of theNote as string) is "{note_id}" then
                        return {{id:(id of theNote as string), name:(name of theNote as string), folder:"{folder_name}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                    end if
                end repeat
                return "error:Note not found"
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await NoteIDUtils.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get note by ID: {result[6:]}")
        
        return NoteIDUtils._parse_single_note_data(result, folder_name)
    
    @staticmethod
    async def _get_note_by_id_in_nested_path(note_id: str, folder_path: str) -> Dict[str, any]:
        """Get note by ID in a nested folder path."""
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
                
                repeat with theNote in notes of currentFolder
                    if (id of theNote as string) is "{note_id}" then
                        return {{id:(id of theNote as string), name:(name of theNote as string), folder:"{folder_path}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                    end if
                end repeat
                return "error:Note not found"
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await NoteIDUtils.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get note by ID: {result[6:]}")
        
        return NoteIDUtils._parse_single_note_data(result, folder_path)
    
    @staticmethod
    def _parse_single_note_data(note_data: str, folder_path: str) -> Dict[str, any]:
        """Parse single note data."""
        try:
            # Extract the note information from the result
            # Format: {id:noteId, name:noteName, folder:folderPath, body:noteBody, creation_date:creationDate, modification_date:modificationDate}
            
            # Parse the AppleScript result format
            note_info = {}
            
            # Extract ID
            id_start = note_data.find('id:') + 3
            id_end = note_data.find(', name:', id_start)
            if id_end == -1:
                id_end = note_data.find(', folder:', id_start)
            note_info['id'] = note_data[id_start:id_end].strip()
            
            # Extract name
            name_start = note_data.find('name:') + 5
            name_end = note_data.find(', folder:', name_start)
            if name_end == -1:
                name_end = note_data.find(', body:', name_start)
            name = note_data[name_start:name_end].strip()
            # Remove quotes if present
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            note_info['name'] = name
            
            # Extract folder
            folder_start = note_data.find('folder:') + 7
            folder_end = note_data.find(', body:', folder_start)
            if folder_end == -1:
                folder_end = note_data.find(', creation_date:', folder_start)
            folder = note_data[folder_start:folder_end].strip()
            # Remove quotes if present
            if folder.startswith('"') and folder.endswith('"'):
                folder = folder[1:-1]
            note_info['folder'] = folder
            
            # Extract body
            body_start = note_data.find('body:') + 5
            body_end = note_data.find(', creation_date:', body_start)
            if body_end == -1:
                body_end = note_data.find(', modification_date:', body_start)
            body = note_data[body_start:body_end].strip()
            # Remove quotes if present
            if body.startswith('"') and body.endswith('"'):
                body = body[1:-1]
            note_info['body'] = body
            
            # Extract creation date
            creation_start = note_data.find('creation_date:') + 14
            creation_end = note_data.find(', modification_date:', creation_start)
            if creation_end == -1:
                creation_end = len(note_data)
            creation_date = note_data[creation_start:creation_end].strip()
            # Remove quotes if present
            if creation_date.startswith('"') and creation_date.endswith('"'):
                creation_date = creation_date[1:-1]
            note_info['creation_date'] = creation_date
            
            # Extract modification date
            modification_start = note_data.find('modification_date:') + 18
            modification_date = note_data[modification_start:].strip()
            # Remove quotes if present
            if modification_date.startswith('"') and modification_date.endswith('"'):
                modification_date = modification_date[1:-1]
            note_info['modification_date'] = modification_date
            
            return {
                'status': 'single',
                'note_id': note_info['id'],
                'name': note_info['name'],
                'folder': note_info['folder'],
                'body': note_info['body'],
                'creation_date': note_info['creation_date'],
                'modification_date': note_info['modification_date'],
                'duplicate_count': 1
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse single note data: {str(e)}")
    
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