from typing import Dict, Any
from .base_operations import BaseAppleScriptOperations

class MoveFolderOperations(BaseAppleScriptOperations):
    """Operations for moving folders in Apple Notes."""
    
    @staticmethod
    def _validate_folder_name(folder_name: str) -> str:
        """Validate and clean folder name."""
        if not folder_name or not folder_name.strip():
            raise ValueError("Folder name cannot be empty")
        
        # Clean the folder name
        folder_name = folder_name.strip()
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in folder_name:
                raise ValueError(f"Folder name contains invalid character '{char}'")
        
        return folder_name
    
    @staticmethod
    def _validate_folder_path(folder_path: str) -> str:
        """Validate and clean folder path."""
        if not folder_path:
            return ""
        
        # Clean the path
        folder_path = folder_path.strip()
        
        # Remove leading/trailing slashes
        folder_path = folder_path.strip('/')
        
        # Check for invalid patterns
        if '//' in folder_path:
            raise ValueError("Folder path contains invalid double slashes")
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in folder_path:
                raise ValueError(f"Folder path contains invalid character '{char}'")
        
        return folder_path
    
    @staticmethod
    def _validate_nesting_depth(source_path: str, target_path: str, folder_name: str) -> None:
        """Validate that the move operation won't exceed maximum nesting depth.
        
        Args:
            source_path: The current path of the folder
            target_path: The target path where the folder will be moved
            folder_name: The name of the folder being moved
            
        Raises:
            ValueError: If the nesting depth would exceed the maximum allowed
        """
        # Count the depth of the target path
        target_depth = 0
        if target_path:
            target_components = target_path.split('/')
            target_depth = len([comp for comp in target_components if comp.strip()])
        
        # Total depth will be target_depth + 1 (for the moved folder)
        total_depth = target_depth + 1
        
        if total_depth > 5:  # Maximum nesting depth
            raise ValueError(
                f"Cannot move folder '{folder_name}' to path '{target_path}'. "
                f"This would create a nesting depth of {total_depth} levels, "
                f"which exceeds the maximum allowed depth of 5 levels. "
                f"Please move the folder to a higher level in the hierarchy."
            )
    
    @staticmethod
    async def _check_folder_exists_at_root(folder_name: str) -> bool:
        """Check if a folder exists at root level."""
        try:
            script = f'''
            tell application "Notes"
                try
                    repeat with rootFolder in every folder
                        if name of rootFolder is "{folder_name}" then
                            return "exists"
                        end if
                    end repeat
                    return "not_found"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
            
            result = await MoveFolderOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    async def _check_path_exists(folder_path: str) -> bool:
        """Check if a folder path exists."""
        try:
            # Handle root level (empty path) - root level always exists
            if not folder_path or folder_path.strip() == "":
                return True
            
            path_components = MoveFolderOperations._validate_folder_path(folder_path).split('/')
            if not path_components or not path_components[0]:
                return False
            
            script = f'''
            tell application "Notes"
                try
                    set currentFolder to missing value
                    set pathComponents to {{{", ".join([f'"{component}"' for component in path_components])}}}
                    
                    repeat with i from 1 to count of pathComponents
                        set componentName to item i of pathComponents
                        
                        if currentFolder is missing value then
                            -- Check root folders
                            set found to false
                            repeat with rootFolder in every folder
                                if name of rootFolder is componentName then
                                    set currentFolder to rootFolder
                                    set found to true
                                    exit repeat
                                end if
                            end repeat
                            if not found then
                                return "error:Folder not found"
                            end if
                        else
                            -- Check subfolders
                            set found to false
                            repeat with subFolder in every folder of currentFolder
                                if name of subFolder is componentName then
                                    set currentFolder to subFolder
                                    set found to true
                                    exit repeat
                                end if
                            end repeat
                            if not found then
                                return "error:Folder not found"
                            end if
                        end if
                    end repeat
                    
                    return "exists"
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
            
            result = await MoveFolderOperations.execute_applescript(script)
            return result == "exists"
        except Exception:
            return False
    
    @staticmethod
    async def move_folder(source_path: str, folder_name: str, target_path: str = "") -> Dict[str, Any]:
        """Move a folder from one location to another in Apple Notes.
        
        Args:
            source_path: The current path of the folder to move
            folder_name: The name of the folder to move
            target_path: The target path where to move the folder. If empty, moves to root level.
        """
        # Validate inputs
        folder_name = MoveFolderOperations._validate_folder_name(folder_name)
        source_path = MoveFolderOperations._validate_folder_path(source_path)
        target_path = MoveFolderOperations._validate_folder_path(target_path)
        
        # Validate nesting depth
        MoveFolderOperations._validate_nesting_depth(source_path, target_path, folder_name)
        
        # Check if source path exists
        source_exists = await MoveFolderOperations._check_path_exists(source_path)
        if not source_exists:
            raise RuntimeError(f"Source path '{source_path}' does not exist")
        
        # Check if target path exists (if provided)
        if target_path:
            target_exists = await MoveFolderOperations._check_path_exists(target_path)
            if not target_exists:
                raise RuntimeError(f"Target path '{target_path}' does not exist")
        
        # Check if folder exists in source path
        if source_path:
            # Source is a nested path
            source_folder_exists = await MoveFolderOperations._check_path_exists(f"{source_path}/{folder_name}")
            if not source_folder_exists:
                raise RuntimeError(f"Folder '{folder_name}' not found in path '{source_path}'")
        else:
            # Source is root level
            source_folder_exists = await MoveFolderOperations._check_folder_exists_at_root(folder_name)
            if not source_folder_exists:
                raise RuntimeError(f"Folder '{folder_name}' not found at root level")
        
        # Check if target already has a folder with the same name
        if target_path:
            target_folder_exists = await MoveFolderOperations._check_path_exists(f"{target_path}/{folder_name}")
            if target_folder_exists:
                raise RuntimeError(f"Target path '{target_path}' already contains a folder named '{folder_name}'")
        else:
            # Check root level for duplicate
            root_folder_exists = await MoveFolderOperations._check_folder_exists_at_root(folder_name)
            if root_folder_exists:
                raise RuntimeError(f"Root level already contains a folder named '{folder_name}'")
        
        # Perform the move operation
        if not target_path:
            # Move to root level
            return await MoveFolderOperations._move_to_root(source_path, folder_name)
        else:
            # Move to target path
            return await MoveFolderOperations._move_to_path(source_path, folder_name, target_path)
    
    @staticmethod
    async def _move_to_root(source_path: str, folder_name: str) -> Dict[str, Any]:
        """Move a folder to root level."""
        script = f'''
        tell application "Notes"
            try
                -- Use a simpler approach: move the folder directly by name
                if "{source_path}" is "" then
                    -- Moving from root to root (no-op)
                    return {{"success", "{folder_name}", "root", "root"}}
                else
                    -- Moving from path to root
                    move folder "{folder_name}" of folder "{source_path}" to beginning of folders
                    return {{"success", "{folder_name}", "{source_path}", "root"}}
                end if
                
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await MoveFolderOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to move folder: {result[6:]}")
        
        # Parse the success result
        try:
            # Format: {"success", folder_name, source_path, target_path}
            clean_result = result.strip('{}')
            parts = [part.strip().strip('"') for part in clean_result.split(',') if part.strip()]
            
            if len(parts) >= 4 and parts[0] == "success":
                return {
                    "status": "success",
                    "folder_name": parts[1],
                    "source_path": parts[2],
                    "target_path": parts[3],
                    "message": f"Successfully moved folder '{parts[1]}' from '{parts[2]}' to '{parts[3]}'"
                }
            else:
                raise RuntimeError("Invalid move result format")
                
        except Exception as e:
            raise RuntimeError(f"Failed to parse move result: {str(e)}")
    
    @staticmethod
    async def _move_to_path(source_path: str, folder_name: str, target_path: str) -> Dict[str, Any]:
        """Move a folder to a specific target path."""
        script = f'''
        tell application "Notes"
            try
                -- Use a simpler approach: move the folder directly by name
                if "{source_path}" is "" then
                    -- Moving from root level
                    if "{target_path}" is "" then
                        -- Moving to root level (no-op)
                        return {{"success", "{folder_name}", "root", "root"}}
                    else
                        -- Moving from root to target path
                        move folder "{folder_name}" to folder "{target_path}"
                        return {{"success", "{folder_name}", "root", "{target_path}"}}
                    end if
                else
                    -- Moving from a path
                    if "{target_path}" is "" then
                        -- Moving from path to root
                        move folder "{folder_name}" of folder "{source_path}" to beginning of folders
                        return {{"success", "{folder_name}", "{source_path}", "root"}}
                    else
                        -- Moving from path to path
                        move folder "{folder_name}" of folder "{source_path}" to folder "{target_path}"
                        return {{"success", "{folder_name}", "{source_path}", "{target_path}"}}
                    end if
                end if
                
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await MoveFolderOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to move folder: {result[6:]}")
        
        # Parse the success result
        try:
            # Format: {"success", folder_name, source_path, target_path}
            clean_result = result.strip('{}')
            parts = [part.strip().strip('"') for part in clean_result.split(',') if part.strip()]
            
            if len(parts) >= 4 and parts[0] == "success":
                return {
                    "status": "success",
                    "folder_name": parts[1],
                    "source_path": parts[2],
                    "target_path": parts[3],
                    "message": f"Successfully moved folder '{parts[1]}' from '{parts[2]}' to '{parts[3]}'"
                }
            else:
                raise RuntimeError("Invalid move result format")
                
        except Exception as e:
            raise RuntimeError(f"Failed to parse move result: {str(e)}")
