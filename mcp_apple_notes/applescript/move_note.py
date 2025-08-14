from typing import Dict
from .base_operations import BaseAppleScriptOperations
from .validation_utils import ValidationUtils

class MoveNoteOperations(BaseAppleScriptOperations):
    """Operations for moving Apple Notes between folders."""
    
    @staticmethod
    async def move_note(note_id: str, source_folder_path: str, target_folder_path: str) -> Dict[str, str]:
        """Move a note from source folder to target folder.
        
        This method performs comprehensive validation before moving:
        1. Validate note ID is not empty
        2. Check source and target paths are different
        3. Verify note exists in source folder
        4. Verify target folder path exists
        5. Perform move operation using simple AppleScript
        
        Args:
            note_id: Primary key ID of the note to move (e.g., "p1308")
            source_folder_path: Current folder path where note is located
            target_folder_path: Target folder path where to move the note
            
        Returns:
            Move result with status and details
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If note not found, paths don't exist, or move fails
        """
        # Step 1: Validate note ID is not empty
        if not note_id or not note_id.strip():
            raise ValueError("Note ID cannot be empty")
        
        note_id = note_id.strip()
        
        # Step 2: Check source and target paths are different
        if source_folder_path.strip() == target_folder_path.strip():
            raise ValueError("Source and target folder paths must be different")
        
        # Clean and validate paths
        source_folder_path = ValidationUtils.validate_folder_path(source_folder_path)
        target_folder_path = ValidationUtils.validate_folder_path(target_folder_path)
        
        # Step 3: Verify note exists in source folder
        note_exists = await MoveNoteOperations._verify_note_in_folder(note_id, source_folder_path)
        if not note_exists:
            raise RuntimeError(f"Note with ID '{note_id}' not found in source folder '{source_folder_path}'")
        
        # Step 4: Verify target folder path exists
        target_exists = await ValidationUtils.check_path_exists(target_folder_path)
        if not target_exists:
            raise RuntimeError(f"Target folder path '{target_folder_path}' does not exist")
        
        # Step 5: Perform move operation using simple AppleScript
        return await MoveNoteOperations._perform_move_operation(note_id, source_folder_path, target_folder_path)
    
    @staticmethod
    async def _verify_note_in_folder(note_id: str, folder_path: str) -> bool:
        """Verify that a note exists in the specified folder."""
        # Escape parameters for AppleScript
        escaped_note_id = ValidationUtils.create_applescript_quoted_string(note_id)
        
        # Handle root level vs nested path
        if not folder_path or folder_path.strip() == "":
            # Root level - check in root folders
            script = f'''
            tell application "Notes"
                try
                    repeat with rootFolder in folders
                        repeat with noteItem in notes of rootFolder
                            set noteId to id of noteItem as string
                            if noteId ends with {escaped_note_id} then
                                return "true"
                            end if
                        end repeat
                    end repeat
                    return "false"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Nested path - navigate to folder
            path_components = ValidationUtils.parse_folder_path(folder_path)
            
            script = f'''
            tell application "Notes"
                try
                    set currentFolder to missing value
                    set pathComponents to {{{", ".join([ValidationUtils.create_applescript_quoted_string(component) for component in path_components])}}}
                    
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
                    
                    -- Check if note exists in the target folder
                    if currentFolder is not missing value then
                        repeat with noteItem in notes of currentFolder
                            set noteId to id of noteItem as string
                            if noteId ends with {escaped_note_id} then
                                return "true"
                            end if
                        end repeat
                    end if
                    
                    return "false"
                    
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Error verifying note: {result[6:]}")
        
        return result.strip() == "true"
    
    @staticmethod
    async def _perform_move_operation(note_id: str, source_folder_path: str, target_folder_path: str) -> Dict[str, str]:
        """Perform the move operation using simple AppleScript."""
        # Get the full note ID (we need the complete x-coredata:// URL)
        full_note_id = await MoveNoteOperations._get_full_note_id(note_id, source_folder_path)
        
        # Escape parameters for AppleScript
        escaped_full_note_id = ValidationUtils.create_applescript_quoted_string(full_note_id)
        escaped_target_folder = ValidationUtils.create_applescript_quoted_string(target_folder_path)
        
        # Simple move operation
        script = f'''
        tell application "Notes"
            try
                move note id {escaped_full_note_id} to folder {escaped_target_folder}
                return "moved:success:{note_id}:{source_folder_path}:{target_folder_path}"
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to move note: {result[6:]}")
        
        return MoveNoteOperations._parse_move_result(result, note_id, source_folder_path, target_folder_path)
    
    @staticmethod
    async def _get_full_note_id(note_id: str, folder_path: str) -> str:
        """Get the full note ID (x-coredata:// URL) from the short ID."""
        # Escape parameters for AppleScript
        escaped_note_id = ValidationUtils.create_applescript_quoted_string(note_id)
        
        # Handle root level vs nested path
        if not folder_path or folder_path.strip() == "":
            # Root level - check in root folders
            script = f'''
            tell application "Notes"
                try
                    repeat with rootFolder in folders
                        repeat with noteItem in notes of rootFolder
                            set noteId to id of noteItem as string
                            if noteId ends with {escaped_note_id} then
                                return noteId
                            end if
                        end repeat
                    end repeat
                    return "error:Note not found"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Nested path - navigate to folder
            path_components = ValidationUtils.parse_folder_path(folder_path)
            
            script = f'''
            tell application "Notes"
                try
                    set currentFolder to missing value
                    set pathComponents to {{{", ".join([ValidationUtils.create_applescript_quoted_string(component) for component in path_components])}}}
                    
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
                    
                    -- Get note ID from the target folder
                    if currentFolder is not missing value then
                        repeat with noteItem in notes of currentFolder
                            set noteId to id of noteItem as string
                            if noteId ends with {escaped_note_id} then
                                return noteId
                            end if
                        end repeat
                    end if
                    
                    return "error:Note not found"
                    
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Error getting full note ID: {result[6:]}")
        
        return result.strip()
    
    @staticmethod
    def _parse_move_result(result: str, note_id: str, source_folder_path: str, target_folder_path: str) -> Dict[str, str]:
        """Parse the AppleScript result and return structured data."""
        try:
            if result.startswith("moved:success:"):
                # Parse the moved result format: "moved:success:noteId:sourceFolder:targetFolder"
                parts = result.split(":")
                if len(parts) >= 5:
                    note_id = parts[2]
                    source_folder = parts[3]
                    target_folder = parts[4]
                    
                    return {
                        "name": f"Note {note_id}",
                        "note_id": note_id,
                        "source_folder": source_folder,
                        "target_folder": target_folder,
                        "status": "moved",
                        "message": "Note moved successfully",
                        "creation_date": "N/A",
                        "modification_date": "N/A"
                    }
            
            # Fallback to input-based response
            return {
                "name": f"Note {note_id}",
                "note_id": note_id,
                "source_folder": source_folder_path or "Root",
                "target_folder": target_folder_path or "Root",
                "status": "moved",
                "message": "Note moved successfully",
                "creation_date": "N/A",
                "modification_date": "N/A"
            }
        except Exception as e:
            raise RuntimeError(f"Error parsing move result: {str(e)}")
