from typing import List
from .base_operations import BaseAppleScriptOperations

class ListFoldersOperations(BaseAppleScriptOperations):
    """Operations for listing Apple Notes folders."""
    
    @staticmethod
    async def list_all_folders() -> List[str]:
        """Get all folder names."""
        script = '''
        tell application "Notes"
            set folderList to {}
            repeat with theFolder in folders
                copy (name of theFolder) to end of folderList
            end repeat
            return folderList
        end tell
        '''
        result = await ListFoldersOperations.execute_applescript(script)
        
        # Parse AppleScript result and convert to list of folder names
        if result:
            # Split by commas and clean up each name
            folder_names = [name.strip() for name in result.split(',') if name.strip()]
            return folder_names
        else:
            return []
