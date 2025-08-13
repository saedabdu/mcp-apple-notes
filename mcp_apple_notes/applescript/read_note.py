from typing import Dict, Optional, List
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils
from .validation_utils import ValidationUtils

class ReadNoteOperations(BaseAppleScriptOperations):
    """Operations for reading Apple Notes content."""
    
    @staticmethod
    def _validate_note_name(name: str) -> str:
        """Validate and clean note name."""
        return ValidationUtils.validate_note_name(name)
    
    @staticmethod
    def _truncate_note_name(name: str, max_length: int = 250) -> str:
        """Intelligently truncate note name to fit Apple Notes limit."""
        if len(name) <= max_length:
            return name
        
        # Try to truncate at word boundaries
        truncated = name[:max_length-3]  # Leave room for "..."
        
        # Find the last space to avoid cutting words
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:  # If we can find a space in the last 30%
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    @staticmethod
    def _find_note_by_partial_name(note_name: str, folder_path: str) -> List[Dict[str, str]]:
        """Find notes by partial name matching for long names."""
        # This will be implemented in the AppleScript layer
        # For now, return empty list - will be enhanced later
        return []
    
    @staticmethod
    def _create_applescript_quoted_string(text: str) -> str:
        """Create AppleScript quoted string that handles special characters properly.
        
        Args:
            text: The text to quote
            
        Returns:
            AppleScript quoted string
        """
        if not text:
            return '""'
        
        # Escape the text for AppleScript string literals
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped_text}"'
    
    @staticmethod
    async def read_note(note_name: str, folder_path: str = "Notes") -> List[Dict[str, str]]:
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
        # Validate inputs
        try:
            note_name = ReadNoteOperations._validate_note_name(note_name)
        except ValueError as e:
            # If name is too long, try to find it with partial matching
            if "exceeds Apple Notes limit" in str(e):
                # Try with truncated name first
                truncated_name = ReadNoteOperations._truncate_note_name(note_name)
                try:
                    note_name = ReadNoteOperations._validate_note_name(truncated_name)
                except ValueError:
                    # If still too long, use the first 250 characters
                    note_name = note_name[:250]
            else:
                raise e
        
        folder_path = folder_path.strip()
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            return await ReadNoteOperations._read_note_in_simple_folder(note_name, folder_path)
        else:
            # Nested path - validate path exists and read note
            return await ReadNoteOperations._read_note_in_nested_path(note_name, folder_path)
    
    @staticmethod
    async def _read_note_in_simple_folder(note_name: str, folder_name: str) -> List[Dict[str, str]]:
        """Read notes with the given name in a simple folder (no nested paths)."""
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = ReadNoteOperations._create_applescript_quoted_string(note_name)
        
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set noteList to {{}}
                repeat with theNote in notes of targetFolder
                    if name of theNote is {quoted_note_name} then
                        set noteInfo to {{name:(name of theNote), folder:"{folder_name}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                        copy noteInfo to end of noteList
                    end if
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note: {result[6:]}")
        
        return ReadNoteOperations._parse_note_list_result(result, folder_name)
    
    @staticmethod
    async def _read_note_in_nested_path(note_name: str, folder_path: str) -> List[Dict[str, str]]:
        """Read notes with the given name in a nested folder path. Path must exist."""
        # Validate that the folder path exists
        path_exists = await ReadNoteOperations._check_path_exists(folder_path)
        if not path_exists:
            raise RuntimeError(f"Folder path '{folder_path}' does not exist.")
        
        # Parse the path components
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        # Read the note in the existing folder
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = ReadNoteOperations._create_applescript_quoted_string(note_name)
        
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
                    if name of theNote is {quoted_note_name} then
                        set noteInfo to {{name:(name of theNote), folder:"{folder_path}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                        copy noteInfo to end of noteList
                    end if
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note: {result[6:]}")
        
        return ReadNoteOperations._parse_note_list_result(result, folder_path)
    
    @staticmethod
    async def _check_path_exists(folder_path: str) -> bool:
        """Check if a folder path exists."""
        try:
            path_components = FolderPathUtils.parse_folder_path(folder_path)
            if not path_components:
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
                            repeat with rootFolder in folders
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
                            repeat with subFolder in folders of currentFolder
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
            
            result = await ReadNoteOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    def _parse_note_list_result(result: str, folder_path: str) -> List[Dict[str, str]]:
        """Parse the AppleScript result and return list of note information."""
        try:
            # Parse multiple notes from the result
            # Format: {name:noteName, folder:folderPath, body:noteBody, creation_date:date, modification_date:date}, {name:noteName2, ...}
            notes = []
            
            # Split the result into individual note entries
            # Each note entry starts with 'name:' and contains 5 fields
            entries = result.split('name:')
            
            for entry in entries[1:]:  # Skip the first empty entry
                try:
                    # Find the end of the name (before ', folder:')
                    name_end = entry.find(', folder:')
                    if name_end == -1:
                        continue
                        
                    name = entry[:name_end].strip()
                    
                    # Find folder
                    folder_start = entry.find('folder:') + 7
                    folder_end = entry.find(', body:', folder_start)
                    if folder_end == -1:
                        continue
                        
                    folder = entry[folder_start:folder_end].strip()
                    
                    # Find body (this is tricky because body can contain commas and special characters)
                    body_start = entry.find(', body:') + 7
                    body_end = entry.find(', creation_date:', body_start)
                    if body_end == -1:
                        # If no creation_date, body goes to the end
                        body_end = entry.find(', modification_date:', body_start)
                        if body_end == -1:
                            body_end = len(entry)
                    
                    body = entry[body_start:body_end].strip()
                    
                    # Find creation_date
                    creation_start = entry.find('creation_date:') + 14
                    creation_end = entry.find(', modification_date:', creation_start)
                    if creation_end == -1:
                        creation_end = len(entry)
                    creation_date = entry[creation_start:creation_end].strip().rstrip(',')
                    
                    # Find modification_date (go to end or next 'name:')
                    modification_start = entry.find('modification_date:') + 18
                    modification_end = entry.find(', name:', modification_start)
                    if modification_end == -1:
                        modification_end = len(entry)
                        
                    modification_date = entry[modification_start:modification_end].strip().rstrip(',')
                    
                    notes.append({
                        'name': name,
                        'folder': folder,
                        'body': body,
                        'creation_date': creation_date,
                        'modification_date': modification_date
                    })
                    
                except Exception as e:
                    # Skip malformed entries
                    continue
            
            return notes
        except Exception as e:
            raise RuntimeError(f"Failed to parse note content: {str(e)}")
    
    @staticmethod
    async def read_note_by_name(note_name: str, folder_name: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set noteList to {{}}
                repeat with theNote in notes of targetFolder
                    if name of theNote is "{note_name}" then
                        set noteInfo to {{name:(name of theNote), folder:"{folder_name}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                        copy noteInfo to end of noteList
                    end if
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note: {result[6:]}")
        
        # Parse the result manually since body content may contain commas and special characters
        try:
            # Parse multiple notes from the result
            # Format: {name:noteName, folder:folderName, body:noteBody, creation_date:date, modification_date:date}, {name:noteName2, ...}
            notes = []
            
            # Split the result into individual note entries
            # Each note entry starts with 'name:' and contains 5 fields
            entries = result.split('name:')
            
            for entry in entries[1:]:  # Skip the first empty entry
                try:
                    # Find the end of the name (before ', folder:')
                    name_end = entry.find(', folder:')
                    if name_end == -1:
                        continue
                        
                    name = entry[:name_end].strip()
                    
                    # Find folder
                    folder_start = entry.find('folder:') + 7
                    folder_end = entry.find(', body:', folder_start)
                    if folder_end == -1:
                        continue
                        
                    folder = entry[folder_start:folder_end].strip()
                    
                    # Find body (this is tricky because body can contain commas and special characters)
                    body_start = entry.find(', body:') + 7
                    body_end = entry.find(', creation_date:', body_start)
                    if body_end == -1:
                        # If no creation_date, body goes to the end
                        body_end = entry.find(', modification_date:', body_start)
                        if body_end == -1:
                            body_end = len(entry)
                    
                    body = entry[body_start:body_end].strip()
                    
                    # Find creation_date
                    creation_start = entry.find('creation_date:') + 14
                    creation_end = entry.find(', modification_date:', creation_start)
                    if creation_end == -1:
                        creation_end = len(entry)
                    creation_date = entry[creation_start:creation_end].strip().rstrip(',')
                    
                    # Find modification_date (go to end or next 'name:')
                    modification_start = entry.find('modification_date:') + 18
                    modification_end = entry.find(', name:', modification_start)
                    if modification_end == -1:
                        modification_end = len(entry)
                        
                    modification_date = entry[modification_start:modification_end].strip().rstrip(',')
                    
                    notes.append({
                        'name': name,
                        'folder': folder,
                        'body': body,
                        'creation_date': creation_date,
                        'modification_date': modification_date
                    })
                    
                except Exception as e:
                    # Skip malformed entries
                    continue
            
            return notes
        except Exception as e:
            raise RuntimeError(f"Failed to parse note content: {str(e)}")
    
    @staticmethod
    async def read_note_by_name_in_path(note_name: str, folder_path: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder path."""
        # First resolve the folder path
        folder_info = await FolderPathUtils.resolve_folder_path(folder_path)
        
        # Then search for notes in that folder
        script = f'''
        tell application "Notes"
            try
                set currentFolder to missing value
                set pathComponents to {{{", ".join([f'"{component}"' for component in folder_info['components']])}}}
                
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
                    return "error:Folder not found"
                end if
                
                set noteList to {{}}
                repeat with theNote in notes of currentFolder
                    if name of theNote is "{note_name}" then
                        set noteInfo to {{name:(name of theNote), folder:"{folder_path}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                        copy noteInfo to end of noteList
                    end if
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note by path: {result[6:]}")
        
        # Parse the result using the same logic as the original method
        try:
            # Parse multiple notes from the result
            # Format: {name:noteName, folder:folderPath, body:noteBody, creation_date:date, modification_date:date}, {name:noteName2, ...}
            notes = []
            
            # Split the result into individual note entries
            # Each note entry starts with 'name:' and contains 5 fields
            entries = result.split('name:')
            
            for entry in entries[1:]:  # Skip the first empty entry
                try:
                    # Find the end of the name (before ', folder:')
                    name_end = entry.find(', folder:')
                    if name_end == -1:
                        continue
                        
                    name = entry[:name_end].strip()
                    
                    # Find folder
                    folder_start = entry.find('folder:') + 7
                    folder_end = entry.find(', body:', folder_start)
                    if folder_end == -1:
                        continue
                        
                    folder = entry[folder_start:folder_end].strip()
                    
                    # Find body (this is tricky because body can contain commas and special characters)
                    body_start = entry.find(', body:') + 7
                    body_end = entry.find(', creation_date:', body_start)
                    if body_end == -1:
                        # If no creation_date, body goes to the end
                        body_end = entry.find(', modification_date:', body_start)
                        if body_end == -1:
                            body_end = len(entry)
                    
                    body = entry[body_start:body_end].strip()
                    
                    # Find creation_date
                    creation_start = entry.find('creation_date:') + 14
                    creation_end = entry.find(', modification_date:', creation_start)
                    if creation_end == -1:
                        creation_end = len(entry)
                    creation_date = entry[creation_start:creation_end].strip().rstrip(',')
                    
                    # Find modification_date (go to end or next 'name:')
                    modification_start = entry.find('modification_date:') + 18
                    modification_end = entry.find(', name:', modification_start)
                    if modification_end == -1:
                        modification_end = len(entry)
                        
                    modification_date = entry[modification_start:modification_end].strip().rstrip(',')
                    
                    notes.append({
                        'name': name,
                        'folder': folder,
                        'body': body,
                        'creation_date': creation_date,
                        'modification_date': modification_date
                    })
                    
                except Exception as e:
                    # Skip malformed entries
                    continue
            
            return notes
        except Exception as e:
            raise RuntimeError(f"Failed to parse note content: {str(e)}")
