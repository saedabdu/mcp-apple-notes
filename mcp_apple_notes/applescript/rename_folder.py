from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations
from .validation_utils import ValidationUtils

class RenameFolderOperations(BaseAppleScriptOperations):
    """Operations for renaming folders in Apple Notes."""
    
    @staticmethod
    def _create_applescript_quoted_string(text: str) -> str:
        """Escape text for safe AppleScript usage."""
        return ValidationUtils.create_applescript_quoted_string(text)
    
    @staticmethod
    async def _check_duplicate_name(new_name: str, folder_path: str, current_name: str) -> None:
        """Check if the new folder name would create a duplicate."""
        # Get all folder names in the target location
        if not folder_path:
            # Root level - check root folders
            script = '''
            tell application "Notes"
                try
                    set folderNames to {}
                    repeat with rootFolder in folders
                        set end of folderNames to name of rootFolder
                    end repeat
                    return folderNames
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Nested level - navigate to parent and check subfolders
            path_components = ValidationUtils.parse_folder_path(folder_path)
            script = f'''
            tell application "Notes"
                try
                    set currentFolder to missing value
                    set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
                    
                    repeat with i from 1 to count of pathComponents
                        set componentName to item i of pathComponents
                        
                        if currentFolder is missing value then
                            repeat with rootFolder in folders
                                if name of rootFolder is componentName then
                                    set currentFolder to rootFolder
                                    exit repeat
                                end if
                            end repeat
                        else
                            repeat with subFolder in folders of currentFolder
                                if name of subFolder is componentName then
                                    set currentFolder to subFolder
                                    exit repeat
                                end if
                            end repeat
                        end if
                    end repeat
                    
                    if currentFolder is missing value then
                        return "error:Path not found"
                    end if
                    
                    set folderNames to {{}}
                    repeat with subFolder in folders of currentFolder
                        set end of folderNames to name of subFolder
                    end repeat
                    return folderNames
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await RenameFolderOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to check duplicates: {result[6:]}")
        
        # Parse folder names and check for duplicates
        if result and result != "{}":
            # Split the result by comma and check each name
            folder_names = [name.strip().strip('"') for name in result.split(',') if name.strip()]
            
            for folder_name in folder_names:
                # Check if the new name already exists (excluding the current folder being renamed)
                if folder_name == new_name:
                    # Only raise error if it's not the same folder being renamed
                    # OR if the new name is different from current name
                    if folder_name != current_name:
                        location = "root level" if not folder_path else f"folder '{folder_path}'"
                        raise ValueError(f"A folder named '{new_name}' already exists in {location}")
    
    @staticmethod
    async def rename_folder(folder_path: str, current_name: str, new_name: str) -> Dict[str, Any]:
        """Rename a folder in Apple Notes with comprehensive validation."""
        # Validate inputs using the same validation as create_folder
        try:
            # Validate folder names
            validated_current_name = ValidationUtils.validate_folder_name(current_name)
            validated_new_name = ValidationUtils.validate_folder_name(new_name)
            
            # Validate folder path if provided
            validated_folder_path = ValidationUtils.validate_folder_path(folder_path)
            
            # Check if new name is same as current name
            if validated_current_name == validated_new_name:
                raise ValueError("New folder name cannot be the same as current name")
                
        except ValueError as e:
            raise ValueError(f"Invalid input: {str(e)}")
        
        # Check if the folder path exists (if provided)
        if validated_folder_path:
            path_exists = await ValidationUtils.check_path_exists(validated_folder_path)
            if not path_exists:
                raise RuntimeError(f"Folder path '{validated_folder_path}' does not exist")
        
        # Check for duplicate folder names in the target location
        await RenameFolderOperations._check_duplicate_name(validated_new_name, validated_folder_path, validated_current_name)
        
        # Escape all strings for safe AppleScript usage
        escaped_folder_path = RenameFolderOperations._create_applescript_quoted_string(validated_folder_path)
        escaped_current_name = RenameFolderOperations._create_applescript_quoted_string(validated_current_name)
        escaped_new_name = RenameFolderOperations._create_applescript_quoted_string(validated_new_name)
        
        script = f'''
tell application "Notes"
    try
        set targetFolder to missing value
        
        -- Handle root level folder rename (when folder_path is empty or same as current_name)
        if {escaped_folder_path} is "" or {escaped_folder_path} is {escaped_current_name} then
            repeat with rootFolder in folders
                if name of rootFolder is {escaped_current_name} then
                    set name of rootFolder to {escaped_new_name}
                    return {{"success", {escaped_current_name}, {escaped_new_name}, "root"}}
                end if
            end repeat
            return "error:Root folder " & {escaped_current_name} & " not found"
        end if
        
        -- Handle nested folder rename
        set pathParts to my splitString({escaped_folder_path}, "/")
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
                if name of targetFolder is {escaped_current_name} then
                    set name of targetFolder to {escaped_new_name}
                    return {{"success", {escaped_current_name}, {escaped_new_name}, {escaped_folder_path}}}
                end if
            end repeat
            return "error:Target folder " & {escaped_current_name} & " not found in path " & {escaped_folder_path}
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
