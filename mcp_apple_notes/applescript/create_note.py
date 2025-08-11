from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils

class CreateNoteOperations(BaseAppleScriptOperations):
    """Operations for creating Apple Notes."""
    
    @staticmethod
    def _escape_applescript_string(text: str) -> str:
        """Escape problematic characters for AppleScript strings.
        
        Args:
            text: The text to escape
            
        Returns:
            Escaped text safe for AppleScript
        """
        if not text:
            return ""
        
        # Escape backslashes first (to avoid double-escaping)
        text = text.replace("\\", "\\\\")
        
        # Escape double quotes
        text = text.replace('"', '\\"')
        
        return text
    
    @staticmethod
    def _validate_note_name(name: str) -> str:
        """Validate and clean note name."""
        if not name or not name.strip():
            raise ValueError("Note name cannot be empty or contain only whitespace")
        
        # Clean the name
        name = name.strip()
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Note name contains invalid character '{char}'")
        
        return name
    
    @staticmethod
    def _validate_note_body(body: str) -> str:
        """Validate note body."""
        if body is None:
            body = ""
        return str(body)
    
    @staticmethod
    async def create_note(name: str, body: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Create a new note with specified name, body, and folder path.
        
        This unified method handles both simple folders and nested paths.
        The folder path must exist before creating the note.
        
        Args:
            name: Name of the note
            body: Content of the note
            folder_path: Folder path (e.g., "Work" or "Work/Projects/2024"). 
                        Must exist before creating note. Defaults to "Notes".
        """
        # Validate and clean inputs
        name = CreateNoteOperations._validate_note_name(name)
        body = CreateNoteOperations._validate_note_body(body)
        folder_path = folder_path.strip()
        
        # Escape problematic characters for AppleScript
        name = CreateNoteOperations._escape_applescript_string(name)
        body = CreateNoteOperations._escape_applescript_string(body)
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            return await CreateNoteOperations._create_note_in_simple_folder(name, body, folder_path)
        else:
            # Nested path - validate path exists and create note
            return await CreateNoteOperations._create_note_in_nested_path(name, body, folder_path)
    
    @staticmethod
    async def _create_note_in_simple_folder(name: str, body: str, folder_name: str) -> Dict[str, str]:
        """Create a new note in a simple folder (no nested paths)."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set newNote to make new note at targetFolder with properties {{name:"{name}", body:"{body}"}}
                return {{name:(name of newNote), folder:"{folder_name}", creation_date:(creation date of newNote as string), modification_date:(modification date of newNote as string)}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        result = await CreateNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to create note: {result[6:]}")
        
        return CreateNoteOperations._parse_note_result(result, folder_name)
    
    @staticmethod
    async def _create_note_in_nested_path(name: str, body: str, folder_path: str) -> Dict[str, str]:
        """Create a new note in a nested folder path. Path must exist."""
        # Validate that the folder path exists
        path_exists = await CreateNoteOperations._check_path_exists(folder_path)
        if not path_exists:
            raise RuntimeError(f"Folder path '{folder_path}' does not exist. Please create the folder structure first.")
        
        # Parse the path components
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        # Create the note in the existing folder
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
                
                set newNote to make new note at currentFolder with properties {{name:"{name}", body:"{body}"}}
                return {{name:(name of newNote), folder:"{folder_path}", creation_date:(creation date of newNote as string), modification_date:(modification date of newNote as string)}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await CreateNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to create note: {result[6:]}")
        
        return CreateNoteOperations._parse_note_result(result, folder_path)
    
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
            
            result = await CreateNoteOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    def _parse_note_result(result: str, folder_path: str) -> Dict[str, str]:
        """Parse the AppleScript result and return note information."""
        try:
            # Extract the note information from the result
            name_start = result.find('name:') + 5
            name_end = result.find(', folder:', name_start)
            name = result[name_start:name_end].strip()
            
            folder_start = result.find('folder:') + 7
            folder_end = result.find(', creation_date:', folder_start)
            folder = result[folder_start:folder_end].strip()
            
            creation_start = result.find('creation_date:') + 14
            creation_end = result.find(', modification_date:', creation_start)
            creation_date = result[creation_start:creation_end].strip()
            
            modification_start = result.find('modification_date:') + 18
            modification_date = result[modification_start:].strip().rstrip(',')
            
            return {
                'name': name,
                'folder': folder,
                'creation_date': creation_date,
                'modification_date': modification_date
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse created note result: {str(e)}")
