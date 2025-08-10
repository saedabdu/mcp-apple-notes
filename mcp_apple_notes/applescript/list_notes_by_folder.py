from typing import List, Dict, Any
from .base_operations import BaseAppleScriptOperations

class ListNotesByFolderOperations(BaseAppleScriptOperations):
    """Operations for listing Apple Notes by folder."""
    
    @staticmethod
    async def list_notes_by_folder(folder_name: str) -> List[Dict[str, str]]:
        """Get all notes from a specific folder."""
        script = f'''
        tell application "Notes"
            try
                set targetFolder to folder "{folder_name}"
                set noteList to {{}}
                repeat with theNote in notes of targetFolder
                    set noteInfo to {{name:(name of theNote), folder:"{folder_name}", creation_date:(creation date of theNote as string), modification_date:(modification date of theNote as string)}}
                    copy noteInfo to end of noteList
                end repeat
                return noteList
            on error errMsg
                return "error:" & errMsg
            end try
        end tell
        '''
        result = await ListNotesByFolderOperations.execute_applescript(script)
        
        # Check if there was an error
        if result.startswith("error:"):
            raise RuntimeError(f"Failed to list notes by folder: {result[6:]}")
        
        # Parse AppleScript result manually since dates contain commas
        notes = []
        
        # Split the result into individual note entries
        # Each note entry starts with 'name:' and contains 4 fields
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
                folder_end = entry.find(', creation_date:', folder_start)
                if folder_end == -1:
                    continue
                    
                folder = entry[folder_start:folder_end].strip()
                
                # Find creation_date
                creation_start = entry.find('creation_date:') + 14
                creation_end = entry.find(', modification_date:', creation_start)
                if creation_end == -1:
                    continue
                    
                creation_date = entry[creation_start:creation_end].strip()
                
                # Find modification_date (go to end or next 'name:')
                modification_start = entry.find('modification_date:') + 18
                modification_end = entry.find(', name:', modification_start)
                if modification_end == -1:
                    modification_end = len(entry)
                    
                modification_date = entry[modification_start:modification_end].strip().rstrip(',')
                
                notes.append({
                    'name': name,
                    'folder': folder,
                    'creation_date': creation_date,
                    'modification_date': modification_date
                })
                
            except Exception as e:
                # Skip malformed entries
                continue
        
        return notes
