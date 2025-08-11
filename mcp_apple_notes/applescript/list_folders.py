from typing import List
from .base_operations import BaseAppleScriptOperations

class ListFoldersOperations(BaseAppleScriptOperations):
    """Operations for listing Apple Notes folders."""
    
    @staticmethod
    async def list_folders() -> List[str]:
        """Get a list of all folder names (root and subfolders)."""
        script = '''
tell application "Notes"
    set folderList to {}
    set allFolders to every folder
    repeat with currentFolder in allFolders
        set folderName to name of currentFolder
        set end of folderList to folderName
    end repeat
    return folderList
end tell
        '''
        
        result = await ListFoldersOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get folder list: {result[6:]}")
        
        # Parse the AppleScript list result
        # AppleScript returns lists as comma-separated values
        folder_names = []
        if result and result != "{}":
            # Remove curly braces and split by comma
            clean_result = result.strip('{}')
            folder_names = [name.strip() for name in clean_result.split(',') if name.strip()]
        
        return folder_names
