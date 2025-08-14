from typing import Dict
from .base_operations import BaseAppleScriptOperations

class ReadNoteOperations(BaseAppleScriptOperations):
    """Operations for reading Apple Notes by ID."""
    
    @staticmethod
    async def read_note_by_id(note_id: str, folder_path: str = "Notes") -> Dict[str, str]:
        """Read a note by its primary key ID with folder path verification.
        
        This method verifies that the note with the given ID exists in the specified 
        folder path before reading, providing better error handling and security.
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1308")
            folder_path: Folder path where the note should be located (default: "Notes")
            
        Returns:
            Note data with content, metadata, and verification info
            
        Raises:
            ValueError: If note ID is empty or invalid
            RuntimeError: If folder path doesn't exist, note not found, or note not in specified folder
        """
        # Validate inputs
        if not note_id or not note_id.strip():
            raise ValueError("Note ID cannot be empty or contain only whitespace")
        
        note_id = note_id.strip()
        
        # Validate folder path
        if not folder_path or not folder_path.strip():
            folder_path = "Notes"
        folder_path = folder_path.strip()
        
        # Check if folder path exists
        from .validation_utils import ValidationUtils
        if not await ValidationUtils.check_path_exists(folder_path):
            raise RuntimeError(f"Folder path '{folder_path}' does not exist")
        
        # Verify that the note exists in the specified folder by searching all notes
        try:
            from .note_id_utils import NoteIDUtils
            all_notes = await NoteIDUtils.get_all_notes_in_folder(folder_path)
            
            # Look for a note with matching primary key ID
            note_found = False
            for note in all_notes:
                # Extract primary key from the full ID
                note_primary_key = NoteIDUtils.extract_primary_key(note['id'])
                if note_primary_key == note_id:
                    note_found = True
                    break
            
            if not note_found:
                raise RuntimeError(f"Note with ID '{note_id}' not found in folder path '{folder_path}'")
                
        except RuntimeError as e:
            if "not found" in str(e).lower():
                raise RuntimeError(f"Note with ID '{note_id}' not found in folder path '{folder_path}'")
            else:
                raise e
        
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
        
        sample_result = await ReadNoteOperations.execute_applescript(script_get_uuid)
        if sample_result.startswith("error:"):
            raise RuntimeError(f"Could not get store UUID for reading: {sample_result[6:]}")
        
        # Extract store UUID from sample ID
        store_uuid = sample_result.split("//")[1].split("/")[0]
        full_note_id = f"x-coredata://{store_uuid}/ICNote/{note_id}"
        
        # Read the note using the full note ID
        script = f'''
        tell application "Notes"
            try
                set targetNote to note id "{full_note_id}"
                
                set noteName to name of targetNote
                set noteId to id of targetNote
                set noteBody to body of targetNote
                set creationDate to creation date of targetNote
                set modificationDate to modification date of targetNote
                
                return "success:" & noteName & "|||" & noteId & "|||" & noteBody & "|||" & creationDate & "|||" & modificationDate
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            error_msg = result[6:]
            if "Note not found" in error_msg or "not found" in error_msg:
                raise RuntimeError(f"Note with ID '{note_id}' not found")
            else:
                raise RuntimeError(f"Failed to read note: {error_msg}")
        
        return ReadNoteOperations._parse_read_by_id_result(result, folder_path, note_id)
    
    @staticmethod
    def _parse_read_by_id_result(result: str, folder_path: str, note_id: str) -> Dict[str, str]:
        """Parse the AppleScript result for read by ID and return note information."""
        try:
            # The result format is: success:name|||full_id|||body|||creation_date|||modification_date
            if result.startswith("success:"):
                content = result[8:]  # Remove "success:" prefix
                parts = content.split("|||")
                
                if len(parts) >= 5:
                    from .note_id_utils import NoteIDUtils
                    # Extract primary key from full ID
                    primary_key = NoteIDUtils.extract_primary_key(parts[1])
                    
                    return {
                        'name': parts[0],
                        'note_id': primary_key,
                        'body': parts[2],
                        'creation_date': parts[3],
                        'modification_date': parts[4],
                        'folder': folder_path,
                        'status': 'found',
                        'read_method': 'by_id'
                    }
                else:
                    return {
                        'name': 'Unknown',
                        'note_id': note_id,
                        'body': 'Could not retrieve content',
                        'creation_date': 'Unknown',
                        'modification_date': 'Unknown',
                        'folder': folder_path,
                        'status': 'found',
                        'read_method': 'by_id'
                    }
            else:
                raise RuntimeError(f"Unexpected result format: {result}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse read by ID result: {str(e)}")