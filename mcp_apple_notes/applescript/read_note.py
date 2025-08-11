from typing import Dict, Optional, List
from .base_operations import BaseAppleScriptOperations
from .folder_utils import FolderPathUtils

class ReadNoteOperations(BaseAppleScriptOperations):
    """Operations for reading Apple Notes content."""
    
    @staticmethod
    async def read_note_by_name(note_name: str, folder_name: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set noteList to {{}}
                repeat with theNote in notes of targetFolder
                    if name of theNote is "{note_name}" then
                        set noteInfo to {{name:(name of theNote), folder:"{folder_name}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                        copy noteInfo to end of noteList
                    end if
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note: {result[6:]}")
        
        # Parse the result manually since body content may contain commas and special characters
        try:
            # Parse multiple notes from the result
            # Format: {name:noteName, folder:folderName, body:noteBody, creation_date:date, modification_date:date}, {name:noteName2, ...}
            notes = []
            
            # Split the result into individual note entries
            # Each note entry starts with 'name:' and contains 5 fields
            entries = result.split('name:')
            
            for entry in entries[1:]:  # Skip the first empty entry
                try:
                    # Find the end of the name (before ', folder:')
                    name_end = entry.find(', folder:')
                    if name_end == -1:
                        continue
                        
                    name = entry[:name_end].strip()
                    
                    # Find folder
                    folder_start = entry.find('folder:') + 7
                    folder_end = entry.find(', body:', folder_start)
                    if folder_end == -1:
                        continue
                        
                    folder = entry[folder_start:folder_end].strip()
                    
                    # Find body (this is tricky because body can contain commas and special characters)
                    body_start = entry.find(', body:') + 7
                    body_end = entry.find(', creation_date:', body_start)
                    if body_end == -1:
                        # If no creation_date, body goes to the end
                        body_end = entry.find(', modification_date:', body_start)
                        if body_end == -1:
                            body_end = len(entry)
                    
                    body = entry[body_start:body_end].strip()
                    
                    # Find creation_date
                    creation_start = entry.find('creation_date:') + 14
                    creation_end = entry.find(', modification_date:', creation_start)
                    if creation_end == -1:
                        creation_end = len(entry)
                    creation_date = entry[creation_start:creation_end].strip().rstrip(',')
                    
                    # Find modification_date (go to end or next 'name:')
                    modification_start = entry.find('modification_date:') + 18
                    modification_end = entry.find(', name:', modification_start)
                    if modification_end == -1:
                        modification_end = len(entry)
                        
                    modification_date = entry[modification_start:modification_end].strip().rstrip(',')
                    
                    notes.append({
                        'name': name,
                        'folder': folder,
                        'body': body,
                        'creation_date': creation_date,
                        'modification_date': modification_date
                    })
                    
                except Exception as e:
                    # Skip malformed entries
                    continue
            
            return notes
        except Exception as e:
            raise RuntimeError(f"Failed to parse note content: {str(e)}")
    
    @staticmethod
    async def read_note_by_name_in_path(note_name: str, folder_path: str) -> List[Dict[str, str]]:
        """Read all notes with the given name in the specified folder path."""
        # First resolve the folder path
        folder_info = await FolderPathUtils.resolve_folder_path(folder_path)
        
        # Then search for notes in that folder
        script = f'''
        tell application "Notes"
            try
                set currentFolder to missing value
                set pathComponents to {{{", ".join([f'"{component}"' for component in folder_info['components']])}}}
                
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
                        repeat with subFolder in folders of currentFolder
                            if name of subFolder is componentName then
                                set currentFolder to subFolder
                                exit repeat
                            end if
                        end repeat
                    end if
                end repeat
                
                if currentFolder is missing value then
                    return "error:Folder not found"
                end if
                
                set noteList to {{}}
                repeat with theNote in notes of currentFolder
                    if name of theNote is "{note_name}" then
                        set noteInfo to {{name:(name of theNote), folder:"{folder_path}", body:(body of theNote as string), creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                        copy noteInfo to end of noteList
                    end if
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        
        result = await ReadNoteOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to read note by path: {result[6:]}")
        
        # Parse the result using the same logic as the original method
        try:
            # Parse multiple notes from the result
            # Format: {name:noteName, folder:folderPath, body:noteBody, creation_date:date, modification_date:date}, {name:noteName2, ...}
            notes = []
            
            # Split the result into individual note entries
            # Each note entry starts with 'name:' and contains 5 fields
            entries = result.split('name:')
            
            for entry in entries[1:]:  # Skip the first empty entry
                try:
                    # Find the end of the name (before ', folder:')
                    name_end = entry.find(', folder:')
                    if name_end == -1:
                        continue
                        
                    name = entry[:name_end].strip()
                    
                    # Find folder
                    folder_start = entry.find('folder:') + 7
                    folder_end = entry.find(', body:', folder_start)
                    if folder_end == -1:
                        continue
                        
                    folder = entry[folder_start:folder_end].strip()
                    
                    # Find body (this is tricky because body can contain commas and special characters)
                    body_start = entry.find(', body:') + 7
                    body_end = entry.find(', creation_date:', body_start)
                    if body_end == -1:
                        # If no creation_date, body goes to the end
                        body_end = entry.find(', modification_date:', body_start)
                        if body_end == -1:
                            body_end = len(entry)
                    
                    body = entry[body_start:body_end].strip()
                    
                    # Find creation_date
                    creation_start = entry.find('creation_date:') + 14
                    creation_end = entry.find(', modification_date:', creation_start)
                    if creation_end == -1:
                        creation_end = len(entry)
                    creation_date = entry[creation_start:creation_end].strip().rstrip(',')
                    
                    # Find modification_date (go to end or next 'name:')
                    modification_start = entry.find('modification_date:') + 18
                    modification_end = entry.find(', name:', modification_start)
                    if modification_end == -1:
                        modification_end = len(entry)
                        
                    modification_date = entry[modification_start:modification_end].strip().rstrip(',')
                    
                    notes.append({
                        'name': name,
                        'folder': folder,
                        'body': body,
                        'creation_date': creation_date,
                        'modification_date': modification_date
                    })
                    
                except Exception as e:
                    # Skip malformed entries
                    continue
            
            return notes
        except Exception as e:
            raise RuntimeError(f"Failed to parse note content: {str(e)}")
