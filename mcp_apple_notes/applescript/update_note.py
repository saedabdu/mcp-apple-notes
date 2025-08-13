from typing import Dict, Optional, List
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils
from .validation_utils import ValidationUtils
from .note_id_utils import NoteIDUtils

class UpdateNoteOperations(BaseAppleScriptOperations):
    """Operations for updating Apple Notes content with HTML-based approach."""
    
    @staticmethod
    def _validate_note_name(name: str) -> str:
        """Validate and clean note name."""
        return ValidationUtils.validate_note_name(name)
    
    @staticmethod
    def _validate_note_body(body: str) -> str:
        """Validate note body."""
        return ValidationUtils.validate_note_body(body)
    
    @staticmethod
    async def _get_note_info_by_id(note_id: str) -> Dict[str, str]:
        """Get note information by primary key ID.
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1234")
            
        Returns:
            Dictionary with current_name and current_body
            
        Raises:
            RuntimeError: If note not found by ID
        """
        # Build full Core Data ID from primary key
        # First get a sample note to extract the store UUID
        script_get_uuid = '''
        tell application "Notes"
            try
                set sampleNote to note 1
                set sampleId to id of sampleNote as string
                return sampleId
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        sample_result = await UpdateNoteOperations.execute_applescript(script_get_uuid)
        if sample_result.startswith("error:"):
            raise RuntimeError(f"Could not get store UUID: {sample_result[6:]}")
        
        # Extract store UUID from sample ID
        # Format: x-coredata://UUID/ICNote/pXXX
        store_uuid = sample_result.split("//")[1].split("/")[0]
        full_note_id = f"x-coredata://{store_uuid}/ICNote/{note_id}"
        
        # Use AppleScript to get note info by ID
        script = f'''
        tell application "Notes"
            try
                set targetNote to note id "{full_note_id}"
                set noteName to name of targetNote
                set noteBody to body of targetNote
                
                -- Extract body content after the first h1 tag
                set bodyText to noteBody as string
                set h1Start to "<h1>"
                set h1End to "</h1>"
                
                if bodyText contains h1Start and bodyText contains h1End then
                    set h1StartPos to (offset of h1Start in bodyText) + (length of h1Start)
                    set h1EndPos to offset of h1End in bodyText
                    set titleText to text h1StartPos thru (h1EndPos - 1) of bodyText
                    set bodyStartPos to h1EndPos + (length of h1End)
                    set cleanBody to text bodyStartPos thru -1 of bodyText
                else
                    set titleText to noteName
                    set cleanBody to bodyText
                end if
                
                return {{name:titleText, body:cleanBody}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Note with ID '{note_id}' not found: {result[6:]}")
        
        return UpdateNoteOperations._parse_note_info_result(result)
    
    @staticmethod
    def _parse_note_info_result(result: str) -> Dict[str, str]:
        """Parse AppleScript result for note info."""
        try:
            # Extract name and body from result
            name_start = result.find('name:') + 5
            name_end = result.find(', body:', name_start)
            name = result[name_start:name_end].strip()
            
            body_start = result.find('body:') + 5
            body = result[body_start:].strip().rstrip('}')
            
            # Remove quotes if present
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            if body.startswith('"') and body.endswith('"'):
                body = body[1:-1]
            
            return {
                'current_name': name,
                'current_body': body
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse note info result: {str(e)}")
    
    @staticmethod
    async def _update_note_by_id_direct(note_id: str, html_content: str) -> Dict[str, str]:
        """Update note directly by ID with HTML content.
        
        Args:
            note_id: Primary key ID of the note
            html_content: HTML content including title
            
        Returns:
            Updated note metadata with primary key ID
        """
        # Build full Core Data ID from primary key using dynamic store UUID
        # First get a sample note to extract the store UUID
        script_get_uuid = '''
        tell application "Notes"
            try
                set sampleNote to note 1
                set sampleId to id of sampleNote as string
                return sampleId
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        sample_result = await UpdateNoteOperations.execute_applescript(script_get_uuid)
        if sample_result.startswith("error:"):
            raise RuntimeError(f"Could not get store UUID: {sample_result[6:]}")
        
        # Extract store UUID from sample ID
        store_uuid = sample_result.split("//")[1].split("/")[0]
        full_note_id = f"x-coredata://{store_uuid}/ICNote/{note_id}"
        
        # Use AppleScript to update note by ID
        script = f'''
        tell application "Notes"
            try
                set targetNote to note id "{full_note_id}"
                set body of targetNote to "{html_content}"
                
                return {{name:(name of targetNote), note_id:"{note_id}", creation_date:(creation date of targetNote as string), modification_date:(modification date of targetNote as string)}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to update note with ID '{note_id}': {result[6:]}")
        
        return UpdateNoteOperations._parse_update_result_by_id(result)
    
    @staticmethod
    def _parse_update_result_by_id(result: str) -> Dict[str, str]:
        """Parse AppleScript result for update by ID."""
        try:
            # Extract information from result
            name_start = result.find('name:') + 5
            name_end = result.find(', note_id:', name_start)
            name = result[name_start:name_end].strip()
            
            note_id_start = result.find('note_id:') + 8
            note_id_end = result.find(', creation_date:', note_id_start)
            note_id = result[note_id_start:note_id_end].strip()
            
            creation_start = result.find('creation_date:') + 14
            creation_end = result.find(', modification_date:', creation_start)
            creation_date = result[creation_start:creation_end].strip()
            
            modification_start = result.find('modification_date:') + 18
            modification_date = result[modification_start:].strip().rstrip('}')
            
            # Clean up quotes
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            if note_id.startswith('"') and note_id.endswith('"'):
                note_id = note_id[1:-1]
            
            return {
                'name': name,
                'note_id': note_id,
                'creation_date': creation_date,
                'modification_date': modification_date,
                'status': 'updated'
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse update result: {str(e)}")
    
    @staticmethod
    async def _get_note_info(note_name: str, folder_path: str) -> Dict[str, str]:
        """Get note information including ID, current name, and body using NoteIDUtils.
        
        Args:
            note_name: Name of the note to find
            folder_path: Folder path where the note is located
            
        Returns:
            Dictionary with note_id, current_name, current_body, and total_matches
            
        Raises:
            RuntimeError: If note not found or multiple notes with same name
        """
        # Use NoteIDUtils to get note ID with duplicate checking
        note_info = await NoteIDUtils.get_note_id_by_name_with_duplicate_check(note_name, folder_path)
        
        if note_info['status'] == 'multiple':
            raise RuntimeError(note_info['message'])
        
        # Get the note by ID to get current body content
        note_data = await NoteIDUtils.get_note_by_id(note_info['note_id'], folder_path)
        
        return {
            'note_id': note_info['note_id'],
            'current_name': note_info['name'],
            'current_body': note_data.get('body', ''),
            'total_matches': str(note_info['duplicate_count'])
        }
    
    @staticmethod
    async def _update_note_by_id(note_id: str, folder_path: str, html_content: str) -> Dict[str, str]:
        """Update note by ID with HTML content.
        
        Args:
            note_id: ID of the note to update
            folder_path: Folder path where the note is located
            html_content: Complete HTML content for the note
            
        Returns:
            Updated note metadata
        """
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{folder_path}"
                    set targetNote to missing value
                    
                    -- Find the note by ID
                    repeat with theNote in notes of targetFolder
                        if (id of theNote as string) is "{note_id}" then
                            set targetNote to theNote
                            exit repeat
                        end if
                    end repeat
                    
                    if targetNote is missing value then
                        return "error:Note not found"
                    end if
                    
                    -- Update the note with HTML content
                    set body of targetNote to "{html_content}"
                    
                    return "name:" & (name of targetNote as string) & ", folder:{folder_path}, status:updated, note_id:{note_id}, creation_date:" & (creation date of targetNote as string) & ", modification_date:" & (modification date of targetNote as string)
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
                    
                    -- Find the note by ID
                    repeat with theNote in notes of currentFolder
                        if (id of theNote as string) is "{note_id}" then
                            set targetNote to theNote
                            exit repeat
                        end if
                    end repeat
                    
                    if targetNote is missing value then
                        return "error:Note not found"
                    end if
                    
                    -- Update the note with HTML content
                    set body of targetNote to "{html_content}"
                    
                    return "name:" & (name of targetNote as string) & ", folder:{folder_path}, status:updated, note_id:{note_id}, creation_date:" & (creation date of targetNote as string) & ", modification_date:" & (modification date of targetNote as string)
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            error_msg = result[6:]
            if "Note not found" in error_msg:
                raise RuntimeError(f"Note with ID '{note_id}' not found in folder '{folder_path}'")
            elif "Target folder not found" in error_msg:
                raise RuntimeError(f"Folder path '{folder_path}' does not exist")
            else:
                raise RuntimeError(f"Failed to update note: {error_msg}")
        
        # Parse the result
        try:
            parts = result.split(', ')
            note_info = {}
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    note_info[key.strip()] = value.strip()
            
            return {
                'name': note_info.get('name', 'Unknown'),
                'folder': note_info.get('folder', folder_path),
                'status': note_info.get('status', 'updated'),
                'note_id': note_info.get('note_id', note_id),
                'creation_date': note_info.get('creation_date', 'Unknown'),
                'modification_date': note_info.get('modification_date', 'Unknown')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse update result: {str(e)}")
    
    @staticmethod
    async def update_note_by_id(note_id: str, new_name: Optional[str] = None, new_body: Optional[str] = None) -> Dict[str, str]:
        """Update an existing note by its primary key ID.
        
        This method handles partial updates:
        - If only new_name provided: Updates title, preserves current body
        - If only new_body provided: Updates body, preserves current title  
        - If both provided: Updates both title and body
        - If neither provided: Gets current name and body from ID and preserves both
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1234")
            new_name: New name for the note (optional)
            new_body: New HTML content for the note (optional)
            
        Returns:
            Updated note metadata with primary key ID
            
        Raises:
            ValueError: If note ID is invalid
            RuntimeError: If note not found by ID
        """
        # Validate note_id
        if not note_id or not note_id.strip():
            raise ValueError("Note ID cannot be empty")
        
        note_id = note_id.strip()
        
        # Get current note information by ID to retrieve current name and body if needed
        current_note_info = await UpdateNoteOperations._get_note_info_by_id(note_id)
        current_name = current_note_info['current_name']
        current_body = current_note_info['current_body']
        
        # Validate new_name if provided
        final_title = current_name  # Default to current name
        if new_name is not None:
            try:
                validated_new_name = UpdateNoteOperations._validate_note_name(new_name)
                final_title = validated_new_name
            except ValueError as e:
                raise e
        
        # Validate new_body if provided  
        final_body = current_body  # Default to current body
        if new_body is not None:
            validated_new_body = UpdateNoteOperations._validate_note_body(new_body)
            final_body = validated_new_body
        
        # Create HTML content with title wrapped in h1 tags
        html_content = f"<h1>{final_title}</h1>{final_body}"
        
        # Update the note using its ID
        return await UpdateNoteOperations._update_note_by_id_direct(note_id, html_content)
