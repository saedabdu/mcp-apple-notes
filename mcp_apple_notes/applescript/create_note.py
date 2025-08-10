from typing import Dict
from .base_operations import BaseAppleScriptOperations

class CreateNoteOperations(BaseAppleScriptOperations):
    """Operations for creating Apple Notes."""
    
    @staticmethod
    async def create_note(name: str, body: str, folder_name: str = "Notes") -> Dict[str, str]:
        """Create a new note with specified name, body, and folder."""
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
        
        # Parse the result similar to list_all_notes
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
