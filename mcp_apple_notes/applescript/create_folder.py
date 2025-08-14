from typing import Dict, Any, List
from .base_operations import BaseAppleScriptOperations

from .validation_utils import ValidationUtils

class CreateFolderOperations(BaseAppleScriptOperations):
    """Operations for creating Apple Notes folders."""
    
    # Maximum nesting depth allowed by Apple Notes
    MAX_NESTING_DEPTH = 5
    
    @staticmethod
    def _validate_folder_name(folder_name: str) -> str:
        """Validate and clean folder name."""
        return ValidationUtils.validate_folder_name(folder_name)
    
    @staticmethod
    def _validate_folder_path(folder_path: str) -> str:
        """Validate and clean folder path."""
        return ValidationUtils.validate_folder_path(folder_path)
    
    @staticmethod
    def _validate_nesting_depth(folder_path: str, folder_name: str) -> None:
        """Validate that the folder creation won't exceed maximum nesting depth.
        
        Args:
            folder_path: The path where the folder will be created
            folder_name: The name of the folder to create
            
        Raises:
            ValueError: If the nesting depth would exceed the maximum allowed
        """
        ValidationUtils.validate_nesting_depth(folder_path, folder_name, "create")
    
    @staticmethod
    async def _check_path_exists(folder_path: str) -> bool:
        """Check if a folder path exists."""
        return await ValidationUtils.check_path_exists(folder_path)
    
    @staticmethod
    def _create_applescript_quoted_string(text: str) -> str:
        """Escape text for safe AppleScript usage."""
        return ValidationUtils.create_applescript_quoted_string(text)
    
    @staticmethod
    async def create_folder(folder_name: str, folder_path: str = "") -> Dict[str, Any]:
        """Create a folder in Apple Notes.
        
        Args:
            folder_name: Name of the folder to create
            folder_path: Optional path where to create the folder. If empty, creates at root level.
        """
        # Validate and clean folder name
        folder_name = CreateFolderOperations._validate_folder_name(folder_name)
        
        if not folder_path:
            # Create at root level - validate nesting depth
            CreateFolderOperations._validate_nesting_depth("", folder_name)
            return await CreateFolderOperations._create_root_folder(folder_name)
        else:
            # Validate and clean folder path
            try:
                folder_path = CreateFolderOperations._validate_folder_path(folder_path)
                if not folder_path:
                    # Empty path after validation, create at root level
                    CreateFolderOperations._validate_nesting_depth("", folder_name)
                    return await CreateFolderOperations._create_root_folder(folder_name)
                
                # Validate nesting depth before checking path existence
                CreateFolderOperations._validate_nesting_depth(folder_path, folder_name)
                
                # Check if the parent path exists
                path_exists = await CreateFolderOperations._check_path_exists(folder_path)
                if not path_exists:
                    # Provide helpful error message with suggestions
                    raise RuntimeError(
                        f"Invalid folder path '{folder_path}'. The specified path does not exist. "
                        f"Available options:\n"
                        f"1. Create the parent folders first using: create_folder('parent_folder_name')\n"
                        f"2. Use a valid existing path\n"
                        f"3. Create at root level by omitting the folder_path parameter"
                    )
                
                # Create in specified path (only if path exists)
                full_path = f"{folder_path}/{folder_name}"
                return await CreateFolderOperations._create_nested_folder(full_path)
            except ValueError as e:
                # Re-raise validation errors
                raise
            except RuntimeError as e:
                # Provide more helpful error messages
                error_msg = str(e)
                if "not found" in error_msg.lower():
                    raise RuntimeError(f"Invalid folder path '{folder_path}'. The specified path does not exist. Please check the path and try again.")
                elif "permission" in error_msg.lower():
                    raise RuntimeError(f"Permission denied when creating folder '{folder_name}' in path '{folder_path}'. Please check your Apple Notes permissions.")
                else:
                    raise RuntimeError(f"Failed to create folder '{folder_name}' in path '{folder_path}': {error_msg}")
    
    @staticmethod
    async def _create_root_folder(folder_name: str) -> Dict[str, str]:
        """Create a new folder in Apple Notes (root level)."""
        # Escape the folder name for safe AppleScript usage
        escaped_name = CreateFolderOperations._create_applescript_quoted_string(folder_name)
        
        script = f'''
        tell application "Notes"
            try
                set newFolder to make new folder with properties {{name:{escaped_name}}}
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
    async def _create_nested_folder(folder_path: str) -> Dict[str, Any]:
        """Create a folder in an existing path (does not create parent folders)."""
        path_components = ValidationUtils.parse_folder_path(folder_path)
        
        if len(path_components) == 1:
            # Single level - create at root
            escaped_name = CreateFolderOperations._create_applescript_quoted_string(path_components[0])
            escaped_path = CreateFolderOperations._create_applescript_quoted_string(folder_path)
            
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
            escaped_parent_components = [CreateFolderOperations._create_applescript_quoted_string(comp) for comp in parent_components]
            escaped_final_name = CreateFolderOperations._create_applescript_quoted_string(final_folder_name)
            escaped_path = CreateFolderOperations._create_applescript_quoted_string(folder_path)
            
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
        
        result = await CreateFolderOperations.execute_applescript(script)
        
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
    
    # Backward compatibility methods
    @staticmethod
    async def create_folder_in_existing_path(folder_path: str) -> Dict[str, Any]:
        """Create a folder in an existing path (does not create parent folders)."""
        return await CreateFolderOperations._create_nested_folder(folder_path)
