from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils

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
    
    @staticmethod
    async def create_note_in_path(name: str, body: str, folder_path: str) -> Dict[str, str]:
        """Create a new note with specified name, body, and folder path."""
        # First ensure the folder path exists
        folder_info = await FolderPathUtils.create_nested_folder(folder_path)
        
        # Then create the note in that folder
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
        
        # Parse the result similar to the original method
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
