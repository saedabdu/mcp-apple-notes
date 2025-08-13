from typing import List, Dict, Any
from .base_operations import BaseAppleScriptOperations

class ValidationUtils(BaseAppleScriptOperations):
    """Centralized validation utilities for Apple Notes operations."""
    
    # Constants
    MAX_NESTING_DEPTH = 5
    MAX_NOTE_NAME_LENGTH = 250
    INVALID_CHARS = ['<', '>', ':', '"', '|', '?', '*']
    
    @staticmethod
    def validate_folder_name(folder_name: str) -> str:
        """Validate and clean folder name.
        
        Args:
            folder_name: The folder name to validate
            
        Returns:
            Cleaned folder name
            
        Raises:
            ValueError: If folder name is invalid
        """
        if not folder_name or not folder_name.strip():
            raise ValueError("Folder name cannot be empty or contain only whitespace")
        
        # Clean the name
        folder_name = folder_name.strip()
        
        # Check for invalid characters
        for char in ValidationUtils.INVALID_CHARS:
            if char in folder_name:
                raise ValueError(f"Folder name contains invalid character '{char}'")
        
        return folder_name
    
    @staticmethod
    def validate_folder_path(folder_path: str) -> str:
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
        
        # Check for invalid characters
        for char in ValidationUtils.INVALID_CHARS:
            if char in folder_path:
                raise ValueError(f"Folder path contains invalid character '{char}'")
        
        return folder_path
    
    @staticmethod
    def validate_note_name(name: str) -> str:
        """Validate and clean note name.
        
        Args:
            name: The note name to validate
            
        Returns:
            Cleaned note name
            
        Raises:
            ValueError: If note name is invalid
        """
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
            
            # Check for Apple Notes title length limit
            if len(escaped_name) > ValidationUtils.MAX_NOTE_NAME_LENGTH:
                raise ValueError(f"Note name exceeds Apple Notes limit of {ValidationUtils.MAX_NOTE_NAME_LENGTH} characters (current: {len(escaped_name)} characters)")
            
            # Return the escaped name without backticks
            return escaped_name.strip()
        
        # Check for Apple Notes title length limit
        if len(name) > ValidationUtils.MAX_NOTE_NAME_LENGTH:
            raise ValueError(f"Note name exceeds Apple Notes limit of {ValidationUtils.MAX_NOTE_NAME_LENGTH} characters (current: {len(name)} characters)")
        
        # Check for invalid characters (only for non-escaped names)
        for char in ValidationUtils.INVALID_CHARS:
            if char in name:
                raise ValueError(f"Note name contains invalid character '{char}'. Use backticks (`name`) to escape special characters.")
        
        return name
    
    @staticmethod
    def validate_note_body(body: str) -> str:
        """Validate note body.
        
        Args:
            body: The note body to validate
            
        Returns:
            Validated note body
        """
        if body is None:
            body = ""
        return str(body)
    
    @staticmethod
    def parse_folder_path(folder_path: str) -> List[str]:
        """Parse a folder path into components.
        
        Args:
            folder_path: The folder path to parse
            
        Returns:
            List of folder path components
        """
        if not folder_path:
            return ["Notes"]  # Default folder
        return [part.strip() for part in folder_path.split('/') if part.strip()]
    
    @staticmethod
    def validate_nesting_depth(folder_path: str, folder_name: str = None, operation: str = "create") -> None:
        """Validate that the operation won't exceed maximum nesting depth.
        
        Args:
            folder_path: The path where the operation will occur
            folder_name: The name of the folder (optional, for better error messages)
            operation: The operation being performed (create, move, etc.)
            
        Raises:
            ValueError: If the nesting depth would exceed the maximum allowed
        """
        # Count the depth of the existing path
        path_depth = 0
        if folder_path:
            path_components = folder_path.split('/')
            path_depth = len([comp for comp in path_components if comp.strip()])
        
        # Total depth will be path_depth + 1 (for the new/moved folder)
        total_depth = path_depth + 1
        
        if total_depth > ValidationUtils.MAX_NESTING_DEPTH:
            folder_info = f"'{folder_name}'" if folder_name else "folder"
            raise ValueError(
                f"Cannot {operation} {folder_info} in path '{folder_path}'. "
                f"This would create a nesting depth of {total_depth} levels, "
                f"which exceeds the maximum allowed depth of {ValidationUtils.MAX_NESTING_DEPTH} levels. "
                f"Please {operation} the folder at a higher level in the hierarchy."
            )
    
    @staticmethod
    def validate_move_operation(source_path: str, target_path: str, folder_name: str) -> None:
        """Validate that a move operation is valid.
        
        Args:
            source_path: The current path of the folder
            target_path: The target path where the folder will be moved
            folder_name: The name of the folder being moved
            
        Raises:
            ValueError: If the move operation is invalid
        """
        # Check if source and target are the same
        if source_path == target_path:
            raise ValueError(f"Cannot move folder '{folder_name}' to the same location")
        
        # Validate nesting depth for target path
        ValidationUtils.validate_nesting_depth(target_path, folder_name, "move")
    
    @staticmethod
    async def check_path_exists(folder_path: str) -> bool:
        """Check if a folder path exists.
        
        Args:
            folder_path: The folder path to check
            
        Returns:
            True if path exists, False otherwise
        """
        try:
            # Handle root level (empty path) - root level always exists
            if not folder_path or folder_path.strip() == "":
                return True
            
            path_components = ValidationUtils.parse_folder_path(folder_path)
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
            
            result = await ValidationUtils.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    async def check_folder_exists_at_root(folder_name: str) -> bool:
        """Check if a folder exists at root level.
        
        Args:
            folder_name: The folder name to check
            
        Returns:
            True if folder exists at root, False otherwise
        """
        try:
            script = f'''
            tell application "Notes"
                try
                    repeat with rootFolder in folders
                        if name of rootFolder is "{folder_name}" then
                            return "exists"
                        end if
                    end repeat
                    return "not_found"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
            
            result = await ValidationUtils.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    def escape_applescript_string(text: str) -> str:
        """Escape text for use in AppleScript strings.
        
        Args:
            text: The text to escape
            
        Returns:
            Escaped text
        """
        if not text:
            return '""'
        
        # Replace backslashes with double backslashes
        escaped_text = text.replace('\\', '\\\\')
        
        # Replace quotes with escaped quotes
        escaped_text = escaped_text.replace('"', '\\"')
        
        return f'"{escaped_text}"'
    
    @staticmethod
    def create_applescript_quoted_string(text: str) -> str:
        """Create a properly quoted string for AppleScript.
        
        Args:
            text: The text to quote
            
        Returns:
            Quoted string for AppleScript
        """
        if not text:
            return '""'
        
        # Escape the text for AppleScript string literals
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped_text}"'
    
    @staticmethod
    def truncate_note_name(name: str, max_length: int = None) -> str:
        """Intelligently truncate note name to fit Apple Notes limit.
        
        Args:
            name: The note name to truncate
            max_length: Maximum length (defaults to MAX_NOTE_NAME_LENGTH)
            
        Returns:
            Truncated note name
        """
        if max_length is None:
            max_length = ValidationUtils.MAX_NOTE_NAME_LENGTH
            
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
    async def check_note_name_exists(name: str, folder_path: str, exclude_note_id: str = None) -> bool:
        """Check if a note with the given name already exists in the specified folder.
        
        This is a centralized method for duplicate name validation that can be used
        by both create_note and update_note operations.
        
        Args:
            name: The note name to check
            folder_path: The folder path to check in
            exclude_note_id: Optional note ID to exclude from the check (for updates)
            
        Returns:
            True if a note with the same name exists, False otherwise
            
        Raises:
            ValueError: If the name is invalid
        """
        # Validate the note name first
        try:
            validated_name = ValidationUtils.validate_note_name(name)
        except ValueError as e:
            raise ValueError(f"Invalid note name for duplicate check: {str(e)}")
        
        # Fetch all note names and IDs from the folder
        notes_data = await ValidationUtils._get_notes_from_folder(folder_path)
        
        # Check for duplicates, excluding the specified note ID if provided
        for note_name, note_id in notes_data:
            if note_name == validated_name:
                if exclude_note_id is None or note_id != exclude_note_id:
                    return True
        
        return False
    
    @staticmethod
    async def _get_notes_from_folder(folder_path: str) -> list:
        """Get all note names and IDs from a folder.
        
        Args:
            folder_path: The folder path to get notes from
            
        Returns:
            List of tuples (note_name, note_id)
        """
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_path}"
                    set notesList to {{}}
                    repeat with currentNote in notes of targetFolder
                        set notesList to notesList & {{(name of currentNote as string), (id of currentNote as string)}}
                    end repeat
                    return notesList
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Nested path - navigate to the folder first
            from .folder_utils import FolderPathUtils
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
                        return "error:Folder not found"
                    end if
                    
                    set notesList to {{}}
                    repeat with currentNote in notes of currentFolder
                        set notesList to notesList & {{(name of currentNote as string), (id of currentNote as string)}}
                    end repeat
                    return notesList
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        try:
            result = await ValidationUtils.execute_applescript(script)
            
            # Check if there was an error
            if result.startswith("error:"):
                return []
            
            # Parse the result - AppleScript returns a flat list, so we need to pair them
            # The result format is: "name1, id1, name2, id2, ..."
            if not result or result == "":
                return []
            
            # Split the result and pair them
            items = result.split(", ")
            notes_data = []
            
            for i in range(0, len(items), 2):
                if i + 1 < len(items):
                    note_name = items[i].strip('"')  # Remove quotes
                    note_id = items[i + 1].strip('"')  # Remove quotes
                    notes_data.append((note_name, note_id))
            
            return notes_data
            
        except Exception:
            return []
