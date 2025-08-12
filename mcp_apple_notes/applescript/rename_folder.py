from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations

class RenameFolderOperations(BaseAppleScriptOperations):
    """Operations for renaming folders in Apple Notes."""
    
    @staticmethod
    async def rename_folder(folder_path: str, current_name: str, new_name: str) -> Dict[str, Any]:
        """Rename a folder in Apple Notes."""
        script = f'''
tell application "Notes"
    try
        set targetFolder to missing value
        
        -- Handle root level folder rename (when folder_path is empty or same as current_name)
        if "{folder_path}" is "" or "{folder_path}" is "{current_name}" then
            repeat with rootFolder in folders
                if name of rootFolder is "{current_name}" then
                    set name of rootFolder to "{new_name}"
                    return {{"success", "{current_name}", "{new_name}", "root"}}
                end if
            end repeat
            return "error:Root folder '{current_name}' not found"
        end if
        
        -- Handle nested folder rename
        set pathParts to my splitString("{folder_path}", "/")
        set currentFolder to missing value
        
        -- Navigate to the parent folder (the folder_path is the parent)
        repeat with i from 1 to count of pathParts
            set partName to item i of pathParts
            
            if currentFolder is missing value then
                -- Check root folders
                set found to false
                repeat with rootFolder in folders
                    if name of rootFolder is partName then
                        set currentFolder to rootFolder
                        set found to true
                        exit repeat
                    end if
                end repeat
                if not found then
                    return "error:Parent folder path not found: " & partName
                end if
            else
                -- Check subfolders
                set found to false
                repeat with subFolder in folders of currentFolder
                    if name of subFolder is partName then
                        set currentFolder to subFolder
                        set found to true
                        exit repeat
                    end if
                end repeat
                if not found then
                    return "error:Parent folder path not found: " & partName
                end if
            end if
        end repeat
        
        -- Now find and rename the target folder
        if currentFolder is not missing value then
            repeat with targetFolder in folders of currentFolder
                if name of targetFolder is "{current_name}" then
                    set name of targetFolder to "{new_name}"
                    return {{"success", "{current_name}", "{new_name}", "{folder_path}"}}
                end if
            end repeat
            return "error:Target folder '{current_name}' not found in path '{folder_path}'"
        else
            return "error:Could not navigate to parent folder"
        end if
        
    on error errMsg
        return "error:" & errMsg
    end try
end tell

on splitString(inputString, delimiter)
    set AppleScript's text item delimiters to delimiter
    set stringList to text items of inputString
    set AppleScript's text item delimiters to ""
    return stringList
end splitString
        '''
        
        result = await RenameFolderOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to rename folder: {result[6:]}")
        
        # Parse the success result
        try:
            return RenameFolderOperations._parse_rename_result(result)
        except Exception as e:
            raise RuntimeError(f"Failed to parse rename result: {str(e)}")
    
    @staticmethod
    def _parse_rename_result(result: str) -> Dict[str, Any]:
        """Parse the rename result into a structured format."""
        try:
            # Parse the AppleScript list result
            # Format: {"success", current_name, new_name, folder_path}
            
            # Remove outer braces and split by comma
            clean_result = result.strip('{}')
            parts = [part.strip().strip('"') for part in clean_result.split(',') if part.strip()]
            
            if len(parts) >= 4 and parts[0] == "success":
                return {
                    "status": "success",
                    "current_name": parts[1],
                    "new_name": parts[2],
                    "folder_path": parts[3],
                    "message": f"Successfully renamed folder from '{parts[1]}' to '{parts[2]}'"
                }
            else:
                raise RuntimeError("Invalid rename result format")
                
        except Exception as e:
            raise RuntimeError(f"Failed to parse rename result: {str(e)}")
