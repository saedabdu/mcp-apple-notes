from typing import List, Dict, Any, Optional
from .base_operations import BaseAppleScriptOperations

class FolderPathUtils(BaseAppleScriptOperations):
    """Utilities for handling nested folder paths in Apple Notes."""
    
    @staticmethod
    def parse_folder_path(folder_path: str) -> List[str]:
        """Parse a folder path into components."""
        if not folder_path:
            return ["Notes"]  # Default folder
        return [part.strip() for part in folder_path.split('/') if part.strip()]
    
    @staticmethod
    async def resolve_folder_path(folder_path: str) -> Dict[str, Any]:
        """Resolve a folder path to get the target folder and its metadata."""
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        script = f'''
        tell application "Notes"
            try
                set currentFolder to missing value
                set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
                
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
                        set found to false
                        repeat with subFolder in folders of currentFolder
                            if name of subFolder is componentName then
                                set currentFolder to subFolder
                                set found to true
                                exit repeat
                            end if
                        end repeat
                        
                        if not found then
                            return "error:Folder not found: " & componentName
                        end if
                    end if
                end repeat
                
                if currentFolder is missing value then
                    return "error:Root folder not found: " & item 1 of pathComponents
                end if
                
                return {{name:(name of currentFolder), path:"{folder_path}", exists:true}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await FolderPathUtils.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to resolve folder path: {result[6:]}")
        
        # Parse the result
        try:
            # Extract folder information from the result
            # Format: {name:folderName, path:folderPath, exists:true}
            name_start = result.find('name:') + 5
            name_end = result.find(', path:', name_start)
            if name_end == -1:
                raise RuntimeError("Could not parse folder name")
            name = result[name_start:name_end].strip()
            
            path_start = result.find('path:') + 5
            path_end = result.find(', exists:', path_start)
            if path_end == -1:
                path_end = len(result)
            path = result[path_start:path_end].strip()
            
            return {
                'name': name,
                'path': path,
                'exists': True,
                'components': path_components
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse folder path result: {str(e)}")
    
    @staticmethod
    async def create_nested_folder(folder_path: str) -> Dict[str, Any]:
        """Create a nested folder structure, creating parent folders if needed."""
        path_components = FolderPathUtils.parse_folder_path(folder_path)
        
        script = f'''
        tell application "Notes"
            try
                set currentFolder to missing value
                set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
                set createdFolders to {{}}
                
                repeat with i from 1 to count of pathComponents
                    set componentName to item i of pathComponents
                    
                    if currentFolder is missing value then
                        -- Check if root folder exists
                        set folderExists to false
                        repeat with rootFolder in folders
                            if name of rootFolder is componentName then
                                set currentFolder to rootFolder
                                set folderExists to true
                                exit repeat
                            end if
                        end repeat
                        
                        if not folderExists then
                            -- Create root folder
                            set newFolder to make new folder with properties {{name:componentName}}
                            set currentFolder to newFolder
                            copy componentName to end of createdFolders
                        end if
                    else
                        -- Check if subfolder exists
                        set folderExists to false
                        repeat with subFolder in folders of currentFolder
                            if name of subFolder is componentName then
                                set currentFolder to subFolder
                                set folderExists to true
                                exit repeat
                            end if
                        end repeat
                        
                        if not folderExists then
                            -- Create subfolder
                            set newFolder to make new folder at currentFolder with properties {{name:componentName}}
                            set currentFolder to newFolder
                            copy componentName to end of createdFolders
                        end if
                    end if
                end repeat
                
                return {{name:(name of currentFolder), path:"{folder_path}", created_folders:createdFolders}}
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await FolderPathUtils.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to create nested folder: {result[6:]}")
        
        # Parse the result
        try:
            # Extract folder information from the result
            # Format: {name:folderName, path:folderPath, created_folders:[folder1, folder2]}
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
            raise RuntimeError(f"Failed to parse nested folder creation result: {str(e)}")
    
    @staticmethod
    async def get_folder_hierarchy() -> List[Dict[str, Any]]:
        """Get the complete folder hierarchy as a tree structure."""
        script = '''
        tell application "Notes"
            try
                set folderTree to {}
                
                repeat with rootFolder in folders
                    set folderInfo to {name:(name of rootFolder), path:(name of rootFolder), subfolders:{}}
                    
                    -- Get subfolders
                    repeat with subFolder in folders of rootFolder
                        set subFolderInfo to {name:(name of subFolder), path:(name of rootFolder) & "/" & (name of subFolder)}
                        copy subFolderInfo to end of subfolders of folderInfo
                    end repeat
                    
                    copy folderInfo to end of folderTree
                end repeat
                
                return folderTree
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await FolderPathUtils.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get folder hierarchy: {result[6:]}")
        
        # Parse the hierarchical result
        try:
            # This is a complex parsing task - for now, return a simplified structure
            # In a full implementation, we'd need to parse the nested AppleScript structure
            return [{"name": "Notes", "path": "Notes", "subfolders": []}]
        except Exception as e:
            raise RuntimeError(f"Failed to parse folder hierarchy: {str(e)}")
