from typing import Dict, Optional, List
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils
from .validation_utils import ValidationUtils

class DeleteNoteOperations(BaseAppleScriptOperations):
    """Operations for deleting Apple Notes."""
    
    @staticmethod
    def _validate_note_name(name: str) -> str:
        """Validate and clean note name."""
        if not name or not name.strip():
            raise ValueError("Note name cannot be empty or contain only whitespace")
        
        # Clean the name
        name = name.strip()
        
        # Handle backtick-escaped names
        if name.startswith('`') and name.endswith('`'):
            # Extract the name from backticks and skip validation
            escaped_name = name[1:-1]  # Remove backticks
            if not escaped_name:
                raise ValueError("Note name cannot be empty when using backtick escaping")
            
            # Check for Apple Notes title length limit (250 characters)
            if len(escaped_name) > 250:
                raise ValueError(f"Note name exceeds Apple Notes limit of 250 characters (current: {len(escaped_name)} characters)")
            
            # Return the escaped name without backticks
            return escaped_name.strip()
        
        # Check for Apple Notes title length limit (250 characters)
        if len(name) > 250:
            raise ValueError(f"Note name exceeds Apple Notes limit of 250 characters (current: {len(name)} characters)")
        
        # Check for invalid characters (basic validation) - only for non-escaped names
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Note name contains invalid character '{char}'. Use backticks (`name`) to escape special characters.")
        
        return name
    
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
    async def _get_note_id(note_name: str, folder_path: str) -> Optional[str]:
        """Get the ID of a note by name.
        
        Args:
            note_name: Name of the note
            folder_path: Folder path where the note is located
            
        Returns:
            Note ID if found, None otherwise
        """
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = DeleteNoteOperations._create_applescript_quoted_string(note_name)
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_path}"
                    set targetNote to missing value
                    set noteCount to 0
                    repeat with currentNote in notes of targetFolder
                        if name of currentNote is {quoted_note_name} then
                            set noteCount to noteCount + 1
                            if noteCount is 1 then
                                set targetNote to currentNote
                                exit repeat
                            end if
                        end if
                    end repeat
                    if targetNote is missing value then
                        return "not_found"
                    end if
                    return id of targetNote
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Nested path - navigate to the folder first
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
                    
                    set targetNote to missing value
                    set noteCount to 0
                    repeat with currentNote in notes of currentFolder
                        if name of currentNote is {quoted_note_name} then
                            set noteCount to noteCount + 1
                            if noteCount is 1 then
                                set targetNote to currentNote
                                exit repeat
                            end if
                        end if
                    end repeat
                    if targetNote is missing value then
                        return "not_found"
                    end if
                    return id of targetNote
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await DeleteNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            error_msg = result[6:]
            if "Target folder not found" in error_msg:
                raise RuntimeError(f"Folder path '{folder_path}' does not exist")
            else:
                raise RuntimeError(f"Failed to get note ID: {error_msg}")
        elif result == "not_found":
            raise RuntimeError(f"Note '{note_name}' not found in folder path '{folder_path}'")
        
        return result
    
    @staticmethod
    async def _count_notes_with_name(note_name: str, folder_path: str) -> int:
        """Count how many notes exist with the given name in the folder.
        
        Args:
            note_name: Name of the note to count
            folder_path: Folder path to check in
            
        Returns:
            Number of notes with the given name
        """
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = DeleteNoteOperations._create_applescript_quoted_string(note_name)
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_path}"
                    set noteCount to 0
                    repeat with currentNote in notes of targetFolder
                        if name of currentNote is {quoted_note_name} then
                            set noteCount to noteCount + 1
                        end if
                    end repeat
                    return noteCount
                on error errMsg
                    return 0
                end try
            end tell
            '''
        else:
            # Nested path - navigate to the folder first
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
                        return 0
                    end if
                    
                    set noteCount to 0
                    repeat with currentNote in notes of currentFolder
                        if name of currentNote is {quoted_note_name} then
                            set noteCount to noteCount + 1
                        end if
                    end repeat
                    return noteCount
                on error errMsg
                    return 0
                end try
            end tell
            '''
        
        result = await DeleteNoteOperations.execute_applescript(script)
        try:
            return int(result)
        except ValueError:
            return 0
    
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
            
            result = await DeleteNoteOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    async def delete_note(note_name: str, folder_path: str = "Notes") -> Dict[str, str]:
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
        # Validate inputs
        if not note_name or not note_name.strip():
            raise ValueError("Note name cannot be empty or contain only whitespace")
        
        # Clean and validate note name
        note_name = DeleteNoteOperations._validate_note_name(note_name)
        
        # Validate folder path
        if not folder_path or not folder_path.strip():
            folder_path = "Notes"
        folder_path = folder_path.strip()
        
        # Check if folder path exists
        if not await DeleteNoteOperations._check_path_exists(folder_path):
            raise RuntimeError(f"Folder path '{folder_path}' does not exist")
        
        # Count notes with the same name to provide better feedback
        note_count = await DeleteNoteOperations._count_notes_with_name(note_name, folder_path)
        
        if note_count == 0:
            raise RuntimeError(f"Note '{note_name}' not found in folder path '{folder_path}'")
        
        # If multiple notes exist, return error asking user to change name manually
        if note_count > 1:
            raise RuntimeError(f"Found {note_count} notes with name '{note_name}' in folder path '{folder_path}'. Cannot delete due to duplicate names. Please manually change the name of the note you want to delete first, then try again.")
        
        # Get the note ID for deletion (no index needed since we ensure only one note exists)
        note_id = await DeleteNoteOperations._get_note_id(note_name, folder_path)
        
        if not note_id:
            raise RuntimeError(f"Note '{note_name}' not found in folder path '{folder_path}'")
        
        # Perform the deletion using note ID
        script = f'''
        tell application "Notes"
            try
                set targetNote to note id "{note_id}"
                
                set noteName to name of targetNote
                set noteId to id of targetNote
                set creationDate to creation date of targetNote
                set modificationDate to modification date of targetNote
                
                delete targetNote
                
                return "success:" & noteName & ", " & noteId & ", " & creationDate & ", " & modificationDate & ", 1"
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await DeleteNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            error_msg = result[6:]
            if "Note not found" in error_msg:
                raise RuntimeError(f"Note '{note_name}' not found in folder path '{folder_path}'")
            elif "Target folder not found" in error_msg:
                raise RuntimeError(f"Folder path '{folder_path}' does not exist")
            else:
                raise RuntimeError(f"Failed to delete note: {error_msg}")
        
        return DeleteNoteOperations._parse_delete_result(result, folder_path)
    
    @staticmethod
    def _parse_delete_result(result: str, folder_path: str) -> Dict[str, str]:
        """Parse the AppleScript result and return deletion information."""
        try:
            # The result format is: success:name, id, creation_date, modification_date, total_matches
            if result.startswith("success:"):
                parts = result[8:].split(", ")  # Remove "success:" prefix
                
                if len(parts) >= 5:
                    return {
                        'name': parts[0],
                        'note_id': parts[1],
                        'creation_date': parts[2],
                        'modification_date': parts[3],
                        'total_matches': parts[4],
                        'folder': folder_path,
                        'note_index': "1",
                        'status': 'deleted'
                    }
                else:
                    return {
                        'name': 'Unknown',
                        'note_id': 'Unknown',
                        'creation_date': 'Unknown',
                        'modification_date': 'Unknown',
                        'total_matches': '1',
                        'folder': folder_path,
                        'note_index': "1",
                        'status': 'deleted'
                    }
            else:
                raise RuntimeError(f"Unexpected result format: {result}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse delete result: {str(e)}")
