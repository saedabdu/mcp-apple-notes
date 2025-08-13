from typing import Dict, Any, List, Optional
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils
from .validation_utils import ValidationUtils

class MoveNoteOperations(BaseAppleScriptOperations):
    """Operations for moving Apple Notes between folders."""
    
    @staticmethod
    def _validate_note_name(name: str) -> str:
        """Validate and clean note name."""
        return ValidationUtils.validate_note_name(name)
    
    @staticmethod
    def _create_applescript_quoted_string(text: str) -> str:
        """Create AppleScript quoted string that handles special characters properly."""
        return ValidationUtils.create_applescript_quoted_string(text)
    
    @staticmethod
    async def _check_path_exists(folder_path: str) -> bool:
        """Check if a folder path exists."""
        return await ValidationUtils.check_path_exists(folder_path)
    
    @staticmethod
    async def _check_note_exists(note_name: str, folder_path: str) -> bool:
        """Check if a note exists in a specific folder."""
        quoted_note_name = MoveNoteOperations._create_applescript_quoted_string(note_name)
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in folder_path:
            # Simple folder - use direct folder access
            script = f'''
            tell application "Notes"
                try
                    set folderToCheck to folder "{folder_path}"
                    
                    -- Find the note in the specified folder using a safer approach
                    set noteFound to false
                    set noteCount to 0
                    
                    set allNotes to notes of folderToCheck
                    repeat with i from 1 to count of allNotes
                        set currentNote to item i of allNotes
                        if name of currentNote is {quoted_note_name} then
                            set noteCount to noteCount + 1
                            set noteFound to true
                        end if
                    end repeat
                    
                    return noteFound
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        else:
            # Nested path - navigate to the folder first
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
                                end if
                            end repeat
                        else
                            -- Navigate into subfolders
                            repeat with subFolder in folders of currentFolder
                                if name of subFolder is componentName then
                                    set currentFolder to subFolder
                                end if
                            end repeat
                        end if
                    end repeat
                    
                    if currentFolder is missing value then
                        return "error:Folder not found"
                    end if
                    
                    -- Find the note in the specified folder using a safer approach
                    set noteFound to false
                    set noteCount to 0
                    
                    set allNotes to notes of currentFolder
                    repeat with i from 1 to count of allNotes
                        set currentNote to item i of allNotes
                        if name of currentNote is {quoted_note_name} then
                            set noteCount to noteCount + 1
                            set noteFound to true
                        end if
                    end repeat
                    
                    return noteFound
                on error errMsg
                    return "error:" & errMsg
                end try
            end tell
            '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Error checking note existence: {result[6:]}")
        
        return result == "true"
    
    @staticmethod
    async def move_note(note_name: str, source_folder_path: str, target_folder_path: str) -> Dict[str, Any]:
        """Move a note from one folder to another.
        
        Args:
            note_name: Name of the note to move
            source_folder_path: Current folder path where the note is located
            target_folder_path: Target folder path where to move the note
            
        Returns:
            Move operation result with status and details
            
        Raises:
            ValueError: If note name is empty or invalid
            RuntimeError: If source/target paths don't exist, note not found, or move operation fails
        """
        # Validate inputs
        if not note_name:
            raise ValueError("Note name cannot be empty")
        
        note_name = MoveNoteOperations._validate_note_name(note_name)
        source_folder_path = source_folder_path.strip() if source_folder_path else "Notes"
        target_folder_path = target_folder_path.strip() if target_folder_path else "Notes"
        
        # Don't allow moving to the same location
        if source_folder_path == target_folder_path:
            raise ValueError(f"Cannot move note to the same folder. Source and target paths are identical: '{source_folder_path}'")
        
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in source_folder_path and '/' not in target_folder_path:
            # Both are simple folders - use direct folder access
            return await MoveNoteOperations._move_note_simple_folders(note_name, source_folder_path, target_folder_path)
        else:
            # At least one is a nested path - use path navigation
            return await MoveNoteOperations._move_note_with_paths(note_name, source_folder_path, target_folder_path)
    
    @staticmethod
    async def _move_note_simple_folders(note_name: str, source_folder: str, target_folder: str) -> Dict[str, Any]:
        """Move a note between simple folders (no nested paths)."""
        quoted_note_name = MoveNoteOperations._create_applescript_quoted_string(note_name)
        
        script = f'''
        tell application "Notes"
            try
                set sourceFolder to folder "{source_folder}"
                set targetFolder to folder "{target_folder}"
                set targetNote to missing value
                set noteId to missing value
                set noteCount to 0
                
                -- Find the note in source folder using a safer approach
                set allNotes to notes of sourceFolder
                repeat with i from 1 to count of allNotes
                    set currentNote to item i of allNotes
                    if name of currentNote is {quoted_note_name} then
                        set noteCount to noteCount + 1
                        if noteCount is 1 then
                            set targetNote to currentNote
                            set noteId to id of currentNote
                        end if
                    end if
                end repeat
                
                if noteCount is 0 then
                    return "error:Note not found"
                end if
                
                if noteCount > 1 then
                    return "error:Duplicate notes detected: Found " & noteCount & " notes with the same title '" & {quoted_note_name} & "' in folder '" & name of sourceFolder & "'. Please rename the notes manually to have unique titles before proceeding with moves."
                end if
                
                -- Move the note to target folder
                move targetNote to targetFolder
                
                -- Get note details after move
                set noteName to name of targetNote
                set noteBody to body of targetNote
                set noteCreationDate to creation date of targetNote
                set noteModificationDate to modification date of targetNote
                
                -- Use a safer approach for string concatenation with proper escaping
                set safeNoteBody to noteBody
                if noteBody contains "|" then
                    set safeNoteBody to "Note body contains separator characters"
                end if
                
                set resultString to "success:" & noteName & "|" & safeNoteBody & "|" & noteCreationDate & "|" & noteModificationDate & "|" & "{target_folder}" & "|" & noteCount
                return resultString
                
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        # Parse the result
        if result.startswith("error:"):
            error_msg = result[6:]  # Remove "error:" prefix
            if "Duplicate notes detected" in error_msg:
                raise RuntimeError(f"{error_msg}")
            elif "Note not found" in error_msg:
                raise RuntimeError(f"Note '{note_name}' not found in source folder '{source_folder}'")
            elif "Can't get folder" in error_msg:
                raise RuntimeError(f"Folder '{source_folder}' does not exist")
            else:
                raise RuntimeError(f"Failed to move note: {error_msg}")
        elif result.startswith("success:"):
            # Parse success result
            success_data = result[8:]  # Remove "success:" prefix
            parts = success_data.split("|")
            
            if len(parts) >= 6:
                return {
                    "name": parts[0],
                    "body": parts[1],
                    "creation_date": parts[2],
                    "modification_date": parts[3],
                    "target_folder": parts[4],
                    "total_matches": int(parts[5]) if parts[5].isdigit() else 1,
                    "note_index": 1,
                    "source_folder": source_folder,
                    "status": "moved",
                    "message": f"Note '{note_name}' successfully moved from '{source_folder}' to '{target_folder}'"
                }
            else:
                raise RuntimeError("Unexpected response format from AppleScript")
        else:
            raise RuntimeError(f"Unexpected response from AppleScript: {result}")
    
    @staticmethod
    async def _move_note_with_paths(note_name: str, source_folder_path: str, target_folder_path: str) -> Dict[str, Any]:
        """Move a note using path navigation for nested folders."""
        quoted_note_name = MoveNoteOperations._create_applescript_quoted_string(note_name)
        
        # Parse path components
        source_components = FolderPathUtils.parse_folder_path(source_folder_path)
        target_components = FolderPathUtils.parse_folder_path(target_folder_path)
        
        script = f'''
        tell application "Notes"
            try
                set sourceFolder to missing value
                set targetFolder to missing value
                set noteToMove to missing value
                
                -- Navigate to source folder
                set sourcePathComponents to {{{", ".join([f'"{component}"' for component in source_components])}}}
                repeat with i from 1 to count of sourcePathComponents
                    set componentName to item i of sourcePathComponents
                    
                    if sourceFolder is missing value then
                        -- Start from root folders
                        repeat with rootFolder in folders
                            if name of rootFolder is componentName then
                                set sourceFolder to rootFolder
                            end if
                        end repeat
                    else
                        -- Navigate into subfolders
                        repeat with subFolder in folders of sourceFolder
                            if name of subFolder is componentName then
                                set sourceFolder to subFolder
                            end if
                        end repeat
                    end if
                end repeat
                
                if sourceFolder is missing value then
                    return "error:Source folder not found"
                end if
                
                -- Navigate to target folder
                set targetPathComponents to {{{", ".join([f'"{component}"' for component in target_components])}}}
                repeat with i from 1 to count of targetPathComponents
                    set componentName to item i of targetPathComponents
                    
                    if targetFolder is missing value then
                        -- Start from root folders
                        repeat with rootFolder in folders
                            if name of rootFolder is componentName then
                                set targetFolder to rootFolder
                            end if
                        end repeat
                    else
                        -- Navigate into subfolders
                        repeat with subFolder in folders of targetFolder
                            if name of subFolder is componentName then
                                set targetFolder to subFolder
                            end if
                        end repeat
                    end if
                end repeat
                
                if targetFolder is missing value then
                    return "error:Target folder not found"
                end if
                
                -- Find the note in source folder
                set targetNote to missing value
                set noteId to missing value
                set noteCount to 0
                
                -- Find the note in source folder using a safer approach
                set allNotes to notes of sourceFolder
                repeat with i from 1 to count of allNotes
                    set currentNote to item i of allNotes
                    if name of currentNote is {quoted_note_name} then
                        set noteCount to noteCount + 1
                        if noteCount is 1 then
                            set targetNote to currentNote
                            set noteId to id of currentNote
                        end if
                    end if
                end repeat
                
                if noteCount is 0 then
                    return "error:Note not found"
                end if
                
                if noteCount > 1 then
                    return "error:Duplicate notes detected: Found " & noteCount & " notes with the same title '" & {quoted_note_name} & "' in folder '" & name of sourceFolder & "'. Please rename the notes manually to have unique titles before proceeding with moves."
                end if
                
                -- Move the note to target folder
                move targetNote to targetFolder
                
                -- Get note details after move
                set noteName to name of targetNote
                set noteBody to body of targetNote
                set noteCreationDate to creation date of targetNote
                set noteModificationDate to modification date of targetNote
                
                -- Use a safer approach for string concatenation with proper escaping
                set safeNoteBody to noteBody
                if noteBody contains "|" then
                    set safeNoteBody to "Note body contains separator characters"
                end if
                
                set resultString to "success:" & noteName & "|" & safeNoteBody & "|" & noteCreationDate & "|" & noteModificationDate & "|" & "{target_folder_path}" & "|" & noteCount
                return resultString
                
            on error scriptError
                return "error:" & scriptError
            end try
        end tell
        '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        # Parse the result
        if result.startswith("error:"):
            error_msg = result[6:]  # Remove "error:" prefix
            if "Duplicate notes detected" in error_msg:
                raise RuntimeError(f"{error_msg}")
            elif "Note not found" in error_msg:
                raise RuntimeError(f"Note '{note_name}' not found in source folder '{source_folder_path}'")
            elif "Source folder not found" in error_msg:
                raise RuntimeError(f"Source folder '{source_folder_path}' does not exist")
            elif "Target folder not found" in error_msg:
                raise RuntimeError(f"Target folder '{target_folder_path}' does not exist")
            elif "Can't get folder" in error_msg:
                raise RuntimeError(f"Folder path error: {error_msg}")
            else:
                raise RuntimeError(f"Failed to move note: {error_msg}")
        elif result.startswith("success:"):
            # Parse success result
            success_data = result[8:]  # Remove "success:" prefix
            parts = success_data.split("|")
            
            if len(parts) >= 6:
                return {
                    "name": parts[0],
                    "body": parts[1],
                    "creation_date": parts[2],
                    "modification_date": parts[3],
                    "target_folder": parts[4],
                    "total_matches": int(parts[5]) if parts[5].isdigit() else 1,
                    "note_index": 1,
                    "source_folder": source_folder_path,
                    "status": "moved",
                    "message": f"Note '{note_name}' successfully moved from '{source_folder_path}' to '{target_folder_path}'"
                }
            else:
                raise RuntimeError("Unexpected response format from AppleScript")
        else:
            raise RuntimeError(f"Unexpected response from AppleScript: {result}")
    
    @staticmethod
    async def _move_note_by_id(note_id: str, target_folder_path: str, note_name: str, source_folder_path: str) -> Dict[str, Any]:
        """Move a note by its ID to the target folder."""
        # Check if it's a simple folder (no slashes) or nested path
        if '/' not in target_folder_path:
            # Simple folder - use direct folder access
            script = f'''
            tell application "Notes"
                try
                    set targetFolder to folder "{target_folder_path}"
                    set noteToMove to note id "{note_id}"
                    
                    -- Move the note to target folder
                    move noteToMove to targetFolder
                    
                    -- Get note details after move
                    set noteName to name of noteToMove
                    set noteBody to body of noteToMove
                    set noteCreationDate to creation date of noteToMove
                    set noteModificationDate to modification date of noteToMove
                    
                    -- Use a safer approach for string concatenation with proper escaping
                    set safeNoteBody to noteBody
                    if noteBody contains "|" then
                        set safeNoteBody to "Note body contains separator characters"
                    end if
                    
                    set resultString to "success:" & noteName & "|" & safeNoteBody & "|" & noteCreationDate & "|" & noteModificationDate & "|" & "{target_folder_path}" & "|1"
                    return resultString
                    
                on error scriptError
                    return "error:" & scriptError
                end try
            end tell
            '''
        else:
            # Nested path - navigate to the folder first
            path_components = FolderPathUtils.parse_folder_path(target_folder_path)
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
                                end if
                            end repeat
                        else
                            -- Navigate into subfolders
                            repeat with subFolder in folders of currentFolder
                                if name of subFolder is componentName then
                                    set currentFolder to subFolder
                                end if
                            end repeat
                        end if
                    end repeat
                    
                    if currentFolder is missing value then
                        return "error:Target folder not found"
                    end if
                    
                    set noteToMove to note id "{note_id}"
                    
                    -- Move the note to target folder
                    move noteToMove to currentFolder
                    
                    -- Get note details after move
                    set noteName to name of noteToMove
                    set noteBody to body of noteToMove
                    set noteCreationDate to creation date of noteToMove
                    set noteModificationDate to modification date of noteToMove
                    
                    -- Use a safer approach for string concatenation with proper escaping
                    set safeNoteBody to noteBody
                    if noteBody contains "|" then
                        set safeNoteBody to "Note body contains separator characters"
                    end if
                    
                    set resultString to "success:" & noteName & "|" & safeNoteBody & "|" & noteCreationDate & "|" & noteModificationDate & "|" & "{target_folder_path}" & "|1"
                    return resultString
                    
                on error scriptError
                    return "error:" & scriptError
                end try
            end tell
            '''
        
        result = await MoveNoteOperations.execute_applescript(script)
        
        # Parse the result
        if result.startswith("error:"):
            error_msg = result[6:]  # Remove "error:" prefix
            raise RuntimeError(error_msg)
        elif result.startswith("success:"):
            # Parse success result
            success_data = result[8:]  # Remove "success:" prefix
            parts = success_data.split("|")
            
            if len(parts) >= 6:
                return {
                    "name": parts[0],
                    "body": parts[1],
                    "creation_date": parts[2],
                    "modification_date": parts[3],
                    "target_folder": parts[4],
                    "total_matches": int(parts[5]) if parts[5].isdigit() else 1,
                    "note_index": 1,
                    "source_folder": source_folder_path,
                    "status": "moved",
                    "message": f"Note '{note_name}' successfully moved from '{source_folder_path}' to '{target_folder_path}'"
                }
            else:
                raise RuntimeError("Unexpected response format from AppleScript")
        else:
            raise RuntimeError(f"Unexpected response from AppleScript: {result}")
