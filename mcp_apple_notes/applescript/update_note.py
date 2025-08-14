from typing import Dict
from .base_operations import BaseAppleScriptOperations
from .validation_utils import ValidationUtils

class UpdateNoteOperations(BaseAppleScriptOperations):
    """Operations for updating Apple Notes by ID."""
    
    @staticmethod
    async def update_note_by_id(note_id: str, new_name=None, combined_content: str = None) -> Dict[str, str]:
        """Update an existing note by its primary key ID.
        
        Args:
            note_id: Primary key ID of the note (e.g., "p1234")
            new_name: Unused parameter for compatibility (should be None)
            combined_content: Complete HTML content combining title and body (e.g., '<h1>Title</h1><p>Content</p>')
            
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
        
        # Validate and prepare content
        if combined_content is None:
            raise ValueError("Combined content cannot be None")
        
        html_content = ValidationUtils.validate_note_body(combined_content)
        
        # Build full Core Data ID from primary key using dynamic store UUID
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
        
        # Escape HTML content for AppleScript
        escaped_html = ValidationUtils.create_applescript_quoted_string(html_content)
        
        # Use AppleScript to update note by ID
        script = f'''
        tell application "Notes"
            try
                set targetNote to note id "{full_note_id}"
                set body of targetNote to {escaped_html}
                
                return {{name:(name of targetNote), note_id:"{note_id}", creation_date:(creation date of targetNote as string), modification_date:(modification date of targetNote as string)}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await UpdateNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to update note with ID '{note_id}': {result[6:]}")
        
        return UpdateNoteOperations._parse_update_result(result)
    
    @staticmethod
    def _parse_update_result(result: str) -> Dict[str, str]:
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