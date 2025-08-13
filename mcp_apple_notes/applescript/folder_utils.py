from typing import List, Dict, Any
from .base_operations import BaseAppleScriptOperations
from .validation_utils import ValidationUtils

class FolderPathUtils(BaseAppleScriptOperations):
    """Utilities for handling nested folder paths in Apple Notes."""
    
    @staticmethod
    def parse_folder_path(folder_path: str) -> List[str]:
        """Parse a folder path into components."""
        if not folder_path:
            return ["Notes"]  # Default folder
        return [part.strip() for part in folder_path.split('/') if part.strip()]
    
    @staticmethod
    def _create_applescript_quoted_string(text: str) -> str:
        """Escape text for safe AppleScript usage."""
        return ValidationUtils.create_applescript_quoted_string(text)
    

    
    @staticmethod
    async def create_folder_in_existing_path(folder_path: str) -> Dict[str, Any]:
        """Create a folder in an existing path (does not create parent folders)."""
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        if len(path_components) == 1:
            # Single level - create at root
            escaped_name = FolderPathUtils._create_applescript_quoted_string(path_components[0])
            escaped_path = FolderPathUtils._create_applescript_quoted_string(folder_path)
            
            script = f'''
            tell application "Notes"
                try
                    set newFolder to make new folder with properties {{name:{escaped_name}}}
                    return {{name:(name of newFolder), path:{escaped_path}, created_folders:[{escaped_name}]}}
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Multi-level - navigate to parent and create
            parent_components = path_components[:-1]
            final_folder_name = path_components[-1]
            
            # Escape all strings for safe AppleScript usage
            escaped_parent_components = [FolderPathUtils._create_applescript_quoted_string(comp) for comp in parent_components]
            escaped_final_name = FolderPathUtils._create_applescript_quoted_string(final_folder_name)
            escaped_path = FolderPathUtils._create_applescript_quoted_string(folder_path)
            
            script = f'''
            tell application "Notes"
                try
                    set currentFolder to missing value
                    set pathComponents to {{{", ".join(escaped_parent_components)}}}
                    
                    -- Navigate to the parent folder
                    repeat with i from 1 to count of pathComponents
                        set componentName to item i of pathComponents
                        
                        if currentFolder is missing value then
                            -- Check root folders
                            set found to false
                            repeat with rootFolder in folders
                                if name of rootFolder is componentName then
                                    set currentFolder to rootFolder
                                    set found to true
                                    exit repeat
                                end if
                            end repeat
                            if not found then
                                return "error:Parent folder not found: " & componentName
                            end if
                        else
                            -- Check subfolders
                            set found to false
                            repeat with subFolder in folders of currentFolder
                                if name of subFolder is componentName then
                                    set currentFolder to subFolder
                                    set found to true
                                    exit repeat
                                end if
                            end repeat
                            if not found then
                                return "error:Parent folder not found: " & componentName
                            end if
                        end if
                    end repeat
                    
                    -- Create the final folder
                    set newFolder to make new folder at currentFolder with properties {{name:{escaped_final_name}}}
                    
                    return {{name:(name of newFolder), path:{escaped_path}, created_folders:[{escaped_final_name}]}}
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await FolderPathUtils.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to create folder in existing path: {result[6:]}")
        
        # Parse the result
        try:
            # Extract folder information from the result
            # Format: {name:folderName, path:folderPath, created_folders:[folderName]}
            name_start = result.find('name:') + 5
            name_end = result.find(', path:', name_start)
            if name_end == -1:
                raise RuntimeError("Could not parse folder name")
            name = result[name_start:name_end].strip()
            
            path_start = result.find('path:') + 5
            path_end = result.find(', created_folders:', path_start)
            if path_end == -1:
                path_end = len(result)
            path = result[path_start:path_end].strip()
            
            # Parse created folders list
            created_start = result.find('created_folders:') + 16
            created_end = result.find('}', created_start)
            if created_end == -1:
                created_end = len(result)
            created_folders_str = result[created_start:created_end].strip()
            
            created_folders = []
            if created_folders_str and created_folders_str != "{}":
                # Parse the list of created folder names
                created_folders = [name.strip() for name in created_folders_str.split(',') if name.strip()]
            
            return {
                'name': name,
                'path': path,
                'created_folders': created_folders,
                'components': path_components
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse folder creation result: {str(e)}")


    

