from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils

class CreateFolderOperations(BaseAppleScriptOperations):
    """Operations for creating Apple Notes folders."""
    
    @staticmethod
    async def create_folder(folder_name: str) -> Dict[str, str]:
        """Create a new folder in Apple Notes (backward compatibility)."""
        script = f'''
        tell application "Notes"
            try
                set newFolder to make new folder with properties {{name:"{folder_name}"}}
                return {{name:(name of newFolder)}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        result = await CreateFolderOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to create folder: {result[6:]}")
        
        # Parse the result
        try:
            # Extract the folder information from the result
            # Format: {name:folderName}
            name_start = result.find('name:') + 5
            name_end = result.find('}', name_start)
            if name_end == -1:
                name_end = len(result)
            name = result[name_start:name_end].strip()
            
            return {
                'name': name,
                'status': 'created'
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse created folder result: {str(e)}")
    
    @staticmethod
    async def create_folder_with_path(folder_path: str) -> Dict[str, Any]:
        """Create a nested folder structure, creating parent folders if needed."""
        return await FolderPathUtils.create_nested_folder(folder_path)
