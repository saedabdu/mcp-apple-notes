from typing import Dict, Optional, List
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils

class UpdateNoteOperations(BaseAppleScriptOperations):
    """Operations for updating Apple Notes content."""
    
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
    def _validate_note_body(body: str) -> str:
        """Validate note body."""
        if body is None:
            body = ""
        return str(body)
    
    @staticmethod
    async def _check_duplicate_note(name: str, folder_path: str, exclude_note_id: Optional[str] = None) -> bool:
        """Check if a note with the same name already exists in the target folder.
        
        Args:
            name: Name of the note to check
            folder_path: Folder path to check in
            exclude_note_id: Optional note ID to exclude from the check (for updates)
            
        Returns:
            True if a note with the same name exists, False otherwise
        """
        # Use AppleScript's quoted form for better special character handling
        quoted_name = UpdateNoteOperations._create_applescript_quoted_string(name)
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            if exclude_note_id:
                script = f'''
                tell application "Notes"
                    try
                        set targetFolder to folder "{folder_path}"
                        set noteCount to 0
                        repeat with currentNote in notes of targetFolder
                            if name of currentNote is {quoted_name} and id of currentNote is not "{exclude_note_id}" then
                                set noteCount to noteCount + 1
                            end if
                        end repeat
                        return noteCount > 0
                    on error errMsg
                        return false
                    end try
                end tell
                '''
            else:
                script = f'''
                tell application "Notes"
                    try
                        set targetFolder to folder "{folder_path}"
                        set noteCount to 0
                        repeat with currentNote in notes of targetFolder
                            if name of currentNote is {quoted_name} then
                                set noteCount to noteCount + 1
                            end if
                        end repeat
                        return noteCount > 0
                    on error errMsg
                        return false
                    end try
                end tell
                '''
        else:
            # Nested path - navigate to the folder first
            path_components = FolderPathUtils.parse_folder_path(folder_path)
            if exclude_note_id:
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
                            return false
                        end if
                        
                        set noteCount to 0
                        repeat with currentNote in notes of currentFolder
                            if name of currentNote is {quoted_name} and id of currentNote is not "{exclude_note_id}" then
                                set noteCount to noteCount + 1
                            end if
                        end repeat
                        return noteCount > 0
                    on error errMsg
                        return false
                    end try
                end tell
                '''
            else:
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
                            return false
                        end if
                        
                        set noteCount to 0
                        repeat with currentNote in notes of currentFolder
                            if name of currentNote is {quoted_name} then
                                set noteCount to noteCount + 1
                            end if
                        end repeat
                        return noteCount > 0
                    on error errMsg
                        return false
                    end try
                end tell
                '''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        return result == "true"
    
    @staticmethod
    async def _get_note_id(note_name: str, folder_path: str, note_index: Optional[int] = None) -> Optional[str]:
        """Get the ID of a note by name and optional index.
        
        Args:
            note_name: Name of the note
            folder_path: Folder path where the note is located
            note_index: Index of the note if multiple exist (1-based, optional)
            
        Returns:
            Note ID if found, None otherwise
        """
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = UpdateNoteOperations._create_applescript_quoted_string(note_name)
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            if note_index is not None:
                script = f'''
                tell application "Notes"
                    try
                        set targetFolder to folder "{folder_path}"
                        set targetNote to missing value
                        set noteCount to 0
                        repeat with currentNote in notes of targetFolder
                            if name of currentNote is {quoted_note_name} then
                                set noteCount to noteCount + 1
                                if noteCount is {note_index} then
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
            if note_index is not None:
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
                            return "not_found"
                        end if
                        
                        set targetNote to missing value
                        set noteCount to 0
                        repeat with currentNote in notes of currentFolder
                            if name of currentNote is {quoted_note_name} then
                                set noteCount to noteCount + 1
                                if noteCount is {note_index} then
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
                            return "not_found"
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
        
        result = await UpdateNoteOperations.execute_applescript(script)
        if result.startswith("error:") or result == "not_found":
            return None
        return result
    
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
    async def update_note(note_name: str, folder_path: str = "Notes", 
                         new_name: Optional[str] = None, new_body: Optional[str] = None,
                         note_index: Optional[int] = None) -> Dict[str, str]:
        """Update an existing note's name and/or content.
        
        This unified method handles both simple folders and nested paths.
        At least one of new_name or new_body must be provided.
        
        Args:
            note_name: Current name of the note to update
            folder_path: Folder path where the note is located (default: "Notes")
            new_name: New name for the note (optional)
            new_body: New content for the note (optional)
            note_index: Index of the note to update if multiple notes have the same name (1-based, optional)
            
        Returns:
            Updated note metadata
            
        Raises:
            ValueError: If note name is empty or invalid, or if no updates provided
            RuntimeError: If folder path doesn't exist or note not found
        """
        # Validate that at least one update is provided
        if new_name is None and new_body is None:
            raise ValueError("At least one of new_name or new_body must be provided for update")
        
        # Validate note_index if provided
        if note_index is not None and note_index < 1:
            raise ValueError("note_index must be 1 or greater")
        
        # Validate inputs
        try:
            validated_note_name = UpdateNoteOperations._validate_note_name(note_name)
        except ValueError as e:
            # If name is too long, truncate it intelligently
            if "exceeds Apple Notes limit" in str(e):
                validated_note_name = UpdateNoteOperations._truncate_note_name(note_name)
                validated_note_name = UpdateNoteOperations._validate_note_name(validated_note_name)
            else:
                raise e
        
        # Validate new_name if provided
        validated_new_name = None
        if new_name is not None:
            try:
                validated_new_name = UpdateNoteOperations._validate_note_name(new_name)
            except ValueError as e:
                # If name is too long, truncate it intelligently
                if "exceeds Apple Notes limit" in str(e):
                    validated_new_name = UpdateNoteOperations._truncate_note_name(new_name)
                    validated_new_name = UpdateNoteOperations._validate_note_name(validated_new_name)
                else:
                    raise e
        
        # Validate new_body if provided
        validated_new_body = None
        if new_body is not None:
            validated_new_body = UpdateNoteOperations._validate_note_body(new_body)
        
        # Clean folder path
        folder_path = folder_path.strip()
        
        # Use the validated note name (which has backticks removed if present)
        note_name = validated_note_name
        
        # Check for duplicate new_name if provided
        if validated_new_name is not None:
            # First, we need to get the note ID to exclude it from duplicate check
            note_id = await UpdateNoteOperations._get_note_id(note_name, folder_path, note_index)
            if note_id:
                # Check for duplicate new_name, excluding the current note
                duplicate_exists = await UpdateNoteOperations._check_duplicate_note(validated_new_name, folder_path, note_id)
                if duplicate_exists:
                    raise ValueError(f"Note with name '{validated_new_name}' already exists in folder '{folder_path}'. Please use a different name.")
            else:
                # If we can't get the note ID, just check for any duplicate
                duplicate_exists = await UpdateNoteOperations._check_duplicate_note(validated_new_name, folder_path)
                if duplicate_exists:
                    raise ValueError(f"Note with name '{validated_new_name}' already exists in folder '{folder_path}'. Please use a different name.")
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            return await UpdateNoteOperations._update_note_in_simple_folder(
                note_name, folder_path, validated_new_name, validated_new_body, note_index
            )
        else:
            # Nested path - validate path exists and update note
            return await UpdateNoteOperations._update_note_in_nested_path(
                note_name, folder_path, validated_new_name, validated_new_body, note_index
            )
    
    @staticmethod
    async def _update_note_in_simple_folder(note_name: str, folder_name: str, 
                                          new_name: Optional[str], new_body: Optional[str],
                                          note_index: Optional[int] = None) -> Dict[str, str]:
        """Update a note in a simple folder (no nested paths) using note ID."""
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = UpdateNoteOperations._create_applescript_quoted_string(note_name)
        
        # Prepare update statements
        update_statements = []
        
        if new_name is not None:
            quoted_new_name = UpdateNoteOperations._create_applescript_quoted_string(new_name)
            update_statements.append(f'set name of targetNote to {quoted_new_name}')
        
        if new_body is not None:
            quoted_new_body = UpdateNoteOperations._create_applescript_quoted_string(new_body)
            update_statements.append(f'set body of targetNote to {quoted_new_body}')
        
        # Check if we have any updates to make
        if not update_statements:
            raise ValueError("No updates provided. At least one of new_name or new_body must be provided.")
        
        update_statements_text = '\n                    '.join(update_statements)
        

        
        script = f'''tell application "Notes"
    try
        set targetFolder to folder "{folder_name}"
        set targetNote to missing value
        set noteId to missing value
        set noteCount to 0
        repeat with currentNote in notes of targetFolder
            if name of currentNote is {quoted_note_name} then
                set noteCount to noteCount + 1
                if noteCount is 1 then
                    set targetNote to currentNote
                    set noteId to id of currentNote
                    exit repeat
                end if
            end if
        end repeat
        if targetNote is missing value then
            return "error:Note not found"
        end if
        if noteCount > 1 then
            return "error:Duplicate notes detected: Found " & noteCount & " notes with the same title '" & {quoted_note_name} & "' in folder '" & name of currentFolder & "'. Please rename the notes manually to have unique titles before proceeding with updates."
        end if
        {update_statements_text}
        return {{name:name of targetNote, folder:"{folder_name}", status:"updated", note_id:noteId}}
    on error errMsg
        return "error:" & errMsg
    end try
end tell'''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            error_msg = result[6:]
            if "Duplicate notes detected" in error_msg:
                raise RuntimeError(f"{error_msg}")
            elif "Note not found" in error_msg:
                if note_index:
                    raise RuntimeError(f"Note '{note_name}' not found at index {note_index} in folder '{folder_name}'")
                else:
                    raise RuntimeError(f"Note '{note_name}' not found in folder '{folder_name}'")
            elif "Can't get folder" in error_msg:
                raise RuntimeError(f"Folder '{folder_name}' does not exist")
            else:
                raise RuntimeError(f"Failed to update note: {error_msg}")
        
        return UpdateNoteOperations._parse_update_result(result, folder_name)
    
    @staticmethod
    async def _update_note_in_nested_path(note_name: str, folder_path: str, 
                                        new_name: Optional[str], new_body: Optional[str],
                                        note_index: Optional[int] = None) -> Dict[str, str]:
        """Update a note in a nested folder path using note ID. Path must exist."""
        # Validate that the folder path exists
        path_exists = await UpdateNoteOperations._check_path_exists(folder_path)
        if not path_exists:
            raise RuntimeError(f"Folder path '{folder_path}' does not exist. Please create the folder structure first.")
        
        # Parse the path components
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        # Use AppleScript's quoted form for better special character handling
        quoted_note_name = UpdateNoteOperations._create_applescript_quoted_string(note_name)
        
        # Prepare update statements
        update_statements = []
        
        if new_name is not None:
            quoted_new_name = UpdateNoteOperations._create_applescript_quoted_string(new_name)
            update_statements.append(f'set name of targetNote to {quoted_new_name}')
        
        if new_body is not None:
            quoted_new_body = UpdateNoteOperations._create_applescript_quoted_string(new_body)
            update_statements.append(f'set body of targetNote to {quoted_new_body}')
        
        # Check if we have any updates to make
        if not update_statements:
            raise ValueError("No updates provided. At least one of new_name or new_body must be provided.")
        
        update_statements_text = '\n                    '.join(update_statements)
        
        # Build the note selection logic based on note_index
        if note_index is not None:
            note_selection_logic = f'''
        set targetNote to missing value
        set noteId to missing value
        set noteCount to 0
        repeat with currentNote in notes of currentFolder
            if name of currentNote is {quoted_note_name} then
                set noteCount to noteCount + 1
                if noteCount is {note_index} then
                    set targetNote to currentNote
                    set noteId to id of currentNote
                    exit repeat
                end if
            end if
        end repeat
        if targetNote is missing value then
            return "error:Note not found at index {note_index}"
        end if'''
        else:
            note_selection_logic = f'''
        set targetNote to missing value
        set noteId to missing value
        set noteCount to 0
        repeat with currentNote in notes of currentFolder
            if name of currentNote is {quoted_note_name} then
                set noteCount to noteCount + 1
                if noteCount is 1 then
                    set targetNote to currentNote
                    set noteId to id of currentNote
                end if
            end if
        end repeat
        if noteCount is 0 then
            return "error:Note not found"
        end if
        if noteCount > 1 then
            return "error:Duplicate notes detected: Found " & noteCount & " notes with the same title. Please rename the notes manually to have unique titles before proceeding with updates."
        end if'''
        
        script = f'''tell application "Notes"
    try
        set currentFolder to missing value
        set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
        repeat with i from 1 to count of pathComponents
            set componentName to item i of pathComponents
            if currentFolder is missing value then
                repeat with rootFolder in folders
                    if name of rootFolder is componentName then
                        set currentFolder to rootFolder
                        exit repeat
                    end if
                end repeat
            else
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
        {note_selection_logic}
        {update_statements_text}
        return {{name:name of targetNote, folder:"{folder_path}", status:"updated", note_id:noteId}}
    on error errMsg
        return "error:" & errMsg
    end try
end tell'''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            error_msg = result[6:]
            if "Duplicate notes detected" in error_msg:
                raise RuntimeError(f"{error_msg}")
            elif "Note not found" in error_msg:
                if note_index:
                    raise RuntimeError(f"Note '{note_name}' not found at index {note_index} in folder path '{folder_path}'")
                else:
                    raise RuntimeError(f"Note '{note_name}' not found in folder path '{folder_path}'")
            elif "Target folder not found" in error_msg:
                raise RuntimeError(f"Folder path '{folder_path}' does not exist")
            else:
                raise RuntimeError(f"Failed to update note: {error_msg}")
        
        return UpdateNoteOperations._parse_update_result(result, folder_path)
    
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
            
            result = await UpdateNoteOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    def _parse_update_result(result: str, folder_path: str) -> Dict[str, str]:
        """Parse the AppleScript result and return note information."""
        try:
            # The result format is: name:value, folder:value, status:value, note_id:value, total_matches:value
            # Parse each field
            parts = result.split(', ')
            parsed = {}
            
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    parsed[key.strip()] = value.strip()
            
            # Return with default values for missing fields
            return {
                'name': parsed.get('name', 'Unknown'),
                'folder': parsed.get('folder', folder_path),
                'creation_date': parsed.get('creation_date', 'Unknown'),
                'modification_date': parsed.get('modification_date', 'Unknown'),
                'status': parsed.get('status', 'updated'),
                'note_id': parsed.get('note_id', None),
                'total_matches': parsed.get('total_matches', '1')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse updated note result: {str(e)}")
