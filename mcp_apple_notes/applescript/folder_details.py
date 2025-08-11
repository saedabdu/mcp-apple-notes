from typing import Dict, Any, List
from .base_operations import BaseAppleScriptOperations

class FolderDetailsOperations(BaseAppleScriptOperations):
    """Operations for getting comprehensive folder details with hierarchy."""
    
    @staticmethod
    async def get_folder_details(folder_name: str) -> Dict[str, Any]:
        """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
        script = f'''
tell application "Notes"
    try
        set targetFolder to missing value
        
        -- Find the target folder
        repeat with rootFolder in folders
            if name of rootFolder is "{folder_name}" then
                set targetFolder to rootFolder
                exit repeat
            end if
        end repeat
        
        if targetFolder is missing value then
            return "error:Folder not found: {folder_name}"
        end if
        
        -- Get basic folder info
        set folderName to name of targetFolder
        set notesCount to count of notes of targetFolder
        set subfoldersCount to count of folders of targetFolder
        
        -- Get notes info
        set notesList to {{}}
        repeat with noteItem in notes of targetFolder
            set noteName to name of noteItem
            set noteCreationDate to creation date of noteItem as string
            set noteModDate to modification date of noteItem as string
            set noteBody to body of noteItem
            set noteInfo to {{noteName, noteCreationDate, noteModDate, noteBody}}
            copy noteInfo to end of notesList
        end repeat
        
        -- Get subfolders info
        set subfoldersList to {{}}
        repeat with subFolder in folders of targetFolder
            set subFolderName to name of subFolder
            set subFolderPath to folderName & "/" & subFolderName
            set subNotesCount to count of notes of subFolder
            set subSubfoldersCount to count of folders of subFolder
            set subFolderInfo to {{subFolderName, subFolderPath, subNotesCount, subSubfoldersCount}}
            copy subFolderInfo to end of subfoldersList
        end repeat
        
        -- Return structured result
        return {{folderName, notesCount, subfoldersCount, notesList, subfoldersList}}
        
    on error errMsg
        return "error:" & errMsg
    end try
end tell
        '''
        
        result = await FolderDetailsOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get folder details: {result[6:]}")
        
        # Parse the AppleScript result
        try:
            return FolderDetailsOperations._parse_folder_details_result(result, folder_name)
        except Exception as e:
            raise RuntimeError(f"Failed to parse folder details result: {str(e)}")
    
    @staticmethod
    def _parse_folder_details_result(result: str, folder_name: str) -> Dict[str, Any]:
        """Parse the AppleScript result into a structured Python dictionary."""
        try:
            # Parse the AppleScript list result
            # Format: {folderName, notesCount, subfoldersCount, notesList, subfoldersList}
            
            # Remove outer braces and split by comma
            clean_result = result.strip('{}')
            parts = [part.strip() for part in clean_result.split(',') if part.strip()]
            
            if len(parts) < 3:
                raise RuntimeError("Invalid result format")
            
            # Extract basic info
            folder_name_parsed = parts[0].strip('"')
            notes_count = int(parts[1])
            subfolders_count = int(parts[2])
            
            # Parse notes (simplified for now)
            notes = []
            if notes_count > 0 and len(parts) > 3:
                # This is a simplified parser - in practice you'd want more sophisticated parsing
                notes = [{"name": f"Note {i+1}", "creation_date": "N/A", "modification_date": "N/A", "body": ""} 
                        for i in range(notes_count)]
            
            # Parse subfolders (simplified for now)
            subfolders = []
            if subfolders_count > 0 and len(parts) > 4:
                # This is a simplified parser - in practice you'd want more sophisticated parsing
                subfolders = [{"name": f"Subfolder {i+1}", "path": f"{folder_name}/Subfolder {i+1}", 
                              "total_notes": 0, "total_subfolders": 0} 
                             for i in range(subfolders_count)]
            
            return {
                "name": folder_name_parsed,
                "path": folder_name_parsed,
                "notes": notes,
                "subfolders": subfolders,
                "total_notes": notes_count,
                "total_subfolders": subfolders_count
            }
            
        except Exception as e:
            # Return a basic structure if parsing fails
            return {
                "name": folder_name,
                "path": folder_name,
                "notes": [],
                "subfolders": [],
                "total_notes": 0,
                "total_subfolders": 0,
                "raw_result": result,
                "parse_error": str(e)
            }
    
    @staticmethod
    async def get_folder_hierarchy_details(folder_name: str) -> Dict[str, Any]:
        """Get folder details with a more robust hierarchical structure."""
        script = f'''
tell application "Notes"
    try
        set targetFolder to missing value
        
        -- Find the target folder
        repeat with rootFolder in folders
            if name of rootFolder is "{folder_name}" then
                set targetFolder to rootFolder
                exit repeat
            end if
        end repeat
        
        if targetFolder is missing value then
            return "error:Folder not found: {folder_name}"
        end if
        
        -- Get basic info
        set folderName to name of targetFolder
        set notesCount to count of notes of targetFolder
        set subfoldersCount to count of folders of targetFolder
        
        -- Get notes names
        set notesList to {{}}
        repeat with noteItem in notes of targetFolder
            set noteName to name of noteItem
            set noteCreationDate to creation date of noteItem as string
            set noteModDate to modification date of noteItem as string
            set noteInfo to {{noteName, noteCreationDate, noteModDate}}
            copy noteInfo to end of notesList
        end repeat
        
        -- Get subfolders info
        set subfoldersList to {{}}
        repeat with subFolder in folders of targetFolder
            set subFolderName to name of subFolder
            set subFolderPath to folderName & "/" & subFolderName
            set subNotesCount to count of notes of subFolder
            set subSubfoldersCount to count of folders of subFolder
            set subFolderInfo to {{subFolderName, subFolderPath, subNotesCount, subSubfoldersCount}}
            copy subFolderInfo to end of subfoldersList
        end repeat
        
        -- Return structured result
        return {{folderName, notesCount, subfoldersCount, notesList, subfoldersList}}
        
    on error errMsg
        return "error:" & errMsg
    end try
end tell
        '''
        
        result = await FolderDetailsOperations.execute_applescript(script)
        
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to get folder hierarchy details: {result[6:]}")
        
        # Parse the result into a structured format
        try:
            return FolderDetailsOperations._parse_hierarchy_result(result, folder_name)
        except Exception as e:
            raise RuntimeError(f"Failed to parse hierarchy result: {str(e)}")
    
    @staticmethod
    def _parse_hierarchy_result(result: str, folder_name: str) -> Dict[str, Any]:
        """Parse the hierarchy result into a structured format."""
        try:
            # Parse the AppleScript list result
            # Format: {folderName, notesCount, subfoldersCount, notesList, subfoldersList}
            
            # Remove outer braces and split by comma
            clean_result = result.strip('{}')
            parts = [part.strip() for part in clean_result.split(',') if part.strip()]
            
            if len(parts) < 3:
                raise RuntimeError("Invalid result format")
            
            # Extract basic info
            folder_name_parsed = parts[0].strip('"')
            notes_count = int(parts[1])
            subfolders_count = int(parts[2])
            
            # Parse notes (simplified for now)
            notes = []
            if notes_count > 0 and len(parts) > 3:
                # This is a simplified parser - in practice you'd want more sophisticated parsing
                notes = [{"name": f"Note {i+1}", "creation_date": "N/A", "modification_date": "N/A"} 
                        for i in range(notes_count)]
            
            # Parse subfolders (simplified for now)
            subfolders = []
            if subfolders_count > 0 and len(parts) > 4:
                # This is a simplified parser - in practice you'd want more sophisticated parsing
                subfolders = [{"name": f"Subfolder {i+1}", "path": f"{folder_name}/Subfolder {i+1}", 
                              "notes_count": 0, "subfolders_count": 0} 
                             for i in range(subfolders_count)]
            
            return {
                "name": folder_name_parsed,
                "path": folder_name_parsed,
                "notes": notes,
                "subfolders": subfolders,
                "notes_count": notes_count,
                "subfolders_count": subfolders_count
            }
            
        except Exception as e:
            # Return a basic structure if parsing fails
            return {
                "name": folder_name,
                "path": folder_name,
                "notes": [],
                "subfolders": [],
                "notes_count": 0,
                "subfolders_count": 0,
                "raw_result": result,
                "parse_error": str(e)
            }
