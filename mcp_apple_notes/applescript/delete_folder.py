import asyncio
import subprocess
from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations

class DeleteFolderOperations(BaseAppleScriptOperations):
    """Operations for deleting folders in Apple Notes."""
    
    @staticmethod
    async def delete_folder(folder_name: str, folder_path: str = "") -> Dict[str, Any]:
        """Delete a folder in Apple Notes.
        
        Args:
            folder_name: Name of the folder to delete
            folder_path: Path where the folder is located (empty for root level)
            
        Returns:
            Dictionary with deletion result details
        """
        try:
            # Build the AppleScript command
            if folder_path:
                # Delete folder in nested path
                script = f'''
                tell application "Notes"
                    set targetFolder to folder "{folder_name}" of folder "{folder_path}"
                    delete targetFolder
                    return "success"
                end tell
                '''
            else:
                # Delete folder at root level
                script = f'''
                tell application "Notes"
                    set targetFolder to folder "{folder_name}"
                    delete targetFolder
                    return "success"
                end tell
                '''
            
            # Execute the AppleScript
            result = await DeleteFolderOperations.execute_applescript(script)
            
            return {
                'folder_name': folder_name,
                'folder_path': folder_path if folder_path else "root level",
                'status': 'deleted',
                'message': 'Folder deleted successfully'
            }
            
        except subprocess.CalledProcessError as e:
            # Handle AppleScript errors
            error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise RuntimeError(f"Failed to delete folder: {error_message}")
        except Exception as e:
            # Handle other errors
            raise RuntimeError(f"Unexpected error deleting folder: {str(e)}")
